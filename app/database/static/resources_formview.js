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
desc = document.getElementById("inputDesc").value;
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
      max_cargo_volume: inputCarVol
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
        type: "PropulsiveVehicle",
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
    case "Discrete":{
      message = JSON.stringify({
        name: name,
        description: desc,
        class_of_supply: classOS,
        type: "discrete",
        units: unit,
        unit_mass: mass,
        unit_volume: vol
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
      location.href = 'resources_table.html'
    }
  });

}
