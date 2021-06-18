
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
  alert(nType);
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
