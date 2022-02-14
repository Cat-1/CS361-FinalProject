function newAccount(){
  var modal = document.getElementById('modal-new-account');
  modal.toggle();
  console.log("Done");
}


function addEditColumn(){
  var tbody = document.getElementsByName('table__main')[0].lastElementChild;
  var headerCell = document.createElement("th");
  headerCell.textContent = "Edit/Delete";
  headerCell.className = "edit_delete_cell";

  if(tbody.firstChild.lastElementChild.textContent =="Edit/Delete"){
    console.log("Edit column is displayed");
    return;
  }

  tbody.firstChild.appendChild(headerCell);
  var curNode = tbody.firstChild.nextElementSibling;
  while(curNode){
    var newCell = document.createElement("td");
    curNode.appendChild(newCell);
    if(curNode.attributes?.name?.value=="table__normal__row"){
      newCell.innerHTML = "<i class=\"edit__delete__icon bi bi-pencil-fill\"></i>   <i class=\"edit__delete__icon bi bi-trash3-fill\"></i>";
    }
    newCell.className="edit_delete_cell";
    curNode = curNode.nextElementSibling;
  }
}

function removeEditColumn(){
  var cellsToDelete = document.getElementsByClassName("edit_delete_cell");

  while(cellsToDelete[0]){
      cellsToDelete[0].remove();
  }

}
