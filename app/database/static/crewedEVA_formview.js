name = "";
origin_id = 0;
dest_id = 0;
dur = 0;
dist = 0;
max_crew = 0;
max_cargo = 0;
desc = "";



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

        $(container).append('<input type="text"' +'placeholder="[available time fraction = ____, EVA state = ___]" class="crew" id=tb' + itxtCnt + ' value="" />');

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

        $(container).append('<input type="text"' +'placeholder="[resource type= ___, resource = ___, units= ___]" class="demand" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#demandmain').after(container);
    });
}


function onComplete(){
    name = document.getElementById("inputName").value;
    node = document.getElementById("inputNode").value;
    time = document.getElementById("inputTime").value;
    priority = document.getElementById("inputPriority").value;
    eva_duration = document.getElementById("inputEVADuration").value;
    crew_vehicle = document.getElementById("inputCrewVehicle").value

    var crewMem = new Array();
    $('.crew').each(function () {
        if (this.value != '')
            crewMem.push(this.value);
    });

    var addDemands = new Array();
    $('.demand').each(function () {
        if (this.value != '')
            addDemands.push(this.value);
    });

    alert(addDemands);
    message= JSON.stringify({
      name : name,
      node : node,
      time : time,
      priority : priority,
      eva_duration : eva_duration,
      crew_vehicle : crew_vehicle,
      crew : crewMem,
      additional_demand : addDemands
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
