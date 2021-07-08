name = "";
origin_node = "";
destination_node = "";
time= 0;
priority = 0;


$(document).ready(function () {
    ElementList();
    BurnsStages();
});



function ElementList() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO SERVE A CONTAINER TO THE ELEMENTS.
    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

        // CREATE THE ELEMENTS.
    $('#eleAdd').click(function () {
        itxtCnt = itxtCnt + 1;

        $(container).append('<input type="text"' +'placeholder="Element" class="elements" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#elementmain').after(container);
    });
}



function BurnsStages() {

    var itxtCnt = 0;    // COUNTER TO SET ELEMENT IDs.

    // CREATE A DIV DYNAMICALLY TO SERVE A CONTAINER TO THE ELEMENTS.
    var container = $(document.createElement('div')).css({
        width: '100%',
        clear: 'both',
        'margin-top': '10px',
        'margin-bottom': '10px'
        });

        // CREATE THE ELEMENTS.
    $('#seqAdd').click(function () {
        itxtCnt = itxtCnt + 1;

        $(container).append('<input type="text"' +'placeholder="[element= element1, burnstage = burn/stage], [element = element2, burnstage = burn/stage], ..." class="burnstage" id=tb' + itxtCnt + ' value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#burnstagemain').after(container);
    });
}



function onComplete() {
    name = document.getElementById("inputName").value;
    origin_node = document.getElementById("inputOriginNode").value;
    destination_node = document.getElementById("inputDestinationNode").value;
    time = document.getElementById("inputTime").value;
    priority = document.getElementById("inputPriority").value;

    var elementvalues = new Array();
    $('.elements').each(function () {
        if (this.value != '')
            elementvalues.push(this.value);
    });

    var burnStageProfile = new Array();
    $('.burnstage').each(function () {
        if (this.value != '')
            burnStageProfile.push(this.value);
    });
    alert(burnStageProfile);
    message= JSON.stringify({
      name : name,
      origin_node : origin_node,
      destination_node : destination_node,
      time : time,
      priority : priority,
      elements : elementvalues,
      burnStageProfile : burnstagevalues
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
