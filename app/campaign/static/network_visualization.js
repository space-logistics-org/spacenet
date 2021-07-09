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
        {
            "name": "Mars place",
            "description": "Kennedy Space Center",
            "body_1": "Mars",
            "latitude": 28.6,
            "longitude": -80.6,
            "type": "Surface"
          },
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

// var mapping = loadMapping()


var dstCanvas = d3.select('#network').node();
    
var dstContext = dstCanvas.getContext('2d');

function setUpCanvas () {
    dstContext.fillStyle = '#000000'
    dstContext.fillRect(0, 0, dstCanvas.width, dstCanvas.height);
};


function warpImage(imageURL, location, scale, nodes, mapping) {
    var planet = {type: 'Sphere'},
    rasterWarper;
    
    var dstProj = d3.geoAzimuthalEqualArea()
        .scale(scale)
        .translate(location);
    
    
    path = d3.geoPath().projection(dstProj).context(dstContext);
    
    var geoGenerator = d3.geoPath()
    .projection(dstProj)
    .context(dstContext);
    

    
    var geoCircle = d3.geoCircle().precision(1);
    
    var srcImg = document.createElement('img');

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
    srcImg.src = imageURL
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

var DisplaySun = true

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

async function drawBodies(mapping) {
    var mapping = await loadMapping()
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
        var sunImg = document.createElement('img');
        sunImg.src = PLANET_IMAGES['Sun']
        console.log(sunImg)
        var w = dstCanvas.width
        var h = dstCanvas.height
        var sunW = sunImg.width
        var sunH = sunImg.height
        dstContext.drawImage(sunImg, 0, h/4, sunW*h/(sunH*2), h/2)
        
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
            bodies.forEach(function (body) {
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
                projected_nodes.push.apply(projected_nodes, warpImage(srcImage, [dstCanvas.width * widthRatio, dstCanvas.height*heightRatio], scale, surfaceNodes[body], mapping))
            })
        }
    }
    return projected_nodes
}

async function drawNodes() {
    var projected_nodes = await drawBodies()
    console.log(projected_nodes)
    projected_nodes.forEach( function(node) {
        dstContext.fillStyle = "#ff0000 "; // Red color

        var defined_node = JSON.parse(JSON.stringify(node))
        console.log(defined_node)
        dstContext.beginPath();
        var x = defined_node.canvasPt
        console.log(x)
        var y = node.longitude
        dstContext.arc(x, y, 4, 0, Math.PI * 2, true);
        dstContext.fill();
    })
}

function drawCanvas() {
    // var mapping = loadMapping();
    // var projected_nodes = drawBodies(mapping)
    // drawNodes(projected_nodes)
    drawNodes()
    }



setUpCanvas();
drawCanvas();
