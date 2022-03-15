import yaml
import requests


class DatabaseBusinessLogic(object):

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
        SELECT categories.categoryId, categories.name as categoryName, buckets.bucketId, 
        buckets.name as bucketName, buckets.assigned, balance from categories
        LEFT JOIN buckets ON categories.categoryId = buckets.categoryId
        ORDER BY buckets.categoryId, buckets.name;"""}
        return self.MakeRequest(body)

    def GetBuckets(self):
        body = {"Query": "SELECT * from buckets ORDER BY name"}
        return self.MakeRequest(body)

    def GetBucketByName(self, name):
        body = {"Query": "SELECT * from buckets WHERE name like %s LIMIT 1",
                "Parameters": [name]}
        result = self.MakeRequest(body)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def GetBucketById(self, bucketId):
        body = {"Query": "SELECT * from buckets WHERE bucketId = %s LIMIT 1",
                "Parameters": [bucketId]}
        return self.MakeRequest(body)[0]

    def UpdateAssignedAmountsBucketList(self, bucketArray):
        for bucketId in bucketArray.keys():
            bucketInfo = self.GetBucketById(bucketId)
            newAmount = float(bucketArray[bucketId])
            oldAmount = float(bucketInfo["assigned"])
            # only update what we need
            if oldAmount != newAmount:
                self.UpdateBucketAssignedAmount(bucketId, newAmount)

    def UpdateBucketAssignedAmount(self, bucketId, newAmount):
        body = {"Query": "UPDATE buckets SET assigned = %s WHERE bucketId = %s",
                "Parameters": [newAmount, bucketId]}
        self.MakeRequest(body)

    def UpdateBucketBalance(self, bucketId, assignedAmount = None):
        # This is a negative number
        sumOfAllMoneySpent = self.GetTransactionSumForABucket(bucketId)
        if assignedAmount is not None:
            return float(assignedAmount) + sumOfAllMoneySpent


    #####################################################
    #
    #       Categories Functions
    #
    #####################################################
    def CreateCategory(self, categoryName):
        body = {"Query": "INSERT INTO categories (name) VALUES (%s)",
                "Parameters": [categoryName]}
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
    def CreateTransaction(self, bucketId, accountId, payee, total,
                          transactionType, transactionDate, notes="", cleared=False):
        payeeId = self.GetPayeeId(payee)
        body = {
            "Query": """INSERT INTO transactions (accountId, payeeId, transactionType, 
                     transactionDate, notes, cleared) 
                     VALUES(%s,%s,%s,%s,%s,%s)""",
            "Parameters": [accountId, payeeId, transactionType, transactionDate, notes, cleared]
            }
        self.MakeRequest(body)
        transactionInfo = self.GetMostRecentTransaction()

        # Relationship table, so that in the future 1 transaction can deduct from many buckets. Not an option now.
        body = {"Query": """
        INSERT INTO transactions_buckets (transactionId, bucketId, amount)
        VALUES (%s, %s, %s)""",
                "Parameters": [transactionInfo["transactionId"], bucketId, total]};
        return self.MakeRequest(body)

    def GetBaseTransactionQuery(self):
        return """
        SELECT transactions.transactionId, DATE_FORMAT(transactionDate, "%m/%d/%y") as transactionDate, 
        payees.name as payee, buckets.name as bucket, notes, amount, transactionType, cleared from transactions
        JOIN transactions_buckets ON transactions.transactionId = transactions_buckets.transactionId
        JOIN buckets ON transactions_buckets.bucketId = buckets.bucketId
        JOIN payees ON transactions.payeeId = payees.payeeId"""

    def GetTransactionsByBucketId(self, bucketId):
        query = self.GetBaseTransactionQuery()
        query += "WHERE buckets.bucketId = %s"
        body = {"Query": query, "Parameters": [bucketId]}
        response = self.MakeTransactionQuery(body)
        return response

    def GetTransactionByTransactionId(self, transactionId):
        query = self.GetBaseTransactionQuery()
        query += " where transactionId = %s """
        body = {"Query": query, "Parameters": [transactionId]}
        response = self.MakeTransactionQuery(body)
        return response[0]

    def GetTransactionsByAccountId(self, accountId):
        query = self.GetBaseTransactionQuery()
        query += """
            WHERE accountId = %s
            ORDER BY transactionDate desc,
            transactionType desc,
            amount desc"""
        body = {"Query": query, "Parameters": [accountId]}
        response = self.MakeTransactionQuery(body)
        return response

    def MakeTransactionQuery(self, body):
        response = self.MakeRequest(body)
        response = self.ParseTransactionType(response)
        return response

    def ParseTransactionType(self, list):
        for row in list:
            transactionType = row["transactionType"]
            # we now have a result.inflow = X or a result.outflow = x -- this makes it easier for building the html template
            row[transactionType] = "$" + str(row["amount"])
        return list

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
        return self.MakeRequest(body)

    def UpdateClearedTransactionStatus(self, transactionId, status):
        body = {"Query": "UPDATE transactions set cleared = %s WHERE transactionId = %s",
                "Parameters": [status, transactionId]}
        return self.MakeRequest(body)

    def GetTransactionSumForABucket(self, key, searchValue):
        bucketList = self.GetAllTransactionSums()
        bucket = self.FindBucket(bucketList, key, searchValue)
        if bucket is None:
            return 0
        else:
            return bucket["amount"]

    '''
    ' Iterates over a list of items and returns the item that has a 
    ' property (key) that matches the search value (value)
    '''
    def FindBucket(self, list, key, value):
        for item in list:
            if item[key] == value:
                return item
        return None

    def GetAllTransactionSums(self):
        body = {"Query": """
                    SELECT buckets.bucketId as bucketId, buckets.name as bucketName, 
                    SUM(IF(transactionType = 'inflow', amount, (-1 * amount))) amount 
                    FROM transactions
                    JOIN transactions_buckets ON transactions.transactionId = transactions_buckets.transactionId
                    JOIN buckets ON transactions_buckets.bucketId = buckets.bucketId
                    GROUP BY bucketId;"""}
        return self.MakeRequest(body)

    def __init__(self):
        try:
            from yaml import CLoader as loader, CDumper as dumper
        except ImportError:
            from yaml import loader, dumper
        stream = open("Config.yaml")
        config = yaml.load(stream, loader)
        self.mysqlUrl = config["MySqlUrl"]

