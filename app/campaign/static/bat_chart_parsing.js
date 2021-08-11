const COLOR_MAPPINGS = {
    'MakeElements': 'green',
    'FlightTransport': 'red',
    'SpaceTransport': 'yellow',
    'CrewedExploration': 'blue',
    'RemoveElements': 'black',
    'ReconfigureGroup': 'orange',
    'MoveElements': 'orange'
}

const POINT_SIZES = {
    'MakeElements': 4,
    'FlightTransport': 1,
    'CrewedExploration': 1,
    'RemoveElements': 3.5,
    'ReconfigureGroup': 3,
    'MoveElements': 5
}
var DateTime = luxon.DateTime;

const scenario = {
	"name": "Apollo 17",
	"description": "Apollo 17 Mission",
	"startDate": "1972-12-05T12:53",
	"scenarioType": "Lunar",
	"network": {
	  "nodes": {
		"cb3aa87b-893c-4dbd-9acb-d1c5b7017644": {
		  "type": "SurfaceNode",
		  "name": "KSC",
		  "description": "Kennedy Space Center",
		  "body_1": "Earth",
		  "latitude": 28.6,
		  "longitude": -80.6
		},
		"a2e22fe6-7f6b-48d0-8049-93a7fac9069b": {
		  "type": "OrbitalNode",
		  "name": "LEO",
		  "description": "Low-Earth Orbit",
		  "body_1": "Earth",
		  "apoapsis": 296.0,
		  "periapsis": 296.0,
		  "inclination": 28.5
		},
		"53fc1b8b-33c1-4b0f-b380-9436de076162": {
		  "type": "OrbitalNode",
		  "name": "28 km Lunar Orbit",
		  "description": "Lunar Orbit at 28 km",
		  "body_1": "Moon",
		  "apoapsis": 28.0,
		  "periapsis": 28.0,
		  "inclination": 30
		},
		"e8eb8492-9158-488e-9265-90e98f8b5eb6": {
		  "type": "OrbitalNode",
		  "name": "11.5 km Lunar Orbit",
		  "description": "Lunar orbit at 11.5 km",
		  "body_1": "Moon",
		  "apoapsis": 11.5,
		  "periapsis": 11.5,
		  "inclination": 30
		},
		"0c9814e1-3b9e-42fd-82cb-c979bca0ba6c": {
		  "type": "SurfaceNode",
		  "name": "Taurus-Littrow",
		  "description": "A valley on the face of the moon",
		  "body_1": "Moon",
		  "latitude": 20.0,
		  "longitude": 31.0
		},
		"f49db8a6-6cac-48f6-9d27-6276ae08faf8": {
		  "type": "SurfaceNode",
		  "name": "Pacific Splashdown",
		  "description": "The pacific ocean splashdown site for Apollo 17",
		  "body_1": "Earth",
		  "latitude": -18.0,
		  "longitude": -165.0
		}
	  },
	  "edges": {
		"0d70a94d-0c03-4f26-b807-844b12649453": {
		  "type": "SpaceEdge",
		  "name": "KSC-LEO",
		  "description": "Kennedy Space Center to Low-Earth Orbit",
		  "origin_id": "cb3aa87b-893c-4dbd-9acb-d1c5b7017644",
		  "destination_id": "a2e22fe6-7f6b-48d0-8049-93a7fac9069b",
		  "duration": 0.25
		},
		"710e4e69-e70c-4fc1-9216-8c8e0fb763f2": {
		  "type": "SpaceEdge",
		  "name": "LEO-28 km Lunar Orbit",
		  "description": "Low-Earth Orbit to 28km lunar orbit",
		  "origin_id": "a2e22fe6-7f6b-48d0-8049-93a7fac9069b",
		  "destination_id": "53fc1b8b-33c1-4b0f-b380-9436de076162",
		  "duration": 3.5
		},
		"22e72f69-8e84-4c5e-ac65-6d7d0e228f76": {
		  "type": "SpaceEdge",
		  "name": "28 km to 11.5 km lunar orbit",
		  "description": "Decent from a 28 km orbit to an 11.5 km orbit",
		  "origin_id": "53fc1b8b-33c1-4b0f-b380-9436de076162",
		  "destination_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
		  "duration": 0.1
		},
		"6c2f54ef-a4ba-444a-b0af-4cdd4f31aba2": {
		  "type": "SpaceEdge",
		  "name": "11.5 km orbit-Taurus-Littrow",
		  "description": "Decent from lunar orbit to the surface of the moon",
		  "origin_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
		  "destination_id": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
		  "duration": 0.1
		},
		"ff2715a9-c93c-4c60-870b-00e177b9c2ec": {
		  "type": "SpaceEdge",
		  "name": "Taurus-Littrow-11.5 km orbit",
		  "description": "Ascent from the lunar surface to orbit",
		  "origin_id": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
		  "destination_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
		  "duration": 0.1
		},
		"32615681-1c5e-4231-8f89-ba2c556a108c": {
		  "type": "SpaceEdge",
		  "name": "Lunar orbit to Pacific Splashdown",
		  "description": "Return trip from lunar orbit to the Pacific Ocean",
		  "origin_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
		  "destination_id": "f49db8a6-6cac-48f6-9d27-6276ae08faf8",
		  "duration": 2.83
		}
	  }
	},
	"resourceTypes": [
	  {
		"id": 1001,
		"name": "Kerosene-LOX",
		"description": "Kerosene and Liquid Oxygen",
		"class_of_supply": 104,
		"units": "kg",
		"unit_mass": 1.0
	  },
	  {
		"id": 1002,
		"name": "LOX-LH2",
		"description": "Liquid Hydrogen and Liquid Oxygen",
		"class_of_supply": 101,
		"units": "kg",
		"unit_mass": 1.0
	  },
	  {
		"id": 1003,
		"name": "Aerozine-NTO",
		"description": "Aerozine 50 and dinitrogen tetroxide",
		"class_of_supply": 102,
		"units": "kg",
		"unit_mass": 1.0
	  }
	],
	"elementList": {
	  "69018bea-fc19-412d-8557-14393a16922c": {
		"type": "PropulsiveVehicle",
		"name": "S-IC",
		"description": "First stage of the Saturn V",
		"environment": "Unpressurized",
		"accommodation_mass": 0,
		"class_of_supply": 9021,
		"mass": 113982.0,
		"volume": 0,
		"isp": 304.0,
		"max_fuel": 2135839.0,
		"max_crew": 0,
		"propellant_id": 1002
	  },
	  "4aab255e-be48-492e-a322-0323ba72e2a7": {
		"type": "PropulsiveVehicle",
		"name": "S-II",
		"description": "Second stage of the Saturn V",
		"environment": "Unpressurized",
		"accommodation_mass": 0,
		"class_of_supply": 9021,
		"mass": 38415.0,
		"volume": 0,
		"isp": 421.0,
		"max_fuel": 2135839.0,
		"max_crew": 0,
		"propellant_id": 1002
	  },
	  "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302": {
		"type": "PropulsiveVehicle",
		"name": "S-IVB",
		"description": "Third stage of the Saturn V",
		"environment": "Unpressurized",
		"accommodation_mass": 0,
		"class_of_supply": 9021,
		"mass": 12014.0,
		"volume": 0,
		"isp": 421.0,
		"max_fuel": 2135839.0,
		"max_crew": 0,
		"propellant_id": 1002
	  },
	  "9ed11cf6-38d3-4d98-9af0-03ab6c173353": {
		"type": "PropulsiveVehicle",
		"name": "Lunar Module DM",
		"description": "The lunar module Challenger decent module.",
		"environment": "Pressurized",
		"accommodation_mass": 0,
		"class_of_supply": 9023,
		"mass": 6100.0,
		"volume": 0,
		"isp": 311.0,
		"max_fuel": 19500.0,
		"max_crew": 2,
		"propellant_id": 1003
	  },
	  "4df36b84-c111-4e64-ada0-5c212321370d": {
		"type": "PropulsiveVehicle",
		"name": "Lunar Module AM",
		"description": "The lunar module Challenger decent module.",
		"environment": "Pressurized",
		"accommodation_mass": 0,
		"class_of_supply": 9023,
		"mass": 4700.0,
		"volume": 0,
		"isp": 311.0,
		"max_fuel": 5200.0,
		"max_crew": 2,
		"propellant_id": 1003
	  },
	  "0fbec9f6-ee3b-44d2-b30c-b20e0d5dd92a": {
		"type": "RoboticAgent",
		"name": "LRV",
		"description": "Lunar Roving Vehicle",
		"environment": "Unpressurized",
		"accommodation_mass": 0,
		"class_of_supply": 8041,
		"mass": 460,
		"volume": 0,
		"active_time_fraction": 0.5
	  },
	  "677fe98e-a8e3-4b6c-a148-d7004287d43e": {
		"type": "PropulsiveVehicle",
		"name": "CSM",
		"description": "Apollo Command and Service Module",
		"environment": "Pressurized",
		"accommodation_mass": 0,
		"class_of_supply": 9022,
		"mass": 11900,
		"volume": 0,
		"isp": 319,
		"max_fuel": 3000,
		"max_crew": 3,
		"propellant_id": 1003
	  },
	  "5d95732e-5380-48ad-9cfb-867684231a14": {
		"type": "HumanAgent",
		"name": "Crew Member",
		"description": "Typical human astronaut",
		"environment": "Pressurized",
		"accommodation_mass": 0,
		"class_of_supply": 0,
		"mass": 70,
		"volume": 0,
		"active_time_fraction": 0.67
	  },
	  "d794e69a-f6cf-466f-b054-687fff1346ad": {
		"type": "HumanAgent",
		"name": "Crew Member",
		"description": "Typical human astronaut",
		"environment": "Pressurized",
		"accommodation_mass": 0,
		"class_of_supply": 0,
		"mass": 70,
		"volume": 0,
		"active_time_fraction": 0.67
	  }
	},
	"missionList": [
	  {
		"name": "Apollo 17",
		"start_date": "1972-12-05T12:53",
		"events": [
		  {
			"name": "Create Apollo 17 Saturn-V Stack at KSC",
			"mission_time": "00",
			"type": "MakeElements",
			"priority": 1,
			"entry_point_id": "cb3aa87b-893c-4dbd-9acb-d1c5b7017644",
			"elements": [
			  "69018bea-fc19-412d-8557-14393a16922c",
			  "4aab255e-be48-492e-a322-0323ba72e2a7",
			  "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302",
			  "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			  "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			  "4df36b84-c111-4e64-ada0-5c212321370d",
			  "0fbec9f6-ee3b-44d2-b30c-b20e0d5dd92a"
			]
		  },
		  {
			"name": "Create crew members in the CSM",
			"mission_time": "00",
			"type": "MakeElements",
			"priority": 2,
			"entry_point_id": "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			"elements": [
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			]
		  },
		  {
			"name": "Launch to LEO",
			"mission_time": "00",
			"type": "SpaceTransport",
			"priority": 3,
			"origin_node_id": "cb3aa87b-893c-4dbd-9acb-d1c5b7017644",
			"destination_node_id": "a2e22fe6-7f6b-48d0-8049-93a7fac9069b",
			"edge_id": "0d70a94d-0c03-4f26-b807-844b12649453",
			"exec_time": "06:00:00",
			"elements_id_list": [
			  "69018bea-fc19-412d-8557-14393a16922c",
			  "4aab255e-be48-492e-a322-0323ba72e2a7",
			  "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302",
			  "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			  "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			  "4df36b84-c111-4e64-ada0-5c212321370d",
			  "0fbec9f6-ee3b-44d2-b30c-b20e0d5dd92a",
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"burnStageProfile": [
			  {
				"burn_stage_sequence": [
				  {
					"burnStage": "Burn",
					"element_id": "69018bea-fc19-412d-8557-14393a16922c"
				  },
				  {
					"burnStage": "Stage",
					"element_id": "69018bea-fc19-412d-8557-14393a16922c"
				  },
				  {
					"burnStage": "Burn",
					"element_id": "4aab255e-be48-492e-a322-0323ba72e2a7"
				  },
				  {
					"burnStage": "Stage",
					"element_id": "4aab255e-be48-492e-a322-0323ba72e2a7"
				  },
				  {
					"burnStage": "Burn",
					"element_id": "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302"
				  }
				]
			  }
			]
		  },
		  {
			"name": "Translunar Injection",
			"mission_time": "03:18:36.64",
			"type": "SpaceTransport",
			"priority": 1,
			"origin_node_id": "a2e22fe6-7f6b-48d0-8049-93a7fac9069b",
			"destination_node_id": "53fc1b8b-33c1-4b0f-b380-9436de076162",
			"edge_id": "710e4e69-e70c-4fc1-9216-8c8e0fb763f2",
			"exec_time": "3 12:00:00",
			"elements_id_list": [
			  "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302",
			  "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			  "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			  "4df36b84-c111-4e64-ada0-5c212321370d",
			  "0fbec9f6-ee3b-44d2-b30c-b20e0d5dd92a",
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"burnStageProfile": [
			  {
				"burn_stage_sequence": [
				  {
					"burnStage": "Burn",
					"element_id": "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302"
				  },
				  {
					"burnStage": "Stage",
					"element_id": "9ad8c701-1e76-41d4-bcdd-ccaa0ef47302"
				  }
				]
			  }
			]
		  },
		  {
			"name": "1st decent orbit insertion",
			"mission_time": "90:31:37.43",
			"type": "SpaceTransport",
			"priority": 1,
			"origin_node_id": "53fc1b8b-33c1-4b0f-b380-9436de076162",
			"destination_node_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
			"edge_id": "22e72f69-8e84-4c5e-ac65-6d7d0e228f76",
			"exec_time": "02:30:00",
			"elements_id_list": [
			  "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			  "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			  "4df36b84-c111-4e64-ada0-5c212321370d",
			  "0fbec9f6-ee3b-44d2-b30c-b20e0d5dd92a",
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"burnStageProfile": [
			  {
				"burn_stage_sequence": [
				  {
					"burnStage": "Burn",
					"element_id": "677fe98e-a8e3-4b6c-a148-d7004287d43e"
				  }
				]
			  }
			]
		  },
		  {
			"name": "Move crew to LM",
			"mission_time": "105:02:00",
			"type": "MoveElements",
			"priority": 1,
			"to_move": [
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"origin_id": "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			"destination_id": "9ed11cf6-38d3-4d98-9af0-03ab6c173353"
		  },
		  {
			"name": "Lunar Decent",
			"mission_time": "109:22:42",
			"type": "SpaceTransport",
			"priority": 1,
			"origin_node_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
			"destination_node_id": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
			"edge_id": "6c2f54ef-a4ba-444a-b0af-4cdd4f31aba2",
			"exec_time": "2:00:00",
			"elements_id_list": [
			  "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			  "4df36b84-c111-4e64-ada0-5c212321370d",
			  "0fbec9f6-ee3b-44d2-b30c-b20e0d5dd92a",
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"burnStageProfile": [
			  {
				"burn_stage_sequence": [
				  {
					"burnStage": "Burn",
					"element_id": "9ed11cf6-38d3-4d98-9af0-03ab6c173353"
				  }
				]
			  }
			]
		  },
		  {
			"name": "Apollo 17 crewed exploration",
			"node": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
			"mission_time": "114:21:49",
			"type": "CrewedExploration",
			"priority": 1,
			"eva_duration": "08:00:00",
			"crew_location": "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			"crew": [
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"duration": "3 00:00:00",
			"eva_per_week": 7
		  },
		  {
			"name": "Transfer Crew to Lunar AM",
			"mission_time": "185:31:37",
			"type": "MoveElements",
			"priority": 2,
			"to_move": [
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"origin_id": "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			"destination_id": "4df36b84-c111-4e64-ada0-5c212321370d"
		  },
		  {
			"name": "Lunar ascent",
			"mission_time": "185:31:37",
			"type": "SpaceTransport",
			"priority": 2,
			"origin_node_id": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
			"destination_node_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
			"edge_id": "ff2715a9-c93c-4c60-870b-00e177b9c2ec",
			"exec_time": "02:00:00",
			"elements_id_list": [
			  "4df36b84-c111-4e64-ada0-5c212321370d",
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"burnStageProfile": [
			  {
				"burn_stage_sequence": [
				  {
					"burnStage": "Burn",
					"element_id": "4df36b84-c111-4e64-ada0-5c212321370d"
				  }
				]
			  }
			]
		  },
		  {
			"name": "Move crew to CM",
			"mission_time": "190:10:00",
			"type": "MoveElements",
			"priority": 1,
			"to_move": [
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"origin_id": "9ed11cf6-38d3-4d98-9af0-03ab6c173353",
			"destination_id": "677fe98e-a8e3-4b6c-a148-d7004287d43e"
		  },
		  {
			"name": "Transearth injection",
			"mission_time": "234:02:09.18",
			"type": "SpaceTransport",
			"priority": 1,
			"origin_node_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
			"destination_node_id": "f49db8a6-6cac-48f6-9d27-6276ae08faf8",
			"edge_id": "32615681-1c5e-4231-8f89-ba2c556a108c",
			"exec_time": "2 16:00:00",
			"elements_id_list": [
			  "677fe98e-a8e3-4b6c-a148-d7004287d43e",
			  "5d95732e-5380-48ad-9cfb-867684231a14",
			  "d794e69a-f6cf-466f-b054-687fff1346ad"
			],
			"burnStageProfile": [
			  {
				"burn_stage_sequence": [
				  {
					"burnStage": "Burn",
					"element_id": "677fe98e-a8e3-4b6c-a148-d7004287d43e"
				  }
				]
			  }
			]
		  }
		],
		"demand_models": [],
		"origin": "cb3aa87b-893c-4dbd-9acb-d1c5b7017644",
		"destination": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
		"return_origin": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
		"return_destination": "f49db8a6-6cac-48f6-9d27-6276ae08faf8"
	  }
	],
	"manifest": {
	  "container_events": []
	},
	"volumeConstrained": false,
	"environmentConstrained": false
  }


const oneNodeEvents = ['MakeElements', 'MoveElements', 'RemoveElements', 'ReconfigureElements', 'ReconfigureGroup', 'ConsumeResources', 'TransferResources']

let nodeLocations = {};
let ind = 0;
Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
    nodeLocations[uuid] = ind
    nodeLocations[ind] = uuid
    ind += 1
});

console.log('node locations:', nodeLocations)

function getNodeLocation (uuid) {
    if (Object.keys(nodeLocations).includes(uuid)) {
        return nodeLocations[uuid]
    } else {
        return null
    }
}

function parseTime(timestring) {
    let hours = '0',
        minutes = '0',
        seconds = '0',
        milliseconds = '0';

    var times = [hours, minutes, seconds, milliseconds];

    let ind = 0;

    for (let i=0; i < timestring.length; i++) {
        let val = timestring[i]
        if (val !== ':') {
            times[ind] += val
        } else {
            ind += 1
        }
    }
    return times
}


function parseMission(mission) {
    var startDate = DateTime.fromISO(mission.start_date);
    var datasets = [];
    var lastLocation = 0;


    mission.events.forEach(function (event) {
        var addedTime = parseTime(event.mission_time)
        var newDate = startDate.plus({hours: addedTime[0], minutes: addedTime[1], seconds: addedTime[2]})

        var dataset = {
            label: event.name,
            borderColor: COLOR_MAPPINGS[event.type],
            backgroundColor: COLOR_MAPPINGS[event.type],
        }

        if (oneNodeEvents.includes(event.type)) {
            //if event occurs in only one node
            if (event.type === 'MoveElements') {
                var node = event.origin_id
            } else {
                var node = event.entry_point_id
            }

            if (getNodeLocation(node)) {
                newLocation = getNodeLocation(node)
                lastLocation = newLocation
            } else {
                newLocation = lastLocation
            }
            

            var info = [{
                x: newDate,
                y: newLocation
            }]
            dataset.pointRadius = POINT_SIZES[event.type]
        } else {

            if (event.type === 'CrewedExploration') {
                evaAddedTime = parseTime(event.eva_duration)


                if (getNodeLocation(event.node)) {
                    newLocation = getNodeLocation(event.node)
                    lastLocation = newLocation
                } else {
                    newLocation = lastLocation
                }
    

                var info = [{
                    x: newDate,
                    y: newLocation
                }, {
                    x: newDate.plus({hours: evaAddedTime[0], minutes: evaAddedTime[1], seconds: evaAddedTime[2]}),
                    y: newLocation
                }
                ]
            } else {
                //if event occurs in two nodes connected by an edge
                var edge = scenario.network.edges[event.edge_id]

                var info = [{
                    x: newDate,
                    y: getNodeLocation(event.origin_node_id)
                }, {
                    x: newDate.plus({days: edge.duration}),
                    y: getNodeLocation(event.destination_node_id)
                }
                ]
                lastLocation = getNodeLocation(event.destination_node_id)
            }

        }
        dataset.data = info
        datasets.push(dataset)
    });
    return datasets
}



var missions = scenario.missionList

var all_data = [];
missions.forEach(function(item) {
    var parsed = parseMission(item);
    parsed.forEach(function (dataset) {
        all_data.push(dataset)
    })
})

const data = {
    datasets: all_data
};


const config = {
    type: 'line',
    data: data,
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: false,
                text: 'Scenario'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        var label = context.dataset.label || '';
                        var nodeUUID = nodeLocations[context.parsed.y]
                        var nodeName = scenario.network.nodes[nodeUUID].name

                        if (label) {
                            label += ' (';
                        }
                        if (context.parsed.y !== null) {
                            label += nodeName;
                            label += ')'
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    // Luxon format string
                    tooltipFormat: 'DD T'
                },
                title: {
                    display: true,
                    text: 'Date'
                },
            },
            y: {
                title: {
                display: true,
                text: 'Location'
                },
                ticks: {
                    stepSize: 1.0,
                    callback: function(value, index, values) {
                        console.log(index)
                        var nodeUUID = nodeLocations[index]
                        console.log(nodeUUID)
                        var nodeName = scenario.network.nodes[nodeUUID].name
                        return nodeName
                    }
                }
            }
        },
    }
};

var myChart = new Chart(
    document.getElementById('batChart'),
    config
);