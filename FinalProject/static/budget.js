var newBucketModal = document.getElementById("modal-new-bucket");
newBucketModal.addEventListener('show.bs.modal', function(event){
  var button = event.relatedTarget;
  var categoryId = button.getAttribute('data-bs-modal-id');
  var modalBodyInput = newBucketModal.querySelector('.modal-body select');
  modalBodyInput.value = categoryId;
});


var formAssignMoney = document.getElementById("form-assign-money");
formAssignMoney.addEventListener('submit', async function(event){
  event.preventDefault();
  let response = await fetch('/budget', {
    method: 'POST',
    body: new FormData(formAssignMoney)
  })
  .then(result => window.location.reload());
});


var formNewBucket = document.getElementById("form-new-bucket");
formNewBucket.addEventListener('submit', async function(event){
  event.preventDefault();
  let response = await fetch('/buckets',{
    method: 'POST',
    body: new FormData(formNewBucket)
  })
    .then(result => window.location.reload());
});


var formNewCategory = document.getElementById("form-new-category");
formNewCategory.addEventListener('submit', async function(event){
  event.preventDefault();
  let response = await fetch('/categories',{
    method: 'POST',
    body: new FormData(formNewCategory)
  })
    .then(result => window.location.reload());
});
