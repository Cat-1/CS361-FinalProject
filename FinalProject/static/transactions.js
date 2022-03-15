async function NewTransaction(accountId){
  let formTransaction = document.getElementById("form-new-transaction");
  let response = await fetch('/transactions/'+accountId, {
    method: 'Post',
    body: new FormData(formTransaction)
  }).then(async (result) => await ReloadTransactions(accountId));
}

async function ReloadTransactions(accountId){
  console.log("Reloading");
  let response =  await fetch('/transactions/'+accountId, {
    method: 'GET'
  }).then(result => window.location.reload());
}

var deleteTransactionModal = document.getElementById("modal-delete-confirmation");
deleteTransactionModal.addEventListener('show.bs.modal', function(event){
  var button = event.relatedTarget;
  console.log(button);
  var transactionId = button.getAttribute('data-bs-modal-id');
  var accountId = button.getAttribute('data-bs-modal-account');
  var deleteButton = deleteTransactionModal.querySelector('[name="button-delete"]');
  deleteButton.setAttribute("onclick","DeleteTransaction(" + transactionId + "," + accountId + ")");
});

async function DeleteTransaction(transactionId, accountId){
  let response = await fetch('/transactions/'+transactionId,{
    method: 'DELETE'
  })
  .then(async (result) => await ReloadTransactions(accountId) );
}

async function ToggleCleared(transactionId, clearedStatus, accountId){
  let data = {}
  data.Cleared = Math.abs(clearedStatus - 1); // if cleared is 0, then it becomes 1
  let response = await fetch('/transactions/'+transactionId,{
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
    .then(async (result) => await ReloadTransactions(accountId));
}
