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

    def GetCategoriesAndBuckets(self):
        body = {"Query": """
       select buckets.categoryId, categories.name as categoryName, buckets.bucketId, buckets.name as bucketName, buckets.assigned, balance from buckets
join categories on buckets.categoryId = categories.categoryId
WHERE buckets.categoryId is not NULL
order by buckets.categoryId, buckets.name;"""
               }
        return self.MakeRequest(body)

    def GetBuckets(self, includeUnbucketed = False):

        query = "select bucketId, name from buckets"

        if(includeUnbucketed == False):
            query += " WHERE categoryId is not NULL"

        query += " ORDER BY name"
        body = {"Query": query}
        return self.MakeRequest(body)

    def GetAccounts(self):
        body = {"Query": "SELECT * from Accounts"}
        return self.MakeRequest(body)

    def CreateTransaction(self, bucketId, accountId, payee, total, transactionType, transactionDate, notes="", cleared=False):

        payeeId = self.GetPayeeId(payee)
        body = {"Query": "INSERT INTO transactions (accountId, payeeId, total, transactionType, transactionDate, notes, cleared) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                "Parameters": [accountId, payeeId, total, transactionType, transactionDate, notes, cleared]
                }
        self.MakeRequest(body)

        body = {"Query": "SELECT transactionId from transactions order by transactionId desc limit 1;"}

        transactionInfo = self.MakeRequest(body)[0]

        body = {"Query": """INSERT INTO transactions_buckets (transactionId, bucketId, amount, transactionType)
        VALUES (%s, %s, %s, %s""", "Parameters": [transactionInfo["transactionId"], bucketId, total, transactionType]};

        self.MakeRequest(body)

    def CreateBucket(self, categoryId, bucketName):
        body = {"Query": "INSERT INTO buckets (categoryId, name) VALUES (%s, %s)",
                "Parameters": [categoryId, bucketName]}
        return self.MakeRequest(body);

    def GetPayeeId(self, payee):
        parameters = []
        parameters.append(payee)
        body = {"Query": "SELECT payeeId from payees WHERE name=%s", "Parameters": parameters}
        payeeResponse = self.MakeRequest(body)

        if(len(payeeResponse) == 0):
            body = {"Query": "INSERT INTO payees (name) VALUES(%s)", "Parameters": parameters}
            payeeResponse = self.MakeRequest(body)

        return payeeResponse[0]["payeeId"]

    def __init__(self):
        try:
            from yaml import CLoader as loader, CDumper as dumper
        except ImportError:
            from yaml import loader, dumper
        stream = open("Config.yaml")
        config = yaml.load(stream, loader)
        self.mysqlUrl = config["MySqlUrl"]