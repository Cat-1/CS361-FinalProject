from flask import Flask, render_template
from TransactionsAPI import transactions_api
from BucketsApi import buckets_api
from AccountsApi import accounts_api
from CategoriesApi import categories_api
from BudgetApi import budget_api
from DatabaseBusinessLogic import DatabaseBusinessLogic
from Buckets import Buckets

app = Flask(__name__)
app.register_blueprint(transactions_api, url_prefix='/transactions')
app.register_blueprint(buckets_api, url_prefix='/buckets')
app.register_blueprint(accounts_api, url_prefix='/accounts')
app.register_blueprint(categories_api, url_prefix='/categories')
app.register_blueprint(budget_api, url_prefix='/budget')
businessLogic = DatabaseBusinessLogic()
Buckets = Buckets()


@app.route('/')
def budgetPage():
    accounts = businessLogic.GetAccounts()
    categoryBuckets = Buckets.GetCategoriesAndBuckets()
    unbucketedBalance = Buckets.GetUnbucketedBalance()
    buckets = businessLogic.GetBuckets()
    # The number of parameters is due to the requirements of the HTML template
    # I want to make the HTML as dynamic as possible
    return render_template("budget.html", accounts=accounts, transaction_relativeUrl="transactions",
                           categoriesAndBuckets=categoryBuckets, buckets=buckets, unbucketedBalance=unbucketedBalance)


if __name__ == '__main__':
    app.run(port=5001)
