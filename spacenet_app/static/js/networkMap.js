// Draws the network as a schematic map: bodies as disks, surface nodes
// projected on their body, orbital nodes on rings, and Lagrange nodes
// between bodies. The layout is purely presentational.

import { clear, svg } from "./util.js";

const WIDTH = 1000;
const HEIGHT = 520;

const BODIES = {
  Sun: { radius: 46, color: "#f5c542" },
  Earth: { radius: 62, color: "#2a6fb0" },
  Moon: { radius: 36, color: "#9aa0a6" },
  Mars: { radius: 48, color: "#b5533c" },
};

const EDGE_COLORS = {
  "Space Edge": "#ff5a52",
  "Surface Edge": "#4cd964",
  "Flight Edge": "#ffd43b",
};

const NODE_COLORS = {
  "Surface Node": "#4cd964",
  "Orbital Node": "#ff9f43",
  "Lagrange Node": "#c792ea",
};

function layoutBodies(nodes) {
  const used = new Set();
  for (const node of nodes) {
    used.add(node.body1);
    if (node.body2) used.add(node.body2);
  }
  const order = ["Sun", "Earth", "Moon", "Mars"].filter((body) => used.has(body));
  if (!order.length) order.push("Earth");
  const positions = {};
  const step = WIDTH / (order.length + 1);
  order.forEach((body, index) => {
    positions[body] = { x: step * (index + 1), y: HEIGHT / 2, ...BODIES[body] };
  });
  return positions;
}

/** Projects a latitude and longitude on a disk (Lambert azimuthal equal-area). */
function project(latitude, longitude, radius) {
  const phi = (latitude * Math.PI) / 180;
  const lambda = (longitude * Math.PI) / 180;
  const denominator = Math.max(1e-6, 1 + Math.cos(phi) * Math.cos(lambda));
  const k = Math.sqrt(2 / denominator);
  let x = k * Math.cos(phi) * Math.sin(lambda);
  let y = k * Math.sin(phi);
  const length = Math.hypot(x, y);
  if (length > 2) {
    x = (x / length) * 2;
    y = (y / length) * 2;
  }
  // points beyond the visible hemisphere are compressed towards the limb
  const scale = (radius * 0.92) / 2;
  return { x: x * scale, y: -y * scale };
}

function layoutNodes(nodes, bodies) {
  const positions = {};
  const orbits = {};
  for (const node of nodes) {
    const body = bodies[node.body1];
    if (!body) continue;
    if (node.type === "Surface Node") {
      const offset = project(node.latitude ?? 0, node.longitude ?? 0, body.radius);
      positions[node.id] = { x: body.x + offset.x, y: body.y + offset.y };
    } else if (node.type === "Orbital Node") {
      (orbits[node.body1] ||= []).push(node);
    } else {
      const minor = bodies[node.body2] || { x: body.x + 200, y: body.y };
      const dx = minor.x - body.x;
      const dy = minor.y - body.y;
      const fractions = { 1: 0.72, 2: 1.28, 3: -0.45 };
      const point = node.lpNumber ?? 1;
      if (point <= 3) {
        positions[node.id] = {
          x: body.x + dx * fractions[point],
          y: body.y + dy * fractions[point] - 26,
        };
      } else {
        const sign = point === 4 ? -1 : 1;
        positions[node.id] = { x: body.x + dx * 0.5, y: body.y + sign * Math.abs(dx) * 0.45 };
      }
    }
  }
  for (const [name, list] of Object.entries(orbits)) {
    const body = bodies[name];
    // lower orbits are drawn closer to the body
    list.sort((a, b) => (a.apoapsis ?? 0) - (b.apoapsis ?? 0));
    list.forEach((node, index) => {
      const radius = body.radius + 26 + index * 22;
      const angle = -Math.PI / 2 + (index % 2 ? 0.6 : -0.6) + index * 0.35;
      positions[node.id] = {
        x: body.x + radius * Math.cos(angle),
        y: body.y + radius * Math.sin(angle),
        ring: radius,
        body,
      };
    });
  }
  return positions;
}

/**
 * Draws a network.
 *
 * Options:
 *   selected: Set of selected node and edge identifiers
 *   onSelect(id): called when a node, edge, or element marker is clicked
 *   counts: map of location identifier to a number of elements shown as a marker
 */
export function drawNetwork(container, network, { selected = new Set(), onSelect = null, counts = null } = {}) {
  const nodes = network.nodes || [];
  const bodies = layoutBodies(nodes);
  const positions = layoutNodes(nodes, bodies);
  const root = svg("svg", {
    class: "sn-map",
    viewBox: `0 0 ${WIDTH} ${HEIGHT}`,
    preserveAspectRatio: "xMidYMid meet",
  });

  for (const [name, body] of Object.entries(bodies)) {
    root.append(
      svg("circle", { cx: body.x, cy: body.y, r: body.radius, fill: body.color, opacity: 0.9 }),
      svg(
        "text",
        { x: body.x, y: body.y + body.radius + 18, "text-anchor": "middle", class: "sn-body-label" },
        name
      )
    );
  }
  for (const position of Object.values(positions)) {
    if (position.ring) {
      root.append(
        svg("circle", {
          cx: position.body.x,
          cy: position.body.y,
          r: position.ring,
          fill: "none",
          stroke: "#495057",
          "stroke-dasharray": "3 4",
        })
      );
    }
  }

  const midpoints = {};
  const pairs = {};
  for (const edge of network.edges || []) {
    const from = positions[edge.origin];
    const to = positions[edge.destination];
    if (!from || !to) continue;
    // edges between the same pair of nodes are drawn with different curvature
    const pair = [edge.origin, edge.destination].sort().join("|");
    const index = (pairs[pair] = (pairs[pair] ?? -1) + 1);
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const length = Math.hypot(dx, dy) || 1;
    const direction = edge.origin < edge.destination ? 1 : -1;
    const bend =
      edge.type === "Surface Edge" && index === 0
        ? 0
        : direction * (0.18 + 0.12 * index) * length * (index % 2 ? -1 : 1);
    const cx = (from.x + to.x) / 2 - (dy / length) * bend;
    const cy = (from.y + to.y) / 2 + (dx / length) * bend;
    midpoints[edge.id] = {
      x: 0.25 * from.x + 0.5 * cx + 0.25 * to.x,
      y: 0.25 * from.y + 0.5 * cy + 0.25 * to.y,
    };
    const isSelected = selected.has(edge.id);
    root.append(
      svg(
        "path",
        {
          d: `M ${from.x} ${from.y} Q ${cx} ${cy} ${to.x} ${to.y}`,
          class: "sn-edge" + (isSelected ? " selected" : ""),
          stroke: isSelected ? null : EDGE_COLORS[edge.type] || "#adb5bd",
          style: onSelect ? "cursor: pointer" : null,
          onClick: onSelect ? () => onSelect(edge.id) : null,
        },
        svg("title", {}, `${edge.name} (${edge.type})`)
      )
    );
    if (isSelected) {
      root.append(
        svg(
          "text",
          { x: midpoints[edge.id].x, y: midpoints[edge.id].y - 8, "text-anchor": "middle" },
          edge.name
        )
      );
    }
  }

  for (const node of nodes) {
    const position = positions[node.id];
    if (!position) continue;
    const isSelected = selected.has(node.id);
    root.append(
      svg(
        "circle",
        {
          cx: position.x,
          cy: position.y,
          r: isSelected ? 7 : 5.5,
          fill: NODE_COLORS[node.type] || "#fff",
          class: "sn-node" + (isSelected ? " selected" : ""),
          onClick: onSelect ? () => onSelect(node.id) : null,
        },
        svg("title", {}, `${node.name} (${node.type})`)
      ),
      svg("text", { x: position.x + 9, y: position.y + 4 }, node.name)
    );
  }

  if (counts) {
    for (const [id, count] of Object.entries(counts)) {
      const position = positions[id] || midpoints[id];
      if (!position || !count) continue;
      const isSelected = selected.has(id);
      root.append(
        svg("circle", {
          cx: position.x,
          cy: position.y - 16,
          r: 10,
          class: "sn-elements",
          "stroke-width": isSelected ? 3.5 : 1.5,
          onClick: onSelect ? () => onSelect(id) : null,
        }),
        svg(
          "text",
          {
            x: position.x,
            y: position.y - 12,
            "text-anchor": "middle",
            class: "sn-elements-label",
          },
          count
        )
      );
    }
  }

  clear(container).append(root);
}
