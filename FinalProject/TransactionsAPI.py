import time
from flask import Blueprint, request, render_template, jsonify
from DatabaseBusinessLogic import DatabaseBusinessLogic
import os
from os.path import exists
import subprocess


writeFilePath = "values.txt"
readFilePath = "sums.txt"
sumMicroService = "running_count.py"
transactions_api = Blueprint('transactions_api', __name__)
businessLogic = DatabaseBusinessLogic()


@transactions_api.route("/<accountId>", methods=['GET'])
def index(accountId):
    return BuildTransactionTemplate(accountId)


@transactions_api.route("/<transactionId>", methods=['DELETE'])
def DeleteTransaction(transactionId):
    businessLogic.DeleteTransaction(transactionId)
    return jsonify("Success"), 200


@transactions_api.route("/<transactionId>", methods=['PUT'])
def UpdateCleared(transactionId):
    data = request.get_json()
    businessLogic.UpdateClearedTransactionStatus(transactionId, data["Cleared"])
    return jsonify("Success"), 200


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
    # I recognize the number of parameters may be a code smell, but I don't want my business logic class to know/care
    # about what an object is -- the parameters are all fed into the DB query, so all parameters are required
    result = businessLogic.CreateTransaction(data["bucket-id"], accountId, data["payee"], total, transactionType,
                                             data["transaction-date"], data["notes"], cleared)
    return BuildTransactionTemplate(accountId)


def BuildTransactionTemplate(accountId):
    accounts = businessLogic.GetAccounts()
    account = businessLogic.GetAccount(accountId)[0]
    buckets = businessLogic.GetBuckets()
    transactions = businessLogic.GetTransactionsByAccountId(accountId)
    GetRunningTotal(transactions)
    return render_template("transactions.html", accounts=accounts, buckets=buckets, account=account, transactions=transactions)


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


def ReadSums(readFilePath, transactions):
    with open(readFilePath, "r") as readFile:
        for i in range(len(transactions) - 1, -1, -1):
            val = readFile.readline()
            transactions[i]["runningTotal"] = FloatToDollars(val)


def GetRunningTotal(transactions):
    if len(transactions) > 0:
        WriteSums(transactions)
        subprocess.call(sumMicroService, shell=True)
        fileExists = False
        while not fileExists:
            if exists(readFilePath):
                fileExists = True
            else:
                time.sleep(.01)
        ReadSums(readFilePath, transactions)

def FloatToDollars(val):
    numVal =float(val)
    if(numVal < 0):
        return "-${:.2f}".format(numVal * -1)
    else:
        return "${:.2f}".format(numVal)

