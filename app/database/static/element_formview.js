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

  var elType = $('#' + modalType + 'DropPick').val();

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




function subclassSet(modalType){
  elCOS = $("#" + modalType + "InputCOS").val();
  console.log(elCOS)

  $("#" + modalType + "InputCOSSub1").hide();
  $("#" + modalType + "InputCOSSub2").hide();
  $("#" + modalType + "InputCOSSub3").hide();
  $("#" + modalType + "InputCOSSub4").hide();
  $("#" + modalType + "InputCOSSub5").hide();
  $("#" + modalType + "InputCOSSub6").hide();
  $("#" + modalType + "InputCOSSub7").hide();
  $("#" + modalType + "InputCOSSub8").hide();
  $("#" + modalType + "InputCOSSub9").hide();
  $("#" + modalType + "InputCOSSub4Sub").hide();
  $("#" + modalType + "InputCOSSub8Sub").hide();
  $("#" + modalType + "InputCOSSub9Sub").hide();

  switch(elCOS){
    case 'Propellants and Fuels':{
      $("#" + modalType + "InputCOSSub1").show();
      classOS = 1;
      break;
    }
    case 'Crew Provisions':{
      $("#" + modalType + "InputCOSSub2").show();
      classOS = 2;
      break;
    }
    case 'Crew Operations':{
      $("#" + modalType + "InputCOSSub3").show();
      classOS = 3;
      break;
    }
    case 'Maintenence and Upkeep':{
      $("#" + modalType + "InputCOSSub4").show();
      classOS = 4;
      break;
    }
    case 'Stowage and Restraint':{
      $("#" + modalType + "InputCOSSub5").show();
      classOS = 5;
      break;
    }
    case 'Exploration and Research':{
      $("#" + modalType + "InputCOSSub6").show();
      classOS = 6;
      break;
    }
    case 'Waste and Disposal':{
      $("#" + modalType + "InputCOSSub7").show();
      classOS = 7;
      break;
    }
    case 'Habitation and Infrastructure':{
      $("#" + modalType + "InputCOSSub8").show();
      classOS = 8;
      break;
    }
    case 'Transportation and Carriers':{
      $("#" + modalType + "InputCOSSub9").show();
      classOS = 9;
      break;
    }
  }
}

function setCOS(modalType){
  switch(classOS){
    case 1: {
      switch($("#" + modalType + "InputCOSSub1").val()){
        case 'Cryogens' : {classOS = 101; break;}
        case 'Hypergols': {classOS = 102; break;}
        case 'Nuclear Fuel' : {classOS = 103; break;}
        case 'Petroleum Fuels':{ classOS = 104; break;}
        case 'Other Fuels': {classOS = 105; break;}
    } break; }
    case 2: {
      switch($("#" + modalType + "InputCOSSub2").val()){
        case 'Water and Support Equipment' : {classOS = 201; break;}
        case 'Food and Support Equipment' : {classOS = 202; break;}
        case 'Gases' : {classOS = 203; break;}
        case 'Hygiene Items' : {classOS = 204; break;}
        case 'Clothing' : {classOS = 205; break;}
        case 'Personal Items' : {classOS = 206; break;}
      } break; }
    case 3: {
      switch($("#" + modalType + "InputCOSSub3").val()){
        case 'Office Equipment and Supplies' : {classOS = 301; break;}
        case 'EVA Equipment and Consumables' : {classOS = 302; break;}
        case 'Health Equipment and Consumables' : {classOS = 303; break;}
        case 'Safety Equipment' : {classOS = 304; break;}
        case 'Communications Equipment' : {classOS = 305; break;}
        case 'Computers and Support Equipment' : {classOS = 306; break;}
      } break; }
    case 4: {
      switch($("#" + modalType + "InputCOSSub4").val()){
        case 'Spares and Repair Parts' : {classOS = 401; break;}
        case 'Maintenence Tools' : {classOS = 402; break;}
        case 'Lubricants and Bulk Chemicals' : {classOS = 403; break;}
        case 'Batteries' : {classOS = 404; break;}
        case 'Cleaning Equipment and Consumables' : {classOS = 405; break;}
      } break; }
    case 401: {
      switch($("#" + modalType + "InputCOSSub4Sub").val()){
        case 'Spares' : {classOS = 4011; break;}
        case 'Repair Parts' : {classOS = 4012; break;}
      } break; }
    case 5: {
      switch($("#" + modalType + "InputCOSSub5").val()){
        case 'Cargo Containers and Restraints' : {classOS = 501; break;}
        case 'Inventory Management Equipment' : {classOS = 502; break;}
      } break; }
    case 6: {
      switch($("#" + modalType + "InputCOSSub6").val()){
        case 'Science Payloads and Instruments' : {classOS = 601; break;}
        case 'Field Equipment' : {classOS = 602; break;}
        case 'Samples' : {classOS = 603; break;}
      } break; }
    case 7: {
      switch($("#" + modalType + "InputCOSSub7").val()){
        case 'Waste' : {classOS = 701; break;}
        case 'Waste Management Equipment' : {classOS = 702; break;}
        case 'Failed Pairs' : {classOS = 703; break;}
      } break; }
    case 8: {
      switch($("#" + modalType + "InputCOSSub8").val()){
        case 'Habitation Facilities' : {classOS = 801; break;}
        case 'Surface Mobility Systems' : {classOS = 802; break;}
        case 'Power Systems' : {classOS = 803; break;}
        case 'Robotic Systems' : {classOS = 804; break;}
        case 'Resource Utilization Systems' : {classOS = 805; break;}
        case 'Orbiting Service Systems' : {classOS = 806; break;}
      } break; }
    case 804: {
      switch($("#" + modalType + "InputCOSSub8Sub").val()){
        case 'Science Robotics' : {classOS = 8041; break;}
        case 'Construction/Maintenence Robotics' : {classOS = 8042; break;}
      } break; }
    case 9: {
      switch($("#" + modalType + "InputCOSSub9").val()){
        case 'Carriers, Non-propulsive Elements' : {classOS = 901; break;}
        case 'Propulsive Elements' : {classOS = 902; break;}
      } break; }
    case 902: {
      switch($("#" + modalType + "InputCOSSub9Sub").val()){
        case 'Launch Vehicles' : {classOS = 9021; break;}
        case 'Upper Stages/In-Space Propulsion Systems' : {classOS = 9022; break;}
        case 'Descent Stages' : {classOS = 9023; break;}
        case 'Ascent Stages' : {classOS = 9024; break;}
      } break; }

  }
}

function subSelect4(modalType){
  sub4 = $("#" + modalType + "InputCOSSub4").val();
  if(sub4 == "Spares and Repair Parts"){
    $("#" + modalType + "InputCOSSub4Sub").show();
  }
}

function subSelect8(modalType){
  sub8 = $("#" + modalType + "InputCOSSub8").val();
  if(sub8 == "Robotic Systems"){
    $("#" + modalType + "InputCOSSub8Sub").show();
  }
}

function subSelect9(modalType){
  sub9 = $("#" + modalType + "InputCOSSub9").val();
  if(sub9 == "Propulsive Elements"){
    $("#" + modalType + "InputCOSSub9Sub").show();

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
  var elType = TYPES[data.type]
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