const COLOR_MAPPINGS = {
    'CreateElements': 'green',
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
    'CreateElements': 4,
    'FlightTransport': 1,
    'CrewedExploration': 1,
    'RemoveElements': 3.5,
    'ReconfigureGroup': 3,
    'MoveElements': 5
}


var DateTime = luxon.DateTime;


const scenario = compileScenario();
console.log("scenario:", scenario)

const oneNodeEvents = ['CreateElements', 'MoveElements', 'RemoveElements', 'ReconfigureElements', 'ReconfigureGroup', 'ConsumeResources', 'TransferResources']

var nodeLocations = getElt('NodeIDstoUUIDs');
// let ind = 0;
// Object.entries(scenario.network.nodes).forEach( function([uuid, node]) {
//     nodeLocations[uuid] = ind
//     nodeLocations[ind] = uuid
//     ind += 1
// });

// console.log('node locations:', nodeLocations)
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
                evaAddedTime = parseTime(event.duration)


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

console.log("data:", data)


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
                min: 1,
                ticks: {
                    stepSize: 1,
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
