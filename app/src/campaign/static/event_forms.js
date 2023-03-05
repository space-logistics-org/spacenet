const scenario = compileScenario();

function getTime () {
	function makeTwoDigits (timestring) {
		if (timestring.length < 2) {
			timestring = '0' + timestring
		}
		return timestring
    }

    var hrs = $('#hours').val()
    var mins = $('#minutes').val()
	var secs = $('#seconds').val()
    
    if (!hrs || !mins || !secs) {
        return null
    }

    var hrs = makeTwoDigits(hrs)
    var mins = makeTwoDigits(mins)
    var secs = makeTwoDigits(secs)

    return hrs + ':' + mins + ':' + secs + '.00'
}

function getSimTime () {
    var hrs = $('#hours').val()
    var mins = $('#minutes').val()
    var secs = $('#seconds').val()
    
    if (!hrs || !mins|| !secs) {
        return null
    } 
    if (parseInt(mins) > 0 || parseInt(secs) > 0) {
        return (parseInt(hrs) + 1).toString()
    }
    return (parseInt(hrs)).toString()
}

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
            'cascade': 'undetermined'
        },
      });
    
}

function nestedDropdown(simResult, startingNodeUUID, divID) {
    var namespace = simResult.result.namespace

    function makeTreeObj (UUID, contents) {
        var Obj = namespace[UUID].inner
        if (contents === []) {
            if (Obj.type === 'HumanAgent') {
                return {
                    "text": Obj.name + " (active time fraction:" + Obj.active_time_fraction + ")",
                    "id": UUID
                }
            }
            return {
                "text": Obj.name,
                "id": UUID
            }
        } else {

            var children = []
            contents.forEach( function (elt) {
                children.push(makeTreeObj(elt, findEltContents(elt, simResult)))
            })

            if (Obj.type === 'HumanAgent') {
                return {
                    "text": Obj.name + " (active time fraction:" + Obj.active_time_fraction + ")",
                    "id": UUID,
                    "children": children
                }
            }
            
            return {
                "text": Obj.name,
                "id": UUID,
                "children": children  
            }
        }
    }

    var startingNodeContents = findNodeContents(startingNodeUUID, simResult)
    var data = []

    startingNodeContents.forEach( function (elt) {
        data.push(makeTreeObj(elt, findEltContents(elt, simResult)))
    })

    function addRow(dataObj, tab) {
        $(divID).append('<label style="padding-left: ' + tab.toString() + 'px" for=' + dataObj.id + '><input type="checkbox" value=' + dataObj.id + '/>' + dataObj.text + '</label>')
        if (dataObj.children) {
            dataObj.children.forEach( function(child) {
                addRow(child, tab + 18)
            })
        }
    }

    data.forEach( function(dataObj) {
        addRow(dataObj, 10)
    })

    
    
}

function getTreeSelected () {
    return $("#elementsTree").jstree("get_checked")
}

function getChecked (checkBoxDivID) {
    var checked = []
    $(checkBoxDivID + ' input[type=checkbox]:checked').each(function() { 
      checked.push($(this).val().slice(0,-1)); 
    });
    return checked
  }
  
  var expanded = false;
  
function showCheckboxes(checkBoxDivID) {
    var checkboxes = document.getElementById(checkBoxDivID);
    if (!expanded) {
      checkboxes.style.display = "block";
      expanded = true;
    } else {
      checkboxes.style.display = "none";
      expanded = false;
    }
  }
