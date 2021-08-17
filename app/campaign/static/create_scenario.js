function deleteScenario() {
    $('#deleteModal').modal('hide');
    window.localStorage.clear()
    location.reload()
}

function fillScenario() {
    $('#editScenarioButton').hide()
    $('#deleteScenarioButton').hide()

    var currentScenario = JSON.parse(window.localStorage.getItem('scenarioInfo'))
    if (currentScenario) {
        $('#pickStartDate').val(currentScenario.startDate),
        $('#inputName').val(currentScenario.name),
        $('#inputDesc').val(currentScenario.description),
        $('#pickScenarioType').val(currentScenario.scenarioType)
        $('#pickVolumeConstrained').val(currentScenario.volumeConstrained)
        $('#pickEnvironmentConstrained').val(currentScenario.environmentConstrained)
        $('#submitButton').hide()
        $('#editScenarioButton').show()
        $('#deleteScenarioButton').show()

    }
}


function onComplete(){

  var startDate = $('#pickStartDate').val(),
	  name = $('#inputName').val(),
	  description = $('#inputDesc').val(),
    scenarioType = $('#pickScenarioType').val(),
    volumeConstrained = $('#pickVolumeConstrained').val(),
    environmentConstrained = $('#pickEnvironmentConstrained').val();


    scenario = {
		startDate: startDate,
		name: name,
		description: description,
    scenarioType: scenarioType,
    volumeConstrained: volumeConstrained,
    environmentConstrained: environmentConstrained
    }

    window.localStorage.setItem('scenarioInfo', JSON.stringify(scenario))
    alert('scenario created! Now choose your network.')

    document.getElementById('createScenario').reset()
    fillScenario()

}

function showDeleteModal() {
    $('#deleteModal').modal('show');
}