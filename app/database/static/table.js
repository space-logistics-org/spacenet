const COLUMNS = {
    'edge': [
        {data: null},
        {data: 'name'},
        {data: 'type'},
        {data: 'origin_id'},
        {data: 'destination_id'},
        {data: 'description'}
    ],
    'element': [
        {data: null},
        {data: 'name'},
        {data: 'type'},
        {data: 'class_of_supply'},
        {data: 'environment'},
        {data: 'accommodation_mass'},
        {data: 'mass'},
        {data: 'volume'},
        {data: 'description'}
    ],
    'node': [
        {data: null},
        {data: 'name'},
        {data: 'type'},
        {data: 'body_1'},
        {data: 'description'},
    ],
    'resource': [
        {data: null},
        {data: 'name'},
        {data: 'type'},
        {data: 'class_of_supply'},
        {data: 'units'},
        {data: 'unit_mass'},
        {data: 'unit_volume'},
        {data: 'description'},
    ],
    'state': [
        {data: null},
        {data: 'name'},
        {data: 'state_type'},
        {data: 'element_id'},
        {data: 'is_initial_state'},
    ]
};


$(document).ready(function () {
    const dataType = document.getElementsByName('dataType')[0].content;

    $('#' + dataType + '_table tfoot th').each(function () {
        if ($(this).index() !== 0) {
            const title = $(this).text();
            $(this).html('<input type="text" placeholder="Search ' + title + '" />');
        }
    });

    $.fn.dataTable.ext.buttons.delete = {
        extend: 'selected',
        text: '<span data-customTooltip="Select row(s) to delete">Delete</span>',
        className: 'btn-style',
        action: function (e, dt, node, config) {
            $('#deleteModal').modal('show');
        }
    };

    $.fn.dataTable.ext.buttons.edit = {
        extend: 'selectedSingle',
        text: '<span data-customTooltip="Select row(s) to view/edit">View/Edit</span>',
        className: 'btn-style',
        action: function (e, dt, node, config) {
            const record = table.rows({selected: true}).data();
            const data = record[0];
            formFill(data)
            $('#editModal').modal('show');
        }
    };


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


    let table = $("#" + dataType + "_table").DataTable({
        scrollX: true,
        ajax: {
            url: "/database/api/" + dataType + "/",
            dataSrc: ''
        },
        columns: COLUMNS[dataType],
        buttons: [
            'export',
            'filter',
            'delete',
            'edit'
        ],
        language: {
            searchBuilder: {
                button: {
                    0: 'Apply Filters',
                    1: 'Filters (one selected)',
                    _: 'Filters (%d)'
                },
                add: 'Add Filter',
                title: 'Apply Custom Filters',
                data: 'Property',
            }
        },
        dom: 'BQlfrtip',
        columnDefs: [
            {
                targets: 0,
                searchable: false,
                orderable: false,
                defaultContent: '',
                className: 'select-checkbox',
                width: '8%',
            }],
        select: {
            style: 'multi',
            selector: 'td:first-child'
        },
        order: [[1, 'asc']],
    });

    $('#modalDeleteButton').on('click', function () {
        const record = table.rows({selected: true}).data();
        for (i = 0; i < record.length; i++) {
            const element = record[i];
            console.log(element)
            $.ajax({
                url: "/database/api/" + dataType + "/" + element.id,
                method: "DELETE",
                success: function (data) {
                    $('#deleteModal').modal('hide');
                    table.ajax.reload();
                }
            });
        }
    });

    $('#addModal').on('hide.bs.modal', function () {
        $('#addModal #addType').trigger('reset');
        $('#addModal #addComponents').trigger('reset');
        $("#addModal :input").show();
    })

    $('#editModal').on('hide.bs.modal', function () {
        $('#editModal #type').trigger('reset');
        $('#editModal #components').trigger('reset');
        $("#editModal :input").show();
    })

    table.on('select deselect hide.bs.modal', function (e, dt, type, indexes) {
        const num_selected = table.rows({selected: true}).data().length;
        if (num_selected === 0) {
            dt.buttons([2]).text('<span data-customTooltip="Select row(s) to delete">Delete</span>')
            dt.buttons([3]).text('<span data-customTooltip="Select 1 row to view/edit">Edit</span>')
        } else if (num_selected === 1) {
            dt.buttons([2]).text('Delete Row')
            dt.buttons([3]).text('View/Edit row')
        } else {
            dt.buttons([2]).text('Delete ' + num_selected + ' Rows')
            dt.buttons([3]).text('<span data-customTooltip="Select 1 row to view/edit">View/Edit</span>')
        }
    });

    $('#updateButton').on('click', function () {
        message = getMessage('edit')
        console.log(message)
        const record = table.rows({selected: true}).data();
        const data = record[0];
        $.ajax({
            url: "/database/api/" + dataType + "/" + data.id,
            method: "PATCH",
            contentType: 'application/json; charset=utf-8',
            dataType: "json",
            data: message,
            success: function (data) {
                $('#editModal').modal('hide');
                table.ajax.reload();
            }
        });
    })

    $('#addButton').on('click', function () {
        message = getMessage('add')
        console.log(message)
        $.ajax({
            url: "/database/api/" + dataType + "/",
            data: message,
            contentType: 'application/json; charset=utf-8',
            dataType: "json",
            method: "POST",
            success: function () {
                $('#addModal').modal('hide');
                table.ajax.reload()
            }
        });
    })


    table.columns().every(function () {
        const that = this;

        $('input', this.footer()).on('keyup change', function () {
            if (that.search() !== this.value) {
                that
                    .search(this.value)
                    .draw();
            }
        });
    });
});