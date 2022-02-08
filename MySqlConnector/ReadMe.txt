POST Request

Expected Sample Request Body
{
    "Query": "SELECT * FROM payee WHERE name like %s",
    "Parameters": ["test%"]
}

Sample Response:
[
    {
        "name": "test1",
        "payeeId": 2
    },
    {
        "name": "test2",
        "payeeId": 3
    }
]