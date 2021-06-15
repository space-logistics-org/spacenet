
function formSet(){

  $("#components #inputName").prop("disabled",true);
  $("#components #inputCOS").prop("disabled",true);
  $("#components #inputEnv").prop("disabled",true);
  $("#components #inputAccMass").prop("disabled",true);
  $("#components #inputMass").prop("disabled",true);
  $("#components #inputVol").prop("disabled",true);
  $("#components #inputCarMass").prop("disabled",true);
  $("#components #inputCarVol").prop("disabled",true);
  $("#components #inputATF").prop("disabled",true);
  $("#components #inputMaxCrew").prop("disabled",true);
  $("#components #inputSpecImp").prop("disabled",true);
  $("#components #inputMaxFuel").prop("disabled",true);
  $("#components #inputMaxSpeed").prop("disabled",true);

  var elType = document.getElementById('dropPick').value;

  switch(elType) {
    case 'def':{
      $("#components #inputName").prop("disabled",true);
      $("#components #inputCOS").prop("disabled",true);
      $("#components #inputEnv").prop("disabled",true);
      $("#components #inputAccMass").prop("disabled",true);
      $("#components #inputMass").prop("disabled",true);
      $("#components #inputVol").prop("disabled",true);
      $("#components #inputCarMass").prop("disabled",true);
      $("#components #inputCarVol").prop("disabled",true);
      $("#components #inputATF").prop("disabled",true);
      $("#components #inputMaxCrew").prop("disabled",true);
      $("#components #inputSpecImp").prop("disabled",true);
      $("#components #inputMaxFuel").prop("disabled",true);
      $("#components #inputMaxSpeed").prop("disabled",true);
      break;
    }
    case 'Element': {
      $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      break;
        }
    case 'Resource Container':{
      $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputCarMass").prop("disabled",false);
      $("#components #inputCarVol").prop("disabled",false);
      break;}
    case 'Element Carrier':
    {  $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      break;}
    case 'Human Agent':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Robotic Agent':
    {  $("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputATF").prop("disabled",false);
      break;}
    case 'Propulsive Vehicle':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputMaxCrew").prop("disabled",false);
      $("#components #inputSpecImp").prop("disabled",false);
      $("#components #inputMaxFuel").prop("disabled",false);
      break;}
    case 'Surface Vehicle':
      {$("#components #inputName").prop("disabled",false);
      $("#components #inputCOS").prop("disabled",false);
      $("#components #inputEnv").prop("disabled",false);
      $("#components #inputAccMass").prop("disabled",false);
      $("#components #inputMass").prop("disabled",false);
      $("#components #inputVol").prop("disabled",false);
      $("#components #inputMaxCrew").prop("disabled",false);
      $("#components #inputMaxSpeed").prop("disabled",false);
      $("#components #inputMaxFuel").prop("disabled",false);
    break;}
  }
}
