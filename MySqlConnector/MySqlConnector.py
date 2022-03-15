import yaml
import mysql.connector
from flask import Flask, jsonify, request
app = Flask(__name__)

def LoadConfig():
    try:
        from yaml import CLoader as loader, CDumper as dumper
    except ImportError:
        from yaml import loader, dumper
    stream = open("config.yaml")
    config = yaml.load(stream, loader)
    conn = mysql.connector.connect(**config["MySql"])
    return conn

def JsonifyMySql(columns, data):
    result = []
    columnHeader = BuildColumnHeaders(columns)
    for rowIndex in range(len(data)):
        obj = {}
        row = data[rowIndex]
        for columnIndex in range(len(data[rowIndex])):
            columnName = columnHeader[columnIndex]
            obj[columnName] = data[rowIndex][columnIndex]
        result.append(obj)
    return jsonify(result)

def BuildColumnHeaders(columns):
    columnHeader = []
    for i in range(len(columns)):
        columnName = columns[i]
        columnHeader.append(columnName)
    return columnHeader


@app.route('/', methods=['POST'])
def Index():
    body = request.get_json()
    # For debugging
    print(body)
    db = conn.cursor()
    if 'Parameters' in body:
        ExecuteQueryWithParameters(db, body)
    else:
       ExecuteQueryWithNoParameters(db, body)
    return FormatReturnType(db, body)


def FormatReturnType(db, body):
    rows = db.fetchall()
    columnHeaders = db.column_names
    if "ReturnType" in body and body["ReturnType"].upper() == "JSON":
        return JsonifyMySql(columnHeaders, rows)
    else:
        result = {"Headers": columnHeaders, "Data": rows}
        return result


def ExecuteQueryWithParameters(db, body):
    param = body["Parameters"]
    db.execute(body["Query"], param)
    if "INSERT" in body["Query"]:
        conn.commit()

def ExecuteQueryWithNoParameters(db, body):
    db.execute(body["Query"])
    # You need to commit inserts and delete in MySQL
    if ("INSERT" in body["Query"] or "DELETE" in body["Query"]):
        conn.commit()

conn = LoadConfig()
try:
    app.run()
except:
    print("Exception")
finally:
    conn.close()
