name = "";
desc = "";
classOS = 0;
type = "";
body1 = "";
body2 = "";
lat = 0;
long = 0;
lpn = 0;
apo = 0;
per = 0;
inc = 0;


const TYPES = {
    'SurfaceNode': 'Surface Node',
    'OrbitalNode': 'Orbital Node',
    'LagrangeNode': 'Lagrange Node'
}

function formSet(modalType) {


    let inputName = $("#" + modalType + "InputName").hide();
	inputName.hide()
    let inputDesc = $("#" + modalType + "InputDesc").hide();
	inputDesc.hide()
    let body1 = $("#" + modalType + "Body1").hide();
	body1.hide()
    let body2 = $("#" + modalType + "Body2").hide();
	body2.hide()
    let inputLat = $("#" + modalType + "InputLat").hide();
	inputLat.hide()
    let inputLong = $("#" + modalType + "InputLong").hide();
	inputLong.hide()
    let inputApo = $("#" + modalType + "InputApo").hide();
	inputApo.hide()
    let inputPeri = $("#" + modalType + "InputPeri").hide();
	inputPeri.hide()
    let inputInc = $("#" + modalType + "InputInc").hide();
	inputInc.hide()
    let inputlpNum = $("#" + modalType + "InputlpNum").hide();
	inputlpNum.hide()

    let inputNameLabel = $("#" + modalType + "InputNameLabel").hide();
	inputNameLabel.hide()
    let inputDescLabel = $("#" + modalType + "InputDescLabel").hide();
	inputDescLabel.hide()
    let body1Label = $("#" + modalType + "Body1Label").hide();
	body1Label.hide()
    let body2Label = $("#" + modalType + "Body2Label").hide();
	body2Label.hide()
    let inputLatLabel = $("#" + modalType + "InputLatLabel").hide();
	inputLatLabel.hide()
    let inputLongLabel = $("#" + modalType + "InputLongLabel").hide();
	inputLongLabel.hide()
    let inputApoLabel = $("#" + modalType + "InputApoLabel").hide();
	inputApoLabel.hide()
    let inputPeriLabel = $("#" + modalType + "InputPeriLabel").hide();
	inputPeriLabel.hide()
    let inputIncLabel = $("#" + modalType + "InputIncLabel").hide();
	inputIncLabel.hide()
    let inputlpNumLabel = $("#" + modalType + "InputlpNumLabel").hide();
	inputlpNumLabel.hide()

    nType = TYPES[$("#" + modalType + "DropPick").val()];
    console.log(nType)

    switch (nType) {
        case 'def': {
            inputName.hide();
            inputDesc.hide();
            body1.hide();
            body2.hide();
            inputLat.hide();
            inputLong.hide();
            inputApo.hide();
            inputPeri.hide();
            inputInc.hide();
            inputlpNum.hide();

            inputNameLabel.hide();
            inputDescLabel.hide();
            body1Label.hide();
            body2Label.hide();
            inputLatLabel.hide();
            inputLongLabel.hide();
            inputApoLabel.hide();
            inputPeriLabel.hide();
            inputIncLabel.hide();
            inputlpNumLabel.hide();
            break;
        }
        case 'Surface Node': {
            inputName.show();
            inputDesc.show();
            body1.show();
            inputLat.show();
            inputLong.show();

            inputNameLabel.show();
            inputDescLabel.show();
            body1Label.show();
            inputLatLabel.show();
            inputLongLabel.show();

            break;
        }
        case 'Orbital Node': {
            inputName.show();
            inputDesc.show();
            body1.show();
            inputApo.show();
            inputPeri.show();
            inputInc.show();

            inputNameLabel.show();
            inputDescLabel.show();
            body1Label.show();
            inputApoLabel.show();
            inputPeriLabel.show();
            inputIncLabel.show();

            break;
        }
        case 'Lagrange Node': {
            inputName.show();
            inputDesc.show();
            body1.show();
            body2.show();
            inputlpNum.show();

            inputNameLabel.show();
            inputDescLabel.show();
            body1Label.show();
            body2Label.show();
            inputlpNumLabel.show();

            break;
        }
    }
}

function getMessage(modalType) {
    name = $("#" + modalType + "InputName").val();
    desc = $("#" + modalType + "InputDesc").val();
    type = TYPES[$("#" + modalType + "DropPick").val()];
    body1 = $("#" + modalType + "Body1").val();
    body2 = $("#" + modalType + "Body2").val();
    lat = $("#" + modalType + "InputLat").val();
    long = $("#" + modalType + "InputLong").val();
    lpn = $("#" + modalType + "InputlpNum").val();
    apo = $("#" + modalType + "InputApo").val();
    peri = $("#" + modalType + "InputPeri").val();
    inc = $("#" + modalType + "InputInc").val();

    switch (type) {
        case "Surface Node": {
            message = JSON.stringify({
                name: name,
                description: desc,
                type: "SurfaceNode",
                body_1: body1,
                latitude: lat,
                longitude: long
            });
            break;
        }
        case "Orbital Node": {
            message = JSON.stringify({
                name: name,
                description: desc,
                type: "OrbitalNode",
                body_1: body1,
                apoapsis: apo,
                periapsis: peri,
                inclination: inc
            });
            break;
        }
        case "Lagrange Node": {
            message = JSON.stringify({
                name: name,
                description: desc,
                type: "LagrangeNode",
                body_1: body1,
                body_2: body2,
                lp_number: parseInt(lpn)
            });
            break;
        }
    }
    return message

}


function formFill(data) {
    const nType = data.type;
    $("#editDropPick").val(nType).trigger('change')
    $("#editInputName").val(data.name);
    $("#editInputDesc").val(data.description);
    body1 = $("#editBody1").val(data.body_1);
    lat = $("#editInputLat").val(data.latitude);
    long = $("#editInputLong").val(data.longitude);

    if (nType === 'OrbitalNode') {
        apo = $("#editInputApo").val(data.apoapsis);
        peri = $("#editInputPeri").val(data.periapsis);
        inc = $("#editInputInc").val(data.inclination);
    } else if (nType === 'LagrangeNode') {
        body2 = $("#editBody2").val(data.body_2);
        lpn = $("#editInputlpNum").val(data.lp_number);
    }
}