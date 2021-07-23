
function getMessage(modalType) {
    name = $("#" + modalType + "InputName").val();
    state_type = $("#" + modalType + "DropPick").val();
    element_id = $("#" + modalType + "InputElement_ID").val();

    if ($("#" + modalType + "InitialState").prop('checked')) {
        is_initial_state = true
    } else {
        is_initial_state = false
    }

    message = JSON.stringify({
        name: name,
        state_type: state_type,
        element_id: parseInt(element_id),
        is_initial_state: is_initial_state
    });

    return message

}


function formFill(data) {
    $("#editDropPick").val(data.state_type)
    $("#editInputName").val(data.name);
    $("#editInputElement_ID").val(data.element_id);
    $("#editInitialState").prop('checked', data.is_initial_state);
}