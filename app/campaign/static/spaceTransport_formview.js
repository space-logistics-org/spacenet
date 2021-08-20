$(document).ready(function () {


	//didn't do populate node function since ids are different
  Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputOriginNode').append('<option value="' + uuid + '">' + node.name + '</option>')
		}
	);
  Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
		$('#inputDestinationNode').append('<option value="' + uuid + '">' + node.name + '</option>')
		}
	);

	//Add/Burn/Delete rows from tables
	$('#addBurn').on('click', function() {
		elementName = $("#elementSeqSel option:selected").text();
    name = $('#inputName').val()

    $('#myTabContent div.tab-pane.active div table').append('<tr><td><input type="checkbox"></td><td> '+ elementName +  '</td><td>Burn</td><td>' + name + '</td>')
  })

  $('#addStage').on('click', function() {
    elementName = $("#elementSeqSel option:selected").text();
    name = $('#inputName').val()

    $('#myTabContent div.tab-pane.active div table').append('<tr><td><input type="checkbox"></td><td> '+ elementName + ' </td><td>Stage</td><td>' + name + '</td>')
	})

  $('#delete').on('click', function() {
		tagger=$('#myTabContent').find('div.tab-pane.active div tbody').attr('id')
    var tableRef = document.getElementById(tagger);
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


	//Creating a tab and appending a table to tab.
	var tab = 1;
	function createTab() {
		//Creates tab
		$("#myTab").append('<li class="nav-item" role="presentation"><a class="nav-link" id="tab-'+tab+'" data-toggle="tab" href="#content'+tab+'" role="tab" aria-controls="content'+tab+' aria-selected="false">Propulsive Burn '+tab+'</a></li>');

		//Creates tab content(table).
		var content = $('<div class="tab-pane fade" id="content'+tab+'" role="tabpanel" aria-labelledby="tab-'+tab+'"></div>');
		content.append('<div class="text-center"><label for="propulsiveBurnTable'+tab+'">Sequence</label><table id="propulsiveBurnTable'+tab+'" class="table table-striped table-bordered col-md-12"><thead class="thead-dark"><tr><th class="col-md-"></th><th class="col-md-">Element Name</th><th class="col-md-">Type</th><th class="col-md-">Name</th></tr></thead><tbody id="propulsiveBurnTableBody'+tab+'"></tbody></table></div>');
		$("#myTabContent").append(content);
		$('#tab-'+tab).tab('show')
		tab += 1;
	}
	$("#createTab").click(createTab);
	//Creates a single tab automatically.
	createTab();

})



// Populate Element selector with elements based on simulation filter.
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
                    if (eltObj.type !== 'HumanAgent') {
                      $('#elementTransportSelector').append('<option value=' + contentUUID + '>' + eltObj.name + '</option>')
                    } else {
                      $('#elementTransportSelector').append('<option value=' + contentUUID + '>' + eltObj.name+"(active time fraction:" + eltObj.active_time_fraction+ ")" + '</option>')
                    }


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

								$("#elementTransportSelector > option").each(function() {
									if (namespace[this.value].inner.type !== 'HumanAgent' && namespace[this.value].inner.type !== 'RoboticAgent') {
										$('#elementSeqSel').append('<option value="' + this.value + '">' + this.text + '</option>');
									}
								});
							}
						})
					}
				}




function onComplete() {

      name = $("#inputName").val();
      elements_id_list = $("#elementTransportSelector").val();
      type = "SpaceTransport"
      //optional=deltav
      origin_node_id = $("#inputOriginNode").val();
      destination_node_id = $("#inputDestinationNode").val();
  		priority = $('#pickPriority').val();
  		mission_time = $('#inputTime').val();

      edge_name= $("#inputOriginNode option:selected").text() + "-" + $("#inputDestinationNode option:selected").text()

      Object.entries(scenario.network.edges).forEach( function([uuid, edge]) {
        if (origin_node_id == edge.origin_id && destination_node_id == edge.destination_id){
          edge_id = uuid;
          exec_time = edge.duration
        }
      });



      tabNum=document.querySelectorAll("#myTab li").length;
      burnStageProfile = new Array


      for (tabNumLooper=1; tabNumLooper < tabNum+1 ; tabNumLooper++ ) {
        var currentTab = document.getElementById('propulsiveBurnTable' + tabNumLooper);
        burnStageSequence = new Array
        burnStageSequenceReformat = {}

        // LOOP THROUGH EACH ROW OF THE TABLE AFTER HEADER.
        for (i = 1; i < currentTab.rows.length; i++) {
          burnStageItem = {}

          // GET THE CELLS COLLECTION OF THE CURRENT ROW.
          var objCells = currentTab.rows.item(i).cells;

          // LOOP THROUGH EACH CELL OF THE CURENT ROW TO READ CELL VALUES.
          for (var j = 1; j < objCells.length-1; j++) {
            //Get element ID rather than the innerHTML
            if ( j == 1 ){
              Object.entries(scenario.elementList).forEach( function([uuid, element]) {
                if (objCells.item(j).innerHTML.trim() == element.name.trim()){
                  burnStageItem["element_id"] = uuid
                }
              });
            } else {
              burnStageItem["burnStage"]= objCells.item(j).innerHTML
            }
          }
          burnStageSequence.push(burnStageItem)

        }
        burnStageSequenceReformat['burnStageSequence'] = burnStageSequence
        burnStageProfile.push(burnStageSequenceReformat)
      }


      data = {
        name: name,
        elements_id_list: elements_id_list,
        type: type,
        origin_node_id: origin_node_id,
        destination_node_id: destination_node_id,
        exec_time: exec_time,
        type: type,
        priority: priority,
  			mission_time : mission_time,
  			edge_id: edge_id,
        exec_time: exec_time,
        burnStageProfile: burnStageProfile
      }
      console.log(data);
  		addEvent(data);
}
