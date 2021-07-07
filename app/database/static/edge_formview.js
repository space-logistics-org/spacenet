name = "";
origin_id = 0;
dest_id = 0;
dur = 0;
dist = 0;
max_crew = 0;
max_cargo = 0;
desc = "";


function formSet(modalType) {

  $("#" + modalType + "InputName").hide();
  $("#" + modalType + "InputNameLabel").hide();
  $("#" + modalType + "InputOrigin_ID").hide();
  $("#" + modalType + "InputOrigin_IDLabel").hide();
  $("#" + modalType + "InputDestination_ID").hide();
  $("#" + modalType + "InputDestination_IDLabel").hide();
  $("#" + modalType + "InputDuration").hide();
  $("#" + modalType + "InputDurationLabel").hide();
  $("#" + modalType + "InputDistance").hide();
  $("#" + modalType + "InputDistanceLabel").hide();
  $("#" + modalType + "InputMax_Crew").hide();
  $("#" + modalType + "InputMax_CrewLabel").hide();
  $("#" + modalType + "InputMax_Cargo").hide();
  $("#" + modalType + "InputMax_CargoLabel").hide();
  $("#" + modalType + "InputDescription").hide();
  $("#" + modalType + "InputDescriptionLabel").hide();

  var edgeType = $('#' + modalType + 'DropPick').val();

  switch(edgeType) {
    case 'def':{
      $("#" + modalType + "InputName").hide();
      $("#" + modalType + "InputNameLabel").hide();
      $("#" + modalType + "InputOrigin_ID").hide();
      $("#" + modalType + "InputOrigin_IDLabel").hide();
      $("#" + modalType + "InputDestination_ID").hide();
      $("#" + modalType + "InputDestination_IDLabel").hide();
      $("#" + modalType + "InputDuration").hide();
      $("#" + modalType + "InputDurationLabel").hide();
      $("#" + modalType + "InputDistance").hide();
      $("#" + modalType + "InputDistanceLabel").hide();
      $("#" + modalType + "InputMax_Crew").hide();
      $("#" + modalType + "InputMax_CrewLabel").hide();
      $("#" + modalType + "InputMax_Cargo").hide();
      $("#" + modalType + "InputMax_CargoLabel").hide();
      $("#" + modalType + "InputDescription").hide();
      $("#" + modalType + "InputDescriptionLabel").hide();
      break;
    }
    case 'Flight': {
      $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputNameLabel").show();

      $("#" + modalType + "InputOrigin_ID").show();
      $("#" + modalType + "InputOrigin_IDLabel").show();

      $("#" + modalType + "InputDestination_ID").show();
      $("#" + modalType + "InputDestination_IDLabel").show();

      $("#" + modalType + "InputDuration").show();
      $("#" + modalType + "InputDurationLabel").show();

      $("#" + modalType + "InputMax_Crew").show();
      $("#" + modalType + "InputMax_CrewLabel").show();

      $("#" + modalType + "InputMax_Cargo").show();
      $("#" + modalType + "InputMax_CargoLabel").show();

      $("#" + modalType + "InputDescription").show();
      $("#" + modalType + "InputDescriptionLabel").show();

      break;
        }
    case 'Space':{
      $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputNameLabel").show();

      $("#" + modalType + "InputOrigin_ID").show();
      $("#" + modalType + "InputOrigin_IDLabel").show();

      $("#" + modalType + "InputDestination_ID").show();
      $("#" + modalType + "InputDestination_IDLabel").show();

      $("#" + modalType + "InputDuration").show();
      $("#" + modalType + "InputDurationLabel").show();

      $("#" + modalType + "InputDescription").show();
      $("#" + modalType + "InputDescriptionLabel").show();

      break;
    }

    case 'Surface':{
      $("#" + modalType + "InputName").show();
      $("#" + modalType + "InputNameLabel").show();

      $("#" + modalType + "InputOrigin_ID").show();
      $("#" + modalType + "InputOrigin_IDLabel").show();

      $("#" + modalType + "InputDestination_ID").show();
      $("#" + modalType + "InputDestination_IDLabel").show();

      $("#" + modalType + "InputDistance").show();
      $("#" + modalType + "InputDistanceLabel").show();

      $("#" + modalType + "InputDescription").show();
      $("#" + modalType + "InputDescriptionLabel").show();
      break;}
  }
}


function getMessage(modalType) {

  name = $("#" + modalType + "InputName").val();
  type = $("#" + modalType + "DropPick").val();
  origin_id = $("#" + modalType + "InputOrigin_ID").val();
  dest_id = $("#" + modalType + "InputDestination_ID").val();
  dur = $("#" + modalType + "InputDuration").val();
  dist = $("#" + modalType + "InputDistance").val();
  max_crew = $("#" + modalType + "InputMax_Crew").val();
  max_cargo = $("#" + modalType + "InputMax_Cargo").val();
  desc = $("#" + modalType + "InputDescription").val();

  switch(type){

    case "Flight":{
        message = JSON.stringify({
        type : "FlightEdge",
        name : name,
        origin_id :  parseInt(origin_id),
        destination_id : parseInt(dest_id),
        duration : parseInt(dur),
        max_crew : parseInt(max_crew),
        max_cargo : parseInt(max_cargo),
        description : desc,
        });
        break;
      }
    case "Space":{
      message = JSON.stringify({
        type : "SpaceEdge",
        name : name,
        origin_id :  parseInt(origin_id),
        destination_id : parseInt(dest_id),
        duration : parseInt(dur),
        description : desc,
    });
    break;
  }
    case "Surface":{
      message = JSON.stringify({
        type : "SurfaceEdge",
        name : name,
        origin_id :  parseInt(origin_id),
        destination_id : parseInt(dest_id),
        distance : parseInt(dist),
        description : desc,
      });
      break;
  }
}

return message;
}



function formFill(data) {
  console.log(data)
  var edgeType = data.type
  $('#editDropPick').val(edgeType).trigger('change')
  $("#editInputName").val(data.name)
  $("#editInputOrigin_ID").val(data.origin_id)
  $("#editInputDestination_ID").val(data.destination_id)
  $("#editInputDescription").val(data.description)

  if (edgeType === 'Flight') 
    {
      $("#editInputMax_Crew").val(data.max_crew);
      $("#editInputMax_Cargo").val(data.max_cargo);
      $("#editInputDuration").val(data.duration);

    }
  else if (edgeType === 'Space')
    {
      $("#editInputDuration").val(data.duration);
    }
  else if (edgeType === 'Surface')
    {
      $("#editInputDistance").val(data.distance);
    }
  }