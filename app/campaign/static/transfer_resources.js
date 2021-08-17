function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	$('#pickTo').hide()  
	$('#pickFrom').hide()  
}

  $(document).ready( function() {
    populateNodes();
	
	showUnselectedInstructions()
  })


function setTransfer() {

	let from = $('#pickFrom').val(),
		to = $('#pickTo').val();

	if (from && to !== 'Choose...') {
	    $('#transferResourcesTable > tbody').append('<tr><td>' + 'x' + '</td><td>' + from + '</td><td>' + to + '</td></tr>')
	}

}


function loadSim() {
	let node = $('#pickNode').val(),
		time = $('#inputTime').val(),
		priority = $('#pickPriority').val();

	if (node !== 'def' && time && priority !== 'def') {
		$('.selected-instructions').show()
		$('.unselected-instructions').hide()
		$('#pickTo').show()  
		$('#pickFrom').show()  
		$('#pickFrom').find('option:not(:first)').remove();
    	$('#pickTo').find('option:not(:first)').remove();

		$.ajax({
			url: "/campaign/api/simulation/?days_to_run_for=" + time,
			data: JSON.stringify(scenario),
			contentType: 'application/json',
			dataType: "json",	  
			method: "POST",
			success: function (simResult) {
				var namespace = simResult.result.namespace

				var allContents = getAllContents(findNodeContents(node, simResult), simResult)

				if (allContents.length === 0) {
					alert("No elements available at given time, please choose a different mission time")

				} else {
					$('#pickFrom').append('<option value=' + node + '>' + namespace[node].inner.name + '</option>')
					$('#pickTo').append('<option value=' + node + '>' + namespace[node].inner.name + '</option>')
					allContents.forEach( function (contentUUID) {
						var eltObj = namespace[contentUUID].inner
						console.log(eltObj)
						if (eltObj.type === 'ElementCarrier' || eltObj.type === 'PropulsiveVehicle') {
							$('#pickFrom').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
							$('#pickTo').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
		
						}
					})
					createTree(simResult, node)

				}
			}
		})
	} else {
		showUnselectedInstructions()
	}
}

function onComplete(){

    var name = $("#inputName").val(),
    node = $("#pickNode").val(),
    time = $("#inputTime").val(),
    priority = $("#pickPriority").val(),
    origin_id = $("#pickFrom").val(),
    destination_id = $("#pickTo").val();

    document.getElementById("transferResources").reset();

    to_transfer = []

    data = {
      name: name,
      node: node,
      time: time,
      priority: priority,
      origin_id: origin_id,
      destination_id: destination_id,
      to_transfer: to_transfer
    }

	addEvent(data)
	alert('Event added')
	location.reload()
	console.log(compileScenario())
}
