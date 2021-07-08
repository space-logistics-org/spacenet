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

const TYPES = {
  'Element': 'Element',
  'ResourceContainer': 'Resource Container',
  'ElementCarrier': 'Element Carrier',
  'HumanAgent': 'Human Agent',
  'RoboticAgent': 'Robotic Agent',
  'SurfaceVehicle': 'Surface Vehicle',
  'PropulsiveVehicle': 'Propulsive Vehicle'
}

function formSet(modalType){

  $("#" + modalType + "InputName").hide();
  $("#" + modalType + "InputDesc").hide();
  $("#" + modalType + "InputCOS").hide();
  $("#" + modalType + "InputEnv").hide();
  $("#" + modalType + "InputAccMass").hide();
  $("#" + modalType + "InputMass").hide();
  $("#" + modalType + "InputVol").hide();
  $("#" + modalType + "InputCarMass").hide();
  $("#" + modalType + "InputCarVol").hide();
  $("#" + modalType + "InputATF").hide();
  $("#" + modalType + "InputMaxCrew").hide();
  $("#" + modalType + "InputSpecImp").hide();
  $("#" + modalType + "InputMaxFuel").hide();
  $("#" + modalType + "InputMaxSpeed").hide();

  $("#" + modalType + "InputNameLabel").hide();
  $("#" + modalType + "InputDescLabel").hide();
  $("#" + modalType + "InputCOSLabel").hide();
  $("#" + modalType + "InputEnvLabel").hide();
  $("#" + modalType + "InputAccMassLabel").hide();
  $("#" + modalType + "InputMassLabel").hide();
  $("#" + modalType + "InputVolLabel").hide();
  $("#" + modalType + "InputCarMassLabel").hide();
  $("#" + modalType + "InputCarVolLabel").hide();
  $("#" + modalType + "InputATFLabel").hide();
  $("#" + modalType + "InputMaxCrewLabel").hide();
  $("#" + modalType + "InputSpecImpLabel").hide();
  $("#" + modalType + "InputMaxFuelLabel").hide();
  $("#" + modalType + "InputMaxSpeedLabel").hide();

    const elType = $('#' + modalType + 'DropPick').val();

    switch(elType) {
    case 'def':{
      $("#" + modalType + "InputName").hide();
      $("#" + modalType + "InputDesc").hide();
      $("#" + modalType + "InputCOS").hide();
      $("#" + modalType + "InputEnv").hide();
      $("#" + modalType + "InputAccMass").hide();
      $("#" + modalType + "InputMass").hide();
      $("#" + modalType + "InputVol").hide();
      $("#" + modalType + "InputCarMass").hide();
      $("#" + modalType + "InputCarVol").hide();
      $("#" + modalType + "InputATF").hide();
      $("#" + modalType + "InputMaxCrew").hide();
      $("#" + modalType + "InputSpecImp").hide();
      $("#" + modalType + "InputMaxFuel").hide();
      $("#" + modalType + "InputMaxSpeed").hide();

      $("#" + modalType + "InputNameLabel").hide();
      $("#" + modalType + "InputDescLabel").hide();
      $("#" + modalType + "InputCOSLabel").hide();
      $("#" + modalType + "InputEnvLabel").hide();
      $("#" + modalType + "InputAccMassLabel").hide();
      $("#" + modalType + "InputMassLabel").hide();
      $("#" + modalType + "InputVolLabel").hide();
      $("#" + modalType + "InputCarMassLabel").hide();
      $("#" + modalType + "InputCarVolLabel").hide();
      $("#" + modalType + "InputATFLabel").hide();
      $("#" + modalType + "InputMaxCrewLabel").hide();
      $("#" + modalType + "InputSpecImpLabel").hide();
      $("#" + modalType + "InputMaxFuelLabel").hide();
      $("#" + modalType + "InputMaxSpeedLabel").hide();
      break;
    }
    case 'Element': {
      $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      break;
        }
    case 'Resource Container':{
      $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();
      $("#" + modalType + "InputCarMass").show();
      $("#" + modalType + "InputCarVol").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      $("#" + modalType + "InputCarMassLabel").show();
      $("#" + modalType + "InputCarVolLabel").show();
      break;}
    case 'Element Carrier':
    {  $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputCarMass").show();
      $("#" + modalType + "InputCarVol").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      $("#" + modalType + "InputCarMassLabel").show();
      $("#" + modalType + "InputCarVolLabel").show();

      break;}
    case 'Human Agent':
      {$("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();
      $("#" + modalType + "InputATF").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      $("#" + modalType + "InputATFLabel").show();

      break;}
    case 'Robotic Agent':
    {  $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();
      $("#" + modalType + "InputATF").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      $("#" + modalType + "InputATFLabel").show();

      break;}
    case 'Propulsive Vehicle':
      {$("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();
      $("#" + modalType + "InputMaxCrew").show();
      $("#" + modalType + "InputSpecImp").show();
      $("#" + modalType + "InputMaxFuel").show();
      $("#" + modalType + "InputCarMass").show();
      $("#" + modalType + "InputCarVol").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      $("#" + modalType + "InputCarMassLabel").show();
      $("#" + modalType + "InputCarVolLabel").show();
      $("#" + modalType + "InputMaxCrewLabel").show();
      $("#" + modalType + "InputSpecImpLabel").show();
      $("#" + modalType + "InputMaxFuelLabel").show();


      break;}
    case 'Surface Vehicle':
      {$("#" + modalType + "InputName").show();
      $("#" + modalType + "InputDesc").show();
      $("#" + modalType + "InputCOS").show();
      $("#" + modalType + "InputEnv").show();
      $("#" + modalType + "InputAccMass").show();
      $("#" + modalType + "InputMass").show();
      $("#" + modalType + "InputVol").show();
      $("#" + modalType + "InputMaxCrew").show();
      $("#" + modalType + "InputMaxSpeed").show();
      $("#" + modalType + "InputMaxFuel").show();
      $("#" + modalType + "InputCarMass").show();
      $("#" + modalType + "InputCarVol").show();

      $("#" + modalType + "InputNameLabel").show();
      $("#" + modalType + "InputDescLabel").show();
      $("#" + modalType + "InputCOSLabel").show();
      $("#" + modalType + "InputEnvLabel").show();
      $("#" + modalType + "InputAccMassLabel").show();
      $("#" + modalType + "InputMassLabel").show();
      $("#" + modalType + "InputVolLabel").show();
      $("#" + modalType + "InputCarMassLabel").show();
      $("#" + modalType + "InputCarVolLabel").show();
      $("#" + modalType + "InputMaxCrewLabel").show();
      $("#" + modalType + "InputSpecImpLabel").show();
      $("#" + modalType + "InputMaxFuelLabel").show();

    break;}
  }
}




function getMessage(modalType){
name = $("#" + modalType + "InputName").val();
desc = $("#" + modalType + "InputDesc").val();
type = $("#" + modalType + "DropPick").val();
env = $("#" + modalType + "InputEnv").val();
accMass = $("#" + modalType + "InputAccMass").val();
mass = $("#" + modalType + "InputMass").val();
vol = $("#" + modalType + "InputVol").val();
carMass = $("#" + modalType + "InputCarMass").val();
carVol = $("#" + modalType + "InputCarVol").val();
atf = $("#" + modalType + "InputATF").val();
maxCC = $("#" + modalType + "InputMaxCrew").val();
specImp = $("#" + modalType + "InputSpecImp").val();
maxFuel = $("#" + modalType + "InputMaxFuel").val();
maxSpeed = $("#" + modalType + "InputMaxSpeed").val();

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
        type: "PropulsiveVehicle",
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
        type: "SurfaceVehicle",
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
  return message
}


function formFill(data) {
  console.log(data)
  const elType = TYPES[data.type];
  console.log(elType)
  $('#editDropPick').val(elType).trigger('change')
  $('#' + data.class_of_supply).attr('selected', true)
  $("#editInputName").val(data.name)
  $("#editInputDesc").val(data.description)
  $("#editInputEnv").val(data.environment)
  $("#editInputMass").val(data.environment)
  $("#editInputVol").val(data.volume)
  $("#editInputAccMass").val(data.accommodation_mass)
  $("#editInputAccMass").val(data.accommodation_mass)

  if (elType === 'Resource Container') {
    $("#editInputCarMass").val(data.max_cargo_mass);
    $("#editInputCarVol").val(data.max_cargo_volume);
  }

  else if (elType === 'Element Carrier') {  
    $("#editInputCarMass").val(data.max_cargo_mass);
    $("#editInputCarVol").val(data.max_cargo_volume);
  }
  else if (elType === 'Human Agent')
    {
    $("#editInputATF").val(data.active_time_fraction);
  }
  else if (elType === 'Robotic Agent')
    {  
  $("#editInputATF").val(data.active_time_fraction);
  }
  else if (elType === 'Propulsive Vehicle')
    {
    $("#editInputMaxCrew").val(data.max_crew);
    $("#editInputSpecImp").val(data.isp);
    $("#editInputMaxFuel").val(data.max_fuel);
    $("#editInputCarMass").val(data.max_cargo_mass);
    $("#editInputCarVol").val(data.max_cargo_volume);
    }
  else if (elType === 'Surface Vehicle')
    {
    $("#editInputMaxCrew").val(data.max_crew);
    $("#editInputMaxSpeed").val(data.max_speed);
    $("#editInputMaxFuel").val(data.max_fuel);
    $("#editInputCarMass").val(data.max_cargo_mass);
    $("#editInputCarVol").val(data.max_cargo_volume);
  }
  }