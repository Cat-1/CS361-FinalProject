async function DeleteTransaction(transactionId, accountId){
  let response = await fetch('/transactions/'+transactionId,{
    method: 'DELETE'
  })
  .then(async (result) => {
    let response = await fetch('/transactions/'+accountId, {
      method: 'GET'
    });
     window.location.reload();
  });
}


async function ToggleCleared(transactionId, clearedStatus, accountId){
  let data = {}
  data.Cleared = Math.abs(clearedStatus - 1); // if cleared is 0, then it becomes 1
  let response = await fetch('/transactions/'+transactionId,{
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
    .then(async (result) => {
      let response = await fetch('/transactions/'+accountId, {
        method: 'GET'
      });
    });
}
