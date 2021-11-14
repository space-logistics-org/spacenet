$(document).ready( function() {
	Object.entries(scenario.network.edges).forEach( function([uuid, edge]) {
		value = JSON.stringify({"origin_id" : edge.origin_id , "edge_uuid" : uuid});
		$('#pickEdge').append('<option value= ' + value  + ' >' + edge.name + '</option>')
	  });

	$('#addBurn').on('click', function() {
		elementName = $("#elementSeqSel option:selected").text();
		name = $('#inputName').val()

		$('#propulsiveBurnTable').append('<tr><td><input type="checkbox"></td><td> '+ elementName +  '</td><td>Burn</td><td>' + name + '</td>')
	})

	$('#addStage').on('click', function() {
		elementName = $("#elementSeqSel option:selected").text();
		name = $('#inputName').val()

		$('#propulsiveBurnTable').append('<tr><td><input type="checkbox"></td><td> '+ elementName +  '</td><td>Stage</td><td>' + name + '</td>')
	})


		$('#delete').on('click', function() {
			var tableRef = document.getElementById('propulsiveBurnTableBody');
		  var tableRows = tableRef.rows;

		  var checkedRows = [];
		 	for (var i = 0; i < tableRows.length; i++) {
				if (tableRows[i].querySelector('input').checked) {
					checkedRows.push(tableRows[i]);
				}
			}
			for (var k = 0; k < checkedRows.length; k++) {
				checkedRows[k].parentNode.removeChild(checkedRows[k]);
			}
		})
	})




function loadSim(){
	var edge = $('#pickEdge').val();
	//will raise JSON error if edge is not chosen first but doesn't really matter.
	node = JSON.parse(edge).origin_id

  time = getSimTime(),
  priority = $('#pickPriority').val();



  if (node !== 'def' && time && priority !== 'def') {
    $('#elementSeqSel').empty();

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
										if (eltObj.type !== 'HumanAgent' && eltObj.type !== 'RoboticAgent'){
											$('#elementSeqSel').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
										}
									});
								}
								//Sorts elements in element selector
								var options = $("#elementSeqSel option");
								options.detach().sort(function(a,b) {
									var at = $(a).text();
									var bt = $(b).text();
									return (at > bt)?1:((at < bt)?-1:0);
								});
								options.appendTo("#elementSeqSel");
							}
						})
					}
				}


  function onComplete(){
		name = $("#inputName").val();
		elements = $("#elementTransportSelector").val();
		type = "PropulsiveBurn"
		delta_v = $('#inputDelta').val();
		priority = $('#pickPriority').val();
		mission_time = getTime();

		//used for the Burn property
		var edge = $('#pickEdge').val();
		edge_values = JSON.parse(edge)
		node_id = edge_values.origin_id
		edge_id = edge_values.edge_uuid

		burn = {edge_id : edge_id , time : mission_time , delta_v : delta_v }

		var currentTab = document.getElementById('propulsiveBurnTable');
		burn_stage_sequence = new Array

		// LOOP THROUGH EACH ROW OF THE TABLE AFTER HEADER.
		for (i = 1; i < currentTab.rows.length; i++) {
			burnStageItem = {}

			// GET THE CELLS COLLECTION OF THE CURRENT ROW.
			var objCells = currentTab.rows.item(i).cells;

			// LOOP THROUGH EACH CELL OF THE CURENT ROW TO READ CELL VALUES.
			for (var j = 1; j < objCells.length-1; j++) {
				//Get element ID rather than the innerHTML
				if ( j == 1 ){
					Object.entries(scenario.elementList).forEach( function([uuid, element]) {
						if (objCells.item(j).innerHTML.trim() == element.name.trim()){
							burnStageItem["element_id"] = uuid
						}
					});
				} else {
					burnStageItem["burnStage"]= objCells.item(j).innerHTML
				}
			}
			burn_stage_sequence.push(burnStageItem)
		}

		data = {
			name: name,
			elements: elements,
			type: type,
			delta_v: delta_v,
			priority: priority,
			mission_time: mission_time,
			type: type,
			priority: priority,
			mission_time : mission_time,
			burn: burn,
			burn_stage_sequence: burn_stage_sequence
		}
		console.log(data);
		addEvent(data);
		alert('Event added')
		location.reload()
		}
