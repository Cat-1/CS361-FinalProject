from flask import Blueprint, request, render_template, jsonify
from DatabaseBusinessLogic import DatabaseBusinessLogic

buckets_api = Blueprint('buckets_api', __name__)
businessLogic = DatabaseBusinessLogic()


class BucketsApi:

    @buckets_api.route("/", methods=['GET'])
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

@buckets_api.route("/", methods=['POST'])
def CreateBucket():
    data = request.form
    result = businessLogic.CreateBucket(int(data["category-select"]), data["new-bucket-name"])
    return "pony"