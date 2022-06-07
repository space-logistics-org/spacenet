const COLUMNS = {
    'edge': [
        {data: null},
        {data: 'type'},
        {data: 'name'},
        {data: 'origin_id'},
        {data: 'destination_id'}
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
        {data: 'type'},
        {data: 'name'},
        {data: 'body_1'},
        // {data: 'description'},
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

var getSelected;

function buildTable(dataType) {
    console.log(dataType)

    $('#' + dataType + '_table tfoot th').each(function () {
        if ($(this).index() !== 0) {
            const title = $(this).text();
            $(this).html('<input type="text" placeholder="Search ' + title + '" />');
        }
    });


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
            'filter'
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
        dom: 'Btip',
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

    getSelected = function () {
        const record = table.rows({selected: true}).data();
        let selectedElts = []
        for (i=0; i<record.length; i++) {
            selectedElts.push(record[i])
        }
        return selectedElts
    }
}
