function statusSet() {
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").hide();
  $("#netDirect").hide();
}



function elDiv(){
  $("#elDirect").show();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").hide();
  $("#netDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="create_elements.html" ></object>';
}

function misDiv(){
  $("#elDirect").hide();
  $("#missionDirect").show();
  $("#resDirect").hide();
  $("#visDirect").hide();
  $("#netDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="crewed_exploration_formview.html" ></object>';
}

function resDiv(){
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").show();
  $("#visDirect").hide();
  $("#netDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="consume_resources_formview.html" ></object>';
}

function visDiv(){
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").show();
  $("#netDirect").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="bat_chart.html" ></object>';
}

function networkDiv(){
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").hide();
  $("#netDirect").show();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="network_selection.html" ></object>';
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

function netSelectDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="network_selection.html" ></object>';
}

function reconDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="reconfigure_element_formview.html" ></object>';
}

function fliDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="flight_transport_formview.html" ></object>';
}

function propBurnDiv(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="propulsive_burn_formview.html" ></object>';
}

function missDev(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="mission_demand_model.html" ></object>';
}

function crewEVA(){
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="crewedEVA_formview.html" ></object>';
}
