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

function formSet(){

  $("#components #inputName").prop("disabled",true);
  $("#components #inputDesc").prop("disabled",true);
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
      $("#components #inputName").prop("disabled",true);
      $("#components #inputDesc").prop("disabled",true);
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
      $("#components #inputDesc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      break;
        }
    case 'Resource Container':{
      $("#components #inputName").prop("disabled",false);
      $("#components #inputDesc").prop("disabled",false);
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
      $("#components #inputDesc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputCarMass").prop("disabled",false);
      $("#components #inputCarVol").prop("disabled",false);

      break;}
    case 'Human Agent':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputDesc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Robotic Agent':
    {  $("#components #inputName").prop("disabled",false);
      $("#components #inputDesc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Propulsive Vehicle':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputDesc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputMaxCrew").prop("disabled",false);
      $("#components #inputSpecImp").prop("disabled",false);
      $("#components #inputMaxFuel").prop("disabled",false);
      $("#components #inputCarMass").prop("disabled",false);
      $("#components #inputCarVol").prop("disabled",false);
      break;}
    case 'Surface Vehicle':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputDesc").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputMaxCrew").prop("disabled",false);
      $("#components #inputMaxSpeed").prop("disabled",false);
      $("#components #inputMaxFuel").prop("disabled",false);
      $("#components #inputCarMass").prop("disabled",false);
      $("#components #inputCarVol").prop("disabled",false);
    break;}
  }
}




function onComplete(){
name = document.getElementById("inputName").value;
desc = document.getElementById("inputDesc").value;
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
          type: "Element",
          environment: env,
          accommodation_mass: accMass,
          mass: mass,
          volume: vol,
          max_cargo_mass: carMass,
          max_cargo_volume: carVol,
          cargo_environment: env,
          accommodation_mass: accMass,
          active_time_fraction: atf,
          max_crew: maxCC,
          isp: specImp,
          propellant_id:1,
          max_fuel: maxFuel,
          max_speed: maxSpeed
      });
      break;
    }
  case "Resource Container":{
    message = JSON.stringify({
      name: name,
      description: desc,
      class_of_supply: classOS,
      type: "ResourceContainer",
      environment: env,
      accommodation_mass: accMass,
      mass: mass,
      volume: vol,
      max_cargo_mass: carMass,
      max_cargo_volume: carVol
  });
  break;
}
  case "Element Carrier":{
    message = JSON.stringify({
        name: name,
        description: desc,
        class_of_supply: classOS,
        type: "ElementCarrier",
        environment: env,
        accommodation_mass: accMass,
        mass: mass,
        volume: vol,
        max_cargo_mass: carMass,
        max_cargo_volume: carVol,
        cargo_environment: env
    });
    break;
    }
  case "Human Agent":{
    message = JSON.stringify({
      name: name,
      description: desc,
      class_of_supply: classOS,
      type: "HumanAgent",
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
      type: "RoboticAgent",
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
        type: "Propulsive",
        environment: env,
        accommodation_mass: accMass,
        mass: mass,
        volume: vol,
        max_cargo_mass: carMass,
        max_cargo_volume: carVol,
        max_crew: parseInt(maxCC),
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
        type: "Surface",
        environment: env,
        accommodation_mass: accMass,
        mass: mass,
        volume: vol,
        max_cargo_mass: carMass,
        max_cargo_volume: carVol,
        max_crew: parseInt(maxCC),
        max_speed: maxSpeed,
        max_fuel: maxFuel,
        fuel_id:1
      });
      break;
    }
  }

  console.log(message)
  $.ajax({
    url: "/database/api/element/",
    data: message,
    contentType: 'application/json; charset=utf-8',
    dataType: "json",
    method: "POST",
    success: function() {
      document.getElementById("element").reset();
      document.getElementById("components").reset();
      location.href = 'element_table.html'
    }
  });

}
