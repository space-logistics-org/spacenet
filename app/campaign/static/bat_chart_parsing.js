const COLOR_MAPPINGS = {
    'MakeElements': 'green',
    'FlightTransport': 'red',
    'SpaceTransport': 'yellow',
    'CrewedExploration': 'blue',
    'RemoveElements': 'black',
    'ReconfigureGroup': 'orange',
    'MoveElements': 'purple',
    'ConsumeResources': 'pink',
    'TransferResources': 'lightblue'
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


const scenario =
{
  "name": "Mars Exploration",
  "description": "Analyzes a human exploration to mars between 2035 and 2040.",
  "startDate": "2035-01-01T00:00:00",
  "scenarioType": "Martian",
  "network": {
    "nodes": {
      "9533b255-526f-4197-9319-6013ca01ec97": {
        "type": "SurfaceNode",
        "name": "KSC",
        "description": "Kennedy Space Center",
        "body_1": "Earth",
        "latitude": 28.6,
        "longitude": -80.6
      },
      "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a": {
        "type": "OrbitalNode",
        "name": "LEO",
        "description": "Low Earth Orbit",
        "body_1": "Earth",
        "apoapsis": 407,
        "periapsis": 407,
        "inclination": 28.5
      },
      "5dd3e569-c900-4406-b2a8-83cc531085bb": {
        "type": "OrbitalNode",
        "name": "RMO",
        "description": "Reference Mars Orbit",
        "body_1": "Mars",
        "apoapsis": 250,
        "periapsis": 33793,
        "inclination": 70
      },
      "9032bcfa-7457-4ff7-9c07-2d698d728778": {
        "type": "SurfaceNode",
        "name": "MV",
        "description": "Mawrth Vallis",
        "body_1": "Mars",
        "latitude": 24,
        "longitude": 19
      },
      "7305bc6b-fa82-40c9-9a82-8dfe8b7b60f9": {
        "type": "SurfaceNode",
        "name": "GC",
        "description": "Gale Crater",
        "body_1": "Mars",
        "latitude": -4.6,
        "longitude": 137.2
      },
      "831885d7-e7e0-463a-beef-987add3b32ca": {
        "type": "SurfaceNode",
        "name": "HC",
        "description": "Holden Crater Fan",
        "body_1": "Mars",
        "latitude": -26.4,
        "longitude": -34.7
      },
      "09d7dbbc-fb1c-441b-b9e6-f424458d5ddf": {
        "type": "SurfaceNode",
        "name": "PSZ",
        "description": "Pacific Splashdown Zone",
        "body_1": "Earth",
        "latitude": 15,
        "longitude": -160
      }
    },
    "edges": {
      "1204f9f9-6f71-4a88-a7b4-db6d8c81e931": {
        "type": "SpaceEdge",
        "name": "KSC Launch to LEO",
        "description": "KSC Launch to LEO",
        "origin_id": "9533b255-526f-4197-9319-6013ca01ec97",
        "destination_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
        "duration": 0.1,
        "delta_v": 9800
      },
      "e44e1484-80d6-41fa-81ed-b49ca2a24067": {
        "type": "SpaceEdge",
        "name": "TMI/MOI (AC)",
        "description": "Trans-Mars Injection / Mars Orbit Insertion (Aerocapture)",
        "origin_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
        "destination_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "duration": 202,
        "delta_v": 3700
      },
      "cb720ee2-37c2-4500-bdcb-a52b04356899": {
        "type": "SpaceEdge",
        "name": "TMI/MOI (P)",
        "description": "Trans-Mars Injection / Mars Orbit Insertion (Propulsive)",
        "origin_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
        "destination_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "duration": 174,
        "delta_v": 5800
      },
      "ada1b096-2991-470e-a0d9-6f27fc2e068d": {
        "type": "SpaceEdge",
        "name": "Descent to MV",
        "description": "Descent to Mawrth Vallis",
        "origin_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "destination_id": "9032bcfa-7457-4ff7-9c07-2d698d728778",
        "duration": 0.1,
        "delta_v": 610
      },
      "87907b2b-b1b8-4567-9677-e509d5653c4f": {
        "type": "SpaceEdge",
        "name": "Ascent from MV",
        "description": "Ascent from Mawrth Vallis",
        "origin_id": "9032bcfa-7457-4ff7-9c07-2d698d728778",
        "destination_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "duration": 0.1,
        "delta_v": 4100
      },
      "4195e41b-c875-4441-9e94-6fb5f862e1ec": {
        "type": "SpaceEdge",
        "name": "Descent to GC",
        "description": "Descent to Gale Crater",
        "origin_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "destination_id": "7305bc6b-fa82-40c9-9a82-8dfe8b7b60f9",
        "duration": 0.1,
        "delta_v": 610
      },
      "ac156f74-8903-44fc-88d7-f1c3ab7614bf": {
        "type": "SpaceEdge",
        "name": "Ascent from GC",
        "description": "Ascent from Gale Crater",
        "origin_id": "7305bc6b-fa82-40c9-9a82-8dfe8b7b60f9",
        "destination_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "duration": 0.1,
        "delta_v": 4100
      },
      "58b2ec36-2d45-4bdd-a46a-4c0ccfcd8af7": {
        "type": "SpaceEdge",
        "name": "Descent to HC",
        "description": "Descent to Holden Crater Fan",
        "origin_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "destination_id": "831885d7-e7e0-463a-beef-987add3b32ca",
        "duration": 0.1,
        "delta_v": 610
      },
      "93c7f7f4-0600-4cdc-a4cb-8c2ce8d23d2b": {
        "type": "SpaceEdge",
        "name": "Ascent from HC",
        "description": "Ascent from Holden Crater Fan",
        "origin_id": "831885d7-e7e0-463a-beef-987add3b32ca",
        "destination_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "duration": 0.1,
        "delta_v": 4100
      },
      "11ec7971-923d-4d01-a890-e090100d95e3": {
        "type": "SpaceEdge",
        "name": "TEI to Splashdown",
        "description": "Trans-Earth Injection / Splashdown in Pacific",
        "origin_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "destination_id": "09d7dbbc-fb1c-441b-b9e6-f424458d5ddf",
        "duration": 201,
        "delta_v": 2400
      },
      "34decaba-822a-429b-afd1-f3ed78fb2f65": {
        "type": "FlightEdge",
        "name": "Crew Launch to LEO",
        "description": "Crew Launch to LEO",
        "origin_id": "9533b255-526f-4197-9319-6013ca01ec97",
        "destination_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
        "duration": 0.1,
        "max_crew": 6,
        "max_cargo": 100
      },
      "d9ec7e42-7c89-461e-bdcb-d945c03d0d06": {
        "type": "FlightEdge",
        "name": "MAV Ascent from MV",
        "description": "Mars Ascent Vehicle Launch",
        "origin_id": "9032bcfa-7457-4ff7-9c07-2d698d728778",
        "destination_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
        "duration": 0.1,
        "max_crew": 6,
        "max_cargo": 300
      }
    }
  },
  "elementList": {
    "23a5c8d6-ed25-470b-bdf9-3e13079640ea": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core A",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "d7047003-ca2b-4b99-8d01-aaf6dce60670": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS A",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "52c62e45-3375-4d27-8893-878dd94c0f68": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage A",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "690af366-a470-4b5a-a30a-6a4b61b79b57": {
      "type": "Element",
      "name": "M.01 | Ares V PLF A",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "96710fa0-e04a-48d0-b78b-66ec1d48a9cd": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs A",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "96231a63-2635-4465-a939-e7fa4370ad6c": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | NTR Core A",
      "description": "Nuclear Thermal Rocket Core Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 33700,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 59400,
      "max_crew": 0,
      "propellant_id": 0
    },
    "60e9dff7-7c54-4649-abfb-6e9b6bfbc4ed": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core B",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "e06e6917-2808-44d8-88d4-ad32b5120d99": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS B",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "f680eb85-9881-4e6a-961c-fe2eb63a2a53": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage B",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "6178d9db-cb97-4bc7-955b-a8f4b987bfb4": {
      "type": "Element",
      "name": "M.01 | Ares V PLF B",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "1fde5118-355c-454f-9023-cb3e2f5ffdda": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs B",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "2c4d2492-e892-441d-ba6a-6dbf03c698f8": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | NTR Core B",
      "description": "Nuclear Thermal Rocket Core Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 33700,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 59400,
      "max_crew": 0,
      "propellant_id": 0
    },
    "92198e0c-4557-4864-92f2-14be3f77d53b": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core C",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "ba4b8739-740d-477f-902f-f415654517dc": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS C",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "bf6e9140-b4de-40a2-96d4-b8bdca7d46a7": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage C",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "ee09f52a-53ac-4a9b-af4b-e000571290b6": {
      "type": "Element",
      "name": "M.01 | Ares V PLF C",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "b668d325-6dc3-4b27-bcf4-b57561edb2a7": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs C",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "0d4bda92-ec8f-4d8d-b76b-352367d77438": {
      "type": "ElementCarrier",
      "name": "M.01 | CFC A",
      "description": "Contingency Food Canister",
      "class_of_supply": 9,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 1860,
      "volume": 0,
      "max_cargo_mass": 7940,
      "max_cargo_volume": 0,
      "cargo_environment": "Pressurized"
    },
    "c8302aa8-10e3-4f58-b6ad-db35e78f0a86": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | In-line LH2 A",
      "description": "In-Line LH2 Tank (for NTR)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 10800,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 34100,
      "max_crew": 0,
      "propellant_id": 0
    },
    "d5d4bf29-68f0-4635-b993-f345eef39df0": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | In-line LH2 B",
      "description": "In-Line LH2 Tank (for NTR)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 10800,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 34100,
      "max_crew": 0,
      "propellant_id": 0
    },
    "1516c56c-2bf0-49fa-a2d2-9d38ad0c88ac": {
      "type": "ResourceContainer",
      "name": "CFC Resource Container A",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 7940,
      "max_cargo_volume": 0
    },
    "fbf4ee23-3e9d-4cb9-a4fe-57df190169c1": {
      "type": "Element",
      "name": "M.01 | Aeroshell A",
      "description": "Dual-use Aeroshell Shroud",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 40700,
      "volume": 0
    },
    "0bf1a6e0-729d-4ca1-8bd4-90823994d14a": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core D",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "b28e6405-502e-4afb-8935-87f96c654135": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS D",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "8ddea594-a0ce-4ea7-a1f2-e90e5ccc381f": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage D",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "499867a0-2409-42fc-8004-257f0fbc001f": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs D",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "dba6909b-4073-4fa0-aaff-23cc40bda6ba": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Cargo Lander",
      "description": "Mars Descent-Ascent Vehicle (Cargo Lander) with Aeroshell",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9023,
      "mass": 25780,
      "volume": 0,
      "max_cargo_mass": 5500,
      "max_cargo_volume": 0,
      "isp": 369,
      "max_fuel": 10600,
      "max_crew": 0,
      "propellant_id": 0
    },
    "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | MAV",
      "description": "Mars Ascent Vehicle",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9024,
      "mass": 21500,
      "volume": 0,
      "max_cargo_mass": 300,
      "max_cargo_volume": 0,
      "isp": 369,
      "max_fuel": 0,
      "max_crew": 6,
      "propellant_id": 0
    },
    "2dd553ad-9697-453e-8538-0ddc27edf8fa": {
      "type": "ResourceContainer",
      "name": "CEV/MAV Resource Container A",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 50,
      "max_cargo_volume": 0
    },
    "679fe70f-847e-4ba4-ad34-f27a4ed3a6bb": {
      "type": "ResourceContainer",
      "name": "MDAV Resource Container",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 5500,
      "max_cargo_volume": 0
    },
    "be981a4b-c81e-4b44-b08d-a6a38eed6af8": {
      "type": "Element",
      "name": "M.01 | Aeroshell B",
      "description": "Dual-use Aeroshell Shroud",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 40700,
      "volume": 0
    },
    "03b812e3-aaab-4b23-9981-d05bd09b7c12": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core E",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "c3b23236-23ee-440b-a7c9-6f5879c7f933": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS E",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "2e13e104-c4e4-4508-8dbc-8561d54c0e99": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage E",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "15224631-563c-4e5f-9643-1ff62487887f": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs E",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "1b9476c4-80ad-4a89-b761-e3d87f721dad": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Habitat Lander",
      "description": "Surface Habitat (Habitat Lander) with Aeroshell",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9023,
      "mass": 52060,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 369,
      "max_fuel": 10600,
      "max_crew": 0,
      "propellant_id": 0
    },
    "2f089adf-40ca-44a2-90bd-aab6547e7caa": {
      "type": "ResourceContainer",
      "name": "SHAB Resource Container",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 1500,
      "max_cargo_volume": 0
    },
    "6bb9bf6a-6a0b-4c38-8ad5-a264855b660c": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core F",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "9f49f4ef-de74-494e-b91d-daabd7cdbf92": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS F",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "f561660c-b62b-4f3b-b982-59ea2be27f55": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage F",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "6de3394b-3feb-47f6-88d3-718bfc5312bf": {
      "type": "Element",
      "name": "M.01 | Ares V PLF F",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "219a18b6-9475-40f1-9acd-af5dbf0ecdcd": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs F",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "523063ff-1202-40a4-ac35-59fd077211a5": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | NTR Core (S)",
      "description": "Nuclear Thermal Rocket Core Stage with Shielding",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 41700,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 59700,
      "max_crew": 0,
      "propellant_id": 0
    },
    "45cfef8e-f5c0-4789-9a1b-142e0bf96add": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core G",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "983f01d6-295b-475c-ba6d-6f046aa0fbf3": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS G",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "b79f8efb-38d2-40fa-89e9-41dfa0a5e2fc": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage G",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "98f8f0eb-aa97-404f-82c2-75c470377e84": {
      "type": "Element",
      "name": "M.01 | Ares V PLF G",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "3d4f97c3-744e-47a4-b832-5c0cd0d7e7bd": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs G",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "fff699af-df9d-4d32-b2ce-cbb6de5a47b4": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | In-line LH2 Tank (S)",
      "description": "In-Line LH2 Tank (for NTRS)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 21500,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 69900,
      "max_crew": 0,
      "propellant_id": 0
    },
    "a6a859af-a186-4fa1-bef5-8b479bf2ca52": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core H",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "1df1780e-4aed-4adb-b4c1-620533e06089": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS H",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "73232641-c275-4a28-84c4-4f761cf5a6d5": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage H",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "ab443263-0a49-4fbf-9268-00d3023b8b63": {
      "type": "Element",
      "name": "M.01 | Ares V PLF H",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "57410d9f-5a01-4528-b4a9-50576ffb2743": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs H",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "0a3b8d76-3f3f-4e9b-a5e4-b2f1d5022e20": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | LH2 Drop Tank",
      "description": "LH2 Drop Tank",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 14000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 950,
      "max_fuel": 73100,
      "max_crew": 0,
      "propellant_id": 0
    },
    "eefa1728-940c-46cf-97ad-c516b8a56b91": {
      "type": "Element",
      "name": "M.01 | Long Saddle Truss",
      "description": "Long Saddle Truss",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 8900,
      "volume": 0
    },
    "71a4e5a2-eed4-4c0f-993e-de36fdfeef13": {
      "type": "Element",
      "name": "M.01 | 2nd Docking Module",
      "description": "2nd Docking Module",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 1800,
      "volume": 0
    },
    "d3b81f14-3da1-4bec-b079-979c7c55373d": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V Core I",
      "description": "Ares V Core",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 173680,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 414,
      "max_fuel": 1587000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "479f65d6-0672-45f3-ada5-7c0c8abccb79": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V EDS I",
      "description": "Ares V Earth Departure Stage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9022,
      "mass": 26390,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 449,
      "max_fuel": 253000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "28bbdd78-a862-45f5-8e50-ee1b686067dd": {
      "type": "Element",
      "name": "M.01 | Ares V Interstage I",
      "description": "Ares V Interstage",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9190,
      "volume": 0
    },
    "a50bb936-3828-4c5e-9ac1-59526d1d0ebe": {
      "type": "Element",
      "name": "M.01 | Ares V PLF I",
      "description": "Ares V Payload Fairing",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 9049,
      "volume": 0
    },
    "0a221b84-763a-47ac-836f-2d19738f266d": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | Ares V SRBs I",
      "description": "Ares V Boosters (2)",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9021,
      "mass": 213000,
      "volume": 0,
      "max_cargo_mass": 0,
      "max_cargo_volume": 0,
      "isp": 269,
      "max_fuel": 1370000,
      "max_crew": 0,
      "propellant_id": 0
    },
    "1d85334f-169a-4f3f-94f4-d7fba28beb7b": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | CEV A",
      "description": "Crewed Exploration Vehicle",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 901,
      "mass": 14000,
      "volume": 0,
      "max_cargo_mass": 250,
      "max_cargo_volume": 0,
      "isp": 301,
      "max_fuel": 1000,
      "max_crew": 6,
      "propellant_id": 0
    },
    "bf76062d-3dc4-4a4b-8247-ddef23cda38a": {
      "type": "ElementCarrier",
      "name": "M.01 | CFC B",
      "description": "Contingency Food Canister",
      "class_of_supply": 9,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 1860,
      "volume": 0,
      "max_cargo_mass": 7940,
      "max_cargo_volume": 0,
      "cargo_environment": "Pressurized"
    },
    "f8f213a7-ae92-4e37-a01c-98c5937ff333": {
      "type": "ElementCarrier",
      "name": "M.01 | MTH",
      "description": "Mars Transfer Habitat",
      "class_of_supply": 8,
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "mass": 27540,
      "volume": 0,
      "max_cargo_mass": 5300,
      "max_cargo_volume": 0,
      "cargo_environment": "Pressurized"
    },
    "035a8cf6-902b-47cb-bfa1-752b38c8e287": {
      "type": "Element",
      "name": "M.01 | Short Saddle Truss",
      "description": "Short Saddle Truss",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 9,
      "mass": 4700,
      "volume": 0
    },
    "b28e48c2-6659-4d52-9b82-5774e458215b": {
      "type": "ResourceContainer",
      "name": "CFC Resource Container B",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 7940,
      "max_cargo_volume": 0
    },
    "45c71d17-9007-4972-a984-d48acd38e18b": {
      "type": "ResourceContainer",
      "name": "MTH Resource Container",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 5300,
      "max_cargo_volume": 0
    },
    "3771661d-1442-46a8-8646-b87d93346b63": {
      "type": "PropulsiveVehicle",
      "name": "M.01 | CEV B",
      "description": "Crewed Exploration Vehicle",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 901,
      "mass": 14000,
      "volume": 0,
      "max_cargo_mass": 250,
      "max_cargo_volume": 0,
      "isp": 301,
      "max_fuel": 1000,
      "max_crew": 6,
      "propellant_id": 0
    },
    "555d8e54-ca96-41d1-8dd0-b9cbd466d9a7": {
      "type": "ResourceContainer",
      "name": "CEV/MAV Resource Container B",
      "description": "Notional Resource Container",
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "class_of_supply": 5,
      "mass": 0,
      "volume": 0,
      "max_cargo_mass": 50,
      "max_cargo_volume": 0
    },
    "9871984f-3125-4218-8707-87a903caeeb1": {
      "type": "HumanAgent",
      "name": "M.01 | Crew Member A",
      "description": "Generic Astronaut",
      "class_of_supply": 0,
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "mass": 93.3,
      "volume": 0,
      "active_time_fraction": 0.667
    },
    "cad7444a-4eb2-4166-af74-79a2edc39405": {
      "type": "HumanAgent",
      "name": "M.01 | Crew Member B",
      "description": "Generic Astronaut",
      "class_of_supply": 0,
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "mass": 93.3,
      "volume": 0,
      "active_time_fraction": 0.667
    },
    "a82b0d59-e835-4218-bc4b-cd0a2a621659": {
      "type": "HumanAgent",
      "name": "M.01 | Crew Member C",
      "description": "Generic Astronaut",
      "class_of_supply": 0,
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "mass": 93.3,
      "volume": 0,
      "active_time_fraction": 0.667
    },
    "888ab476-cefc-4ea4-a135-c1ccad03b3df": {
      "type": "HumanAgent",
      "name": "M.01 | Crew Member D",
      "description": "Generic Astronaut",
      "class_of_supply": 0,
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "mass": 93.3,
      "volume": 0,
      "active_time_fraction": 0.667
    },
    "6d20c083-1aae-44e6-af3d-98daf4f3e5c3": {
      "type": "HumanAgent",
      "name": "M.01 | Crew Member E",
      "description": "Generic Astronaut",
      "class_of_supply": 0,
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "mass": 93.3,
      "volume": 0,
      "active_time_fraction": 0.667
    },
    "8837cd3b-081f-4439-bb0e-d9c4d008ee6b": {
      "type": "HumanAgent",
      "name": "M.01 | Crew Member F",
      "description": "Generic Astronaut",
      "class_of_supply": 0,
      "environment": "Pressurized",
      "accommodation_mass": 0,
      "mass": 93.3,
      "volume": 0,
      "active_time_fraction": 0.667
    },
    "9b395aec-8321-4670-882d-69d22695db06": {
      "type": "Element",
      "name": "M.01 | Samples",
      "description": "Martian Samples",
      "environment": "Unpressurized",
      "accommodation_mass": 0,
      "class_of_supply": 6,
      "mass": 250,
      "volume": 0
    }
  },
  "missionList": [
    {
      "name": "M.01 Mawrth Vallis Exploration",
      "start_date": "2035-01-01T00:00:00",
      "events": [
        {
          "name": "M.01 | Create Stack 1",
          "mission_time": "00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "23a5c8d6-ed25-470b-bdf9-3e13079640ea",
            "d7047003-ca2b-4b99-8d01-aaf6dce60670",
            "52c62e45-3375-4d27-8893-878dd94c0f68",
            "690af366-a470-4b5a-a30a-6a4b61b79b57",
            "96710fa0-e04a-48d0-b78b-66ec1d48a9cd",
            "96231a63-2635-4465-a939-e7fa4370ad6c"
          ]
        },
        {
          "name": "M.01 | Launch 1",
          "mission_time": "00",
          "type": "SpaceTransport",
          "priority": 2,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "23a5c8d6-ed25-470b-bdf9-3e13079640ea",
            "d7047003-ca2b-4b99-8d01-aaf6dce60670",
            "52c62e45-3375-4d27-8893-878dd94c0f68",
            "690af366-a470-4b5a-a30a-6a4b61b79b57",
            "96710fa0-e04a-48d0-b78b-66ec1d48a9cd",
            "96231a63-2635-4465-a939-e7fa4370ad6c"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "96710fa0-e04a-48d0-b78b-66ec1d48a9cd"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "96710fa0-e04a-48d0-b78b-66ec1d48a9cd"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "23a5c8d6-ed25-470b-bdf9-3e13079640ea"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "23a5c8d6-ed25-470b-bdf9-3e13079640ea"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "52c62e45-3375-4d27-8893-878dd94c0f68"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "690af366-a470-4b5a-a30a-6a4b61b79b57"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "d7047003-ca2b-4b99-8d01-aaf6dce60670"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 2",
          "mission_time": "31 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "60e9dff7-7c54-4649-abfb-6e9b6bfbc4ed",
            "e06e6917-2808-44d8-88d4-ad32b5120d99",
            "f680eb85-9881-4e6a-961c-fe2eb63a2a53",
            "6178d9db-cb97-4bc7-955b-a8f4b987bfb4",
            "1fde5118-355c-454f-9023-cb3e2f5ffdda",
            "2c4d2492-e892-441d-ba6a-6dbf03c698f8"
          ]
        },
        {
          "name": "M.01 | Launch 2",
          "mission_time": "31 00:00:00",
          "type": "SpaceTransport",
          "priority": 2,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "60e9dff7-7c54-4649-abfb-6e9b6bfbc4ed",
            "e06e6917-2808-44d8-88d4-ad32b5120d99",
            "f680eb85-9881-4e6a-961c-fe2eb63a2a53",
            "6178d9db-cb97-4bc7-955b-a8f4b987bfb4",
            "1fde5118-355c-454f-9023-cb3e2f5ffdda",
            "2c4d2492-e892-441d-ba6a-6dbf03c698f8"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "1fde5118-355c-454f-9023-cb3e2f5ffdda"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "1fde5118-355c-454f-9023-cb3e2f5ffdda"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "60e9dff7-7c54-4649-abfb-6e9b6bfbc4ed"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "60e9dff7-7c54-4649-abfb-6e9b6bfbc4ed"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "f680eb85-9881-4e6a-961c-fe2eb63a2a53"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "6178d9db-cb97-4bc7-955b-a8f4b987bfb4"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "e06e6917-2808-44d8-88d4-ad32b5120d99"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 3",
          "mission_time": "59 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "92198e0c-4557-4864-92f2-14be3f77d53b",
            "ba4b8739-740d-477f-902f-f415654517dc",
            "bf6e9140-b4de-40a2-96d4-b8bdca7d46a7",
            "ee09f52a-53ac-4a9b-af4b-e000571290b6",
            "b668d325-6dc3-4b27-bcf4-b57561edb2a7",
            "0d4bda92-ec8f-4d8d-b76b-352367d77438",
            "c8302aa8-10e3-4f58-b6ad-db35e78f0a86",
            "d5d4bf29-68f0-4635-b993-f345eef39df0"
          ]
        },
        {
          "name": "M.01 | Create CFC Resources A",
          "mission_time": "59 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "0d4bda92-ec8f-4d8d-b76b-352367d77438",
          "elements": [
            "1516c56c-2bf0-49fa-a2d2-9d38ad0c88ac"
          ]
        },
        {
          "name": "M.01 | Launch 3",
          "mission_time": "59 00:00:00",
          "type": "SpaceTransport",
          "priority": 3,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "92198e0c-4557-4864-92f2-14be3f77d53b",
            "ba4b8739-740d-477f-902f-f415654517dc",
            "bf6e9140-b4de-40a2-96d4-b8bdca7d46a7",
            "ee09f52a-53ac-4a9b-af4b-e000571290b6",
            "b668d325-6dc3-4b27-bcf4-b57561edb2a7",
            "0d4bda92-ec8f-4d8d-b76b-352367d77438",
            "c8302aa8-10e3-4f58-b6ad-db35e78f0a86",
            "d5d4bf29-68f0-4635-b993-f345eef39df0"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "b668d325-6dc3-4b27-bcf4-b57561edb2a7"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "b668d325-6dc3-4b27-bcf4-b57561edb2a7"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "92198e0c-4557-4864-92f2-14be3f77d53b"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "92198e0c-4557-4864-92f2-14be3f77d53b"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "bf6e9140-b4de-40a2-96d4-b8bdca7d46a7"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "ee09f52a-53ac-4a9b-af4b-e000571290b6"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "ba4b8739-740d-477f-902f-f415654517dc"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 4",
          "mission_time": "90 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "fbf4ee23-3e9d-4cb9-a4fe-57df190169c1",
            "0bf1a6e0-729d-4ca1-8bd4-90823994d14a",
            "b28e6405-502e-4afb-8935-87f96c654135",
            "8ddea594-a0ce-4ea7-a1f2-e90e5ccc381f",
            "499867a0-2409-42fc-8004-257f0fbc001f",
            "dba6909b-4073-4fa0-aaff-23cc40bda6ba",
            "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3"
          ]
        },
        {
          "name": "M.01 | Create MAV Resources",
          "mission_time": "90 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3",
          "elements": [
            "2dd553ad-9697-453e-8538-0ddc27edf8fa"
          ]
        },
        {
          "name": "M.01 | Create MDAV Resources",
          "mission_time": "90 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "dba6909b-4073-4fa0-aaff-23cc40bda6ba",
          "elements": [
            "679fe70f-847e-4ba4-ad34-f27a4ed3a6bb"
          ]
        },
        {
          "name": "M.01 | Launch 4",
          "mission_time": "90 00:00:00",
          "type": "SpaceTransport",
          "priority": 3,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "fbf4ee23-3e9d-4cb9-a4fe-57df190169c1",
            "0bf1a6e0-729d-4ca1-8bd4-90823994d14a",
            "b28e6405-502e-4afb-8935-87f96c654135",
            "8ddea594-a0ce-4ea7-a1f2-e90e5ccc381f",
            "499867a0-2409-42fc-8004-257f0fbc001f",
            "dba6909b-4073-4fa0-aaff-23cc40bda6ba",
            "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "499867a0-2409-42fc-8004-257f0fbc001f"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "499867a0-2409-42fc-8004-257f0fbc001f"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "0bf1a6e0-729d-4ca1-8bd4-90823994d14a"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "0bf1a6e0-729d-4ca1-8bd4-90823994d14a"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "8ddea594-a0ce-4ea7-a1f2-e90e5ccc381f"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "b28e6405-502e-4afb-8935-87f96c654135"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 5",
          "mission_time": "120 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "be981a4b-c81e-4b44-b08d-a6a38eed6af8",
            "03b812e3-aaab-4b23-9981-d05bd09b7c12",
            "c3b23236-23ee-440b-a7c9-6f5879c7f933",
            "2e13e104-c4e4-4508-8dbc-8561d54c0e99",
            "15224631-563c-4e5f-9643-1ff62487887f",
            "1b9476c4-80ad-4a89-b761-e3d87f721dad"
          ]
        },
        {
          "name": "M.01 | Create SHAB Resources",
          "mission_time": "120 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "1b9476c4-80ad-4a89-b761-e3d87f721dad",
          "elements": [
            "2f089adf-40ca-44a2-90bd-aab6547e7caa"
          ]
        },
        {
          "name": "M.01 | Launch 5",
          "mission_time": "120 00:00:00",
          "type": "SpaceTransport",
          "priority": 3,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "be981a4b-c81e-4b44-b08d-a6a38eed6af8",
            "03b812e3-aaab-4b23-9981-d05bd09b7c12",
            "c3b23236-23ee-440b-a7c9-6f5879c7f933",
            "2e13e104-c4e4-4508-8dbc-8561d54c0e99",
            "15224631-563c-4e5f-9643-1ff62487887f",
            "1b9476c4-80ad-4a89-b761-e3d87f721dad"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "15224631-563c-4e5f-9643-1ff62487887f"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "15224631-563c-4e5f-9643-1ff62487887f"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "03b812e3-aaab-4b23-9981-d05bd09b7c12"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "03b812e3-aaab-4b23-9981-d05bd09b7c12"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "2e13e104-c4e4-4508-8dbc-8561d54c0e99"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "c3b23236-23ee-440b-a7c9-6f5879c7f933"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | TMI/MOV 1",
          "mission_time": "177 00:00:00",
          "type": "SpaceTransport",
          "priority": 1,
          "origin_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "destination_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "edge_id": "e44e1484-80d6-41fa-81ed-b49ca2a24067",
          "exec_time": "202 00:00:00",
          "elements_id_list": [
            "fbf4ee23-3e9d-4cb9-a4fe-57df190169c1",
            "dba6909b-4073-4fa0-aaff-23cc40bda6ba",
            "c8302aa8-10e3-4f58-b6ad-db35e78f0a86",
            "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3",
            "96231a63-2635-4465-a939-e7fa4370ad6c"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "96231a63-2635-4465-a939-e7fa4370ad6c"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "c8302aa8-10e3-4f58-b6ad-db35e78f0a86"
                }
              ]
            }

          ]
        },
        {
          "name": "M.01 | TMI/MOV 2",
          "mission_time": "184 00:00:00",
          "type": "SpaceTransport",
          "priority": 1,
          "origin_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "destination_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "edge_id": "e44e1484-80d6-41fa-81ed-b49ca2a24067",
          "exec_time": "202 00:00:00",
          "elements_id_list": [
            "be981a4b-c81e-4b44-b08d-a6a38eed6af8",
            "0d4bda92-ec8f-4d8d-b76b-352367d77438",
            "1b9476c4-80ad-4a89-b761-e3d87f721dad",
            "d5d4bf29-68f0-4635-b993-f345eef39df0",
            "2c4d2492-e892-441d-ba6a-6dbf03c698f8"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "2c4d2492-e892-441d-ba6a-6dbf03c698f8"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "d5d4bf29-68f0-4635-b993-f345eef39df0"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | TMI/MOV 2",
          "mission_time": "184 00:00:00",
          "type": "SpaceTransport",
          "priority": 1,
          "origin_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "destination_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "edge_id": "e44e1484-80d6-41fa-81ed-b49ca2a24067",
          "exec_time": "202 00:00:00",
          "elements_id_list": [
            "be981a4b-c81e-4b44-b08d-a6a38eed6af8",
            "0d4bda92-ec8f-4d8d-b76b-352367d77438",
            "1b9476c4-80ad-4a89-b761-e3d87f721dad",
            "d5d4bf29-68f0-4635-b993-f345eef39df0",
            "2c4d2492-e892-441d-ba6a-6dbf03c698f8"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "2c4d2492-e892-441d-ba6a-6dbf03c698f8"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "d5d4bf29-68f0-4635-b993-f345eef39df0"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Cargo Lander Descent",
          "mission_time": "400 00:00:00",
          "type": "SpaceTransport",
          "priority": 1,
          "origin_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "destination_node_id": "9032bcfa-7457-4ff7-9c07-2d698d728778",
          "edge_id": "ada1b096-2991-470e-a0d9-6f27fc2e068d",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "fbf4ee23-3e9d-4cb9-a4fe-57df190169c1",
            "dba6909b-4073-4fa0-aaff-23cc40bda6ba",
            "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "dba6909b-4073-4fa0-aaff-23cc40bda6ba"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 6",
          "mission_time": "821 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "6bb9bf6a-6a0b-4c38-8ad5-a264855b660c",
            "9f49f4ef-de74-494e-b91d-daabd7cdbf92",
            "f561660c-b62b-4f3b-b982-59ea2be27f55",
            "6de3394b-3feb-47f6-88d3-718bfc5312bf",
            "219a18b6-9475-40f1-9acd-af5dbf0ecdcd",
            "523063ff-1202-40a4-ac35-59fd077211a5"
          ]
        },
        {
          "name": "M.01 | Launch 6",
          "mission_time": "821 00:00:00",
          "type": "SpaceTransport",
          "priority": 2,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "6bb9bf6a-6a0b-4c38-8ad5-a264855b660c",
            "9f49f4ef-de74-494e-b91d-daabd7cdbf92",
            "f561660c-b62b-4f3b-b982-59ea2be27f55",
            "6de3394b-3feb-47f6-88d3-718bfc5312bf",
            "219a18b6-9475-40f1-9acd-af5dbf0ecdcd",
            "523063ff-1202-40a4-ac35-59fd077211a5"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "219a18b6-9475-40f1-9acd-af5dbf0ecdcd"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "219a18b6-9475-40f1-9acd-af5dbf0ecdcd"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "6bb9bf6a-6a0b-4c38-8ad5-a264855b660c"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "6bb9bf6a-6a0b-4c38-8ad5-a264855b660c"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "f561660c-b62b-4f3b-b982-59ea2be27f55"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "6de3394b-3feb-47f6-88d3-718bfc5312bf"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "9f49f4ef-de74-494e-b91d-daabd7cdbf92"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 7",
          "mission_time": "851 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "45cfef8e-f5c0-4789-9a1b-142e0bf96add",
            "983f01d6-295b-475c-ba6d-6f046aa0fbf3",
            "b79f8efb-38d2-40fa-89e9-41dfa0a5e2fc",
            "98f8f0eb-aa97-404f-82c2-75c470377e84",
            "3d4f97c3-744e-47a4-b832-5c0cd0d7e7bd",
            "fff699af-df9d-4d32-b2ce-cbb6de5a47b4"
          ]
        },
        {
          "name": "M.01 | Launch 7",
          "mission_time": "821 00:00:00",
          "type": "SpaceTransport",
          "priority": 2,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "45cfef8e-f5c0-4789-9a1b-142e0bf96add",
            "983f01d6-295b-475c-ba6d-6f046aa0fbf3",
            "b79f8efb-38d2-40fa-89e9-41dfa0a5e2fc",
            "98f8f0eb-aa97-404f-82c2-75c470377e84",
            "3d4f97c3-744e-47a4-b832-5c0cd0d7e7bd",
            "fff699af-df9d-4d32-b2ce-cbb6de5a47b4"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "3d4f97c3-744e-47a4-b832-5c0cd0d7e7bd"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "3d4f97c3-744e-47a4-b832-5c0cd0d7e7bd"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "45cfef8e-f5c0-4789-9a1b-142e0bf96add"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "45cfef8e-f5c0-4789-9a1b-142e0bf96add"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "b79f8efb-38d2-40fa-89e9-41dfa0a5e2fc"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "98f8f0eb-aa97-404f-82c2-75c470377e84"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "983f01d6-295b-475c-ba6d-6f046aa0fbf3"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 8",
          "mission_time": "882 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "a6a859af-a186-4fa1-bef5-8b479bf2ca52",
            "1df1780e-4aed-4adb-b4c1-620533e06089",
            "73232641-c275-4a28-84c4-4f761cf5a6d5",
            "ab443263-0a49-4fbf-9268-00d3023b8b63",
            "57410d9f-5a01-4528-b4a9-50576ffb2743",
            "0a3b8d76-3f3f-4e9b-a5e4-b2f1d5022e20",
            "eefa1728-940c-46cf-97ad-c516b8a56b91"
          ]
        },
        {
          "name": "M.01 | Launch 8",
          "mission_time": "882 00:00:00",
          "type": "SpaceTransport",
          "priority": 2,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "a6a859af-a186-4fa1-bef5-8b479bf2ca52",
            "1df1780e-4aed-4adb-b4c1-620533e06089",
            "73232641-c275-4a28-84c4-4f761cf5a6d5",
            "ab443263-0a49-4fbf-9268-00d3023b8b63",
            "57410d9f-5a01-4528-b4a9-50576ffb2743",
            "0a3b8d76-3f3f-4e9b-a5e4-b2f1d5022e20",
            "eefa1728-940c-46cf-97ad-c516b8a56b91"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "57410d9f-5a01-4528-b4a9-50576ffb2743"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "57410d9f-5a01-4528-b4a9-50576ffb2743"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "a6a859af-a186-4fa1-bef5-8b479bf2ca52"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "a6a859af-a186-4fa1-bef5-8b479bf2ca52"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "73232641-c275-4a28-84c4-4f761cf5a6d5"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "ab443263-0a49-4fbf-9268-00d3023b8b63"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "1df1780e-4aed-4adb-b4c1-620533e06089"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create Stack 9",
          "mission_time": "912 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "71a4e5a2-eed4-4c0f-993e-de36fdfeef13",
            "d3b81f14-3da1-4bec-b079-979c7c55373d",
            "479f65d6-0672-45f3-ada5-7c0c8abccb79",
            "28bbdd78-a862-45f5-8e50-ee1b686067dd",
            "a50bb936-3828-4c5e-9ac1-59526d1d0ebe",
            "0a221b84-763a-47ac-836f-2d19738f266d",
            "1d85334f-169a-4f3f-94f4-d7fba28beb7b",
            "bf76062d-3dc4-4a4b-8247-ddef23cda38a",
            "f8f213a7-ae92-4e37-a01c-98c5937ff333",
            "035a8cf6-902b-47cb-bfa1-752b38c8e287"
          ]
        },
        {
          "name": "M.01 | Create CFC Resources B",
          "mission_time": "912 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "bf76062d-3dc4-4a4b-8247-ddef23cda38a",
          "elements": [
            "b28e48c2-6659-4d52-9b82-5774e458215b"
          ]
        },
        {
          "name": "M.01 | Create MTH Resources",
          "mission_time": "912 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "f8f213a7-ae92-4e37-a01c-98c5937ff333",
          "elements": [
            "45c71d17-9007-4972-a984-d48acd38e18b"
          ]
        },
        {
          "name": "M.01 | Launch 9",
          "mission_time": "912 00:00:00",
          "type": "SpaceTransport",
          "priority": 3,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "1204f9f9-6f71-4a88-a7b4-db6d8c81e931",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "71a4e5a2-eed4-4c0f-993e-de36fdfeef13",
            "d3b81f14-3da1-4bec-b079-979c7c55373d",
            "479f65d6-0672-45f3-ada5-7c0c8abccb79",
            "28bbdd78-a862-45f5-8e50-ee1b686067dd",
            "a50bb936-3828-4c5e-9ac1-59526d1d0ebe",
            "0a221b84-763a-47ac-836f-2d19738f266d",
            "1d85334f-169a-4f3f-94f4-d7fba28beb7b",
            "bf76062d-3dc4-4a4b-8247-ddef23cda38a",
            "f8f213a7-ae92-4e37-a01c-98c5937ff333",
            "035a8cf6-902b-47cb-bfa1-752b38c8e287"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "0a221b84-763a-47ac-836f-2d19738f266d"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "0a221b84-763a-47ac-836f-2d19738f266d"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "d3b81f14-3da1-4bec-b079-979c7c55373d"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "d3b81f14-3da1-4bec-b079-979c7c55373d"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "28bbdd78-a862-45f5-8e50-ee1b686067dd"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "a50bb936-3828-4c5e-9ac1-59526d1d0ebe"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "479f65d6-0672-45f3-ada5-7c0c8abccb79"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Create CM and SM",
          "mission_time": "964 00:00:00",
          "type": "MakeElements",
          "priority": 1,
          "entry_point_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "elements": [
            "3771661d-1442-46a8-8646-b87d93346b63"
          ]
        },
        {
          "name": "M.01 | Create Crew",
          "mission_time": "964 00:00:00",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "3771661d-1442-46a8-8646-b87d93346b63",
          "elements": [
            "555d8e54-ca96-41d1-8dd0-b9cbd466d9a7",
            "9871984f-3125-4218-8707-87a903caeeb1",
            "cad7444a-4eb2-4166-af74-79a2edc39405",
            "a82b0d59-e835-4218-bc4b-cd0a2a621659",
            "888ab476-cefc-4ea4-a135-c1ccad03b3df",
            "6d20c083-1aae-44e6-af3d-98daf4f3e5c3",
            "8837cd3b-081f-4439-bb0e-d9c4d008ee6b"
          ]
        },
        {
          "name": "M.01 | Launch Crew",
          "mission_time": "964 00:00:00",
          "type": "FlightTransport",
          "priority": 3,
          "origin_node_id": "9533b255-526f-4197-9319-6013ca01ec97",
          "destination_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "edge_id": "34decaba-822a-429b-afd1-f3ed78fb2f65",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "3771661d-1442-46a8-8646-b87d93346b63"
          ]
        },
        {
          "name": "M.01 | Transfer Crew to CTH",
          "mission_time": "964 02:00:01",
          "type": "MoveElements",
          "priority": 1,
          "origin_id": "3771661d-1442-46a8-8646-b87d93346b63",
          "destination_id": "f8f213a7-ae92-4e37-a01c-98c5937ff333",
          "to_move": [
            "9871984f-3125-4218-8707-87a903caeeb1",
            "cad7444a-4eb2-4166-af74-79a2edc39405",
            "a82b0d59-e835-4218-bc4b-cd0a2a621659",
            "888ab476-cefc-4ea4-a135-c1ccad03b3df",
            "6d20c083-1aae-44e6-af3d-98daf4f3e5c3",
            "8837cd3b-081f-4439-bb0e-d9c4d008ee6b"
          ]
        },
        {
          "name": "M.01 | TMI/MOV 3",
          "mission_time": "969 00:00:00",
          "type": "SpaceTransport",
          "priority": 1,
          "origin_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "destination_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "edge_id": "cb720ee2-37c2-4500-bdcb-a52b04356899",
          "exec_time": "174 00:00:00",
          "elements_id_list": [
            "71a4e5a2-eed4-4c0f-993e-de36fdfeef13",
            "1d85334f-169a-4f3f-94f4-d7fba28beb7b",
            "bf76062d-3dc4-4a4b-8247-ddef23cda38a",
            "fff699af-df9d-4d32-b2ce-cbb6de5a47b4",
            "0a3b8d76-3f3f-4e9b-a5e4-b2f1d5022e20",
            "eefa1728-940c-46cf-97ad-c516b8a56b91",
            "f8f213a7-ae92-4e37-a01c-98c5937ff333",
            "523063ff-1202-40a4-ac35-59fd077211a5",
            "035a8cf6-902b-47cb-bfa1-752b38c8e287"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "0a3b8d76-3f3f-4e9b-a5e4-b2f1d5022e20"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "0a3b8d76-3f3f-4e9b-a5e4-b2f1d5022e20"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "523063ff-1202-40a4-ac35-59fd077211a5"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "523063ff-1202-40a4-ac35-59fd077211a5"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "fff699af-df9d-4d32-b2ce-cbb6de5a47b4"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Transfer Crew to Hab Lander",
          "mission_time": "1145 00:00:00",
          "type": "MoveElements",
          "priority": 1,
          "origin_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "destination_id": "1b9476c4-80ad-4a89-b761-e3d87f721dad",
          "to_move": [
            "9871984f-3125-4218-8707-87a903caeeb1",
            "cad7444a-4eb2-4166-af74-79a2edc39405",
            "a82b0d59-e835-4218-bc4b-cd0a2a621659",
            "888ab476-cefc-4ea4-a135-c1ccad03b3df",
            "6d20c083-1aae-44e6-af3d-98daf4f3e5c3",
            "8837cd3b-081f-4439-bb0e-d9c4d008ee6b"
          ]
        },
        {
          "name": "M.01 | Habitat Lander Descent",
          "mission_time": "1145 00:00:00",
          "type": "SpaceTransport",
          "priority": 2,
          "origin_node_id": "53c3a7c1-3d4f-4f1b-9e18-1b28dcd8aa5a",
          "destination_node_id": "9032bcfa-7457-4ff7-9c07-2d698d728778",
          "edge_id": "ada1b096-2991-470e-a0d9-6f27fc2e068d",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "be981a4b-c81e-4b44-b08d-a6a38eed6af8",
            "1b9476c4-80ad-4a89-b761-e3d87f721dad"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "1b9476c4-80ad-4a89-b761-e3d87f721dad"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "be981a4b-c81e-4b44-b08d-a6a38eed6af8"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "1b9476c4-80ad-4a89-b761-e3d87f721dad"
                }
              ]
            }
          ]
        },
        {
          "name": "M.01 | Mawrth Vallis Exploration",
          "mission_time": "1146 00:00:00",
          "type": "CrewedExploration",
          "priority": 1,
          "node": "9032bcfa-7457-4ff7-9c07-2d698d728778",
          "eva_duration": "08:00:00",
          "crew_location": "1b9476c4-80ad-4a89-b761-e3d87f721dad",
          "crew": [
            "9871984f-3125-4218-8707-87a903caeeb1",
            "cad7444a-4eb2-4166-af74-79a2edc39405",
            "a82b0d59-e835-4218-bc4b-cd0a2a621659",
            "888ab476-cefc-4ea4-a135-c1ccad03b3df",
            "6d20c083-1aae-44e6-af3d-98daf4f3e5c3",
            "8837cd3b-081f-4439-bb0e-d9c4d008ee6b"
          ],
          "duration": "531 00:00:00",
          "eva_per_week": 1
        },
        {
          "name": "M.01 | Transfer Crew to MAV",
          "mission_time": "1677 00:00:00",
          "type": "MoveElements",
          "priority": 1,
          "origin_id": "1b9476c4-80ad-4a89-b761-e3d87f721dad",
          "destination_id": "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3",
          "to_move": [
            "9871984f-3125-4218-8707-87a903caeeb1",
            "cad7444a-4eb2-4166-af74-79a2edc39405",
            "a82b0d59-e835-4218-bc4b-cd0a2a621659",
            "888ab476-cefc-4ea4-a135-c1ccad03b3df",
            "6d20c083-1aae-44e6-af3d-98daf4f3e5c3",
            "8837cd3b-081f-4439-bb0e-d9c4d008ee6b"
          ]
        },
        {
          "name": "M.01 | Create Samples",
          "mission_time": "1677",
          "type": "MakeElements",
          "priority": 2,
          "entry_point_id": "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3",
          "elements": [
            "9b395aec-8321-4670-882d-69d22695db06"
          ]
        },
        {
          "name": "M.01 | MAV Ascent",
          "mission_time": "1677 00:00:00",
          "type": "FlightTransport",
          "priority": 3,
          "origin_node_id": "9032bcfa-7457-4ff7-9c07-2d698d728778",
          "destination_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "edge_id": "d9ec7e42-7c89-461e-bdcb-d945c03d0d06",
          "exec_time": "02:00:00",
          "elements_id_list": [
            "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3"
          ]
        },
        {
          "name": "M.01 | Transfer Crew to CM",
          "mission_time": "1677 03:00:00",
          "type": "MoveElements",
          "priority": 1,
          "origin_id": "6c773d1e-2a3f-4396-bdbc-a09bd4157cb3",
          "destination_id": "1d85334f-169a-4f3f-94f4-d7fba28beb7b",
          "to_move": [
            "9871984f-3125-4218-8707-87a903caeeb1",
            "cad7444a-4eb2-4166-af74-79a2edc39405",
            "a82b0d59-e835-4218-bc4b-cd0a2a621659",
            "888ab476-cefc-4ea4-a135-c1ccad03b3df",
            "6d20c083-1aae-44e6-af3d-98daf4f3e5c3",
            "8837cd3b-081f-4439-bb0e-d9c4d008ee6b",
            "9b395aec-8321-4670-882d-69d22695db06"
          ]
        },
        {
          "name": "M.01 | TEI",
          "mission_time": "1682 00:00:00",
          "type": "SpaceTransport",
          "priority": 1,
          "origin_node_id": "5dd3e569-c900-4406-b2a8-83cc531085bb",
          "destination_node_id": "09d7dbbc-fb1c-441b-b9e6-f424458d5ddf",
          "edge_id": "11ec7971-923d-4d01-a890-e090100d95e3",
          "exec_time": "201 00:00:00",
          "elements_id_list": [
            "71a4e5a2-eed4-4c0f-993e-de36fdfeef13",
            "71a4e5a2-eed4-4c0f-993e-de36fdfeef13",
            "fff699af-df9d-4d32-b2ce-cbb6de5a47b4",
            "eefa1728-940c-46cf-97ad-c516b8a56b91",
            "f8f213a7-ae92-4e37-a01c-98c5937ff333",
            "523063ff-1202-40a4-ac35-59fd077211a5",
            "035a8cf6-902b-47cb-bfa1-752b38c8e287"
          ],
          "burnStageProfile": [
            {
              "burn_stage_sequence": [
                {
                  "burnStage": "Burn",
                  "element_id": "fff699af-df9d-4d32-b2ce-cbb6de5a47b4"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "f8f213a7-ae92-4e37-a01c-98c5937ff333"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "fff699af-df9d-4d32-b2ce-cbb6de5a47b4"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "523063ff-1202-40a4-ac35-59fd077211a5"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "eefa1728-940c-46cf-97ad-c516b8a56b91"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "035a8cf6-902b-47cb-bfa1-752b38c8e287"
                },
                {
                  "burnStage": "Stage",
                  "element_id": "71a4e5a2-eed4-4c0f-993e-de36fdfeef13"
                },
                {
                  "burnStage": "Burn",
                  "element_id": "1d85334f-169a-4f3f-94f4-d7fba28beb7b"
                }
              ]
            }
          ]
        }
      ],
      "demand_models": [],
      "origin": "9533b255-526f-4197-9319-6013ca01ec97",
      "destination": "9032bcfa-7457-4ff7-9c07-2d698d728778",
      "return_origin": "9032bcfa-7457-4ff7-9c07-2d698d728778",
      "return_destination": "09d7dbbc-fb1c-441b-b9e6-f424458d5ddf"
    }
  ],
  "manifest": {
    "container_events": []
  },
  "volumeConstrained": false,
  "environmentConstrained": false
}

const oneNodeEvents = ['MakeElements', 'MoveElements', 'RemoveElements', 'ReconfigureElements', 'ReconfigureGroup', 'ConsumeResources', 'TransferResources']

var nodeLocations = getElt('NodeIDstoUUIDs');
let ind = 0;
Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
     nodeLocations[uuid] = ind
     nodeLocations[ind] = uuid
     ind += 1
 });

console.log('node locations:', nodeLocations)
// console.log(scenario.network.nodes)

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
                lastLocation = getNodeLocation(node)
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
                    stepSize: 1,
                    min: 0,
                    callback: function(value, index, values) {
                        var nodeUUID = nodeLocations[value]
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
