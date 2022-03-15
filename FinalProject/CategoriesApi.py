from flask import Blueprint, request
from DatabaseBusinessLogic import DatabaseBusinessLogic

categories_api = Blueprint('categories_api', __name__)
businessLogic = DatabaseBusinessLogic()

@categories_api.route("/", methods=['POST'])
def CreateCategory():
    data = request.form
    result = businessLogic.CreateCategory(data["new-category-name"])
    return "Success"