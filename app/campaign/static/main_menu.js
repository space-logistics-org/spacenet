function statusSet() {
  $("#elDirect").hide();
  $("#missionDirect").hide();
  $("#resDirect").hide();
  $("#visDirect").hide();
  $("#netDirect").hide();
  $("#visSpace").hide();
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
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="consume_resources.html" ></object>';
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
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="create_elements.html" ></object>';
}

function moveDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="move_elements.html" ></object>';
}

function removeDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="remove_elements.html" ></object>';
}

function consumeDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="consume_resources.html" ></object>';
}

function transferDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="transfer_resources.html" ></object>';
}

function batDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="bat_chart.html" ></object>';
}

function netDiv(){
  $("#formSpace").hide();
  $("#visSpace").show();
  document.getElementById("visSpace").innerHTML='<object id = formSpace type="text/html" data="network_visualization.html" ></object>';
}

function crewDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="crewed_exploration_formview.html" ></object>';
}

function sptrDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="spaceTransport_formview.html" ></object>';
}

function netSelectDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="network_selection.html" ></object>';
}

function reconDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="reconfigure_elements.html" ></object>';
}

function fliDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="flight_transport_formview.html" ></object>';
}

function propBurnDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="propulsive_burn_formview.html" ></object>';
}

function missDev(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="mission_demand_model.html" ></object>';
}

function crewEVA(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="crewedEVA_formview.html" ></object>';
}

function missDem(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="mission_model_formview.html" ></object>';
}

function burnDiv(){
  $("#formSpace").show();
  $("#visSpace").hide();
  document.getElementById("formSpace").innerHTML='<object id = formSpace type="text/html" data="prop_burn_visualization.html" ></object>';
}
