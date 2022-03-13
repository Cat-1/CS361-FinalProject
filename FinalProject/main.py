from flask import Flask, render_template
from TransactionsAPI import transactions_api
from BucketsApi import buckets_api
from AccountsApi import accounts_api
from DatabaseBusinessLogic import DatabaseBusinessLogic
from Buckets import Buckets

app = Flask(__name__)
app.register_blueprint(transactions_api, url_prefix='/transactions')
app.register_blueprint(buckets_api, url_prefix='/buckets')
app.register_blueprint(accounts_api, url_prefix='/accounts')
businessLogic = DatabaseBusinessLogic()

Buckets = Buckets()

@app.route('/')
def budgetPage():
    accounts = businessLogic.GetAccounts()
    buckets = Buckets.GetCategoriesAndBuckets()
    unbucketedBalance = Buckets.GetUnbucketedBalance()
    return render_template("budget.html", accounts=accounts, transaction_relativeUrl="transactions",
                           categoriesAndBuckets=buckets, unbucketedBalance=unbucketedBalance)

if __name__ == '__main__':
    app.run(port=5001)
