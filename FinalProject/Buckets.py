from DatabaseBusinessLogic import DatabaseBusinessLogic
businessLogic = DatabaseBusinessLogic()

class Buckets:
    def GetCategoriesAndBuckets(self):
        result = {}
        rows = businessLogic.GetCategoriesAndBuckets()

        for row in rows:
            categoryId = row["categoryId"]
            categoryName = row["categoryName"]
            if categoryId not in result:
                result[categoryId] = {}
                result[categoryId]["category"] = {"name": categoryName, "id": categoryId}
                result[categoryId]["buckets"] = []
            result[categoryId]["buckets"].append({"name": row["bucketName"], "id": row["bucketId"],
                                                  "assigned": row["assigned"], "balance": row["balance"]})
        return result

    def GetUnbucketedBalance(self):
        unbucketed = businessLogic.GetBucketByName("unbucketed")[0]
        transactionSum = businessLogic.GetTransactionSum(unbucketed["bucketId"])
        return float(transactionSum) - float(unbucketed["assigned"])
