var COLUMNS = {
  'edge': [
    {data: null},
    {data: 'type'},
    {data: 'name'},
    {data: 'origin_id'},
    {data: 'destination_id'}
      ],
  'node': [
    {data: null},
    {data: 'type'},
    {data: 'name'},
    {data: 'body_1'}
      ]
}

function openTab(event, tabName) {

   var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
   for (i=0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
   tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
       tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
 event.currentTarget.className += " active";
}

//$.fn.dataTable.ext.search.push(
//    function( settings, data, dataIndex ) {
//        var body = data[3];
//        var scenarioType = $('#planet').val();
//
//        switch(scenarioType) {
//        case 'iss':
//            if (body == 'Earth') {
//                return true }
//            else { return false }
//
//        case 'lunar':
//            if ( body == 'Earth' || body == 'Moon' ) {
//                return true }
//            else { return false }
//
//        case 'moon-only':
//            if ( body == 'Moon' ) {
//                return true }
//            else { return false }
//
//        case 'martian':
//            if ( body == 'Earth' || body == 'Mars' ) {
//                return true }
//            else { return false}
//
//        case 'mars-only':
//            if ( body == 'Mars' ) {
//                return true }
//            else { return false}
//
//        case 'solar system':
//            return true
//    }
//);

$(document).ready(function () {
    var dataType = 'node'
    console.log(dataType)

    var table = $("#" + dataType + "_table").DataTable( {
      ajax: {
        url: "/database/api/" + dataType + "/",
        dataSrc: ''
      },
      columns: COLUMNS[dataType],

      columnDefs: [
      {
        targets:   0,
        searchable: false,
        orderable: false,
        defaultContent: '',
        className: 'select-checkbox',
        width: '8%',
      },
      {
        targets: 1,
        width: '20%'
      }],
      select: {
          style:    'multi',
          selector: 'td:first-child'
      },
      order: [[ 1, 'asc' ]],
      bFilter: true
    });

    table.on( 'select deselect', function ( e, dt, type, indexes ) {
      console.log("selected something")
        var num_selected = table.rows( { selected: true } ).data().length;
    } );

    $('#planet').keyup( function() {
        table.draw();
    } );

    table.columns().every( function() {
      var that = this;

      $('input', this.footer()).on('keyup change', function() {
          if (that.search() !== this.value) {
              that
                  .search(this.value)
                  .draw();
          }
      });
    });
    });

$(document).ready(function () {
    var dataType = 'edge'
    console.log(dataType)

    var table = $("#" + dataType + "_table").DataTable( {
      ajax: {
        url: "/database/api/" + dataType + "/",
        dataSrc: ''
      },
      columns: COLUMNS[dataType],

      columnDefs: [
      {
        targets:   0,
        searchable: false,
        orderable: false,
        defaultContent: '',
        className: 'select-checkbox',
        width: '8%',
      },
      {
        targets: 1,
        width: '20%'
      }],
      select: {
          style:    'multi',
          selector: 'td:first-child'
      },
      order: [[ 1, 'asc' ]],
    });

    table.on( 'select deselect', function ( e, dt, type, indexes ) {
      console.log("selected something")
        var num_selected = table.rows( { selected: true } ).data().length;
    } );


    table.columns().every( function() {
      var that = this;

      $('input', this.footer()).on('keyup change', function() {
          if (that.search() !== this.value) {
              that
                  .search(this.value)
                  .draw();
          }
      });
    });
    });