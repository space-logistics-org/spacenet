const genericResources = ['Generic COS 1', 'Generic COS 2', 'Generic COS 3']



$(document).ready( function() {

	populateNodes();

  // $('#addDemand').on('click', function() {
  //   console.log('add demand button clicked')
  //   $('#demandModal').modal('show')
  // })
	//
  // $('#submitDemand').on('click', function() {
  //   type = $('#typeDropPick').val()
  //   resource = $('#resourceDropPick').val()
  //   amount = $('#inputAmount').val()
  //   units = $('#inputUnits').val()
	//
	//
  //   $('#demandModal').modal('hide')
	//
  //   $('#consumeResourcesTable').append('<tr><td>' + type + '</td><td>' + resource + '</td><td>' + amount + '</td><td>' + units + '</td></tr>')
  // })


  var table = $("#crewTable").DataTable( {
    scrollX: true,
    dom: 't',
    columnDefs: [
    {
      targets:   0,
      searchable: false,
      orderable: false,
      defaultContent: '',
      className: 'select-checkbox',
      width: '8%',
    }],
    select: {
        style:    'multi',
        selector: 'td:first-child'
    },
    order: [[ 1, 'asc' ]],
  });

  // scenario.elements.forEach( function(element) {
  //   if (element.type === 'HumanAgent') {
  //     table.row.add([, element.name,'x']).draw()
  //   }
  // })


})


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
      campaign.resources.forEach( function(resource) {
        if (resource.type === 'Continuous') {
          $('#resourceDropPick').append('<option value="' + resource.name + '">' + resource.name + '</option>')
        }
      })
      break;
    }

    case 'Discrete':
      {
        $('#resourceDropPick').find('option:not(:first)').remove()

      campaign.resources.forEach( function(resource) {
        if (resource.type === 'Discrete') {
          $('#resourceDropPick').find('option').remove()
          $('#resourceDropPick').append('<option value="' + resource.name + '">' + resource.name + '</option>')
        }
      })
      break;
    }
  }


}


function loadSim(){
  let node = $('#pickNode').val(),
  time = getSimTime(),
  priority = $('#pickPriority').val();

  if (node !== 'Choose...' && time!=='' && priority !== 'Choose...') {
    $('#pickLocation').empty();
		$('#pickCrew').empty();

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
											$('#pickLocation').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
										} else if(eltObj.type == 'HumanAgent') {
											$('#pickCrew').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
										}
									});
								}
								//Sorts elements in element selector
								var options = $("#pickLocation option");
								options.detach().sort(function(a,b) {
									var at = $(a).text();
									var bt = $(b).text();
									return (at > bt)?1:((at < bt)?-1:0);
								});
								options.appendTo("#pickLocation");
							}
						});
					}
				}
        // simResult.result.nodes.forEach( function(simNode) {
        //   if (simNode.inner.name === node) {
        //     simNode.contents.forEach( function(elementContained) {
        //       if (elementContained.inner.type !== 'HumanAgent' && elementContained.inner.type !== 'RoboticAgent') {
        //         $('#pickLocation').append('<option value="' + elementContained.inner + '">' + elementContained.inner.name + '</option>')



function onComplete(){

    name = $("#inputName").val();
    node = $("#pickNode").val();
    eva_duration = $("#inputEVADuration").val();
    crew_location = $("#pickLocation").val();
    duration = $("#inputDuration").val();
    eva_per_week = $('#inputNumEVAS').val();
    type = "CrewedExploration"
		priority = $('#pickPriority').val();
		mission_time = getTime();

		crew = $("#pickCrew").val();


    data = {
      name: name,
      node: node,
      eva_duration: eva_duration,
      crew_location: crew_location,
      duration: duration,
      eva_per_week: eva_per_week,
      type: type,
      priority: priority,
			mission_time : mission_time,
			crew: crew
    }
    console.log(data);
    addEvent(data);
    alert('Event added')
    location.reload()

}
