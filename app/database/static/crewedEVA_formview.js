$(document).ready(function () {
    CrewList();
    DemandList();
});



function CrewList() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO SERVE A CONTAINER TO THE ELEMENTS.
    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

        // CREATE THE ELEMENTS.
    $('#crewAdd').click(function () {
        itxtCnt = itxtCnt + 1;

        $(container).append('<input type="text"' +'placeholder="name" class="crewName" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="available time fraction" class="crewTimeFraction" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="EVA State" class="crewState" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#crewmain').after(container);
    });
}



function DemandList() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO SERVE A CONTAINER TO THE ELEMENTS.
    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

        // CREATE THE ELEMENTS.
    $('#demAdd').click(function () {
        itxtCnt = itxtCnt + 1;

        $(container).append('<input type="text"' +'placeholder="Resource Type" class="demandType" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="Resource" class="demandResource" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="Amount" class="demandAmount" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="Units" class="demandUnit" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#demandmain').after(container);
    });c
}


function onComplete(){
    name = document.getElementById("inputName").value;
    node = document.getElementById("inputNode").value;
    time = document.getElementById("inputTime").value;
    priority = document.getElementById("inputPriority").value;
    eva_duration = document.getElementById("inputEVADuration").value;
    crew_vehicle = document.getElementById("inputCrewVehicle").value


    var demandTypeList = new Array();
    var demandResourceList = new Array();
    var demandAmountList = new Array();
    var demandUnitList = new Array();

    $('.demandType').each(function () {
      if (this.value != '')
          demandTypeList.push(this.value);
    });

    $('.demandResource').each(function () {
      if (this.value != '')
          demandResourceList.push(this.value);
    });
    $('.demandAmount').each(function () {
      if (this.value != '')
          demandAmountList.push(this.value);
    });
    $('.demandUnit').each(function () {
      if (this.value != '')
          demandUnitList.push(this.value);
    });

    max = demandTypeList.length
    var evaDemandList = [];

    for ( var i=0 ; i < max ; i++ ){
        evaDemandList[i] = [JSON.stringify({
          resourceType : demandTypeList[i],
          resource : demandResourceList[i],
          amount : demandAmountList[i],
          units : demandUnitList[i]
        })
      ];
    }




    var crewNameList = new Array();
    var crewTimeFractionList = new Array();
    var crewStateList = new Array();

    $('.crewName').each(function () {
      if (this.value != '')
          crewNameList.push(this.value);
    });

    $('.crewTimeFraction').each(function () {
      if (this.value != '')
          crewTimeFractionList.push(this.value);
    });
    $('.crewState').each(function () {
      if (this.value != '')
          crewStateList.push(this.value);
    });

    max = crewNameList.length
    var crewMemEVAList = [];

    for ( var i=0 ; i < max ; i++ ){
        crewMemEVAList[i] = [JSON.stringify({
          name : crewNameList[i],
          active_time_fraction : crewTimeFractionList[i],
          type : "HumanAgent",
          eva_state : crewStateList[i]
        })
      ];
    }



    message= JSON.stringify({
      name : name,
      node : node,
      time : time,
      priority : priority,
      eva_duration : eva_duration,
      crew_vehicle : crew_vehicle,
      crew : JSON.parse(crewMemEVAList),
      additional_demand : JSON.parse(evaDemandList)
    });


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
