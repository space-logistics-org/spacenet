function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	$('#moveTo').hide()  
	$('#elementsTree').jstree("destroy")
}


$(document).ready( function() {
	populateNodes()
  	showUnselectedInstructions()
})



function loadSim() {
	let node = $('#pickNode').val(),
		time = $('#inputTime').val(),
		priority = $('#pickPriority').val();
	
	if (node !== 'def' && time && priority !== 'def') {
		$('.selected-instructions').show()
		$('.unselected-instructions').hide()
		$('#moveTo').show()
		$('#elementsTree').jstree("destroy")
		$('#moveTo').find('option:not(:first)').remove();

		  
		$.ajax({
			url: "/campaign/api/simulation/?days_to_run_for=" + time,
			data: JSON.stringify(scenario),
			contentType: 'application/json',
			dataType: "json",	  
			method: "POST",
			success: function (simResult) {
				var namespace = simResult.result.namespace
				console.log(namespace)

				var allContents = getAllContents(findNodeContents(node, simResult), simResult)
				$('#moveTo').append('<option value=' + node + '>' + namespace[node].inner.name + '</option>')

				if (allContents.length === 0) {
					alert("No elements available at given time, please choose a different mission time")

				} else {
					allContents.forEach( function (contentUUID) {
						var eltObj = namespace[contentUUID].inner
						if (eltObj.type === 'ElementCarrier' || eltObj.type === 'PropulsiveVehicle') {
							$('#moveTo').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
						}
					})
					createTree(simResult, node)

				}
			}
		});
	} else {
		showUnselectedInstructions()
	}


}


function onComplete(){

  var name = $('#inputName').val(),
  	  origin_id = $('#pickNode').val(),
      destination_id = $('#moveTo').val(),
	  to_move = getTreeSelected(),
	  type = 'MoveElements',
	  priority = $('#pickPriority').val(),
	  mission_time = $('#inputTime').val();

	console.log("selected in tree:", to_move)


  document.getElementById("moveElements").reset();

	data = {
		name: name,
		type: type,
		priority: parseInt(priority),
		mission_time: mission_time,
		to_move: to_move,
		origin_id: origin_id,
		destination_id: destination_id
	}

	addEvent(data)
	alert('Event added')
	location.reload()
	console.log(compileScenario())

}
