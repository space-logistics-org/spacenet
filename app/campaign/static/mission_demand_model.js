recT = "";
rec = "";
un = "";
am = 0;
dRate = 0;
resDur = 0;
hVol = 0;
hPres = 0;
hlr = 0;
av = 0;
ae = 0;
wwr = 0;
swr = 0;
br = false;
brp = 0;
ie = false;
imr = false;
evr = false;
ilm = false;
isruproduction = false;
clife = 0;
psci = 0;
unpsci = 0;
td = false;



function statusSet(){
  $("#timedModel").hide();
  $("#ratedModel").hide();
  $("#consumableModel").hide();
}


function formSet(){
  modelType = $('#dropPick').val();

  switch(modelType){
    case "Timed":
      $("#timedModel").show();
      $("#ratedModel").hide();
      $("#consumableModel").hide();
      break;

    case "Rated":
      $("#timedModel").hide();
      $("#ratedModel").show();
      $("#consumableModel").hide();
      break;

    case "Consumables":
      $("#timedModel").hide();
      $("#ratedModel").hide();
      $("#consumableModel").show();
      break;
  }
}

function onSubmit(){
  modelType = $('#dropPick').val();

  switch(modelType){
    case "Timed":
      recT = $('#inputRecType').val();
      rec = $('#inputRec').val();
      un = $('#inputUnits').val();
      am = $('#inputAmount').val();
      message = {
        resourceType: recT,
        resource: rec,
        units: un,
        amount: am
      }
      break;

    case "Rated":
      recT = $('#inputRecType').val();
      rec = $('#inputRec').val();
      un = $('#inputUnits').val();
      dRate = $('#inputDaily').val();
      message = {
        resourceType: recT,
        resource: rec,
        units: un,
        daily_rate: dRate
      }
      break;

    case "Consumables":
      recT = $('#inputRecType').val();
      rec = $('#inputRec').val();
      un = $('#inputUnits').val();
      dRate = $('#inputDaily').val();
      resDur = $('#inputResDur').val();
      hVol = $('#inputHabVol').val();
      hPres = $('#inputHabPres').val();
      hlr = $('#inputHabLeak').val();
      av = $('#inputAirVol').val();
      ae = $('#inputAirEff').val();
      wwr = $('#inputWasteWat').val();
      swr = $('#inputSolidWat').val();
      if ($("#inputBrineRec").is(':checked')) {
        br = true;
      } else { br = false;}
      brp = $('#inputBrineRecPerc').val();
      if ($('#inputIncElec').is(':checked')) {
        ie = true;
      } else { ie = false;}
      if ($('#inputMethRef').is(':checked')) {
        imr = true;
      } else { imr = false;}
      if ($('#inputEVACO2').is(':checked')) {
        evr = true;
      } else { evr = false;}
      if ($('#inputLaundry').is(':checked')) {
        ilm = true;
      } else { ilm = false;}
      isruproduction = $('#inputISRU').val();
      clife = $('#inputClothesLife').val();
      psci = $('#inputPresSci').val();
      unpsci = $('#inputUnpresSci').val();
      if ($('#inputTransDemands').is(':checked')) {
        td = true;
      } else { ts = false;}
      message = {
        resourceType: recT,
        resource: rec,
        units: un,
        reserves_duration: resDur,
        habitat_volume: hVol,
        habitat_pressure: hPres,
        habitat_leak_rate: hlr,
        airlock_volume: av,
        airlock_efficiency: ae,
        waste_water_recovered: wwr,
        solid_water_recovered: swr,
        brine_recycled: br,
        brine_recycled_percentage: brp,
        include_electrolysis: ie,
        include_methane_reformer: imr,
        eva_co2_recovered: evr,
        include_laundry_machine: ilm,
        isru_o2_production: isruproduction,
        clothes_lifetime: clife,
        press_science: psci,
        unpress_science: unpsci,
        transit_demands: td
      }
      alert(br);
      break;
  }
}
