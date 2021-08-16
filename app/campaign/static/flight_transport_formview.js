$(document).ready( function() {
	populateNodes();
})



function retreiveElements(){
  let node = $('#pickNode').val(),
  time = $('#inputTime').val(),
  priority = $('#pickPriority').val();

  if (node && time && priority !== 'Choose...') {
    $('#ElementSel').find('option:not(:first)').remove();

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
											$('#ElementSel').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
										}
									});
								}
								//Sorts elements in element selector
								var options = $("#ElementSel option");
								options.detach().sort(function(a,b) {
									var at = $(a).text();
									var bt = $(b).text();
									return (at > bt)?1:((at < bt)?-1:0);
								});
								options.appendTo("#ElementSel");
							}
						});
					}
				}



  function onComplete(){

      name = $("#inputName").val();
      node_ID = $("#pickNodeID").val();
      exec_time = $("#inputTime").val();
      priority = $("#pickPriority").val();
      elements = $('#ElementSel').val();
      flight = $("#pickFlight").val();
      //duration =$("#Duration").val();

      message = JSON.stringify({
        name: name,
        origin_node_id: node_ID,
        //destination_node_id: dest_node_ID,
        exec_time: exec_time,
        priority: priority,
        flight: flight,
        elements_id_list: elements
        //duration : duration;
      });

      console.log(message);

      //location.reload()
      //console.log(data)

  }
