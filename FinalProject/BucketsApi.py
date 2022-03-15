from flask import Blueprint, request, jsonify
from DatabaseBusinessLogic import DatabaseBusinessLogic

buckets_api = Blueprint('buckets_api', __name__)
businessLogic = DatabaseBusinessLogic()


@buckets_api.route("/", methods=['POST'])
def CreateBucket():
    data = request.form
    result = businessLogic.CreateBucket(int(data["category-select"]), data["new-bucket-name"])
    return jsonify("Success"), 200
