
function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	$('#createIn').hide()  
}



$(document).ready( function() {
	populateNodes();
	showUnselectedInstructions()
	Object.entries(scenario.elementList).forEach(function ([UUID, elt]) {
		addRow(UUID, elt)
	})
})

function loadSim() {
	let node = $('#pickNode').val(),
		time = getSimTime(),
		priority = $('#pickPriority').val();

	if (node !== 'def' && time && priority !== 'def') {
		$('.selected-instructions').show()
		$('.unselected-instructions').hide()
		$('#createIn').show()
		$('#createIn').find('option:not(:first)').remove();
		  
		$.ajax({
			url: "/campaign/api/simulation/?days_to_run_for=" + time + "&propulsive=false",
			data: JSON.stringify(scenario),
			contentType: 'application/json',
			dataType: "json",	  
			method: "POST",
			success: function (simResult) {
				var namespace = simResult.result.namespace

				var allContents = getAllContents(findNodeContents(node, simResult), simResult)
				$('#createIn').append('<option value=' + node + '>' + namespace[node].inner.name + '</option>')

				if (allContents.length !== 0) {
					allContents.forEach( function (contentUUID) {
						var eltObj = namespace[contentUUID].inner
						if (eltObj.type !== 'HumanAgent' && eltObj.type !== 'RoboticAgent') {
							$('#createIn').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
						}
					})
				}
			}
		});
	} else {
		showUnselectedInstructions()
	}


}


function onComplete(){

  var name = $('#inputName').val(),
  	entry_point_id = $('#createIn').val(),
	priority = $('#pickPriority').val(),
	mission_time = getTime(),
    elements = getSelected();

  document.getElementById("createElements").reset();

    data = {
		name: name,
		type: 'MakeElements',
		priority: parseInt(priority),
		mission_time: mission_time,
		elements: elements,
      	entry_point_id: entry_point_id
    }

	addEvent(data)
	alert('Event added')
	location.reload()
	console.log(compileScenario())

}
