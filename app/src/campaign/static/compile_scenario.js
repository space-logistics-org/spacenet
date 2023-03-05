function setElt (itemName, obj) {
    window.localStorage.setItem(itemName, JSON.stringify(obj))
}

function addEvent (eventJSON) {
    var events = getElt('scenarioEvents')
    events.push(eventJSON)
    setElt('scenarioEvents', events)
}

function getElt (itemName) {
    if (window.localStorage.getItem(itemName)) {
        return JSON.parse(window.localStorage.getItem(itemName))
    } else if (itemName === 'scenarioEvents' || itemName === 'scenarioDemandModels') {
        return []
    } else {
        return null
    }
}

function compileScenario() {
    var scenarioInfo = getElt('scenarioInfo')
    var missionInfo = getElt('missionInfo')

    if (!scenarioInfo) {
        return null
    } else if (!missionInfo) {
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
            missionList: [],
            manifest: {
                container_events: []
            },
            volumeConstrained: scenarioInfo.volumeConstrained,
            environmentConstrained: scenarioInfo.environmentConstrained
        }
    }
    else {
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
}