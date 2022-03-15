var formNewAccount = document.getElementById("form-new-account");
formNewAccount.addEventListener('submit', async function(event){
  event.preventDefault();
  let response = await fetch('/accounts',{
    method: 'POST',
    body: new FormData(formNewAccount)
  })
    .then(result => window.location.reload());
});
