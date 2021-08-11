
function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	$('#createIn').hide()  
}

$(document).ready( function() {
	populateNodes();
	showUnselectedInstructions()
})

function loadSim() {
	let node = $('#pickNode').val(),
		time = $('#inputTime').val(),
		priority = $('#pickPriority').val();

	if (node !== 'def' && time && priority !== 'def') {
		$('.selected-instructions').show()
		$('.unselected-instructions').hide()
		$('#createIn').show()
		$('#createIn').find('option:not(:first)').remove();
		  
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
					$('#createIn').append('<option value=' + node + '>' + namespace[node].inner.name + '</option>')
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

  var entry_point_id = $('#createIn').val(),
	priority = $('#pickPriority').val(),
	mission_time = $('#inputTime').val(),
    elements = getSelected();

  document.getElementById("createElements").reset();

    data = {
		type: 'MakeElements',
		priority: parseInt(priority),
		mission_time: mission_time,
		elements: elements,
      	entry_point_id: entry_point_id
    }

    alert(JSON.stringify(data))
    location.reload()

}
