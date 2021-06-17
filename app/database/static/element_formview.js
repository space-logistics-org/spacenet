
function formSet(){

  $("#components #inputName").prop("disabled",true);
  $("#components #inputCOS").prop("disabled",true);
  $("#components #inputEnv").prop("disabled",true);
  $("#components #inputAccMass").prop("disabled",true);
  $("#components #inputMass").prop("disabled",true);
  $("#components #inputVol").prop("disabled",true);
  $("#components #inputCarMass").prop("disabled",true);
  $("#components #inputCarVol").prop("disabled",true);
  $("#components #inputATF").prop("disabled",true);
  $("#components #inputMaxCrew").prop("disabled",true);
  $("#components #inputSpecImp").prop("disabled",true);
  $("#components #inputMaxFuel").prop("disabled",true);
  $("#components #inputMaxSpeed").prop("disabled",true);

  var elType = document.getElementById('dropPick').value;

  switch(elType) {
    case 'def':{
      $("#components #inputName").prop("disabled",true);
      $("#components #inputCOS").prop("disabled",true);
      $("#components #inputEnv").prop("disabled",true);
      $("#components #inputAccMass").prop("disabled",true);
      $("#components #inputMass").prop("disabled",true);
      $("#components #inputVol").prop("disabled",true);
      $("#components #inputCarMass").prop("disabled",true);
      $("#components #inputCarVol").prop("disabled",true);
      $("#components #inputATF").prop("disabled",true);
      $("#components #inputMaxCrew").prop("disabled",true);
      $("#components #inputSpecImp").prop("disabled",true);
      $("#components #inputMaxFuel").prop("disabled",true);
      $("#components #inputMaxSpeed").prop("disabled",true);
      break;
    }
    case 'Element': {
      $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      break;
        }
    case 'Resource Container':{
      $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputCarMass").prop("disabled",false);
      $("#components #inputCarVol").prop("disabled",false);
      break;}
    case 'Element Carrier':
    {  $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      break;}
    case 'Human Agent':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Robotic Agent':
    {  $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Propulsive Vehicle':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputMaxCrew").prop("disabled",false);
      $("#components #inputSpecImp").prop("disabled",false);
      $("#components #inputMaxFuel").prop("disabled",false);
      break;}
    case 'Surface Vehicle':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputMaxCrew").prop("disabled",false);
      $("#components #inputMaxSpeed").prop("disabled",false);
      $("#components #inputMaxFuel").prop("disabled",false);
    break;}
  }
}

var elCOS = document.getElementById("inputCOS").value;
function selector(){
}

function subclassSet(){
  elCOS = document.getElementById("inputCOS").value;

  document.getElementById("inputCOSSub1").style.display = "none";
  document.getElementById("inputCOSSub2").style.display = "none";
  document.getElementById("inputCOSSub3").style.display = "none";
  document.getElementById("inputCOSSub4").style.display = "none";
  document.getElementById("inputCOSSub5").style.display = "none";
  document.getElementById("inputCOSSub6").style.display = "none";
  document.getElementById("inputCOSSub7").style.display = "none";
  document.getElementById("inputCOSSub8").style.display = "none";
  document.getElementById("inputCOSSub9").style.display = "none";
  document.getElementById("inputCOSSub4Sub").style.display = "none";
  document.getElementById("inputCOSSub8Sub").style.display = "none";
  document.getElementById("inputCOSSub9Sub").style.display = "none";

  switch(elCOS){
    case 'Propellants and Fuels':{
      document.getElementById("inputCOSSub1").style.display = "block";
      break;
    }
    case 'Crew Provisions':{
      document.getElementById("inputCOSSub2").style.display = "block";
      break;
    }
    case 'Crew Operations':{
      document.getElementById("inputCOSSub3").style.display = "block";
      break;
    }
    case 'Maintenence and Upkeep':{
      document.getElementById("inputCOSSub4").style.display = "block";
      break;
    }
    case 'Stowage and Restraint':{
      document.getElementById("inputCOSSub5").style.display = "block";
      break;
    }
    case 'Exploration and Research':{
      document.getElementById("inputCOSSub6").style.display = "block";
      break;
    }
    case 'Waste and Disposal':{
      document.getElementById("inputCOSSub7").style.display = "block";
      break;
    }
    case 'Habitation and Infrastructure':{
      document.getElementById("inputCOSSub8").style.display = "block";
      break;
    }
    case 'Transportation and Carriers':{
      document.getElementById("inputCOSSub9").style.display = "block";
      break;
    }
  }
}

function subSelect4(){
  sub4 = document.getElementById("inputCOSSub4").value;
  if(sub4 == "Spares and Repair Parts"){
    document.getElementById("inputCOSSub4Sub").style.display = "block";
  }
}

function subSelect8(){
  sub8 = document.getElementById("inputCOSSub8").value;
  if(sub8 == "Robotic Systems"){
    document.getElementById("inputCOSSub8Sub").style.display = "block";
  }
}

function subSelect9(){
  sub9 = document.getElementById("inputCOSSub9").value;
  if(sub9 == "Propulsive Elements"){
    document.getElementById("inputCOSSub9Sub").style.display = "block";
  }
}
