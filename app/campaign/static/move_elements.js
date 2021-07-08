entry_id = 0;
el_list = [];


function onComplete(){

    entry_id = document.getElementById("inputEntryID").value;
    el_list = document.getElementById("inputElementID").value.split(',');

    message = JSON.stringify({
      element_id: el_list,
      entry_point_id : entry_ID
    })


  console.log(message)
  $.ajax({
    url: "/database/api/edge/",
    data: message,
    contentType: 'application/json; charset=utf-8',
    dataType: "json",
    method: "POST",
    success: function() {
      location.reload()
    }
  });


}
