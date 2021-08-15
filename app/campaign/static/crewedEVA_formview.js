$(document).ready(function () {

	populateNodes();

	Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputNode').append('<option value="' + uuid + '">' + node.name + '</option>')
	});

    CrewList();
    DemandList();
});


function retreiveElements(){
  let node = $('#inputNode').val(),
  time = $('#inputTime').val(),
  priority = $('#inputPriority').val();

  if (node && time && priority !== 'Choose...') {
    $('#inputCrewVehicle').empty();

    $.ajax({
      url: "/campaign/api/simulation/?days_to_run_for=" + time,
      data: JSON.stringify(scenario),
      contentType: 'application/json; charset=utf-8',
      dataType: "json",
      method: "POST",
      success: function (simResult) {

								var namespace = simResult.result.namespace

								var allContents = getAllContents(findNodeContents(node, simResult), simResult)

								if (allContents.length === 0) {
									alert("No elements available at given time, please choose a different mission time")

								} else {
									allContents.forEach( function (contentUUID) {
										var eltObj = namespace[contentUUID].inner
										if (eltObj.type !== 'HumanAgent' && eltObj.type !== 'RoboticAgent') {
											$('#inputCrewVehicle').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
										}
									});
								}
								//Sorts elements in element selector
								var options = $("#inputCrewVehicle option");
								options.detach().sort(function(a,b) {
									var at = $(a).text();
									var bt = $(b).text();
									return (at > bt)?1:((at < bt)?-1:0);
								});
								options.appendTo("#inputCrewVehicle");
							}
						});
					}
				}


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
        $(container).append('<input type="text"' +'placeholder="Resource ID" class="demandResource" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="Amount" class="demandAmount" id=tb' + itxtCnt + ' value="" />');
        $(container).append('<input type="text"' +'placeholder="Units" class="demandUnit" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#demandmain').after(container);
    });
}


function onComplete(){
    name = document.getElementById("inputName").value;
    node = document.getElementById("inputNodeID").value;
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
