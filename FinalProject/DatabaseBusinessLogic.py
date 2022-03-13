import yaml
import requests

class DatabaseBusinessLogic(object):
    mysqlUrl = ""

    def MakeRequest(self, body, json=True):
        if json:
            body["ReturnType"] = "JSON"
        response = requests.post(self.mysqlUrl, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    #####################################################
    #
    #       Bucket Functions
    #
    #####################################################

    def CreateBucket(self, categoryId, bucketName):
        body = {"Query": "INSERT INTO buckets (categoryId, name) VALUES (%s, %s)",
                "Parameters": [categoryId, bucketName]}
        return self.MakeRequest(body);

    def GetCategoriesAndBuckets(self):
        body = {"Query": """
       select categories.categoryId, categories.name as categoryName, buckets.bucketId, buckets.name as bucketName, buckets.assigned, balance from categories
left join buckets on categories.categoryId = buckets.categoryId
order by buckets.categoryId, buckets.name;"""}
        return self.MakeRequest(body)

    def GetBuckets(self):
        body = {"Query": "SELECT bucketId, name from buckets ORDER BY name"}
        return self.MakeRequest(body)

    def GetBucketByName(self, name):
        body = {"Query": "SELECT * from buckets WHERE name like %s LIMIT 1",
                "Parameters": [name]}
        return self.MakeRequest(body)

    def GetBucketById(self, bucketId):
        body = {"Query": "SELECT * from buckets WHERE bucketId = %s LIMIT 1",
                "Parameters": [bucketId]}
        return self.MakeRequest(body)

    #####################################################
    #
    #       Account Functions
    #
    #####################################################
    def CreateAccount(self, accountType, accountName):
        body = {"Query": "SELECT accountTypeId from account_types WHERE accountTypeName = %s LIMIT 1",
                "Parameters": [accountType]}
        result = self.MakeRequest(body)[0]

        body = {"Query": "INSERT INTO accounts (accountTypeId, accountName) VALUES (%s, %s)",
                "Parameters": [result["accountTypeId"], accountName]}
        return self.MakeRequest(body)

    def GetAccount(self, accountId = 0, selectJustOne=True):
        query = "SELECT * from Accounts"
        body = {}
        if selectJustOne:
            query += " WHERE accountId = %s"
            body["Query"] = query
            body["Parameters"] = [accountId]
        else:
            body["Query"] = query
        return self.MakeRequest(body)

    def GetAccounts(self):
        return self.GetAccount(selectJustOne=False)

    #####################################################
    #
    #       Transaction Functions
    #
    #####################################################

    # this may be a code smell, but having individual parameters means that the business logic can control the order of the parameters
    # rather than just taking in a prepopulated array and assuming all parameters are included in the right order
    # MySQL is VERY picky about parameters.
    # You cannot call this function unless all the required parameters are passed in.
    def CreateTransaction(self, bucketId, accountId, payee, total, transactionType, transactionDate, notes="", cleared=False):
        payeeId = self.GetPayeeId(payee)
        body = {
            "Query": "INSERT INTO transactions (accountId, payeeId, transactionType, transactionDate, notes, cleared) VALUES(%s,%s,%s,%s,%s,%s)",
            "Parameters": [accountId, payeeId, transactionType, transactionDate, notes, cleared]
            }
        self.MakeRequest(body)

        transactionInfo = self.GetMostRecentTransaction()

        # Relationship table, so that in the future 1 transaction can deduct from many buckets. Not an option now.
        body = {"Query": """INSERT INTO transactions_buckets (transactionId, bucketId, amount)
        VALUES (%s, %s, %s)""", "Parameters": [transactionInfo["transactionId"], bucketId, total]};
        self.MakeRequest(body)

    def GetTransactions(self, accountId):
        query = """select transactions.transactionId, DATE_FORMAT(transactionDate, "%m/%d/%y") as transactionDate, payees.name as payee, buckets.name as bucket, notes, amount, transactionType, cleared from transactions
    join transactions_buckets on transactions.transactionId = transactions_buckets.transactionId
    join buckets on transactions_buckets.bucketId = buckets.bucketId
    join payees on transactions.payeeId = payees.payeeId
    where accountId = %s
    ORDER BY transactionDate desc,
    transactionType desc,
    amount desc"""

        body = {"Query": query, "Parameters": [accountId]}
        response = self.MakeRequest(body)

        for row in response:
            transactionType = row["transactionType"]
            row[transactionType] = "$" + str(row["amount"])

        return response

    def GetMostRecentTransaction(self):
        # Get the transaction with the largest transaction id -- this is the one that was just inserted
        body = {"Query": "SELECT transactionId from transactions order by transactionId desc limit 1;"}
        return self.MakeRequest(body)[0]

    def GetPayeeId(self, payee):
        parameters = []
        parameters.append(payee)
        body = {"Query": "SELECT payeeId from payees WHERE name=%s", "Parameters": parameters}
        payeeResponse = self.MakeRequest(body)

        # Payee does not exist
        if(len(payeeResponse) == 0):
            body = {"Query": "INSERT INTO payees (name) VALUES(%s)", "Parameters": parameters}
            self.MakeRequest(body)
            body = {"Query": "SELECT payeeId from payees ORDER BY payeeId desc LIMIT 1"}
            payeeResponse = self.MakeRequest(body)
        return payeeResponse[0]["payeeId"]

    def DeleteTransaction(self, transactionId):
        body = {"Query": "DELETE FROM transactions where transactionId = %s",
                "Parameters": [transactionId]}
        self.MakeRequest(body)

    def UpdateClearedTransactionStatus(self, transactionId, status):
        body = {"Query": "UPDATE transactions set cleared = %s WHERE transactionId = %s",
                "Parameters": [status, transactionId]}
        self.MakeRequest(body)

    def GetTransactionSum(self, bucketId):
        bucketList = self.GetAllTransactionSums()
        bucket = self.FindBucket(bucketList, bucketId)
        if bucket is not None:
            return bucket["amount"]
        else:
            return None

    def FindBucket(self, list, bucketId):
        for item in list:
            if item["bucketId"] == bucketId:
                return item
        return None

    def GetAllTransactionSums(self):
        body = {"Query":
                    """SELECT buckets.bucketId as bucketId, buckets.name as bucketName, sum(if(transactionType = 'inflow', amount, (-1 * amount))) amount FROM transactions
    join transactions_buckets on transactions.transactionId = transactions_buckets.transactionId
    join buckets on transactions_buckets.bucketId = buckets.bucketId
    group by bucketId;"""}
        return self.MakeRequest(body)

    def __init__(self):
        try:
            from yaml import CLoader as loader, CDumper as dumper
        except ImportError:
            from yaml import loader, dumper
        stream = open("Config.yaml")
        config = yaml.load(stream, loader)
        self.mysqlUrl = config["MySqlUrl"]

