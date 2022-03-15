from DatabaseBusinessLogic import DatabaseBusinessLogic
businessLogic = DatabaseBusinessLogic()


class Buckets:

    def GetCategoriesAndBuckets(self):
        result = {}
        rows = businessLogic.GetCategoriesAndBuckets()
        # sort the buckets into their associated categories
        for row in rows:
            (result, categoryId) = self.CheckForBucketAndAddIfMissing(result, row)
            if row["bucketId"] is not None:
                transactionSum = businessLogic.GetTransactionSumForABucket("bucketId", row["bucketId"])
                balance = float(row["assigned"]) + float(transactionSum)
                result[categoryId]["buckets"].append({"name": row["bucketName"], "id": row["bucketId"],
                                                  "assigned": row["assigned"], "balance": "{:.2f}".format(balance)})
        return result


    def CheckForBucketAndAddIfMissing(self, result, row):
        categoryId = row["categoryId"]
        categoryName = row["categoryName"]
        if categoryId not in result:
            result[categoryId] = {}
            result[categoryId]["category"] = {"name": categoryName, "id": categoryId}
            result[categoryId]["buckets"] = []
        return (result, categoryId)


    # dynamically calculate the unbucketed balance
    def GetUnbucketedBalance(self):
        unbucketed = businessLogic.GetBucketByName("unbucketed")
        unbucketedTransactionSum = businessLogic.GetTransactionSumForABucket("bucketId", unbucketed["bucketId"])
        bucketList = businessLogic.GetBuckets()
        sumBucketed = 0
        for bucket in bucketList:
            sumBucketed += float(bucket["assigned"])
        # transactionSum will be positive; assigned values will be negative
        return float(unbucketedTransactionSum) - float(sumBucketed)

