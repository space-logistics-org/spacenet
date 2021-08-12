
const genericResources = ['Generic COS 1', 'Generic COS 2', 'Generic COS 3']

function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	$('#moveTo').hide()  
	$('#elementsTree').jstree("destroy")
}

$(document).ready( function() {

	populateNodes()

  $('#addDemand').on('click', function() {
    console.log('add demand button clicked')
    $('#demandModal').modal('show')
  })
  
  $('#submitDemand').on('click', function() {
    type = $('#typeDropPick').val()
    resource = $('#resourceDropPick').val()
    amount = $('#inputAmount').val()
    units = $('#inputUnits').val()
  
  
    $('#demandModal').modal('hide')
  
    $('#consumeResourcesTable').append('<tr><td>' + type + '</td><td>' + resource + '</td><td>' + amount + '</td><td>' + units + '</td></tr>')
  })

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
				var namespace = simResult.result.namespace

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



function setResourceType () {

  var resourceType = $('#typeDropPick').val();

  switch(resourceType) {
    case 'Generic':
       {
        $('#resourceDropPick').find('option:not(:first)').remove()
        genericResources.forEach( function (genRec) {
          $('#resourceDropPick').append('<option value="' + genRec + '">' + genRec + '</option>')
        })
      break;
        }
    case 'Continuous':
      {
        $('#resourceDropPick').find('option:not(:first)').remove()
      scenario.resourceTypes.forEach( function(resource) {
        // if (resource.type === 'Continuous') {
          $('#resourceDropPick').append('<option value="' + resource.id + '">' + resource.name + '</option>')
        // }
      })
      break;
    }

    case 'Discrete':
      {
        $('#resourceDropPick').find('option:not(:first)').remove()

      scenario.resourceTypes.forEach( function(resource) {
        // if (resource.type === 'Discrete') {
          $('#resourceDropPick').find('option').remove()
          $('#resourceDropPick').append('<option value="' + resource.id + '">' + resource.name + '</option>')
        // }
      })
      break;
    }
  }


}

function onComplete(){

    var name = $("#inputName").val(),
      node = $("#pickNode").val(),
      time = $("#inputTime").val(),
      priority = $("#pickPriority").val(),
      to_remove = [],
      quantities = [];

      var table = document.getElementById("consumeResourcesTable");
      for (var i = 0, row; row = table.rows[i]; i++) {
         for (var j = 0, col; col = row.cells[j]; j++) {
           if (j === 1) {
             to_remove.push(col)
           } else if (j === 2) {
             quantities.push(col)
           }
         }  
      }

    data = {
      name: name,
      removal_point_id: node,
      time: time,
      priority: priority,
      to_remove: to_remove,
      quantity: quantities
    }

    alert(JSON.stringify(data))
    location.reload()

}
