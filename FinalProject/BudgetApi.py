from flask import Blueprint, request, render_template, jsonify
from DatabaseBusinessLogic import DatabaseBusinessLogic

budget_api = Blueprint('budget_api', __name__)
businessLogic = DatabaseBusinessLogic()

@budget_api.route("/", methods=['POST'])
def AssignMoney():
    data = request.form
    businessLogic.UpdateAssignedAmountsBucketList(data)
    return jsonify("Success"), 200
