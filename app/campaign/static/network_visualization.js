function checkFilledInfo() {
  var nodes = getElt('scenarioNetworkNodes'),
      edges = getElt('scenarioNetworkEdges');
  console.log(nodes)
  console.log(edges)

  if (!nodes || !edges) {
      $('#noNetworkModal').modal('show')
    }

}

// select the body canvas element created in the html.
const bCanvas = document.getElementById('bodies');

const bCtx = bCanvas.getContext('2d');


function setUpBackground () {
    bCtx.fillStyle = '#000000'
    bCtx.fillRect(0, 0, bCanvas.width, bCanvas.height);

};

function drawBody (scale, x, y, url) {
    RAW_WIDTH = 600
    RAW_HEIGHT = 600
    RAW_PROJ_SCALE = 150


    const planetImg = document.createElement('img');

    planetImg.onload = function() {
        bCtx.drawImage(planetImg, x, y, scale*RAW_WIDTH, scale*RAW_HEIGHT)
    }
    planetImg.src = url



    const projection = d3.geoAzimuthalEqualArea()
        .scale(RAW_PROJ_SCALE * scale)
        .translate([x + scale*RAW_WIDTH/2, y + scale*RAW_HEIGHT/2]);

    return projection
}


function drawOutline(proj) {
    // geographic path generator for given projection and canvas context
    const pathGenerator = d3.geoPath(proj, bCtx);


    // Load external data and boot
    d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson", function(data){

        // initialize the path
        bCtx.beginPath();

        // Got the positions of the path
        pathGenerator(data);

        // // Fill the paths
        // ctx.fillStyle = "#999";
        // ctx.fill();

        // Add stroke
        bCtx.strokeStyle = "#69b3a2";
        bCtx.stroke()

    })

}

function drawSun() {
    const sunImg = document.createElement('img');
    let w = bCanvas.width
    let h = bCanvas.height

    sunImg.onload = function() {
      let sunW = sunImg.width
      let sunH = sunImg.height  
      bCtx.drawImage(sunImg, 0, h/8, 3*sunW*h/(sunH*4), 3*h/4)
    }
    sunImg.src = 'sun.jpg'


}

function drawAllBodies (displaySun, scenarioType) {
  if (displaySun) {
    drawSun()
    if (scenarioType === 'ISS') {
      return {'Earth': {
                'proj': drawBody(.6, 600, 120, 'earth_equal_area.png'),
                'rad': 180,
                'center': {'x': 780, 'y': 300}
                }
            }
  } else if (scenarioType === 'Moon-only') {
      return {'Moon': {
                'proj': drawBody(.6, 600, 120, 'moon_equal_area.jpg'),
                'rad': 180,
                'center': {'x': 780, 'y': 300}
              }
            }
  } else if (scenarioType === 'Mars-only') {
    return {'Mars': {
              'proj': drawBody(.6, 600, 120, 'mars_equal_area.jpg'),
              'rad': 180,
              'center': {'x': 780, 'y': 300}
              }
          }
  } else if (scenarioType === 'Lunar') {
    return {'Earth': {
              'proj': drawBody(0.6, 400, 120, 'earth_equal_area.png'),
              'rad': 180,
              'center': {'x': 580, 'y': 300}
              },
            'Moon': {
              'proj': drawBody(0.3, 900, 210, 'moon_equal_area.jpg'),
              'rad': 90,
              'center': {'x': 990, 'y': 300}
              }
          }
  } else if (scenarioType === 'Martian') {
    return {'Earth': {
              'proj': drawBody(0.6, 400, 120, 'earth_equal_area.png'),
              'rad': 180,
              'center': {'x': 580, 'y': 300}
              },
            'Mars': {
              'proj': drawBody(0.3, 900, 210, 'mars_equal_area.jpg'),
              'rad': 90,
              'center': {'x': 990, 'y': 300}
              }
          }
  } else if (scenarioType === 'Solar System') {
    return {'Earth': {
              'proj': drawBody(0.6, 350, 120, 'earth_equal_area.png'),
              'rad': 180,
              'center': {'x': 530, 'y': 300}
              },
            'Mars': {
              'proj': drawBody(0.40, 900, 180, 'mars_equal_area.jpg'),
              'rad': 120,
              'center': {'x': 1020, 'y': 300}
              },
            'Moon': {
              'proj': drawBody(0.2, 700, 80, 'moon_equal_area.jpg'),
              'rad': 60,
              'center': {'x': 760, 'y': 140}
              }
          }
    }
  } 
  
  
  
  else {
    if (scenarioType === 'ISS') {
      return {'Earth': {
                'proj': drawBody(.8, 360, 60, 'earth_equal_area.png'),
                'rad': 240,
                'center': {'x': 600, 'y': 300}
                }
            }
  } else if (scenarioType === 'Moon-only') {
      return {'Moon': {
                'proj': drawBody(.8, 360, 60, 'moon_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 600, 'y': 300}
                }
            }
  } else if (scenarioType === 'Mars-only') {
      return {'Mars': {
                'proj': drawBody(.8, 360, 60, 'mars_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 600, 'y': 300}
                }
            }
  } else if (scenarioType === 'Lunar') {
      return {'Earth': {
                'proj': drawBody(0.8, 100, 60, 'earth_equal_area.png'),
                'rad': 240,
                'center': {'x': 340, 'y': 300}
                },
              'Moon': {
                'proj': drawBody(0.4, 800, 180, 'moon_equal_area.jpg'),
                'rad': 120,
                'center': {'x': 920, 'y': 300}
                }
            }
  } else if (scenarioType === 'Martian') {
      return {'Earth': {
                'proj': drawBody(0.8, 100, 60, 'earth_equal_area.png'),
                'rad': 240,
                'center': {'x': 340, 'y': 300}
                },
              'Mars': {
                'proj': drawBody(0.4, 800, 180, 'mars_equal_area.jpg'),
                'rad': 120,
                'center': {'x': 920, 'y': 300}
                }
            }
  } else if (scenarioType === 'Solar System') {
    drawSun()
    return {'Earth': {
        'proj': drawBody(0.6, 350, 120, 'earth_equal_area.png'),
        'rad': 180,
        'center': {'x': 530, 'y': 300}
        },
      'Mars': {
        'proj': drawBody(0.40, 900, 180, 'mars_equal_area.jpg'),
        'rad': 120,
        'center': {'x': 1020, 'y': 300}
        },
      'Moon': {
        'proj': drawBody(0.2, 700, 80, 'moon_equal_area.jpg'),
        'rad': 60,
        'center': {'x': 760, 'y': 140}
        }
    }
    }
    }
  }






// select the network canvas element created in the html.

const nCanvas = document.getElementById('network');

const nCtx = nCanvas.getContext('2d')

// const network = {
// 		"nodes": {
// 			"cb3aa87b-893c-4dbd-9acb-d1c5b7017644": {
// 				"type": "SurfaceNode",
// 				"name": "KSC",
// 				"description": "Kennedy Space Center",
// 				"body_1": "Earth",
// 				"latitude": 28.6,
// 				"longitude": -80.6
// 			},
// 			"a2e22fe6-7f6b-48d0-8049-93a7fac9069b": {
// 				"type": "OrbitalNode",
// 				"name": "LEO",
// 				"description": "Low-Earth Orbit",
// 				"body_1": "Earth",
// 				"apoapsis": 296.0,
// 				"periapsis": 296.0,
// 				"inclination": 28.5
// 			},
// 			"53fc1b8b-33c1-4b0f-b380-9436de076162": {
// 				"type": "OrbitalNode",
// 				"name": "28 km Lunar Orbit",
// 				"description": "Lunar Orbit at 28 km",
// 				"body_1": "Moon",
// 				"apoapsis": 28.0,
// 				"periapsis": 28.0,
// 				"inclination": 30
// 			},
// 			"e8eb8492-9158-488e-9265-90e98f8b5eb6": {
// 				"type": "OrbitalNode",
// 				"name": "11.5 km Lunar Orbit",
// 				"description": "Lunar orbit at 11.5 km",
// 				"body_1": "Moon",
// 				"apoapsis": 11.5,
// 				"periapsis": 11.5,
// 				"inclination": 30
// 			},
// 			"0c9814e1-3b9e-42fd-82cb-c979bca0ba6c": {
// 				"type": "SurfaceNode",
// 				"name": "Taurus-Littrow",
// 				"description": "A valley on the face of the moon",
// 				"body_1": "Moon",
// 				"latitude": 20.0,
// 				"longitude": 31.0
// 			},
// 			"f49db8a6-6cac-48f6-9d27-6276ae08faf8": {
// 				"type": "SurfaceNode",
// 				"name": "Pacific Splashdown",
// 				"description": "The pacific ocean splashdown site for Apollo 17",
// 				"body_1": "Earth",
// 				"latitude": -18.0,
// 				"longitude": -165.0
// 			}
// 		},
// 		"edges": {
// 			"0d70a94d-0c03-4f26-b807-844b12649453": {
// 				"type": "SpaceEdge",
// 				"name": "KSC-LEO",
// 				"description": "Kennedy Space Center to Low-Earth Orbit",
// 				"origin_id": "cb3aa87b-893c-4dbd-9acb-d1c5b7017644",
// 				"destination_id": "a2e22fe6-7f6b-48d0-8049-93a7fac9069b",
// 				"duration": 0.25
// 			},
// 			"710e4e69-e70c-4fc1-9216-8c8e0fb763f2": {
// 				"type": "SpaceEdge",
// 				"name": "LEO-28 km Lunar Orbit",
// 				"description": "Low-Earth Orbit to 28km lunar orbit",
// 				"origin_id": "a2e22fe6-7f6b-48d0-8049-93a7fac9069b",
// 				"destination_id": "53fc1b8b-33c1-4b0f-b380-9436de076162",
// 				"duration": 3.5
// 			},
// 			"22e72f69-8e84-4c5e-ac65-6d7d0e228f76": {
// 				"type": "SpaceEdge",
// 				"name": "28 km to 11.5 km lunar orbit",
// 				"description": "Decent from a 28 km orbit to an 11.5 km orbit",
// 				"origin_id": "53fc1b8b-33c1-4b0f-b380-9436de076162",
// 				"destination_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
// 				"duration": 0.1
// 			},
// 			"6c2f54ef-a4ba-444a-b0af-4cdd4f31aba2": {
// 				"type": "SpaceEdge",
// 				"name": "11.5 km orbit-Taurus-Littrow",
// 				"description": "Decent from lunar orbit to the surface of the moon",
// 				"origin_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
// 				"destination_id": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
// 				"duration": 0.1
// 			},
// 			"ff2715a9-c93c-4c60-870b-00e177b9c2ec": {
// 				"type": "SpaceEdge",
// 				"name": "Taurus-Littrow-11.5 km orbit",
// 				"description": "Ascent from the lunar surface to orbit",
// 				"origin_id": "0c9814e1-3b9e-42fd-82cb-c979bca0ba6c",
// 				"destination_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
// 				"duration": 0.1
// 			},
// 			"32615681-1c5e-4231-8f89-ba2c556a108c": {
// 				"type": "SpaceEdge",
// 				"name": "Lunar orbit to Pacific Splashdown",
// 				"description": "Return trip from lunar orbit to the Pacific Ocean",
// 				"origin_id": "e8eb8492-9158-488e-9265-90e98f8b5eb6",
// 				"destination_id": "f49db8a6-6cac-48f6-9d27-6276ae08faf8",
// 				"duration": 2.83
// 			}
// 		}
// }

const scenario = compileScenario()
const network = scenario.network
console.log('network:', network)



function drawPoint(context, x, y, label) {
  context.beginPath()
  context.arc(x, y, 4, 0, Math.PI * 2, true)
  context.fillStyle = '#ff0000'
  context.fill();
  context.font = "14px Arial";
  context.fillText(label, x, y - 12) 
}



function drawSurfaceNode(context, node, projFuncs) {
    proj = projFuncs[node.body_1].proj
    coord = [node.longitude, node.latitude]
    pt = proj(coord)
    drawPoint(context, pt[0], pt[1], node.name)
    return {'x': pt[0], 'y': pt[1]}  
}

function drawOrbitalNode(context, node, projFuncs) {
  RAW_KM_TO_PIXELS = 4
  rad = projFuncs[node.body_1].rad
  angle = node.inclination * Math.PI/180
  avg_dist = ((node.apoapsis + node.periapsis)/(2*RAW_KM_TO_PIXELS))

  center = projFuncs[node.body_1].center
  point = { 'x': center.x + rad + avg_dist, 'y': center.y}

  var rotatedX = Math.cos(angle) * (point.x - center.x) - Math.sin(angle) * (point.y-center.y) + center.x;
  var rotatedY = Math.sin(angle) * (point.x - center.x) + Math.cos(angle) * (point.y - center.y) + center.y;

  drawPoint(context, rotatedX, rotatedY, node.name)
  return {'x': rotatedX, 'y': rotatedY}  

}

function drawLunarOrbitalNode(context, node, projFuncs) {
  RAW_KM_TO_PIXELS = 0.5
  rad = projFuncs[node.body_1].rad
  angle = node.inclination * Math.PI/180
  avg_dist = ((node.apoapsis + node.periapsis)/(2*RAW_KM_TO_PIXELS))

  center = projFuncs[node.body_1].center
  point = { 'x': center.x + rad + avg_dist, 'y': center.y}

  var rotatedX = Math.cos(angle) * (point.x - center.x) - Math.sin(angle) * (point.y-center.y) + center.x;
  var rotatedY = Math.sin(angle) * (point.x - center.x) + Math.cos(angle) * (point.y - center.y) + center.y;

  drawPoint(context, rotatedX, rotatedY, node.name)
  return {'x': rotatedX, 'y': rotatedY}  

}

function drawLagrangeNode(context, node, projFuncs) {
  major_center = projFuncs[node.body_1].center

  if (node.body_2 === 'Sun') {
    minor_center = {'x': 0, 'y': bCanvas.height/2}
  } else {
    minor_center = projFuncs[node.body_2].center
  }

  if (node.lp_number === 1) {
    x = Math.abs(major_center.x - Math.abs(major_center.x - minor_center.x)/4)
    y = Math.abs(major_center.y - Math.abs(major_center.y - minor_center.y)/4)
    drawPoint(context, x, y, node.name)
    return {'x': x, 'y': y}  


  } else if (node.lp_number === 2) {

    x = Math.abs(major_center.x + Math.abs(major_center.x - minor_center.x)/4)
    y = Math.abs(major_center.y + Math.abs(major_center.y - minor_center.y)/4)
    drawPoint(context, x, y, node.name)
    return {'x': x, 'y': y}  


  } else if (node.lp_number === 3) {

    x = Math.abs(minor_center.x - Math.abs(major_center.x - minor_center.x))
    y = Math.abs(minor_center.y - Math.abs(major_center.y - minor_center.y))
    drawPoint(context, x, y, node.name)
    return {'x': x, 'y': y}  


  } else if (node.lp_number === 4) {

    x = Math.abs(major_center.x - Math.abs(major_center.x - minor_center.x)/2)
    y = Math.abs(major_center.y - Math.abs(major_center.x - minor_center.x)/3)
    drawPoint(context, x, y, node.name)
    return {'x': x, 'y': y}  


  } else if (node.lp_number === 5) {

    x = Math.abs(major_center.x - Math.abs(major_center.x - minor_center.x)/2)
    y = Math.abs(major_center.y + Math.abs(major_center.x - minor_center.x)/3)
    drawPoint(context, x, y, node.name)
    return {'x': x, 'y': y}  


  }
}





function drawStraightEdge(context, edge) {
  console.log(network.nodes)
  console.log(edge)
  var origin = network.nodes[edge.origin_id].canvasPt
  var dest = network.nodes[edge.destination_id].canvasPt
  
  context.strokeStyle = "#ff0000 ";
  context.beginPath()
  context.moveTo(origin.x, origin.y)
  context.lineTo(dest.x, dest.y)
  context.stroke()
}

function drawSlope(ctx, x1, y1, x2, y2, slope) {
  var dx = x2 - x1,                        // difference between points
      dy = y2 - y1,
      len = Math.sqrt(dx*dx + dy*dy),      // length of line
      angle = Math.atan2(dx, dy),          // angle + 90 deg offset (switch x/y)
      midX = x1 + dx * 0.8,                // mid point
      midY = y1 + dy * 0.8,
      sx = midX + len * slope * Math.cos(angle), // midway slope point
      sy = midY - len * slope * Math.sin(angle);

  ctx.moveTo(x1, y1);
  ctx.quadraticCurveTo(sx, sy, x2, y2);
  ctx.strokeStyle = "#ff0000 ";
  ctx.stroke()
}

function drawCurvedEdge(context, edge) {
  console.log(edge)
  console.log(network.nodes)

  var origin = network.nodes[edge.origin_id].canvasPt
  var dest = network.nodes[edge.destination_id].canvasPt

  if (Math.abs(origin.y - dest.y) < 30) {
    slope = 0
  } else if (Math.abs(origin.x - dest.x) < 30) {
    slope = 0
  } else if (origin.y < dest.y) {
    // slope = origin.y/dest.y
    slope = 0.3
  } else {
    // slope = dest.y/origin.y
    slope = 0.3
  }

  console.log(slope)

  drawSlope(context, dest.x, dest.y, origin.x, origin.y, slope)
}






function drawCanvas(){

  if ($("#displaySun").prop('checked')) {
    var displaySun = true
  } else {
    var displaySun = false
  }
  var scenarioType = $('#pickScenarioType').val()
  console.log(scenarioType)

  // preparing background of canvas
  nCtx.clearRect(0, 0, nCanvas.width, nCanvas.height)
  bCtx.clearRect(0, 0, bCanvas.width, bCanvas.height)
  setUpBackground();

  // drawing planetary bodies
  const projFuncs = drawAllBodies(displaySun, scenarioType)
  console.log(projFuncs)

  // drawing network
  // const nodesByID = {}

  Object.entries(network.nodes).forEach( function([uuid, node]) {
    if (node.type === 'SurfaceNode') {
      node['canvasPt'] = drawSurfaceNode(nCtx, node, projFuncs)
    } else if (node.type === 'OrbitalNode') {
      if (node.body_1 === 'Moon') {
        node['canvasPt'] = drawLunarOrbitalNode(nCtx, node, projFuncs)
      } else {
        node['canvasPt'] = drawOrbitalNode(nCtx, node, projFuncs)
      }
    } else {
      node['canvasPt'] = drawLagrangeNode(nCtx, node, projFuncs)
    }
    // nodesByID[node.id] = node
  })

  Object.entries(network.edges).forEach( function([uuid, edge]) {
    if (edge.type === 'SurfaceEdge') {
      drawStraightEdge(nCtx, edge)
    } else {
      drawCurvedEdge(nCtx, edge)
    }
  })

}


setUpBackground()
console.log('scenario type:', scenario.scenarioType)
$("#pickScenarioType").val(scenario.scenarioType).trigger('change')
