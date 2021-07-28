
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


  campaign.nodes.forEach( function (node) {
    console.log(node)
    $('#pickNode').append('<option value="' + node.origin_id + '">' + node.name + '</option>')
  })

})



function setNode(){
  $('#pickElement').find('option:not(:first)').remove()

  var node = $('#pickNode').val()

  campaign.elements.forEach( function(elt) {
      $('#pickElement').append('<option value="' + elt.name + '">' + elt.name + '</option>')
  })

}

function setTransfer() {

  console.log('set transfer activated')

  campaign.resources.forEach( function(resource) {
    $('#transferResourcesTable > tbody').append('<tr><td>' + resource.name + '</td><td>' + 'amount' + '</td><td>' + 'transfered' + '</td></tr>')
  })

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

function onComplete(){

    name = $("#inputName").val();
    node = $("#pickNode").val();
    time = $("#inputTime").val();
    priority = $("#pickPriority").val();
    element = $("#pickElement").val();


    data = {
      name: name,
      node: node,
      time: time,
      priority: priority,
      element: element
    }

    location.reload()
    console.log(data)

}


$.ajax({
  url: "/database/api/simulation",
  method: "GET",
  data: {}, //insert scenario json here
  success: function (simResult) {
    simResult.elements.forEach( function(element) {
      $('#pickElement').append('<option value="' + element.name + '">' + element.name + '</option>')
    })
  }
});

