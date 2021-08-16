$(document).ready( function() {
	Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#pickNode').append('<option value="' + uuid + '">' + node.name + '</option>')
	  });

	$('#addBurn').on('click', function() {
		console.log('add burn button clicked')

		elementName = $("#ElementSel option:selected").text();
		name = $('#inputName').val()

		$('#propulsiveBurnTable').append('<tr><td><input type="checkbox"></td><td> '+ elementName +  '</td><td>[Burn]</td><td>' + name + '</td>')
	})

	$('#addStage').on('click', function() {
		console.log('add stage button clicked')

		elementName = $("#ElementSel option:selected").text();
		name = $('#inputName').val()

		$('#propulsiveBurnTable').append('<tr><td><input type="checkbox"></td><td> '+ elementName +  '</td><td>[Stage]</td><td>' + name + '</td>')
	})


		$('#delete').on('click', function() {
			var tableRef = document.getElementById('propulsiveBurnTableBody');
		  var tableRows = tableRef.rows;

		  var checkedRows = [];
		 	for (var i = 0; i < tableRows.length; i++) {
				if (tableRows[i].querySelector('input').checked) {
					checkedRows.push(tableRows[i]);
				}
			}
			for (var k = 0; k < checkedRows.length; k++) {
				checkedRows[k].parentNode.removeChild(checkedRows[k]);
			}
		})
	})




function retreiveElements(){
  let node = $('#pickNode').val(),
  time = $('#inputTime').val(),
  priority = $('#pickPriority').val();

  if (node && time && priority !== 'Choose...') {
    $('#elementSeqSel').empty();
		$("#elementTransportSelector").empty();

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
						})
					}
				}


  function onComplete(){

      name = $("#inputName").val();
      node = $("#pickNode").val();
      mission_time = $("#inputTime").val();
      priority = $("#pickPriority").val();


      data = JSON.stringify({
        name : name,
        node : node,
        mission_time : mission_time,
        priority : priority,
        elements : elementsList,
        burn_stage_sequence : burn_stage_sequence
        //sequence
      })

      console.log(data)

  }
