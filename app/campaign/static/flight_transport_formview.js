$(document).ready( function() {
	console.log(compileScenario())


	Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputOriginNode').append('<option value="' + uuid + '">' + node.name + '</option>')
		}
	);
	Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputDestinationNode').append('<option value="' + uuid + '">' + node.name + '</option>')
		}
	);
})



function loadSim(){
  let node = $('#inputOriginNode').val(),
  time = getSimTime(),
  priority = $('#pickPriority').val();

  if (node !== 'def' && time && priority !== 'def') {
    $('#ElementSel').empty();

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
											$('#ElementSel').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
										}
									});
								}
								//Sorts elements in element selector
								var options = $("#ElementSel option");
								options.detach().sort(function(a,b) {
									var at = $(a).text();
									var bt = $(b).text();
									return (at > bt)?1:((at < bt)?-1:0);
								});
								options.appendTo("#ElementSel");
							}
						});
					}
				}



  function onComplete(){

		name = $("#inputName").val();
		elements_id_list = $("#ElementSel").val();
		type = "FlightTransport"
		//optional=deltav
		origin_node_id = $("#inputOriginNode").val();
		destination_node_id = $("#inputDestinationNode").val();
		priority = $('#pickPriority').val();
		mission_time = getTime();

		Object.entries(scenario.network.edges).forEach( function([uuid, edge]) {
			if (origin_node_id == edge.origin_id && destination_node_id == edge.destination_id){
				edge_id = uuid;
				exec_time = edge.duration
			}
		});

		data = {
			name: name,
			elements_id_list: elements_id_list,
			type: type,
			origin_node_id: origin_node_id,
			destination_node_id: destination_node_id,
			exec_time: exec_time,
			type: type,
			priority: priority,
			mission_time : mission_time,
			edge_id: edge_id,
			exec_time: exec_time,
		}
		console.log(data);
		addEvent(data);
		alert('Event added')
		location.reload()


  }
