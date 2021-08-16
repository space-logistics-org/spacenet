var getSelected;
var populateRows;
var clearTable;
$(document).ready(function () {
    const dataType = document.getElementsByName('dataType')[0].content;

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
            },
            {
                targets: 9,
                visible: false
            }
        ],
        select: {
            style: 'multi',
            selector: 'td:first-child'
        },
        order: [[1, 'asc']],
    });

    addRow = function(uuid, elt) {
        var eltRow = [
            null,
            elt.name,
            elt.type,
            elt.class_of_supply,
            elt.environment,
            elt.accommodation_mass,
            elt.mass,
            elt.volume,
            elt.description,
            uuid
        ]
        table.row.add(eltRow).draw()
    }

    clearTable = function() {
        table.rows().remove().draw()
    }


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
            selectedElts.push(record[i][9])
        }
        return selectedElts
    }
});

