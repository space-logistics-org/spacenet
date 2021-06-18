edgeType ="";
name = "";
origin_id = 0;
dest_id = 0;
dur = 0;
dist = 0;
max_crew = 0;
max_cargo = 0;
desc = "";

name = document.getElementById("inputName").value;
origin_id = document.getElementById("inputOrigin_ID").value;
dest_id = document.getElementById("inputDestination_ID").value;
dur = document.getElementById("inputDuration").value;
dist = document.getElementById("inputDistance").value;
max_crew = document.getElementById("inputMax_Crew").value;
max_cargo = document.getElementById("inputMax_Cargo").value;
desc = document.getElementById("inputDescription").value;



function formSet(){

  $("#components #inputName").prop("disabled",true);
  $("#components #inputOrigin_ID").prop("disabled",true);
  $("#components #inputDestination_ID").prop("disabled",true);
  $("#components #inputDuration").prop("disabled",true);
  $("#components #inputDistance").prop("disabled",true);
  $("#components #inputMax_Crew").prop("disabled",true);
  $("#components #inputMax_Cargo").prop("disabled",true);
  $("#components #inputDescription").prop("disabled",true);

  var edgeType = document.getElementById('dropPick').value;

  switch(edgeType) {
    case 'def':{
      $("#components #inputName").prop("disabled",true);
      $("#components #inputOrigin_ID").prop("disabled",true);
      $("#components #inputDestination_ID").prop("disabled",true);
      $("#components #inputDuration").prop("disabled",true);
      $("#components #inputDistance").prop("disabled",true);
      $("#components #inputMax_Crew").prop("disabled",true);
      $("#components #inputMax_Cargo").prop("disabled",true);
      $("#components #inputDescription").prop("disabled",true);
      break;
    }
    case 'Flight': {
      $("#components #inputName").prop("disabled",false);
      $("#components #inputOrigin_ID").prop("disabled",false);
      $("#components #inputDestination_ID").prop("disabled",false);
      $("#components #inputDuration").prop("disabled",false);
      $("#components #inputMax_Crew").prop("disabled",false);
      $("#components #inputMax_Cargo").prop("disabled",false);
      $("#components #inputDescription").prop("disabled",false);
      break;
        }
    case 'Space':{
      $("#components #inputName").prop("disabled",false);
      $("#components #inputOrigin_ID").prop("disabled",false);
      $("#components #inputDestination_ID").prop("disabled",false);
      $("#components #inputDuration").prop("disabled",false);
      $("#components #inputDescription").prop("disabled",false);
      break;}
    case 'Surface':{
      $("#components #inputName").prop("disabled",false);
      $("#components #inputOrigin_ID").prop("disabled",false);
      $("#components #inputDestination_ID").prop("disabled",false);
      $("#components #inputDistance").prop("disabled",false);
      $("#components #inputDescription").prop("disabled",false);
      break;}
  }
}

function onComplete(){

    name = document.getElementById("inputName").value;
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
          origin_id :  origin_id,
          destination_id : dest_id,
          duration : dur,
          max_crew : max_crew,
          max_cargo : max_cargo,
          description : desc,
          });
          break;
        }
      case "Space":{
        message = JSON.stringify({
          type : "Space",
          name : name,
          origin_id :  origin_id,
          destination_id : dest_id,
          duration : dur,
          description : desc,
      });
      break;
    }
      case "Surface":{
        message = JSON.stringify({
          type : "Surface",
          name : name,
          origin_id :  origin_id,
          destination_id : dest_id,
          distance : dist,
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
      location.href = 'edge_table.html'
    }
  });


}
