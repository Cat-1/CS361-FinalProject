from flask import Blueprint, request, render_template, jsonify
from DatabaseBusinessLogic import DatabaseBusinessLogic

accounts_api = Blueprint('accounts_api', __name__)
businessLogic = DatabaseBusinessLogic()


@accounts_api.route("", methods=['POST'])
def CreateAccount():
    print("pony")
    data = request.form
    businessLogic.CreateAccount(data["new-account-type"], data["new-account-name"])
    return data