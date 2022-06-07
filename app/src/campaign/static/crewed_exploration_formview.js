const genericResources = ['Generic COS 1', 'Generic COS 2', 'Generic COS 3']



$(document).ready( function() {

	populateNodes();
})


function getEVATime (ID) {
	function makeTwoDigits (timestring) {
		if (timestring.length < 2) {
			timestring = '0' + timestring
		}
		return timestring
    }

    var hrs = $('#' + ID + 'hours').val()
    var mins = $('#' + ID + 'minutes').val()
	  var secs = $('#' + ID + 'seconds').val()
    
    if (!hrs || !mins || !secs) {
        return null
    }

    var hrs = makeTwoDigits(hrs)
    var mins = makeTwoDigits(mins)
    var secs = makeTwoDigits(secs)

    return hrs + ':' + mins + ':' + secs + '.00'
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

	if (node !== 'def' && time && priority !== 'def') {
    $('#crewECheck').empty();
    $('#pickLocation').find('option:not(:first)').remove();

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
                      $('#crewECheck').append('<label for=' + contentUUID + '><input type="checkbox" value=' + contentUUID + '/>' + eltObj.name + " (active time fraction:" + eltObj.active_time_fraction + ")" +  '</label>')
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



function onComplete(){

    name = $("#inputName").val();
    node = $("#pickNode").val();
    eva_duration = getEVATime('EDur');
    crew_location = $("#pickLocation").val();
    duration = getEVATime('Dur');
    eva_per_week = $('#inputNumEVAS').val();
    type = "CrewedExploration"
		priority = $('#pickPriority').val();
		mission_time = getTime();

		crew = getChecked('#crewECheck');


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
