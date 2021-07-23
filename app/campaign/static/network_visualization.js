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
    if (scenarioType === 'iss') {
      return {'Earth': {
                'proj': drawBody(.6, 600, 120, 'earth_equal_area.jpg'),
                'rad': 180,
                'center': {'x': 780, 'y': 300}
                }
            }
  } else if (scenarioType === 'moon-only') {
      return {'Moon': {
                'proj': drawBody(.6, 600, 120, 'moon_equal_area.jpg'),
                'rad': 180,
                'center': {'x': 780, 'y': 300}
              }
            }
  } else if (scenarioType === 'mars-only') {
    return {'Mars': {
              'proj': drawBody(.6, 600, 120, 'mars_equal_area.jpg'),
              'rad': 180,
              'center': {'x': 780, 'y': 300}
              }
          }
  } else if (scenarioType === 'lunar') {
    return {'Earth': {
              'proj': drawBody(0.6, 400, 120, 'earth_equal_area.jpg'),
              'rad': 180,
              'center': {'x': 580, 'y': 300}
              },
            'Moon': {
              'proj': drawBody(0.3, 900, 210, 'moon_equal_area.jpg'),
              'rad': 90,
              'center': {'x': 990, 'y': 300}
              }
          }
  } else if (scenarioType === 'martian') {
    return {'Earth': {
              'proj': drawBody(0.6, 400, 120, 'earth_equal_area.jpg'),
              'rad': 180,
              'center': {'x': 580, 'y': 300}
              },
            'Mars': {
              'proj': drawBody(0.3, 900, 210, 'mars_equal_area.jpg'),
              'rad': 90,
              'center': {'x': 990, 'y': 300}
              }
          }
  } else if (scenarioType === 'solarSystem') {
    return {'Earth': {
              'proj': drawBody(0.6, 350, 120, 'earth_equal_area.jpg'),
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
    if (scenarioType === 'iss') {
      return {'Earth': {
                'proj': drawBody(.8, 360, 60, 'earth_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 600, 'y': 300}
                }
            }
  } else if (scenarioType === 'moon-only') {
      return {'Moon': {
                'proj': drawBody(.8, 360, 60, 'moon_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 600, 'y': 300}
                }
            }
  } else if (scenarioType === 'mars-only') {
      return {'Mars': {
                'proj': drawBody(.8, 360, 60, 'mars_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 600, 'y': 300}
                }
            }
  } else if (scenarioType === 'lunar') {
      return {'Earth': {
                'proj': drawBody(0.8, 100, 60, 'earth_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 340, 'y': 300}
                },
              'Moon': {
                'proj': drawBody(0.4, 800, 180, 'moon_equal_area.jpg'),
                'rad': 120,
                'center': {'x': 920, 'y': 300}
                }
            }
  } else if (scenarioType === 'martian') {
      return {'Earth': {
                'proj': drawBody(0.8, 100, 60, 'earth_equal_area.jpg'),
                'rad': 240,
                'center': {'x': 340, 'y': 300}
                },
              'Mars': {
                'proj': drawBody(0.4, 800, 180, 'mars_equal_area.jpg'),
                'rad': 120,
                'center': {'x': 920, 'y': 300}
                }
            }
  } else if (scenarioType === 'solarSystem') {
    drawSun()
    return {'Earth': {
        'proj': drawBody(0.6, 350, 120, 'earth_equal_area.jpg'),
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

const network = {
    nodes: [
        {
          "name": "KSC",
          "description": "Kennedy Space Center",
          "body_1": "Earth",
          "latitude": 28.6,
          "longitude": -80.6,
          "type": "Surface",
          "id": 1
        },
        {
          "name": "PAC",
          "description": "Pacific Ocean Splashdown",
          "body_1": "Earth",
          "latitude": 35,
          "longitude": -117.9,
          "type": "Surface",
          "id": 2
        },
        {
          "name": "LSP",
          "description": "Lunar South Pole",
          "body_1": "Moon",
          "latitude": -89.9,
          "longitude": -180,
          "type": "Surface",
          "id": 3
        },
        {
          "name": "LEO",
          "description": "Low Earth Orbit",
          "body_1": "Earth",
          "apoapsis": 296,
          "periapsis": 296,
          "inclination": 28.5,
          "type": "Orbital",
          "id": 4
        },
        {
          "name": "LLPO",
          "description": "Low Lunar Polar Orbit",
          "body_1": "Moon",
          "apoapsis": 100,
          "periapsis": 100,
          "inclination": 89,
          "type": "Orbital",
          "id": 5
        },
        // {
        //     "name": "Mars place",
        //     "description": "Kennedy Space Center",
        //     "body_1": "Mars",
        //     "latitude": 28.6,
        //     "longitude": -80.6,
        //     "type": "Surface"
        //   },
        // {
        //   "name": "lagrange 1",
        //   "description": "Low Lunar Polar Orbit",
        //   "body_1": "Earth",
        //   "body_2": "Sun",
        //   "type": "Lagrange",
        //   "lp_number": 1
        // },
        // {
        //   "name": "lagrange 2",
        //   "description": "Low Lunar Polar Orbit",
        //   "body_1": "Earth",
        //   "body_2": "Sun",
        //   "type": "Lagrange",
        //   "lp_number": 2
        // },
        // {
        //   "name": "lagrange 3",
        //   "description": "Low Lunar Polar Orbit",
        //   "body_1": "Earth",
        //   "body_2": "Sun",
        //   "type": "Lagrange",
        //   "lp_number": 3
        // },
        // {
        //   "name": "lagrange 4",
        //   "description": "Low Lunar Polar Orbit",
        //   "body_1": "Earth",
        //   "body_2": "Sun",
        //   "type": "Lagrange",
        //   "lp_number": 4
        // },
        // {
        //   "name": "lagrange 5",
        //   "description": "Low Lunar Polar Orbit",
        //   "body_1": "Earth",
        //   "body_2": "Sun",
        //   "type": "Lagrange",
        //   "lp_number": 5
        // },
      ],
    edges: [
        {
          "name": "KSC-LEO",
          "description": "Earth Ascent",
          "origin_id": 1,
          "destination_id": 4,
          "duration": 0.25,
          "type": "Space"
        },
        {
          "name": "LEO-LLPO",
          "description": "Lunar Orbit Injection",
          "origin_id": 4,
          "destination_id": 5,
          "duration": 4,
          "type": "Space"
        },
        {
          "name": "LLPO-LSP",
          "description": "Lunar Descent",
          "origin_id": 5,
          "destination_id": 3,
          "duration": 0.5,
          "type": "Space"
        },
        {
          "name": "LSP-LLPO",
          "description": "Lunar Ascent",
          "origin_id": 3,
          "destination_id": 5,
          "duration": 0.5,
          "type": "Space"
        },
        {
          "name": "LLPO-PAC",
          "description": "Trans-Earth Injection",
          "origin_id": 5,
          "destination_id": 2,
          "duration": 4,
          "type": "Space"
        }
      ]
}


function drawPoint(context, x, y, label) {
  context.beginPath()
  context.arc(x, y, 4, 0, Math.PI * 2, true)
  context.fillStyle = '#ff0000'
  context.fill();
  context.font = "14px Arial";
  context.fillText(label, x, y + 20) 
}



function drawSurfaceNode(context, node, projFuncs) {
    proj = projFuncs[node.body_1].proj
    coord = [node.longitude, node.latitude]
    pt = proj(coord)
    drawPoint(context, pt[0], pt[1], node.name)
    return {'x': pt[0], 'y': pt[1]}  
}

function drawOrbitalNode(context, node, projFuncs) {
  RAW_KM_TO_PIXELS = 5
  rad = projFuncs[node.body_1].rad
  angle = node.inclination * Math.PI/180
  avg_dist = ((node.apoapsis + node.periapsis)/2)/RAW_KM_TO_PIXELS

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





function drawStraightEdge(context, edge, nodesByID) {
  origin = nodesByID[edge.origin_id].canvasPt
  dest = nodesByID[edge.destination_id].canvasPt
  
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

function drawCurvedEdge(context, edge, nodesByID) {
  origin = nodesByID[edge.origin_id].canvasPt
  dest = nodesByID[edge.destination_id].canvasPt

  if (Math.abs(origin.y - dest.y) < 30) {
    slope = 0
  } else if (Math.abs(origin.x - dest.x) < 30) {
    slope = 0
  } else if (origin.y < dest.y) {
    slope = origin.y/dest.y
  } else {
    slope = dest.y/origin.y
  }

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
  const nodesByID = {}

  network.nodes.forEach( function (node) {
    if (node.type === 'Surface') {
      node['canvasPt'] = drawSurfaceNode(nCtx, node, projFuncs)
    } else if (node.type === 'Orbital') {
      node['canvasPt'] = drawOrbitalNode(nCtx, node, projFuncs)
    } else {
      node['canvasPt'] = drawLagrangeNode(nCtx, node, projFuncs)
    }
    nodesByID[node.id] = node
  })

  network.edges.forEach( function(edge) {
    if (edge.type === 'Surface') {
      drawStraightEdge(nCtx, edge, nodesByID)
    } else {
      drawCurvedEdge(nCtx, edge, nodesByID)
    }
  })

}


setUpBackground()
$("#pickScenarioType").val('lunar').trigger('change')
