var deltSum = 0;

function showUnselectedInstructions () {
	$('.selected-instructions').hide()
	$('.unselected-instructions').show()
	clearTable()
}

function loadSim() {
	let node = $('#pickNode').val(),
		time = $('#inputTime').val(),
		priority = $('#pickPriority').val();
	
	if (node !== 'def' && time && priority !== 'def') {
		$('.selected-instructions').show()
		$('.unselected-instructions').hide()
		clearTable()
		  
		$.ajax({
			url: "/campaign/api/simulation/?days_to_run_for=" + time + "&propulsive=true",
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
					allContents.forEach(function(uuid) {
						if (namespace[uuid].inner.type === 'PropulsiveVehicle') {
							addRow(uuid, namespace[uuid].inner)
						}
					})
				}
			}
		});
	} else {
		showUnselectedInstructions()
	}


}

  $(document).ready( function() {

	populateNodes()
	showUnselectedInstructions()

    $('#addBurn').on('click', function() {
      console.log('add burn button clicked')

      name = $('#inputName').val();
      dv = $("#inputDelta").val();
      deltSum += Number(dv);

      $('#propulsiveBurnTable').append('<tr><td><input type="checkbox"></td><td>[Burn]</td><td>' + name + '</td><td>' + dv + '</td>' )
    })

    $('#addStage').on('click', function() {
      console.log('add stage button clicked')

      name = $("#inputName").val();
      dv = $("#inputDelta").val();
      deltSum += Number(dv);

      $('#propulsiveBurnTable').append('<tr><td><input type="checkbox"></td><td>[Stage]</td><td>' + name + '</td><td>' + dv + '</td>' )
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
        deltSum = 0;
    })

    $('#prepBurn').on('click', function() {
		var masses = 0;
		var selectedElts = getSelected()
		selectedElts.forEach(function(uuid) {
			m = Number(scenario.elementList[uuid].mass);
			masses = Number(masses + m);
		})
		document.getElementById('mass').innerHTML = masses + " kg";	
    })

    $('#calcDV').on('click', function() {
      document.getElementById('Delta-V_Measure').max = deltSum;
      document.getElementById('dispDV').innerHTML = deltSum;
      // """
      //   Find the delta-v resulting from the burn described by the
      //   given specific impulse and masses.
      //   :param isp: specific impulse in seconds
      //   :param m_0: initial mass
      //   :param m_f: final mass; must be same units as m_0
      //   :return: change in velocity resulting from burning (m_0 - m_f) units of fuel
      //   with given specific impulse
      //   """
      var calcVal =  2.14 * 9.80665 * Math.log(masses / 3);
      document.getElementById('Delta-V_Measure').value = calcVal;
      document.getElementById('dispDVVal').innerHTML = calcVal;
    })

  })




//   function onComplete(){
// 	var selectedElts = getTreeSelected()
// 	selectedElts.forEach(function(uuid) {
// 		m = Number(scenario.elementList[uuid].mass);
// 		masses = Number(masses + m);
// 	})
// 	document.getElementById('mass').innerHTML = masses + " kg";

//   }
