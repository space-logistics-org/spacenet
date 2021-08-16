$(document).ready(function () {

	//Append Nodes to destination and origin selectors nased on scenario object.
  Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputOriginNode').append('<option value="' + uuid + '">' + node.name + '</option>')
		}
	);

  Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputDestinationNode').append('<option value="' + uuid + '">' + node.name + '</option>')
		}
	);
})



//Populate Element selector with elements based on simulation filter.
function retreiveElements(){

	let node = $('#inputOriginNode').val(),
  time = $('#inputTime').val(),
  priority = $('#inputPriority').val();


  	if (node !== 'def' && time && priority !== 'def'){
    $('#elementSeqSel').empty();
		$('#elementTransportSelector').empty();



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
										$('#elementTransportSelector').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')

									});
								}
								//Sorts elements in element selector
								var options = $("#elementTransportSelector option");
								options.detach().sort(function(a,b) {
									var at = $(a).text();
									var bt = $(b).text();
									return (at > bt)?1:((at < bt)?-1:0);
								});
								options.appendTo("#elementTransportSelector");
							}
						});
					}
        }



function onComplete() {
    location.reload()


    // message= JSON.stringify({
    //   name : name,
    //   origin_node : origin_node,
    //   destination_node : destination_node,
    //   time : time,
    //   priority : priority,
    //   elements : JSON.parse(arr),
    //   burnStageProfile : JSON.parse(burnStageProfile)
    // });
    //
    //
    // console.log(message)
    // $.ajax({
    //   url: "/database/api/edge/",
    //   data: message,
    //   contentType: 'application/json; charset=utf-8',
    //   dataType: "json",
    //   method: "POST",
    //   success: function() {
    //     document.getElementById("edge").reset()
    //     document.getElementById("components").reset()
    //     location.href = 'edge_table.html'
    //         }
    // });
  }
