$(document).ready(function() {
    ElementList();
});


function ElementList() {

    var count = 0; 

    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

    $('#eleAdd').click(function () {

        count = count + 1;

        $(container).append('<input type="text"' + 'placeholder="Element ID" class="elements" id=tb' + count + ' value="" />');

        $('#elementmain').after(container);
    });
}


function onComplete() {

    name = document.getElementById("inputName").value;
    origin_node = document.getElementById("inputOriginNodeID").value;
    destination_node = document.getElementById("inputDestinationNodeID").value;
    time = document.getElementById("inputTime").value;
    priority = document.getElementById("inputPriority").value;

    var elementvalues = new Array();

    $('.elements').each(function () {
        if (this.value != '')
            elementvalues.push(this.value);
    });

    var eleList = new Array();

    $('.seqele').each(function () {
      if (this.value != '')
          eleList.push(this.value);
    });

    message = JSON.stringify({
      name : name,
      origin_node : origin_node,
      destination_node : destination_node,
      time : time,
      priority : priority,
      elements : elementvalues,
    });

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
