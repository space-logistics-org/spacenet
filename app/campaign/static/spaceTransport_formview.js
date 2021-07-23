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

        $(container).append('<input type="text"' +'placeholder="Element ID" class="elements" id=tb' + itxtCnt + ' value="" />');

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
        itxtCnt = itxtCnt ;

        $(container).append('<input type="text"' +' placeholder="Element ID"  class="seqele" id=tb1 value="" />');
        $(container).append('<input type="text"' +' placeholder="burn/stage"  class="burnstage" class= "second" id=tb2  value="" />');

        // ADD EVERY ELEMENT TO THE MAIN CONTAINER.
        $('#burnstagemain').after(container);
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


    var burnStageStr = new Array();
    var eleList = new Array();

    $('.burnstage').each(function () {
      if (this.value != '')
          burnStageStr.push(this.value);
    });

    $('.seqele').each(function () {
      if (this.value != '')
          eleList.push(this.value);
    });

    max = eleList.length
    var burnStageProfile = [];

    for ( var i=0 ; i < max ; i++ ){
        burnStageProfile[i] = [JSON.stringify({
          element : eleList[i],
          burnStage : burnStageStr[i]
        })
      ];
    }

    message= JSON.stringify({
      name : name,
      origin_node : origin_node,
      destination_node : destination_node,
      time : time,
      priority : priority,
      elements : elementvalues,
      burnStageProfile : JSON.parse(burnStageProfile)
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
