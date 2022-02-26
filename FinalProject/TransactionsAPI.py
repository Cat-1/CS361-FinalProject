from flask import Blueprint, request, render_template, jsonify
from DatabaseBusinessLogic import DatabaseBusinessLogic

transactions_api = Blueprint('transactions_api', __name__)
businessLogic = DatabaseBusinessLogic()

@transactions_api.route("/<accountId>",  )
def index(accountId):
    return BuildTransactionTemplate(accountId)

# CreateTransaction(self, bucketId, accountId, payee, total, transactionType, transactionDate, notes="", cleared=False):
@transactions_api.route("/<accountId>", methods=['POST'])
def CreateTransaction(accountId):
    data = request.form
    transactionType = None
    val = float(data["inflow"])
    if(val > 0):
        transactionType = "Inflow"
        total = val
    else:
        transactionType = "Outflow"
        total = float(data["outflow"])

    if data["cleared"] == 'on':
        cleared = True
    else:
        cleared = False
    result = businessLogic.CreateTransaction(data["bucket-id"], accountId, data["payee"], total, transactionType, data["transaction-date"], data["notes"], cleared)
    return BuildTransactionTemplate(accountId)


def BuildTransactionTemplate(accountId):
    accounts = businessLogic.GetAccounts()
    buckets = businessLogic.GetBuckets(True)
    #transactions = businessLogic.GetTransactions(accountId)
    return render_template("transactions.html", accounts=accounts, buckets=buckets)