elType ="";
name = "";
desc = "";
classOS = 0;
env = "";
accMass = 0;
mass = 0;
vol = 0;
carMass = 0;
carVol = 0;
atf = 0;
maxCC = 0;
specImp = 0;
maxFuel = 0;
maxSpeed = 0;
message = "fail:(";

function formSet(){

  $("#components #name").prop("disabled",true);
  $("#components #desc").prop("disabled",true);
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

  elType = document.getElementById('dropPick').value;

  switch(elType) {
    case 'def':{
      $("#components #name").prop("disabled",true);
      $("#components #desc").prop("disabled",true);
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
      $("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      break;
        }
    case 'Resource Container':{
      $("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputCarMass").prop("disabled",false);
      $("#components #inputCarVol").prop("disabled",false);
      break;}
    case 'Element Carrier':
    {  $("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      break;}
    case 'Human Agent':
      {$("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Robotic Agent':
    {  $("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Propulsive Vehicle':
      {$("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
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
      {$("#components #name").prop("disabled",false);
      $("#components #desc").prop("disabled",false);
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


function onComplete(){
name = document.getElementById("name").value;
desc = document.getElementById("desc").value;
//classOS =
type = document.getElementById("dropPick").value;
env = document.getElementById("inputEnv").value;
accMass = document.getElementById("inputAccMass").value;
mass = document.getElementById("inputMass").value;
vol = document.getElementById("inputVol").value;
carMass = document.getElementById("inputCarMass").value;
carVol = document.getElementById("inputCarVol").value;
atf = document.getElementById("inputATF").value;
maxCC = document.getElementById("inputMaxCrew").value;
specImp = document.getElementById("inputSpecImp").value;
maxFuel = document.getElementById("inputMaxFuel").value;
maxSpeed = document.getElementById("inputMaxSpeed").value;


switch(type){
  case "Element":{
      message = JSON.stringify({
          name: name,
          description: desc,
          class_of_supply: classOS,
          type: type,
          environment: env,
          accommodation_mass: accMass,
          mass: mass,
          volume: vol
      });
      break;
    }
  case "Resource Container":{
    message = JSON.stringify({
      name: name,
      description: desc,
      class_of_supply: classOS,
      type: type,
      environment: env,
      accommodation_mass: accMass,
      mass: mass,
      volume: vol,
      max_cargo_mass: carMass,
      max_cargo_volume: inputCarVol
  });
  break;
}
  case "Element Carrier":{
    message = JSON.stringify({
        name: name,
        description: desc,
        class_of_supply: classOS,
        type: type,
        environment: env,
        accommodation_mass: accMass,
        mass: mass,
        volume: vol,
        max_cargo_mass: carMass,
        max_cargo_volume: inputCarVol,
        cargo_environment: env
    });
    break;
    }
  case "Human Agent":{
    message = JSON.stringify({
      name: name,
      description: desc,
      class_of_supply: classOS,
      type: type,
      environment: env,
      accommodation_mass: accMass,
      mass: mass,
      volume: vol,
      active_time_fraction: atf
  });
  break;
}
  case "Robotic Agent":{
    message = JSON.stringify({
      name: name,
      description: desc,
      class_of_supply: classOS,
      type: type,
      environment: env,
      accommodation_mass: accMass,
      mass: mass,
      volume: vol,
      active_time_fraction: atf
    });
      break;
    }
    case "Propulsive Vehicle":{
      message = JSON.stringify({
        name: name,
        description: desc,
        class_of_supply: classOS,
        type: type,
        environment: env,
        accommodation_mass: accMass,
        mass: mass,
        volume: vol,
        max_cargo_mass: carMass,
        max_cargo_volume: carVol,
        max_crew: maxCC,
        isp: specImp,
        max_fuel: maxFuel,
        propellant_id:1
      });
      break;
    }
    case "Surface Vehicle":{
      message = JSON.stringify({
        name: name,
        description: desc,
        class_of_supply: classOS,
        type: type,
        environment: env,
        accommodation_mass: accMass,
        mass: mass,
        volume: vol,
        max_cargo_mass: carMass,
        max_cargo_volume: carVol,
        max_speed: maxSpeed,
        max_fuel: maxFuel,
        fuel_id:1
      });
      break;
    }
  }

}

function onSubmit(form){
  var message = JSON.stringify( $("components").serializeArray());
  alert(message[1]);
}

/*var message = {};
formData.forEach(function(value, key){
    message[key] = value;
});
var jsonMessage = JSON.stringify(object);


$("#subButton").onClick = function(){
                $.ajax({
                  url: "/database/api/element/",
                  data: jsonMessage,
                  }),
                  contentType: 'application/json; charset=utf-8',
                  dataType: "json",
                  method: "POST",
                  success: function(item) {
                    dt.ajax.reload();
                  }
                }
*/
