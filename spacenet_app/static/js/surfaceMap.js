// Map of the surface nodes of a planetary body and the surface edges between
// them, in an azimuthal equidistant projection centered on the nodes (so
// distances from the center, e.g., a pole, are true to scale).

import { plot } from "./components.js";
import { fmt } from "./util.js";

/** Mean radius (km) of each body. */
const RADIUS = { Moon: 1737.4, Mars: 3389.5, Earth: 6371.0 };

const NODE_COLOR = "#1baf7a";
const EDGE_COLOR = "#52514e";
const toRadians = (degrees) => (degrees * Math.PI) / 180;

/** Lists the bodies other than Earth with surface nodes in a network. */
export function surfaceBodies(network) {
  const bodies = network.nodes
    .filter((node) => node.type === "Surface Node" && node.body1 !== "Earth")
    .map((node) => node.body1);
  return [...new Set(bodies)];
}

/** The center (latitude, longitude in radians) of a set of surface nodes. */
function centerOf(nodes) {
  let [x, y, z] = [0, 0, 0];
  for (const node of nodes) {
    const lat = toRadians(node.latitude);
    const lon = toRadians(node.longitude);
    x += Math.cos(lat) * Math.cos(lon);
    y += Math.cos(lat) * Math.sin(lon);
    z += Math.sin(lat);
  }
  return [Math.atan2(z, Math.hypot(x, y)), Math.atan2(y, x)];
}

/** Projects a node to (x, y) in km about a center. */
function project(node, [lat0, lon0], radius) {
  const lat = toRadians(node.latitude);
  const dlon = toRadians(node.longitude) - lon0;
  const cosc = Math.min(1, Math.sin(lat0) * Math.sin(lat) + Math.cos(lat0) * Math.cos(lat) * Math.cos(dlon));
  const c = Math.acos(cosc);
  const k = c < 1e-12 ? 1 : c / Math.sin(c);
  return [
    radius * k * Math.cos(lat) * Math.sin(dlon),
    radius * k * (Math.cos(lat0) * Math.sin(lat) - Math.sin(lat0) * Math.cos(lat) * Math.cos(dlon)),
  ];
}

/**
 * Draws the surface map of a body.
 *
 * @param {HTMLElement} element the chart container
 * @param {object} network the scenario network
 * @param {string} body the body
 * @param {object} options `selected` (set of ids) and `onSelect` (callback)
 */
export function drawSurfaceMap(element, network, body, { selected = new Set(), onSelect = null } = {}) {
  const nodes = network.nodes.filter((node) => node.type === "Surface Node" && node.body1 === body);
  const radius = RADIUS[body] ?? RADIUS.Moon;
  const center = centerOf(nodes);
  const points = new Map(nodes.map((node) => [node.id, project(node, center, radius)]));
  const traces = [];
  const labels = { x: [], y: [], text: [] };
  for (const edge of network.edges) {
    if (edge.type !== "Surface Edge" || !points.has(edge.origin) || !points.has(edge.destination)) continue;
    const [x0, y0] = points.get(edge.origin);
    const [x1, y1] = points.get(edge.destination);
    traces.push({
      x: [x0, x1],
      y: [y0, y1],
      mode: "lines",
      line: { color: EDGE_COLOR, width: selected.has(edge.id) ? 4 : 2 },
      hovertemplate: `${edge.name}: ${fmt(edge.distance / 1000, 1)} km<extra></extra>`,
      showlegend: false,
    });
    labels.x.push((x0 + x1) / 2);
    labels.y.push((y0 + y1) / 2);
    labels.text.push(`${fmt(edge.distance / 1000, 1)} km`);
  }
  traces.push({
    ...labels,
    mode: "text",
    textposition: "middle right",
    textfont: { color: EDGE_COLOR, size: 10 },
    hoverinfo: "skip",
    showlegend: false,
  });
  // the pole is a reference for polar sites
  const polar = nodes.length && nodes.every((node) => Math.abs(node.latitude) > 80);
  if (polar) {
    const south = nodes[0].latitude < 0;
    const [x, y] = project({ latitude: south ? -90 : 90, longitude: 0 }, center, radius);
    traces.push({
      x: [x],
      y: [y],
      text: [south ? "South Pole" : "North Pole"],
      mode: "markers+text",
      textposition: "top left",
      textfont: { color: EDGE_COLOR, size: 10 },
      marker: { symbol: "x-thin", size: 10, line: { color: EDGE_COLOR, width: 2 } },
      hoverinfo: "skip",
      showlegend: false,
    });
  }
  const describe = (node) =>
    [
      `<b>${node.name}</b>`,
      `${fmt(node.latitude, 2)}°, ${fmt(node.longitude, 2)}°`,
      `Illumination: ${fmt(100 * (node.illumination ?? 1), 0)}%`,
      node.maxNightDuration ? `Longest night: ${fmt(node.maxNightDuration, 0)} h` : null,
    ]
      .filter(Boolean)
      .join("<br>");
  traces.push({
    x: nodes.map((node) => points.get(node.id)[0]),
    y: nodes.map((node) => points.get(node.id)[1]),
    customdata: nodes.map((node) => node.id),
    text: nodes.map((node) => node.name),
    hovertext: nodes.map(describe),
    mode: "markers+text",
    textposition: "top right",
    marker: {
      size: nodes.map((node) => (selected.has(node.id) ? 16 : 12)),
      color: NODE_COLOR,
      line: { color: "#ffffff", width: 2 },
    },
    hovertemplate: "%{hovertext}<extra></extra>",
    showlegend: false,
  });
  // keep a sensible extent for a single node or nearby nodes
  const xs = [...points.values()].map((p) => p[0]);
  const ys = [...points.values()].map((p) => p[1]);
  const span = Math.max(10, ...xs.map(Math.abs), ...ys.map(Math.abs)) * 1.3;
  plot(element, traces, {
    margin: { l: 50, r: 20, t: 10, b: 40 },
    xaxis: { title: { text: "km" }, range: [-span, span], zeroline: false },
    yaxis: { title: { text: "km" }, range: [-span, span], zeroline: false, scaleanchor: "x" },
    hovermode: "closest",
    showlegend: false,
  });
  if (onSelect && !element.dataset.bound) {
    element.dataset.bound = "true";
    element.on?.("plotly_click", (event) => {
      const id = event.points?.[0]?.customdata;
      if (id) onSelect(id);
    });
  }
}
