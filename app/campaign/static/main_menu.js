function statusSet() {
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
}



function elDiv(){
  $("#elDirect").show();
  $("#missionDirect").hide();
  $("#resDirect").hide();
}

function misDiv(){
  $("#elDirect").hide();
  $("#missionDirect").show();
  $("#resDirect").hide();
}

function resDiv(){
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").show();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="consume_resources_formview.html" ></object>';
}


function createDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="create_elements.html" ></object>';
}

function moveDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="move_elements.html" ></object>';
}

function removeDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="remove_elements.html" ></object>';
}

function consumeDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="consume_resources_formview.html" ></object>';
}

function transferDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="transfer_resources_formview.html" ></object>';
}
