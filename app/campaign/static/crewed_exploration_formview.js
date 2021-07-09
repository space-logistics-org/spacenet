
const campaign = {
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
      "name": "Altair DM",
      "description": "Altair Descent Module",
      "class_of_supply": 9023,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 12000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 500,
      "max_cargo_volume": 0,
      "isp": 448,
      "max_fuel": 24900,
      "propellant_id": 2,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Altair AM",
      "description": "Altair Ascent Module",
      "class_of_supply": 9024,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 3000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 100,
      "max_cargo_volume": 0,
      "isp": 320,
      "max_fuel": 3000,
      "propellant_id": 3,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Ares I First Stage",
      "description": "Ares I Launch Vehicle, First Propulsive Stage",
      "class_of_supply": 9021,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 105000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 267,
      "max_fuel": 620000,
      "propellant_id": 1,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Ares I Upper Stage",
      "description": "Ares I Launch Vehicle, Second Propulsive Stage",
      "class_of_supply": 9021,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 12000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 448,
      "max_fuel": 125000,
      "propellant_id": 1,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Ares V SRBs",
      "description": "Ares V Launch Vehicle, Solid Rocket Boosters",
      "class_of_supply": 9021,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 210000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 270,
      "max_fuel": 1375000,
      "propellant_id": 1,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Ares V Core",
      "description": "Ares V Launch Vehicle, Core Engine",
      "class_of_supply": 9021,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 175000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "propellant_id": 2,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "EDS",
      "description": "Earth Departure System",
      "class_of_supply": 9022,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 26000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 448,
      "max_fuel": 253000,
      "propellant_id": 2,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Orion SM",
      "description": "Orion Service Module",
      "class_of_supply": 9022,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 3000,
      "volume": 0,
      "max_crew": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 328,
      "max_fuel": 10000,
      "propellant_id": 3,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Orion CM",
      "description": "Orion Crew Module",
      "class_of_supply": 9022,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 8000,
      "volume": 0,
      "max_crew": 4,
      "max_cargo_mass": 100,
      "max_cargo_volume": 0,
      "isp": 0,
      "max_fuel": 0,
      "propellant_id": 3,
      "type": "PropulsiveVehicle"
    },
    {
      "name": "Orion LAS",
      "description": "Orion Launch Abort System",
      "class_of_supply": 9021,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 6000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "cargo_environment": "Unpressurized",
      "type": "ElementCarrier"
    },
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

  campaign.elements.forEach( function(element) {
    if (element.type === 'HumanAgent') {
      table.row.add([, element.name,'x']).draw()
    }
  })


})



function setNode(){
  $('#pickLocation').find('option:not(:first)').remove()

  var node = $('#pickNode').val()

  campaign.elements.forEach( function(elt) {
      $('#pickLocation').append('<option value="' + elt.name + '">' + elt.name + '</option>')
  })

}

function setLocation() {

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
    duration = $("#inputDuration").val();
    num_EVAs = $("#inputNumEVAS").val();
    EVA_Duration = $('#inputEVADuration').val();
    crew_location = $('#pickLocation')


    data = {
      name: name,
      node: node,
      time: time,
      priority: priority,
      duration: duration,
      num_EVAs: num_EVAs,
      EVA_Duration: EVA_Duration,
      crew_location: crew_location,
    }

    console.log(data)
    location.reload()
}
