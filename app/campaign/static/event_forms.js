const scenario = compileScenario();

function populateNodes() {
    var nodes = getElt('scenarioNetworkNodes')
    Object.entries(nodes).forEach( function([uuid, node]) {
        $('#pickNode').append('<option value=' + uuid + '>' + node.name + '</option>')
      });
}


function findEltContents(uuid, simResult) {
    var contents;
    simResult.result.elements.forEach( function (elt) {
        if (elt.inner === uuid) {
            contents = elt.contents
        }
    })
    return contents
}

function findNodeContents(uuid, simResult) {
    var contents;
    simResult.result.nodes.forEach( function (node) {
        if (node.inner === uuid) {
            contents = node.contents
        }
    })
    return contents
}

function getAllContents (initialContents, simResult) {
	var finalContents = initialContents
	if (!initialContents) {
		return
	}
	else {
		initialContents.forEach( function(elt) {
			finalContents = [...finalContents, ...(getAllContents(findEltContents(elt, simResult), simResult))]
		})
		return finalContents
	}
}

function createTree(simResult, startingNodeUUID) {
    var namespace = simResult.result.namespace

    function makeTreeObj (UUID, contents) {
        if (contents === []) {
            return {
                "text": namespace[UUID].inner.name,
                "id": UUID
            }
        } else {

            var children = []
            contents.forEach( function (elt) {
                children.push(makeTreeObj(elt, findEltContents(elt, simResult)))
            })
            var treeObj = {
                "text": namespace[UUID].inner.name,
                "id": UUID,
                "children": children  
            }

            return treeObj
        }
    }

    var startingNodeContents = findNodeContents(startingNodeUUID, simResult)
    var data = []

    startingNodeContents.forEach( function (elt) {
        data.push(makeTreeObj(elt, findEltContents(elt, simResult)))
    })

    $('#elementsTree').jstree({
        "core" : {
            'data': data,
            "themes":{
                'name': 'proton',
                'responsive': true,
                'icons': false
            }
        },
        "plugins" : [
          "checkbox",
          "state", "wholerow"
        ],
        "checkbox": {
            'three_state': 'false'
        },
      });
    
}

function getTreeSelected () {
    return $("#elementsTree").jstree("get_checked")
}
