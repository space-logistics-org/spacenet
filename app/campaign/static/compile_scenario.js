
function addEvent (eventJSON) {
    var events = getElt('scenarioEvents')
    if (events) {
        events.push(eventJSON)
    } else {
        var events = [eventJSON]
    }
    window.localStorage.setItem('scenarioEvents', JSON.stringify(events))
}

function getElt (itemName) {
    if (window.localStorage.getItem(itemName)) {
        return JSON.parse(window.localStorage.getItem(itemName))
    } else {
        return []
    }
}

function compileScenario() {
    var scenarioInfo = getElt('scenarioInfo')
    var missionInfo = getElt('missionList')[0]
    console.log(missionInfo)
    return {
        name: scenarioInfo.name,
        description: scenarioInfo.description,
        startDate: scenarioInfo.startDate,
        scenarioType: scenarioInfo.scenarioType,
        network: {
            nodes: getElt('scenarioNetworkNodes'),
            edges: getElt('scenarioNetworkEdges')
        },
        resourceTypes: getElt('scenarioResourceTypes'),
        elementList: getElt('scenarioElementsList'),
        missionList: [
            {
                name: missionInfo.name,
                start_date: missionInfo.start_date,
                events: getElt('scenarioEvents'),
                demand_models: getElt('scenarioDemandModels'),
                origin: missionInfo.origin,
                destination: missionInfo.destination,
                return_origin: missionInfo.return_origin,
                return_destination: missionInfo.return_destination
            }
        ],
        manifest: {
            container_events: []
        },
        volumeConstrained: scenarioInfo.volumeConstrained,
        environmentConstrained: scenarioInfo.environmentConstrained
    }
}