
function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
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
	var name = $('#inputName').val(),
	reconfigure_point_id = $('#pickNode').val(),
	priority = $('#pickPriority').val(),
	mission_time = $('#inputTime').val(),
    elements = getTreeSelected();

	document.getElementById("reconfigureElements").reset();

    data = {
		name: name,
		type: 'ReconfigureElements',
		priority: parseInt(priority),
		mission_time: mission_time,
		to_reconfigure: elements,
      	reconfigure_point_id: reconfigure_point_id
    }

	addEvent(data)
	alert('Event added')
	location.reload()
	console.log(compileScenario())
  
}