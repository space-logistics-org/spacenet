
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
      {data: 'type'},
      {data: 'name'},
      {data: 'class_of_supply'},
      {data: 'environment'},
      {data: 'accommodation_mass'},
      {data: 'mass'},
      {data: 'volume'},
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
      {data: 'type'},
      {data: 'name'},
      {data: 'class_of_supply'},
      {data: 'units'},
      {data: 'unit_mass'},
      {data: 'unit_volume'},
  ],
  'state': [
      {data: null},
      {data: 'name'},
      {data: 'state_type'},
      {data: 'element_id'},
      {data: 'is_initial_state'},
  ]
};

const genUUID = uuid.v4



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

  return table
}


function getSelected (table) {
  const record = table.rows({selected: true}).data();
  let selectedElts = []
  for (i=0; i<record.length; i++) {
      selectedElts.push(record[i])
  }
  return selectedElts
}

function addUUIDS (elts) {
  var withUUIDs = {}
  elts.forEach( function (elt) {
    withUUIDs[genUUID()] = elt
  })
  return withUUIDs
}

var edgeTable;
var nodeTable;
$(document).ready( function() {
  edgeTable = buildTable('edge')
  nodeTable = buildTable('node')
  elementTable = buildTable('element')
  resourceTable = buildTable('resource')
  showNodeTable()
})

function submitNodes() {
  var nodes = addUUIDS(getSelected(nodeTable))
  var IDstoUUIDs = {}
  Object.entries(nodes).forEach( function ([uuid, node]) {
    IDstoUUIDs[node.id] = uuid
    delete node.id
  })
  setElt('NodeIDstoUUIDs', IDstoUUIDs)
  setElt('scenarioNetworkNodes', nodes)
}


function submitEdges() {
  var IDstoUUIDs = getElt('NodeIDstoUUIDs')
  if (IDstoUUIDs === []) {
    alert("Please choose nodes before edges")
  } else {
    var edges = getSelected(edgeTable)
    edges.forEach( function(edge) {
      edge.origin_id = IDstoUUIDs[edge.origin_id]
      edge.destination_id = IDstoUUIDs[edge.destination_id]
      delete edge.id
    })
    var edgeUUIDs = addUUIDS(edges)
    console.log(edgeUUIDs)
    setElt('scenarioNetworkEdges', edges)  
  }
}

function submitElements() {
  var elements = getSelected(elementTable)
  elements.forEach(function (elt) {
    delete elt.id
  })
  var elementUUIDs = addUUIDS(elements)
  console.log(elementUUIDs)
  setElt('scenarioElementsList', elementUUIDs)
}

function submitResources() {
  var resources = getSelected(resourceTable)
  resources.forEach(function (resource) {
    delete resource.id
  })
  var resourceUUIDs = addUUIDS(resources)
  console.log(resourceUUIDs)
  setElt('scenarioResourceTypes', resourceUUIDs)
}

function showNodeTable() {
  $('#Node').show()
  $('#Edge').hide()
  $('#Element').hide()
  $('#Resource').hide()
  nodeTable.columns.adjust().draw()
}

function showEdgeTable() {
  $('#Node').hide()
  $('#Edge').show()
  $('#Element').hide()
  $('#Resource').hide()
  edgeTable.columns.adjust().draw()

}

function showElementTable() {
  $('#Node').hide()
  $('#Edge').hide()
  $('#Element').show()
  $('#Resource').hide()
  elementTable.columns.adjust().draw()

}

function showResourceTable() {
  $('#Node').hide()
  $('#Edge').hide()
  $('#Element').hide()
  $('#Resource').show()
  resourceTable.columns.adjust().draw()

}

