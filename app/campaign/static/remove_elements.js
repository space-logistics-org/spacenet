function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	$('#elementsTree').jstree("destroy")
}

$(document).ready( function() {
	populateNodes();

	showUnselectedInstructions()

})


function loadSim() {
	let node = $('#pickNode').val(),
		time = getSimTime(),
		priority = $('#pickPriority').val();

	if (node !== 'def' && time && priority !== 'def') {
		$('.selected-instructions').show()
		$('.unselected-instructions').hide()
		$('#elementsTree').jstree("destroy")
		  
		$.ajax({
			url: "/campaign/api/simulation/?days_to_run_for=" + time,
			data: JSON.stringify(scenario),
			contentType: 'application/json',
			dataType: "json",	  
			method: "POST",
			success: function (simResult) {
				var allContents = getAllContents(findNodeContents(node, simResult), simResult)

				if (allContents.length === 0) {
					alert("No elements available at given time, please choose a different mission time")

				} else {
					createTree(simResult, node)
				}
			}
		});
	} else {
		showUnselectedInstructions()
	}


}


function onComplete(){


  var name = $('#inputName').val()
  	removal_point_id = $('#pickNode').val(),
	priority = $('#pickPriority').val(),
	mission_time = getTime(),
    elements = getTreeSelected();

	document.getElementById("removeElements").reset();

    data = {
		name: name,
		type: 'RemoveElements',
		priority: parseInt(priority),
		mission_time: mission_time,
		elements: elements,
      	removal_point_id: removal_point_id
    }

	addEvent(data)
	alert('Event added')
	location.reload()
	console.log(compileScenario())

}
