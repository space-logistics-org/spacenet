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


    $("#" + modalType + "InputName").hide();
    $("#" + modalType + "InputDesc").hide();
    $("#" + modalType + "Body1").hide();
    $("#" + modalType + "Body2").hide();
    $("#" + modalType + "InputLat").hide();
    $("#" + modalType + "InputLong").hide();
    $("#" + modalType + "InputApo").hide();
    $("#" + modalType + "InputPeri").hide();
    $("#" + modalType + "InputInc").hide();
    $("#" + modalType + "InputlpNum").hide();

    $("#" + modalType + "InputNameLabel").hide();
    $("#" + modalType + "InputDescLabel").hide();
    $("#" + modalType + "Body1Label").hide();
    $("#" + modalType + "Body2Label").hide();
    $("#" + modalType + "InputLatLabel").hide();
    $("#" + modalType + "InputLongLabel").hide();
    $("#" + modalType + "InputApoLabel").hide();
    $("#" + modalType + "InputPeriLabel").hide();
    $("#" + modalType + "InputIncLabel").hide();
    $("#" + modalType + "InputlpNumLabel").hide();

    nType = TYPES[$("#" + modalType + "DropPick").val()];
    console.log(nType)

    switch (nType) {
        case 'def': {
            $("#" + modalType + "InputName").hide();
            $("#" + modalType + "InputDesc").hide();
            $("#" + modalType + "Body1").hide();
            $("#" + modalType + "Body2").hide();
            $("#" + modalType + "InputLat").hide();
            $("#" + modalType + "InputLong").hide();
            $("#" + modalType + "InputApo").hide();
            $("#" + modalType + "InputPeri").hide();
            $("#" + modalType + "InputInc").hide();
            $("#" + modalType + "InputlpNum").hide();

            $("#" + modalType + "InputNameLabel").hide();
            $("#" + modalType + "InputDescLabel").hide();
            $("#" + modalType + "Body1Label").hide();
            $("#" + modalType + "Body2Label").hide();
            $("#" + modalType + "InputLatLabel").hide();
            $("#" + modalType + "InputLongLabel").hide();
            $("#" + modalType + "InputApoLabel").hide();
            $("#" + modalType + "InputPeriLabel").hide();
            $("#" + modalType + "InputIncLabel").hide();
            $("#" + modalType + "InputlpNumLabel").hide();
            break;
        }
        case 'Surface Node': {
            $("#" + modalType + "InputName").show();
            $("#" + modalType + "InputDesc").show();
            $("#" + modalType + "Body1").show();
            $("#" + modalType + "InputLat").show();
            $("#" + modalType + "InputLong").show();

            $("#" + modalType + "InputNameLabel").show();
            $("#" + modalType + "InputDescLabel").show();
            $("#" + modalType + "Body1Label").show();
            $("#" + modalType + "InputLatLabel").show();
            $("#" + modalType + "InputLongLabel").show();

            break;
        }
        case 'Orbital Node': {
            $("#" + modalType + "InputName").show();
            $("#" + modalType + "InputDesc").show();
            $("#" + modalType + "Body1").show();
            $("#" + modalType + "InputApo").show();
            $("#" + modalType + "InputPeri").show();
            $("#" + modalType + "InputInc").show();

            $("#" + modalType + "InputNameLabel").show();
            $("#" + modalType + "InputDescLabel").show();
            $("#" + modalType + "Body1Label").show();
            $("#" + modalType + "InputApoLabel").show();
            $("#" + modalType + "InputPeriLabel").show();
            $("#" + modalType + "InputIncLabel").show();

            break;
        }
        case 'Lagrange Node': {
            $("#" + modalType + "InputName").show();
            $("#" + modalType + "InputDesc").show();
            $("#" + modalType + "Body1").show();
            $("#" + modalType + "Body2").show();
            $("#" + modalType + "InputlpNum").show();

            $("#" + modalType + "InputNameLabel").show();
            $("#" + modalType + "InputDescLabel").show();
            $("#" + modalType + "Body1Label").show();
            $("#" + modalType + "Body2Label").show();
            $("#" + modalType + "InputlpNumLabel").show();

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