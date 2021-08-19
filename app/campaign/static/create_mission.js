function deleteMission() {
    window.localStorage.removeItem('missionInfo')
    window.localStorage.removeItem('missionList')
    location.reload()
}

function fillMission() {
    $('#deleteMissionButton').hide()

    var currentMission = getElt('missionInfo')
    console.log('current mission:', currentMission)

    if (currentMission) {
        $('#pickStartDate').val(currentMission.start_date)
        $('#inputName').val(currentMission.name)
        $('#pickOrigin').val(currentMission.origin)
        $('#pickDest').val(currentMission.destination)
        $('#pickReturnOrigin').val(currentMission.return_origin)
        $('#pickReturnDest').val(currentMission.return_destination)
        $('#submitButton').hide()
        // $('#editScenarioButton').show()
        $('#deleteMissionButton').show()

    }
}


function onComplete(){

  var startDate = $('#pickStartDate').val(),
	name = $('#inputName').val(),
	origin = $('#pickOrigin').val(),
  dest = $('#pickDest').val()
  return_origin = $('#pickReturnOrigin').val(),
  return_dest = $('#pickReturnDest').val()


    missionInfo = {
      start_date: startDate,
      name: name,
      origin: origin,
      destination: dest,
      return_origin: return_origin,
      return_destination: return_dest
    }

    setElt('missionInfo', missionInfo)

    document.getElementById('createMission').reset()
    alert("Mission created. Add events next.")
    fillMission()

}

function populateNodes() {
  var nodes = JSON.parse(window.localStorage.getItem('scenarioNetworkNodes'))

  Object.entries(nodes).forEach( function([uuid, node]) {
    $('#pickOrigin').append('<option value="' + uuid + '">' + node.name + '</option>')
    $('#pickDest').append('<option value="' + uuid + '">' + node.name + '</option>')
    $('#pickReturnOrigin').append('<option value="' + uuid + '">' + node.name + '</option>')
    $('#pickReturnDest').append('<option value="' + uuid + '">' + node.name + '</option>')

  })

  fillMission()
}