import yaml
import mysql.connector
from flask import Flask, jsonify, request
import json

try:
    from yaml import CLoader as loader, CDumper as dumper
except ImportError:
    from yaml import loader, dumper
stream = open("config.yaml")
config = yaml.load(stream, loader)

conn = mysql.connector.connect(**config["MySql"])

app = Flask(__name__)


def JsonifyMySql(columns, data):
    result = []
    columnHeader = []
    for i in range(len(columns)):
        columnName = columns[i]
        columnHeader.append(columnName)

    for row in range(len(data)):
        obj = {}
        for column in range(len(data[row])):
            obj[columnHeader[column]] = data[row][column]
        result.append(obj)
    return jsonify(result)


@app.route('/', methods=['POST'])
def index():
    body = request.get_json()
    print(body)

    db = conn.cursor()

    if 'Parameters' in body:
        param = body["Parameters"]
        db.execute(body["Query"], param)
        if ("INSERT" in body["Query"]):
            conn.commit()
    else:
        db.execute(body["Query"])
        if("INSERT" in body["Query"]):
            conn.commit()
    rows = db.fetchall()
    columnHeaders = db.column_names

    if "ReturnType" in body and body["ReturnType"].upper() == "JSON":
        return JsonifyMySql(columnHeaders, rows)
    else:
        result = {"Headers": columnHeaders, "Data": rows}
        return result

try:
    app.run()
except:
    print("Exception")
finally:
    conn.close()
