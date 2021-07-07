const COLOR_MAPPINGS = {
    'Create Elements': 'green',
    'Flight Transport': 'yellow',
    'Crewed Exploration': 'blue',
    'Remove Elements': 'black',
    'Reconfigure Group': 'orange',
    'Move Elements': 'orange'
}

const POINT_SIZES = {
    'Create Elements': 3,
    'Flight Transport': 1,
    'Crewed Exploration': 1,
    'Remove Elements': 3.5,
    'Reconfigure Group': 4,
    'Move Elements': 4.5
}
var DateTime = luxon.DateTime;


function parseMission(mission) {
    var nodeNames = {};
    var startDate = DateTime.fromSQL(mission.startDate);
    var datasets = [];
    var total_time = 0;
    mission.events.forEach(function (item) {
        //create a separate dataset for each event
        var dataset = {
            label: item.name,
            borderColor: COLOR_MAPPINGS[item.name],
            backgroundColor: COLOR_MAPPINGS[item.name],
        }

        if (item.node) {
            //if event occurs in only one node
            nodeNames[item.node.id] = item.node.name
            var info = [{
                x: startDate.plus({days: total_time}),
                y: item.node.id
            }]
            dataset.pointRadius = POINT_SIZES[item.name]
        } else if (item.edge) {
            //if event occurs in two nodes connected by an edge
            nodeNames[item.edge.origin_node.id] = item.edge.origin_node.name
            nodeNames[item.edge.destination_node.id] = item.edge.destination_node.name
            
            var info = [{
                x: startDate.plus({days: total_time}),
                y: item.edge.origin_node.id
            }, {
                x: startDate.plus({days: total_time + item.edge.duration}),
                y: item.edge.destination_node.id
            }
            ]
            total_time += item.edge.duration
        }
        dataset.data = info
        datasets.push(dataset)
    });
    return [nodeNames, datasets]
}