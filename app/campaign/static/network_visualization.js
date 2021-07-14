const PLANET_IMAGES = {
    'Sun': 'sun.jpeg',
    'Earth': 'earth.jpg',
    'Moon': 'moon_topo.jpeg',
    'Mars': 'mars_large.jpeg'
}

const RAW_SCALES = {
    'Sun': 100,
    'Earth': 80,
    'Mars': 40,
    'Moon': 20,
}

const network = {
    nodes: [
        {
          "name": "KSC",
          "description": "Kennedy Space Center",
          "body_1": "Earth",
          "latitude": 28.6,
          "longitude": -80.6,
          "type": "Surface"
        },
        {
          "name": "PAC",
          "description": "Pacific Ocean Splashdown",
          "body_1": "Earth",
          "latitude": 35,
          "longitude": -117.9,
          "type": "Surface"
        },
        {
          "name": "LSP",
          "description": "Lunar South Pole",
          "body_1": "Moon",
          "latitude": -89.9,
          "longitude": -180,
          "type": "Surface"
        },
        {
          "name": "LEO",
          "description": "Low Earth Orbit",
          "body_1": "Earth",
          "apoapsis": 296,
          "periapsis": 296,
          "inclination": 28.5,
          "type": "Orbital"
        },
        {
          "name": "LLPO",
          "description": "Low Lunar Polar Orbit",
          "body_1": "Moon",
          "apoapsis": 100,
          "periapsis": 100,
          "inclination": 90,
          "type": "Orbital"
        },
        // {
        //     "name": "Mars place",
        //     "description": "Kennedy Space Center",
        //     "body_1": "Mars",
        //     "latitude": 28.6,
        //     "longitude": -80.6,
        //     "type": "Surface"
        //   },
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

function loadMapping () {
    return d3.json('https://gist.githubusercontent.com/d3indepth/f28e1c3a99ea6d84986f35ac8646fac7/raw/c58cede8dab4673c91a3db702d50f7447b373d98/ne_110m_land.json', function(error, json) {
        if (error) return console.error(error);
        var mapping = json;
        return mapping
    })
}

var DisplaySun = true


var dstCanvas = d3.select('#bodies').node();
    
var dstContext = dstCanvas.getContext('2d');

var netCanvas = d3.select('#network').node()

var netContext = netCanvas.getContext('2d')

function setUpCanvas () {
    dstContext.fillStyle = '#000000'
    dstContext.fillRect(0, 0, dstCanvas.width, dstCanvas.height);

    if (DisplaySun) {
        var sunImg = document.createElement('img');
        sunImg.src = PLANET_IMAGES['Sun']
        console.log(sunImg)
        var w = dstCanvas.width
        var h = dstCanvas.height
        var sunW = sunImg.width
        var sunH = sunImg.height
        dstContext.drawImage(sunImg, 0, h/4, sunW*h/(sunH*2), h/2)
    }
};


function warpImage(imageURL, location, scale, nodes, mapping) {
    var planet = {type: 'Sphere'},
    rasterWarper;
    
    var dstProj = d3.geoAzimuthalEqualArea()
        .scale(scale)
        .translate(location);
    
    path = d3.geoPath().projection(dstProj).context(dstContext);
        
    var srcImg = document.createElement('img');
    srcImg.src = imageURL


    srcImg.onload = function () {
        var srcProj = d3.geoEquirectangular()
        .fitSize([srcImg.width, srcImg.height], planet);
        
        rasterWarper = d3.geoWarp()
        .srcProj(srcProj)
        .dstProj(dstProj)
        .dstContext(dstContext);

        rasterWarper(srcImg);

        dstContext.beginPath();
        dstContext.strokeStyle = 'none';
        dstContext.fillStyle = 'none';
        path(mapping);
        dstContext.closePath();
        
        dstContext.strokeStyle = '#FF0000';
        dstContext.fillStyle = '#FF0000';
        nodes.forEach(function(node) {
            node['canvasPt'] = dstProj([node.longitude, node.latitude])
        })
    }
    return nodes
}

var bodies = new Set()
var surfaceNodes = {
    'Moon': [],
    'Earth': [],
    'Mars': []
}
var lagrangeNodes = {
    'Moon': [],
    'Earth': [],
    'Mars': []
}
var orbitalNodes = {
    'Moon': [],
    'Earth': [],
    'Mars': []
}


network.nodes.forEach( function (node) {
    bodies.add(node.body_1)
    if (node.type === 'Lagrange') {
        bodies.add(node.body_2)
        lagrangeNodes[node.body_1].push(node)
    } else if (node.type === 'Surface') {
        surfaceNodes[node.body_1].push(node)
    } else {
        orbitalNodes[node.body_1].push(node)
    }
})

function drawBodies(mapping) {
    var projected_nodes = []
    if (!DisplaySun) {
        if (bodies.size === 0) {
            setUpCanvas()
        }
        
        else if (bodies.size === 1) {
            var srcImage = PLANET_IMAGES[bodies[0]]
            projected_nodes.push.apply(projected_nodes, warpImage(srcImage, [dstCanvas.width/2, dstCanvas.height/2], 100, surfaceNodes[bodies[0]], mapping))
        }
    
        else if (bodies.size === 2) {
            var ratio = 0.25
            bodies.forEach(function (body) {
                var srcImage = PLANET_IMAGES[body]
                var scale = RAW_SCALES[body]
                projected_nodes.push.apply(projected_nodes, warpImage(srcImage, [dstCanvas.width * ratio, dstCanvas.height/2], scale, surfaceNodes[body], mapping))
                ratio += 0.5    
            })
        }
        else {
            bodies.forEach(function (body) {
                var srcImage = PLANET_IMAGES[body]
                var scale = RAW_SCALES[body]
                if (body === 'Earth') {
                    var widthRatio = 1/5
                    var heightRatio = 1/2
                }
                else if (body === 'Mars') {
                    var widthRatio = 4/5
                    var heightRatio = 1/2
                }  
                else if (body === 'Moon') {
                    var widthRatio = 2/5
                    var heightRatio = 1/5
                }  
                projected_nodes.push.apply(projected_nodes, warpImage(srcImage, [dstCanvas.width * widthRatio, dstCanvas.height*heightRatio], scale, surfaceNodes[body], mapping))
            })

        }
    }
    
    else {
        var notSunBodies = new Set(bodies)
        if (notSunBodies.has('Sun')) {
            notSunBodies.remove('Sun')
        }
        
        if (notSunBodies.size === 0) {
        }
        
        else if (notSunBodies.size === 1) {
            var srcImage = PLANET_IMAGES[bodies[0]]
            projected_nodes.push.apply(projected_nodes, warpImage(srcImage, [dstCanvas.width/2, dstCanvas.height/2], 100, surfaceNodes[bodies[0]], mapping))
        }
    
        else if (notSunBodies.size === 2) {
            bodies.forEach(function (body) {
                var srcImage = PLANET_IMAGES[body]
                var scale = RAW_SCALES[body]
                if (body === 'Earth') {
                    var locationRatio = 2/5
                }
                else {
                    var locationRatio = 4/5
                }  
                projected_nodes.push.apply(projected_nodes, warpImage(srcImage, [dstCanvas.width * locationRatio, dstCanvas.height*(1/2)], scale, surfaceNodes[body], mapping))
            })
        }
        else {
            bodies.forEach( function (body) {
                var srcImage = PLANET_IMAGES[body]
                var scale = RAW_SCALES[body]
                if (body === 'Earth') {
                    var widthRatio = 2/5
                    var heightRatio = 1/2
                }
                else if (body === 'Mars') {
                    var widthRatio = 4/5
                    var heightRatio = 1/2
                }  
                else if (body === 'Moon') {
                    var widthRatio = 3/5
                    var heightRatio = 1/5
                }  
                const new_nodes = warpImage(srcImage, [dstCanvas.width * widthRatio, dstCanvas.height*heightRatio], scale, surfaceNodes[body], mapping)
                projected_nodes.push.apply(projected_nodes, new_nodes)
            })
        }
    }

    console.log(projected_nodes)
    return projected_nodes
     
}

const projectedSurfaceNodes = [
    {
        body_1: "Earth",
        canvasPt: [388.35234999756017, 249.35198576377343],
        description: "Kennedy Space Center",
        latitude: 28.6,
        longitude: -80.6,
        name: "KSC",
        type: "Surface"
    },
    {
        body_1: "Earth",
        canvasPt: [375.7030442988689, 217.36551851770133],
        description: "Pacific Ocean Splashdown",
        latitude: 35,
        longitude: -117.9,
        name: "PAC",
        type: "Surface"
    },
    {
        body_1: "Moon",
        canvasPt: [960, 328.30894315746735],
        description: "Lunar South Pole",
        latitude: -80.9,
        longitude: -180,
        name: "LSP",
        type: "Surface"
    },
    // {
    //     body_1: "Mars",
    //     canvasPt: [914.1761749987801, 274.6759928818867],
    //     description: "Location on mars",
    //     latitude: 28.6,
    //     longitude: -80.6,
    //     name: "Mars Node",
    //     type: "Surface"
    // },
    
]

const projectedOrbitalNodes = [
    {
        "name": "LEO",
        "description": "Low Earth Orbit",
        "body_1": "Earth",
        "apoapsis": 296,
        "periapsis": 296,
        "inclination": 28.5,
        'canvasPt': [650, 375],
        "type": "Orbital"
      },
      {
        "name": "LLPO",
        "description": "Low Lunar Polar Orbit",
        "body_1": "Moon",
        "apoapsis": 100,
        "periapsis": 100,
        "inclination": 90,
        'canvasPt': [960, 360],
        "type": "Orbital"
      },
]


function drawNodes (projectedNodes) {
    projectedNodes.forEach( function(node) {
        netContext.fillStyle = "#ff0000 "; // Red color

        netContext.beginPath();
        var x = node.canvasPt[0]
        var y = node.canvasPt[1]
        netContext.arc(x, y, 4, 0, Math.PI * 2, true);
        netContext.fill();
        netContext.font = "14px Arial";
        netContext.fillText(node.name, x, y + 20)
    })
}

function drawEdges () {
    const KSC = [388.35234999756017, 249.35198576377343]
    const LEO = [650, 375]
    const PAC = [375.7030442988689, 217.36551851770133]
    const LSP = [960, 328.30894315746735]
    const LLPO = [960, 360]
    netContext.strokeStyle = "#ff0000 "; // Red color

    netContext.beginPath()
    netContext.moveTo(KSC[0], KSC[1])
    netContext.lineTo(LEO[0], LEO[1])
    netContext.stroke();
    netContext.lineTo(LLPO[0], LLPO[1])
    netContext.stroke();

    netContext.lineTo(LSP[0], LSP[1])
    netContext.stroke();

    netContext.lineTo(LLPO[0], LLPO[1])
    netContext.stroke();

    netContext.lineTo(PAC[0], PAC[1])
    netContext.stroke();

}

function drawCanvas() {
    var mapping = loadMapping();
    drawBodies(mapping)     
    drawNodes(projectedSurfaceNodes)
    drawNodes(projectedOrbitalNodes)
    drawEdges()
    }



setUpCanvas();
drawCanvas();
