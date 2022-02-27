import time

from flask import Blueprint, request, render_template
from DatabaseBusinessLogic import DatabaseBusinessLogic
import os
from os.path import exists
import subprocess


microserviceFolder = ""
writeFilePath = os.path.join(microserviceFolder,"values.txt")
readFilePath = os.path.join(microserviceFolder, "sums.txt")
sumMicroService = os.path.join(microserviceFolder,"running_count.py")

transactions_api = Blueprint('transactions_api', __name__)
businessLogic = DatabaseBusinessLogic()


@transactions_api.route("/<accountId>", methods=['GET'])
def index(accountId):
    return BuildTransactionTemplate(accountId)


# CreateTransaction(self, bucketId, accountId, payee, total, transactionType, transactionDate, notes="", cleared=False):
@transactions_api.route("/<accountId>", methods=['POST'])
def CreateTransaction(accountId):
    data = request.form
    transactionType = None
    if data["inflow"] != "" and float(data["inflow"]) > 0:
        transactionType = "Inflow"
        total = float(data["inflow"])
    else:
        transactionType = "Outflow"
        total = float(data["outflow"])

    if "cleared" in data.keys() and data["cleared"] == "on":
        cleared = True
    else:
        cleared = False
    result = businessLogic.CreateTransaction(data["bucket-id"], accountId, data["payee"], total, transactionType, data["transaction-date"], data["notes"], cleared)
    return BuildTransactionTemplate(accountId)


def BuildTransactionTemplate(accountId):
    accounts = businessLogic.GetAccounts()
    buckets = businessLogic.GetBuckets(True)
    transactions = businessLogic.GetTransactions(accountId)
    GetRunningTotal(transactions)
    return render_template("transactions.html", accounts=accounts, buckets=buckets, transactions=transactions)


def WriteSums(transactions):

    if exists(readFilePath):
        os.remove(readFilePath)

    with open(writeFilePath, "w") as outfile:
        for i in range(len(transactions) - 1, -1, -1):
            val = 0
            if "inflow" in transactions[i].keys():
                val = transactions[i]["amount"]
            else:
                val = float(transactions[i]["amount"]) * -1
            outfile.write(str(val) + "\n")
        outfile.close()

def GetRunningTotal(transactions):

    WriteSums(transactions)

    subprocess.call(sumMicroService, shell=True)

    fileExists = False
    while not fileExists:
        if exists(readFilePath):
            fileExists = True
        else:
            time.sleep(.01)

    with open(readFilePath, "r") as readFile:
        for i in range(len(transactions) - 1, -1, -1):
            val = readFile.readline()
            transactions[i]["runningTotal"] = FloatToDollars(val)

def FloatToDollars(val):
    numVal =float(val)
    if(numVal < 0):
        return "-${:.2f}".format(numVal * -1)
    else:
        return "${:.2f}".format(numVal)
