elType = "";
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

function formSet(modalType) {

    let inputName = $("#" + modalType + "InputName");
    inputName.hide();
    let inputDesc = $("#" + modalType + "InputDesc");
    inputDesc.hide();
    let inputCOS = $("#" + modalType + "InputCOS");
    inputCOS.hide();
    let inputEnv = $("#" + modalType + "InputEnv");
    inputEnv.hide();
    let inputAccMass = $("#" + modalType + "InputAccMass");
    inputAccMass.hide();
    let inputMass = $("#" + modalType + "InputMass");
    inputMass.hide();
    let inputVol = $("#" + modalType + "InputVol");
    inputVol.hide();
    let inputCarMass = $("#" + modalType + "InputCarMass");
    inputCarMass.hide();
    let inputCarVol = $("#" + modalType + "InputCarVol");
    inputCarVol.hide();
    let inputATF = $("#" + modalType + "InputATF");
    inputATF.hide();
    let inputMaxCrew = $("#" + modalType + "InputMaxCrew");
    inputMaxCrew.hide();
    let inputSpecImp = $("#" + modalType + "InputSpecImp");
    inputSpecImp.hide();
    let inputMaxFuel = $("#" + modalType + "InputMaxFuel");
    inputMaxFuel.hide();
    let inputMaxSpeed = $("#" + modalType + "InputMaxSpeed");
    inputMaxSpeed.hide();

    let inputNameLabel = $("#" + modalType + "InputNameLabel");
    inputNameLabel.hide();
    let inputDescLabel = $("#" + modalType + "InputDescLabel");
    inputDescLabel.hide();
    let inputCOSLabel = $("#" + modalType + "InputCOSLabel");
    inputCOSLabel.hide();
    let inputEnvLabel = $("#" + modalType + "InputEnvLabel");
    inputEnvLabel.hide();
    let inputAccMassLabel = $("#" + modalType + "InputAccMassLabel");
    inputAccMassLabel.hide();
    let inputMassLabel = $("#" + modalType + "InputMassLabel");
    inputMassLabel.hide();
    let inputVolLabel = $("#" + modalType + "InputVolLabel");
    inputVolLabel.hide();
    let inputCarMassLabel = $("#" + modalType + "InputCarMassLabel");
    inputCarMassLabel.hide();
    let inputCarVolLabel = $("#" + modalType + "InputCarVolLabel");
    inputCarVolLabel.hide();
    let inputATFLabel = $("#" + modalType + "InputATFLabel");
    inputATFLabel.hide();
    let inputMaxCrewLabel = $("#" + modalType + "InputMaxCrewLabel");
    inputMaxCrewLabel.hide();
    let inputSpecImpLabel = $("#" + modalType + "InputSpecImpLabel");
    inputSpecImpLabel.hide();
    let inputMaxFuelLabel = $("#" + modalType + "InputMaxFuelLabel");
    inputMaxFuelLabel.hide();
    let inputMaxSpeedLabel = $("#" + modalType + "InputMaxSpeedLabel");
    inputMaxSpeedLabel.hide();

    const elType = $('#' + modalType + 'DropPick').val();

    switch (elType) {
        case 'def': {
            inputName.hide();
            inputDesc.hide();
            inputCOS.hide();
            inputEnv.hide();
            inputAccMass.hide();
            inputMass.hide();
            inputVol.hide();
            inputCarMass.hide();
            inputCarVol.hide();
            inputATF.hide();
            inputMaxCrew.hide();
            inputSpecImp.hide();
            inputMaxFuel.hide();
            inputMaxSpeed.hide();

            inputNameLabel.hide();
            inputDescLabel.hide();
            inputCOSLabel.hide();
            inputEnvLabel.hide();
            inputAccMassLabel.hide();
            inputMassLabel.hide();
            inputVolLabel.hide();
            inputCarMassLabel.hide();
            inputCarVolLabel.hide();
            inputATFLabel.hide();
            inputMaxCrewLabel.hide();
            inputSpecImpLabel.hide();
            inputMaxFuelLabel.hide();
            inputMaxSpeedLabel.hide();
            break;
        }
        case 'Element': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            break;
        }
        case 'Resource Container': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();
            inputCarMass.show();
            inputCarVol.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            inputCarMassLabel.show();
            inputCarVolLabel.show();
            break;
        }
        case 'Element Carrier': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();
            inputEnv.show();
            inputCarMass.show();
            inputCarVol.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            inputCarMassLabel.show();
            inputCarVolLabel.show();

            break;
        }
        case 'Human Agent': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();
            inputATF.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            inputATFLabel.show();

            break;
        }
        case 'Robotic Agent': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();
            inputATF.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            inputATFLabel.show();

            break;
        }
        case 'Propulsive Vehicle': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();
            inputMaxCrew.show();
            inputSpecImp.show();
            inputMaxFuel.show();
            inputCarMass.show();
            inputCarVol.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            inputCarMassLabel.show();
            inputCarVolLabel.show();
            inputMaxCrewLabel.show();
            inputSpecImpLabel.show();
            inputMaxFuelLabel.show();


            break;
        }
        case 'Surface Vehicle': {
            inputName.show();
            inputDesc.show();
            inputCOS.show();
            inputEnv.show();
            inputAccMass.show();
            inputMass.show();
            inputVol.show();
            inputMaxCrew.show();
            inputMaxSpeed.show();
            inputMaxFuel.show();
            inputCarMass.show();
            inputCarVol.show();

            inputNameLabel.show();
            inputDescLabel.show();
            inputCOSLabel.show();
            inputEnvLabel.show();
            inputAccMassLabel.show();
            inputMassLabel.show();
            inputVolLabel.show();
            inputCarMassLabel.show();
            inputCarVolLabel.show();
            inputMaxCrewLabel.show();
            inputSpecImpLabel.show();
            inputMaxFuelLabel.show();

            break;
        }
    }
}


function getMessage(modalType) {
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

    switch (type) {
        case "Element": {
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
                propellant_id: 1,
                max_fuel: maxFuel,
                max_speed: maxSpeed
            });
            break;
        }
        case "Resource Container": {
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
        case "Element Carrier": {
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
        case "Human Agent": {
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
        case "Robotic Agent": {
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
        case "Propulsive Vehicle": {
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
                propellant_id: 1
            });
            break;
        }
        case "Surface Vehicle": {
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
                fuel_id: 1
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
    $("#editInputMass").val(data.mass)
    $("#editInputAccMass").val(data.accommodation_mass)

    if (elType === 'Resource Container') {
        $("#editInputCarMass").val(data.max_cargo_mass);
        $("#editInputCarVol").val(data.max_cargo_volume);
    } else if (elType === 'Element Carrier') {
        $("#editInputCarMass").val(data.max_cargo_mass);
        $("#editInputCarVol").val(data.max_cargo_volume);
    } else if (elType === 'Human Agent') {
        $("#editInputATF").val(data.active_time_fraction);
    } else if (elType === 'Robotic Agent') {
        $("#editInputATF").val(data.active_time_fraction);
    } else if (elType === 'Propulsive Vehicle') {
        $("#editInputMaxCrew").val(data.max_crew);
        $("#editInputSpecImp").val(data.isp);
        $("#editInputMaxFuel").val(data.max_fuel);
        $("#editInputCarMass").val(data.max_cargo_mass);
        $("#editInputCarVol").val(data.max_cargo_volume);
    } else if (elType === 'Surface Vehicle') {
        $("#editInputMaxCrew").val(data.max_crew);
        $("#editInputMaxSpeed").val(data.max_speed);
        $("#editInputMaxFuel").val(data.max_fuel);
        $("#editInputCarMass").val(data.max_cargo_mass);
        $("#editInputCarVol").val(data.max_cargo_volume);
    }
}