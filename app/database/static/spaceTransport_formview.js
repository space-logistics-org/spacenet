//assign classes to the formfield or packaage them inside a different div

name = "";
origin_id = 0;
dest_id = 0;
dur = 0;
dist = 0;
max_crew = 0;
max_cargo = 0;
desc = "";

$(document).ready(function () {
    BindControls();
});

function BindControls() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO SERVE A CONTAINER TO THE ELEMENTS.
    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

        // CREATE THE ELEMENTS.
    $('#btAdd').click(function () {
        itxtCnt = itxtCnt + 1;

        $(container).append('<input type="text"' +'placeholder="Field Name" class="input" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#main').after(container);
    });
}

var values = new Array();

function onComplete() {
    $('.input').each(function () {
        if (this.value != '')
            values.push(this.value);
    });

    if (values != '') {
      console.log(message)
      $.ajax({
        url: "/database/api/edge/",
        data: message,
        contentType: 'application/json; charset=utf-8',
        dataType: "json",
        method: "POST",
        success: function() {
          document.getElementById("edge").reset()
          document.getElementById("components").reset()
          location.href = 'edge_table.html'
        }
      });
    }
    else { alert("Fields cannot be empty.") }
}


// function onComplete(){
//
//       name = document.getElementById("inputName").value;
//       type = document.getElementById("dropPick").value;
//       origin_id = document.getElementById("inputOrigin_ID").value;
//       dest_id = document.getElementById("inputDestination_ID").value;
//       dur = document.getElementById("inputDuration").value;
//       dist = document.getElementById("inputDistance").value;
//       max_crew = document.getElementById("inputMax_Crew").value;
//       max_cargo = document.getElementById("inputMax_Cargo").value;
//       desc = document.getElementById("inputDescription").value;
//
//     switch(type){
//
//       case "Flight":{
//           message = JSON.stringify({
//           type : "Flight",
//           name : name,
//           origin_id :  parseInt(origin_id),
//           destination_id : parseInt(dest_id),
//           duration : parseInt(dur),
//           max_crew : parseInt(max_crew),
//           max_cargo : parseInt(max_cargo),
//           description : desc,
//           });
//           break;
//         }
//       case "Space":{
//         message = JSON.stringify({
//           type : "Space",
//           name : name,
//           origin_id :  parseInt(origin_id),
//           destination_id : parseInt(dest_id),
//           duration : parseInt(dur),
//           description : desc,
//       });
//       break;
//     }
//       case "Surface":{
//         message = JSON.stringify({
//           type : "Surface",
//           name : name,
//           origin_id :  parseInt(origin_id),
//           destination_id : parseInt(dest_id),
//           distance : parseInt(dist),
//           description : desc,
//         });
//         break;
//     }
//   }
//
  // console.log(message)
  // $.ajax({
  //   url: "/database/api/edge/",
  //   data: message,
  //   contentType: 'application/json; charset=utf-8',
  //   dataType: "json",
  //   method: "POST",
  //   success: function() {
  //     document.getElementById("edge").reset()
  //     document.getElementById("components").reset()
  //     location.href = 'edge_table.html'
  //   }
  // });
//
//
// }
