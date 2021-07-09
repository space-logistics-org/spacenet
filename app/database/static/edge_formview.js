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
  console.log('in formset')
  console.log(edgeType)

  switch(edgeType) {

    case 'def':{
      $("#components #inputName").show();
      $("#components #inputOrigin_ID").show();
      $("#components #inputDestination_ID").show();
      $("#compo cxnents #inputDuration").show();
      $("#components #inputDistance").show();
      $("#components #inputMax_Crew").show();
      $("#components #inputMax_Cargo").show();
      $("#components #inputDescription").show();
      break;
    }

    case 'Flight': {
      $(".name").css("display", "block");
      $(".ori").css("display", "block");
      $(".desti").css("display", "block");
      $(".dura").css("display", "block");
      $(".crew").css("display", "block");
      $(".cargo").css("display", "block");
      $(".descr").css("display", "block");

      $(".dista").css({display: "none"});
      break;
    }

    case 'Space':{
      $(".name").css("display", "initial");
      $(".ori").css("display", "initial");
      $(".desti").css("display", "initial");
      $(".dura").css("display", "initial");
      $(".descr").css("display", "initial");

      $(".dista").css({display: "none"});
      $(".crew").css({display: "none"});
      $(".cargo").css({display: "none"});
      break;
    }

    case 'Surface':{
      $(".name").css("display", "initial");
      $(".ori").css("display", "initial");
      $(".desti").css("display", "initial");
      $(".dista").css("display", "initial");
      $(".descr").css("display", "initial");

      $(".dura").css({display: "none"});
      $(".crew").css({display: "none"});
      $(".cargo").css({display: "none"});
      break;
    }
  }
}

function onComplete(){

    name = document.getElementById("inputName").value;
    type = document.getElementById("dropPick").value;
    origin_id = document.getElementById("inputOrigin_ID").value;
    dest_id = document.getElementById("inputDestination_ID").value;
    dur = document.getElementById("inputDuration").value;
    dist = document.getElementById("inputDistance").value;
    max_crew = document.getElementById("inputMax_Crew").value;
    max_cargo = document.getElementById("inputMax_Cargo").value;
    desc = document.getElementById("inputDescription").value;

    switch(type){

      case "Flight":{
          message = JSON.stringify({
          type : "Flight",
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
          type : "Space",
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
          type : "Surface",
          name : name,
          origin_id :  parseInt(origin_id),
          destination_id : parseInt(dest_id),
          distance : parseInt(dist),
          description : desc,
        });
        break;
      }
    case "SpaceEdge":
    case 'Space':
    {
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
    case "SurfaceEdge":
    case 'Surface':
      {
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

  console.log(message)
  $.ajax({
    url: "/database/api/edge/",
    data: message,
    contentType: 'application/json; charset=utf-8',
    dataType: "json",
    method: "POST",
    success: function() {
      document.getElementById("edge").reset()
      document.getElementById("components").reset()
      location.href = 'edge_table.html'
    }
  });


}
