$(document).ready(function () {

	populateNodes();

	Object.entries(scenario.resourceList).forEach( function([uuid, resource]) {
			value= JSON.stringify({resourceType : resource.type, resource : uuid, units : resource.units});
			$('#pickDemands').append('<option value=' + value + '>' + resource.name + '</option>')
		});
});


function loadSim(){
  let node = $('#pickNode').val(),
  time = getSimTime(),
  priority = $('#pickPriority').val();

  if (node && time && priority !== 'Choose...') {
	$('#inputCrewVehicle').find('option:not(:first)').remove();
	$('#checkboxes').empty();

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
					} else if (eltObj.type == 'HumanAgent') {
						$('#crewCheck').append('<label for=' + contentUUID + '><input type="checkbox" value=' + contentUUID + '/>' + eltObj.name + " (active time fraction:" + eltObj.active_time_fraction + ")" +  '</label>')
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




function onComplete(){
	name = $("#inputName").val();
	node_id = $("#pickNode").val();
	eva_duration = $("#inputEVADuration").val();
	type = "CrewedEVA"
	crew_vehicle = $('#inputCrewVehicle').val();
	crew = getChecked('#crewCheck');
	additional_demandJSON = $('#pickDemands').val();
	priority = $('#pickPriority').val();
	mission_time = getTime();

	additional_demand = []
	additional_demandJSON.forEach( function (demand) {
		console.log(demand)
		parsed_demand = JSON.parse(demand)
		additional_demand.push(parsed_demand)
	});

	data = {
		name : name,
		node_id : node_id,
		eva_duration : eva_duration,
		type : type,
		crew_vehicle : crew_vehicle,
		crew : crew,
		additional_demand : additional_demand,
		priority : priority,
		mission_time : mission_time
	}
	console.log(data);
	addEvent(data);
	alert('Event added')
	location.reload()
}
