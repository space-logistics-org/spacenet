function deleteMission() {
    window.localStorage.removeItem('missionList')
    location.reload()
}

function fillMission() {
    // $('#addMissionButton').hide()
    $('#deleteMissionButton').hide()

    var currentMission = JSON.parse(window.localStorage.getItem('missionList'))
    console.log('current mission:', currentMission)
    if (currentMission) {
        $('#pickStartDate').val(currentMission[0].start_date)
        $('#inputName').val(currentMission[0].name)
        $('#pickOrigin').val(currentMission[0].origin)
        $('#pickDest').val(currentMission[0].destination)
        $('#pickReturnOrigin').val(currentMission[0].return_origin)
        $('#pickReturnDest').val(currentMission[0].return_destination)
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


    missionList = [{
      start_date: startDate,
      name: name,
      origin: origin,
      destination: dest,
      return_origin: return_origin,
      return_destination: return_dest
    }]

    window.localStorage.setItem('missionList', JSON.stringify(missionList))
    alert('mission created! Now add events.')

    document.getElementById('createMission').reset()
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