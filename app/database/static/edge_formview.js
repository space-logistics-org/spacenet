name = "";
origin_id = 0;
dest_id = 0;
dur = 0;
dist = 0;
max_crew = 0;
max_cargo = 0;
desc = "";


function formSet(modalType) {

    let inputName = $("#" + modalType + "InputName");
    let inputNameLabel = $("#" + modalType + "InputNameLabel");
    let inputOrigin_ID = $("#" + modalType + "InputOrigin_ID");
    let inputOrigin_IDLabel = $("#" + modalType + "InputOrigin_IDLabel");
    let inputDestination_ID = $("#" + modalType + "InputDestination_ID");
    let inputDestination_IDLabel = $("#" + modalType + "InputDestination_IDLabel");
    let inputDuration = $("#" + modalType + "InputDuration");
    let inputDurationLabel = $("#" + modalType + "InputDurationLabel");
    let inputDistance = $("#" + modalType + "InputDistance");
    let inputDistanceLabel = $("#" + modalType + "InputDistanceLabel");
    let inputMax_Crew = $("#" + modalType + "InputMax_Crew");
    let inputMax_CrewLabel = $("#" + modalType + "InputMax_CrewLabel");
    let inputMax_Cargo = $("#" + modalType + "InputMax_Cargo");
    let inputMax_CargoLabel = $("#" + modalType + "InputMax_CargoLabel");
    let inputDescription = $("#" + modalType + "InputDescription");
    let inputDescriptionLabel = $("#" + modalType + "InputDescriptionLabel");
    inputName.hide();
    inputNameLabel.hide();
    inputOrigin_ID.hide();
    inputOrigin_IDLabel.hide();
    inputDestination_ID.hide();
    inputDestination_IDLabel.hide();
    inputDuration.hide();
    inputDurationLabel.hide();
    inputDistance.hide();
    inputDistanceLabel.hide();
    inputMax_Crew.hide();
    inputMax_CrewLabel.hide();
    inputMax_Cargo.hide();
    inputMax_CargoLabel.hide();
    inputDescription.hide();
    inputDescriptionLabel.hide();

    const edgeType = $('#' + modalType + 'DropPick').val();
    console.log('in formset')
    console.log(edgeType)

    switch (edgeType) {
        case 'def': {
            inputName.hide();
            inputNameLabel.hide();
            inputOrigin_ID.hide();
            inputOrigin_IDLabel.hide();
            inputDestination_ID.hide();
            inputDestination_IDLabel.hide();
            inputDuration.hide();
            inputDurationLabel.hide();
            inputDistance.hide();
            inputDistanceLabel.hide();
            inputMax_Crew.hide();
            inputMax_CrewLabel.hide();
            inputMax_Cargo.hide();
            inputMax_CargoLabel.hide();
            inputDescription.hide();
            inputDescriptionLabel.hide();
            break;
        }
        case 'FlightEdge':
        case 'Flight': {
            inputName.show();
            inputNameLabel.show();

            inputOrigin_ID.show();
            inputOrigin_IDLabel.show();

            inputDestination_ID.show();
            inputDestination_IDLabel.show();

            inputDuration.show();
            inputDurationLabel.show();

            inputMax_Crew.show();
            inputMax_CrewLabel.show();

            inputMax_Cargo.show();
            inputMax_CargoLabel.show();

            inputDescription.show();
            inputDescriptionLabel.show();

            break;
        }
        case 'SpaceEdge':
        case 'Space': {
            inputName.show();
            inputNameLabel.show();

            inputOrigin_ID.show();
            inputOrigin_IDLabel.show();

            inputDestination_ID.show();
            inputDestination_IDLabel.show();

            inputDuration.show();
            inputDurationLabel.show();

            inputDescription.show();
            inputDescriptionLabel.show();

            break;
        }

        case 'SurfaceEdge':
        case 'Surface': {
            inputName.show();
            inputNameLabel.show();

            inputOrigin_ID.show();
            inputOrigin_IDLabel.show();

            inputDestination_ID.show();
            inputDestination_IDLabel.show();

            inputDistance.show();
            inputDistanceLabel.show();

            inputDescription.show();
            inputDescriptionLabel.show();
            break;
        }
    }
}


function getMessage(modalType) {

    let name = $("#" + modalType + "InputName").val();
    let type = $("#" + modalType + "DropPick").val();
    let origin_id = $("#" + modalType + "InputOrigin_ID").val();
    let dest_id = $("#" + modalType + "InputDestination_ID").val();
    let dur = $("#" + modalType + "InputDuration").val();
    let dist = $("#" + modalType + "InputDistance").val();
    let max_crew = $("#" + modalType + "InputMax_Crew").val();
    let max_cargo = $("#" + modalType + "InputMax_Cargo").val();
    let desc = $("#" + modalType + "InputDescription").val();
    let message;
    switch (type) {

        case "FlightEdge":
        case 'Flight': {
            message = JSON.stringify({
                type: "FlightEdge",
                name: name,
                origin_id: parseInt(origin_id),
                destination_id: parseInt(dest_id),
                duration: parseInt(dur),
                max_crew: parseInt(max_crew),
                max_cargo: parseInt(max_cargo),
                description: desc,
            });
            break;
        }
        case "SpaceEdge":
        case 'Space': {
            message = JSON.stringify({
                type: "SpaceEdge",
                name: name,
                origin_id: parseInt(origin_id),
                destination_id: parseInt(dest_id),
                duration: parseInt(dur),
                description: desc,
            });
            break;
        }
        case "SurfaceEdge":
        case 'Surface': {
            message = JSON.stringify({
                type: "SurfaceEdge",
                name: name,
                origin_id: parseInt(origin_id),
                destination_id: parseInt(dest_id),
                distance: parseInt(dist),
                description: desc,
            });
            break;
        }
    }

    return message;
}


function formFill(data) {
    console.log(data)
    const edgeType = data.type
    console.log(edgeType)
    $('#editDropPick').val(edgeType).trigger('change')
    $("#editInputName").val(data.name)
    $("#editInputOrigin_ID").val(data.origin_id)
    $("#editInputDestination_ID").val(data.destination_id)
    $("#editInputDescription").val(data.description)

    if (edgeType === 'FlightEdge') {
        $("#editInputMax_Crew").val(data.max_crew);
        $("#editInputMax_Cargo").val(data.max_cargo);
        $("#editInputDuration").val(data.duration);

    } else if (edgeType === 'SpaceEdge') {
        $("#editInputDuration").val(data.duration);
    } else if (edgeType === 'SurfaceEdge') {
        $("#editInputDistance").val(data.distance);
    }
}