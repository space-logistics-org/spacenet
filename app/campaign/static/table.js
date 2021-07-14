var COLUMNS = {
  'edge': [
    {data: null},
    { data: 'name' },
    { data: 'type' },
    { data: 'origin_id' },
    { data: 'destination_id' },
    { data: 'description' }
      ],
  'element': [
    {data: null},
    { data: 'name' },
    { data: 'type' },
    { data: 'class_of_supply' },
    { data: 'environment' },
    { data: 'accommodation_mass' },
    { data: 'mass' },
    { data: 'volume' },
    { data: 'description' }
      ],
  'node': [
    {data: null},
    { data: 'name' },
    { data: 'type' },
    { data: 'body_1' },
    { data: 'description' },
      ],
  'resource': [
    {data: null},
    { data: 'name' },
    { data: 'type' },
    { data: 'class_of_supply' },
    { data: 'units' },
    { data: 'unit_mass' },
    { data: 'unit_volume' },
    { data: 'description' },
      ],
    'mission': [
      {data: null},
      {data: 'name'},
      {data: 'date'},
      {data: '#'}
    ]
}





$(document).ready(function () {
    var dataType = document.getElementsByName('dataType')[0].content
    console.log(dataType)

    $('#' + dataType + '_table tfoot th').each(function() {
      if ($(this).index() !== 0) {
        var title = $(this).text();
        $(this).html('<input type="text" placeholder="Search ' + title + '" />');
      }
    });

    $.fn.dataTable.ext.buttons.edit = {
      extend: 'selected',
      text: 'Edit',
      className: 'btn-style',
    }

    $.fn.dataTable.ext.buttons.delete = {
        extend: 'selected',
        text: '<span data-customTooltip="Select row(s) to delete">Delete</span>',
        className: 'btn-style',
        action: function ( e, dt, node, config ) {
          $('#deleteModal').modal('show');
        }
    };
    
    $.fn.dataTable.ext.buttons.copy = {
      extend: 'selected',
      text: 'Copy',
      className: 'btn-style',
    }

    $.fn.dataTable.ext.buttons.export = {
      extend: 'excel',
      text: 'Export',
      className: 'btn-style',
    }

    $.fn.dataTable.ext.buttons.filter = {
      extend: 'searchBuilder',
      text: 'Apply Filter',
      className: 'btn-style',
    }

    var table = $("#" + dataType + "_table").DataTable( {
      scrollX: true,
      ajax: {
        url: "../../database/api/" + dataType + "/",
        dataSrc: ''
      },
      columns: COLUMNS[dataType],
      buttons: [
          'export',
          'filter',
          'edit',
          'copy',
          'delete',
      ],
      language: {
        /*searchBuilder: {
          button: {
                0: 'Apply Filters',
                1: 'Filters (one selected)',
                _: 'Filters (%d)'
            },
          add: 'Add Filter',
          title: 'Apply Custom Filters',
          data: 'Property',
        }*/
    },
      dom: 'BQlfrtip',
      columnDefs: [ 
      {
        targets:   0,
        searchable: false,
        orderable: false,
        defaultContent: '',
        className: 'select-checkbox',
        width: '8%',
      }],
      select: {
          style:    'multi',
          selector: 'td:first-child'
      },
      order: [[ 1, 'asc' ]],
    });



   $('#modalDeleteButton').on('click', function () {
        var record = table.rows( { selected: true } ).data();
        console.log(record);
        console.log(record.length);
        for (i=0; i < record.length; i++) {
          var element = record[i]
          console.log(element)
          $.ajax({
              url: "../database/api/" + dataType + "/" + element.id,
              method: "DELETE",
              success: function(data) {
                $('#deleteModal').modal('hide');
                location.reload();
            }
          });
        }
    });

    table.on( 'select deselect', function ( e, dt, type, indexes ) {
      console.log("selected something")
        var num_selected = table.rows( { selected: true } ).data().length;
        if (num_selected === 0) {
          dt.buttons([2]).text('<span data-customTooltip="Select row(s) to delete">Delete</span>')
          // dt.buttons([3]).text('<span data-customTooltip="Select 1 row to edit">Edit</span>')
        } else if (num_selected === 1) {
          dt.buttons([2]).text('Delete Row')
          // dt.buttons([3]).text('Edit row')
        }
        else {
          dt.buttons([2]).text('Delete ' + num_selected + ' Rows')
          // dt.buttons([3]).text('<span data-customTooltip="Select 1 row to edit">Edit</span>')
        }
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

