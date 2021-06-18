name = "";
desc = "";
classOS = 0;
type = "";
mass = 0;
vol = 0;
units = "";

function subclassSet(){
  recCOS = document.getElementById("inputCOS").value;

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

  switch(recCOS){
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

function onComplete(){
name = document.getElementById("inputName").value;
desc = document.getElementById("inputDescription").value;
//classOS =
type = document.getElementById("dropPick").value;
mass = document.getElementById("inputMass").value;
vol = document.getElementById("inputVol").value;
units = document.getElementById("inputUnits").value;



switch(type){
  case "Continuous":{
      message = JSON.stringify({
        name: name,
        description: desc,
        cos: classOS,
        type: "continuous",
        units: units,
        unit_mass: mass,
        unit_vol: vol
      });
      break;
    }
  case "Discrete":{
    message = JSON.stringify({
      name: name,
      description: desc,
      cos: classOS,
      type: "discrete",
      units: units,
      unit_mass: mass,
      unit_vol: vol
  });
  break;
}
  }

  console.log(message)
  $.ajax({
    url: "/database/api/resource/",
    data: message,
    contentType: 'application/json; charset=utf-8',
    dataType: "json",
    method: "POST",
    success: function() {
      document.getElementById("resource").reset();
      document.getElementById("components").reset();
      location.href = 'resource_table.html'
    }
  });

}
