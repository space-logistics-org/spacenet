name = "";
originID = null;
destID = null;
elArray = [];


function onComplete(){

  name = $("#inputName").val();
  originID = $("#inputOriginID").val();
  destID = $("#inputDestinationID").val();
  elArray = $("#moveElement").val();
  $('#moveElementTable').append('<tr><td>' + name + '</td><td>' + destID + '</td><td>' + originID + '</td><td>' + elArray + '</td></tr>');
  document.getElementById("moveElements").reset();


    data = {
      name: name,
      node: node,
      time: time,
      priority: priority,
      origin_id: origin_id,
      destination_id: destination_id,
      to_transfer: to_transfer
    }

    console.log(data)
    location.reload()

}
