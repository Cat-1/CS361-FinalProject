from flask import Flask, render_template
from TransactionsAPI import transactions_api
from BucketsApi import buckets_api, BucketsApi
from DatabaseBusinessLogic import DatabaseBusinessLogic

app = Flask(__name__)
app.register_blueprint(transactions_api, url_prefix='/transactions')
app.register_blueprint(buckets_api, url_prefix='/buckets')
businessLogic = DatabaseBusinessLogic()

Buckets = BucketsApi()

@app.route('/')
def hello_world():
    accounts = businessLogic.GetAccounts()
    buckets = Buckets.GetCategoriesAndBuckets()

    return render_template("budget.html", accounts=accounts, transaction_relativeUrl="transactions",
                           categoriesAndBuckets=buckets)

if __name__ == '__main__':
    app.run(port=5001)
