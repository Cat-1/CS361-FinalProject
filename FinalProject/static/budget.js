/* Add event listener to create new bucket with defaulted category */
var newBucketModal = document.getElementById("modal-new-bucket");
newBucketModal.addEventListener('show.bs.modal', function(event){
  var button = event.relatedTarget;
  var categoryId = button.getAttribute('data-bs-modal-id');

  var modalBodyInput = newBucketModal.querySelector('.modal-body select');
  modalBodyInput.value = "Category-" + categoryId;
  console.log(modalBodyInput.select);
});
