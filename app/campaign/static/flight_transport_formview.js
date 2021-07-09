
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
  
  
    campaign.nodes.forEach( function (node) {
      console.log(node)
      $('#pickNode').append('<option value="' + node.origin_id + '">' + node.name + '</option>')
    })
  
  })
  
  
  
  function setNode(){
  
    var node = $('#pickNode').val()
  
  }

    $("#pickNode").change(function() {
      document.getElementById("#destinationNode").innerHTML = $("#pickNode").val();
    })
  
  function onComplete(){
  
      name = $("#inputName").val();
      node = $("#pickNode").val();
      time = $("#inputTime").val();
      priority = $("#pickPriority").val();
    //  element = $("#pickElement").val();
      flight = $("#pickFlight").val();
      //deltaTime
      //destination
  
  
      data = {
        name: name,
        node: node,
        time: time,
        priority: priority,
    //    element: element,
        flight: flight
        //deltaTime
        //destination

      }
  
      location.reload()
      console.log(data)
  
  }
  