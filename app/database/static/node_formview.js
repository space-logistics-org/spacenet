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

$("#node #inputName").prop("disabled",true);
$("#node #inputDesc").prop("disabled",true);
$("#node #body1").prop("disabled",true);
$("#node #inputLat").prop("disabled",true);
$("#node #inputLong").prop("disabled",true);
$("#node #inputApo").prop("disabled",true);
$("#node #inputPeri").prop("disabled",true);
$("#node #inputInc").prop("disabled",true);

function formSet(){


  $("#node #inputName").prop("disabled",true);
  $("#node #inputDesc").prop("disabled",true);
  $("#node #body1").prop("disabled",true);
  $("#node #body2").prop("disabled",true);
  $("#node #inputLat").prop("disabled",true);
  $("#node #inputLong").prop("disabled",true);
  $("#node #inputApo").prop("disabled",true);
  $("#node #inputPeri").prop("disabled",true);
  $("#node #inputInc").prop("disabled",true);
  $("#node #inputlpNum").prop("disabled",true);

  nType = document.getElementById('dropPick').value;
  switch(nType) {
    case 'def':{
      $("#node #inputName").prop("disabled",true);
      $("#node #inputDesc").prop("disabled",true);
      $("#node #body1").prop("disabled",true);
      $("#node #body2").prop("disabled",true);
      $("#node #inputLat").prop("disabled",true);
      $("#node #inputLong").prop("disabled",true);
      $("#node #inputApo").prop("disabled",true);
      $("#node #inputPeri").prop("disabled",true);
      $("#node #inputInc").prop("disabled",true);
      $("#node #inputlpNum").prop("disabled",true);
      break;
   }
    case 'Surface Node': {
      $("#node #inputName").prop("disabled",false);
      $("#node #inputDesc").prop("disabled",false);
      $("#node #body1").prop("disabled",false);
      $("#node #inputLat").prop("disabled",false);
      $("#node #inputLong").prop("disabled",false);
      break;
        }
    case 'Orbital Node':{
      $("#node #inputName").prop("disabled",false);
      $("#node #inputDesc").prop("disabled",false);
      $("#node #body1").prop("disabled",false);
      $("#node #inputApo").prop("disabled",false);
      $("#node #inputPeri").prop("disabled",false);
      $("#node #inputInc").prop("disabled",false);
      break;}
    case 'Lagrange Node':
    { $("#node #inputName").prop("disabled",false);
      $("#node #inputDesc").prop("disabled",false);
      $("#node #body1").prop("disabled",false);
      $("#node #body2").prop("disabled",false);
      $("#node #inputlpNum").prop("disabled",false);
      break;}
  }
}

function onComplete(){
name = document.getElementById("inputName").value;
desc = document.getElementById("inputDesc").value;
//classOS =
type = document.getElementById("dropPick").value;
body1 = document.getElementById("body1").value;
body2 = document.getElementById("body2").value;
lat = document.getElementById("inputLat").value;
long = document.getElementById("inputLong").value;
lpn = document.getElementById("inputlpNum").value;
apo = document.getElementById("inputApo").value;
peri = document.getElementById("inputPeri").value;
inc = document.getElementById("inputInc").value;

switch(type){
  case "Surface Node":{
      message = JSON.stringify({
          name: name,
          description: desc,
          type: "Surface",
          body_1: body1,
          latitude: lat,
          longitude: long
      });
      break;
    }
  case "Orbital Node":{
    message = JSON.stringify({
      name: name,
      description: desc,
      type: "Orbital",
      body_1: body1,
      apoapsis: apo,
      periapsis: peri,
      inclination: inc
  });
  break;
}
  case "Lagrange Node":{
    message = JSON.stringify({
        name: name,
        description: desc,
        type: "Lagrange",
        body_1: body1,
        body_2: body2,
        lp_number: lpn
    });
    break;
    }
  }

  console.log(message)
  $.ajax({
    url: "/database/api/node/",
    data: message,
    contentType: 'application/json; charset=utf-8',
    dataType: "json",
    method: "POST",
    success: function() {
      document.getElementById("selection").reset();
      document.getElementById("node").reset();
      $('#addModal').modal('hide');
      location.reload()
    }
  });

}
