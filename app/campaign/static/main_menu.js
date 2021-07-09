function statusSet() {
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").hide();
}



function elDiv(){
  $("#elDirect").show();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="create_elements.html" ></object>';
}

function misDiv(){
  $("#elDirect").hide();
  $("#missionDirect").show();
  $("#resDirect").hide();
  $("#visDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="crewed_exploration_formview.html" ></object>';
}

function resDiv(){
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").show();
  $("#visDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="consume_resources_formview.html" ></object>';
}

function visDiv(){
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").show();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="bat_chart.html" ></object>';
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

function batDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="bat_chart.html" ></object>';
}

function netDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="network_visualization.html" ></object>';
}

function crewDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="crewed_exploration_formview.html" ></object>';
}

function sptrDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="spaceTransport_formview.html" ></object>';
}
