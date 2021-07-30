var deltSum = 0;
var masses = 0;
var campaign = {
    nodes: [
      {
        "name": "KSC",
        "description": "Kennedy Space Center",
        "body_1": "Earth",
        "latitude": 28.6,
        "longitude": -80.6,
        "type": "SurfaceNode"
      },
      {
        "name": "PAC",
        "description": "Pacific Ocean Splashdown",
        "body_1": "Earth",
        "latitude": 35,
        "longitude": -117.9,
        "type": "SurfaceNode"
      },
      {
        "name": "LSP",
        "description": "Lunar South Pole",
        "body_1": "Moon",
        "latitude": -89.9,
        "longitude": -180,
        "type": "SurfaceNode"
      },
      {
        "name": "LEO",
        "description": "Low Earth Orbit",
        "body_1": "Earth",
        "apoapsis": 296,
        "periapsis": 296,
        "inclination": 28.5,
        "type": "OrbitalNode"
      },
      {
        "name": "LLPO",
        "description": "Low Lunar Polar Orbit",
        "body_1": "Moon",
        "apoapsis": 100,
        "periapsis": 100,
        "inclination": 90,
        "type": "OrbitalNode"
      }
    ],
    elements: [
      {
        "name": "Crew Member",
        "description": "Crew Member",
        "class_of_supply": 0,
        "environment": "Unpressurized",
        "accommodation_mass": 0,
        "mass": 100,
        "volume": 0,
        "active_time_fraction": 0.66,
        "type": "HumanAgent"
      },
      {
        "name": "Notional Cargo",
        "description": "Cargo",
        "class_of_supply": 6,
        "environment": "Unpressurized",
        "accommodation_mass": 0,
        "mass": 500,
        "volume": 0,
        "type": "ResourceContainer"
      },
      {
        "name": "Lunar Surface Samples",
        "description": "Lunar Surface Samples",
        "class_of_supply": 6,
        "environment": "Unpressurized",
        "accommodation_mass": 0,
        "mass": 100,
        "volume": 0,
        "type": "Element"
      }
    ],
    resources: [
      {
        "name": "PBAN Solid",
        "description": "Solid rocket fuel",
        "class_of_supply": 105,
        "units": "kg",
        "unit_mass": 1,
        "unit_volume": 0,
        "type": "Continuous"
      },
      {
        "name": "LH2/LOX",
        "description": "Liquid oxygen / liquid hydrogen cryogenic fuel",
        "class_of_supply": 101,
        "units": "kg",
        "unit_mass": 1,
        "unit_volume": 0,
        "type": "Continuous"
      },
      {
        "name": "MMH/N2O4",
        "description": "Hypergolic fuel",
        "class_of_supply": 102,
        "units": "kg",
        "unit_mass": 1,
        "unit_volume": 0,
        "type": "Continuous"
      }
    ]
  }

  const genericResources = ['Generic COS 1', 'Generic COS 2', 'Generic COS 3']



  $(document).ready( function() {


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
      var tableRef = document.getElementById('elementTableBody');
      var tableRows = tableRef.rows;
      var checkedRows = [];
      for (var i = 0; i < tableRows.length; i++) {
        m = Number(tableRows[i].cells[6].innerText);
        masses = Number(masses + m);
        document.getElementById('mass').innerHTML = masses + " kg";
      }


        // for (var k = 0; k < checkedRows.length; k++) {
        //   checkedRows[k].parentNode.removeChild(checkedRows[k]);
        // }
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


    campaign.nodes.forEach( function (node) {
      console.log(node)
      $('#pickNode').append('<option value="' + node.origin_id + '">' + node.name + '</option>')
    })

  })



  function setNode(){

    var node = $('#pickNode').val()

    campaign.elements.forEach( function(elt) {
        $('#pickElement').append('<option value="' + elt.name + '">' + elt.name + '</option>')
    })

  }

  function onComplete(){

      document.getElementById("mass").innerHTML = "CHANGED :)"

      name = $("#inputName").val();
      node = $("#pickNode").val();
      time = $("#inputTime").val();
      priority = $("#pickPriority").val();
      //sequnce


      data = {
        name: name,
        node: node,
        time: time,
        priority: priority,
        //sequence
      }

      location.reload()
      console.log(data)

  }
