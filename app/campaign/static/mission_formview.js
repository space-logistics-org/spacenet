$(document).ready(function () {
    EventList();
    DemandList();
});


function EventList() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO SERVE A CONTAINER TO THE ELEMENTS.
    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

        // CREATE THE ELEMENTS.
    $('#eventadd').click(function () {
        itxtCnt = itxtCnt + 1;

        $(container).append('<input type="text"' +'placeholder="Event ID" class="events" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#eventmain').after(container);
    });
}

function DemandList() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO S ERVE A CONTAINER TO THE ELEMENTS.
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
        $(container).append('<input type="text"' +'placeholder="Resource ID" class="demandResource" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="Units" class="demandUnit" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#demandmain').after(container);
    });
}


function onComplete(){
    name = document.getElementById("inputName").value;
    startDate = document.getElementById("inputStartDate").value;
    scenarioName = document.getElementById("inputScenarioName").value;
    originID = document.getElementById("inputOriId").value;
    destID = document.getElementById("inputDestId").value;
    retOriginID = document.getElementById("inputReturnOriId").value;
    retDestinationID = document.getElementById("inputReturnDestId").value;

    var eventIds = new Array();

    $('.events').each(function () {
        if (this.value != '')
            eventIds.push(this.value);
    });

    var demandTypeList = new Array();
    var demandResourceList = new Array();
    var demandUnitList = new Array();

    $('.demandType').each(function () {
      if (this.value != '')
          demandTypeList.push(this.value);
    });

    $('.demandResource').each(function () {
      if (this.value != '')
          demandResourceList.push(this.value);
    });
    $('.demandUnit').each(function () {
      if (this.value != '')
          demandUnitList.push(this.value);
    });

    max = demandTypeList.length
    var missionDemands = [];

    for ( var i=0 ; i < max ; i++ ){
        missionDemands[i] = [JSON.stringify({
          resourceType : demandTypeList[i],
          resource : demandResourceList[i],
          units : demandUnitList[i]
        })
      ];
    }


    message= JSON.stringify({
      name : name,
      startDate : startDate,
      scenarioName : scenarioName,
      eventList : eventIds,
      demandModels : JSON.parse(missionDemands),
      destinationID : destID,
      originID : originID,
      returnOriginID : retOriginID,
      returnDestinationID : retDestinationID
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
