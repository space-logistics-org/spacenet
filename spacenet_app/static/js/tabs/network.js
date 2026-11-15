// Network tab: selects the nodes and edges of the scenario from the library.

import { drawNetwork } from "../networkMap.js";
import { store } from "../store.js";
import { alertDialog, button, clear, clone, fmt, h, isoToDays, select, textInput } from "../util.js";

const state = {
  view: "nodes",
  search: "",
  type: "",
  selected: new Set(),
};

let root;

export function init(container) {
  root = container;
}

/** Lists the uses of a node or an edge which prevent its removal. */
function getUses(id) {
  const scenario = store.scenario;
  const uses = [];
  for (const edge of scenario.network.edges) {
    if (edge.id !== id && (edge.origin === id || edge.destination === id)) {
      uses.push(`Edge ${edge.name}`);
    }
  }
  for (const mission of scenario.missionList) {
    for (const key of ["origin", "destination", "returnOrigin", "returnDestination"]) {
      if (mission[key] === id) uses.push(`Mission ${mission.name}`);
    }
    for (const event of mission.events) {
      if (event.location === id || event.edge === id || event.container === id) {
        uses.push(`Event ${event.name}`);
      }
    }
  }
  const location = store.location(id);
  if (location?.contents?.length) uses.push("Initial elements");
  return [...new Set(uses)];
}

function isVisible(item, bodies) {
  if (item.origin) {
    const nodes = store.library("nodes");
    const origin = nodes.find((node) => node.id === item.origin);
    const destination = nodes.find((node) => node.id === item.destination);
    return Boolean(origin && destination && isVisible(origin, bodies) && isVisible(destination, bodies));
  }
  return bodies.includes(item.body1) && (!item.body2 || bodies.includes(item.body2));
}

function includeNode(node) {
  const network = store.scenario.network;
  if (!network.nodes.some((other) => other.id === node.id)) network.nodes.push(clone(node));
}

function toggle(item, included) {
  const isEdge = Boolean(item.origin);
  if (included) {
    // edges of a node are removed with it unless they are used themselves
    const uses = getUses(item.id).filter((use) => isEdge || !use.startsWith("Edge "));
    if (!isEdge) {
      for (const edge of store.scenario.network.edges) {
        if (edge.origin !== item.id && edge.destination !== item.id) continue;
        uses.push(...getUses(edge.id).map((use) => `${use} (uses edge ${edge.name})`));
      }
    }
    if (uses.length) {
      alertDialog(
        "Cannot Remove",
        h(
          "div",
          {},
          `The following use ${item.name} and must be changed before removal:`,
          h("ul", { class: "mb-0" }, uses.map((use) => h("li", {}, use)))
        )
      );
      return;
    }
    store.update((scenario) => {
      const network = scenario.network;
      if (isEdge) {
        network.edges = network.edges.filter((edge) => edge.id !== item.id);
      } else {
        network.edges = network.edges.filter(
          (edge) => edge.origin !== item.id && edge.destination !== item.id
        );
        network.nodes = network.nodes.filter((node) => node.id !== item.id);
      }
    });
  } else {
    store.update((scenario) => {
      const network = scenario.network;
      const nodes = store.library("nodes");
      if (isEdge) {
        // an edge requires its origin and destination nodes
        for (const id of [item.origin, item.destination]) {
          const node = nodes.find((other) => other.id === id);
          if (node) includeNode(node);
        }
        network.edges.push(clone(item));
      } else {
        includeNode(item);
        // edges between included nodes are added
        const ids = new Set(network.nodes.map((node) => node.id));
        for (const edge of store.library("edges")) {
          if (
            ids.has(edge.origin) &&
            ids.has(edge.destination) &&
            !network.edges.some((other) => other.id === edge.id)
          ) {
            network.edges.push(clone(edge));
          }
        }
      }
    });
  }
}

function details(item) {
  const name = (id) => store.library("nodes").find((node) => node.id === id)?.name ?? "?";
  const rows = [["Type", item.type], ["Description", item.description || ""]];
  if (item.type === "Surface Node") {
    rows.push(["Body", item.body1], ["Latitude", `${fmt(item.latitude)}°`], ["Longitude", `${fmt(item.longitude)}°`]);
  } else if (item.type === "Orbital Node") {
    rows.push(
      ["Body", item.body1],
      ["Periapsis", `${fmt(item.periapsis)} km`],
      ["Apoapsis", `${fmt(item.apoapsis)} km`],
      ["Inclination", `${fmt(item.inclination)}°`]
    );
  } else if (item.type === "Lagrange Node") {
    rows.push(["Major body", item.body1], ["Minor body", item.body2], ["Lagrange point", item.lpNumber]);
  } else {
    rows.push(["Origin", name(item.origin)], ["Destination", name(item.destination)]);
    if (item.type === "Surface Edge") rows.push(["Distance", `${fmt(item.distance / 1000)} km`]);
    if (item.duration !== undefined) rows.push(["Duration", `${fmt(isoToDays(item.duration), 3)} days`]);
    if (item.type === "Flight Edge") {
      rows.push(["Max crew", item.maxCrew], ["Max cargo", `${fmt(item.maxCargo)} kg`]);
    }
    if (item.burns) {
      rows.push([
        "Burns",
        item.burns.map((burn) => `${fmt(burn.deltaV)} m/s at ${fmt(isoToDays(burn.time), 3)} d`).join(", "),
      ]);
    }
  }
  return h(
    "div",
    { class: "card card-body py-2 mt-2" },
    h("div", { class: "fw-semibold" }, item.name),
    h(
      "table",
      { class: "table table-sm mb-0 sn-table" },
      h("tbody", {}, rows.map(([label, value]) => h("tr", {}, h("th", { class: "w-25" }, label), h("td", {}, value))))
    )
  );
}

export function render() {
  if (!root || !store.scenario) return;
  const scenario = store.scenario;
  const network = scenario.network;
  const bodies =
    store.enums.scenarioTypes.find((type) => type.name === scenario.scenarioType)?.bodies ?? [];
  const isNodes = state.view === "nodes";
  const included = new Set((isNodes ? network.nodes : network.edges).map((item) => item.id));
  const types = isNodes ? store.enums.nodeTypes : store.enums.edgeTypes;
  const search = state.search.toLowerCase();
  const items = store
    .library(isNodes ? "nodes" : "edges")
    .filter((item) => included.has(item.id) || isVisible(item, bodies))
    .filter((item) => !state.type || item.type === state.type)
    .filter((item) => !search || item.name.toLowerCase().includes(search));
  const nodeName = (id) => store.library("nodes").find((node) => node.id === id)?.name ?? "?";

  const table = h(
    "table",
    { class: "table table-sm table-hover sn-table mb-0" },
    h(
      "thead",
      {},
      h(
        "tr",
        {},
        h("th", {}, ""),
        h("th", {}, "Name"),
        h("th", {}, "Type"),
        isNodes ? null : [h("th", {}, "Origin"), h("th", {}, "Destination")]
      )
    ),
    h(
      "tbody",
      {},
      items.map((item) =>
        h(
          "tr",
          {
            class: state.selected.has(item.id) ? "table-active" : "",
            onClick: (event) => {
              if (event.target.tagName === "INPUT") return;
              if (!event.ctrlKey && !event.metaKey) state.selected.clear();
              state.selected.add(item.id);
              render();
            },
          },
          h(
            "td",
            {},
            h("input", {
              type: "checkbox",
              class: "form-check-input",
              checked: included.has(item.id),
              onChange: () => toggle(item, included.has(item.id)),
            })
          ),
          h("td", {}, item.name),
          h("td", {}, item.type.replace(/ (Node|Edge)$/, "")),
          isNodes ? null : [h("td", {}, nodeName(item.origin)), h("td", {}, nodeName(item.destination))]
        )
      ),
      items.length
        ? null
        : h(
            "tr",
            {},
            h(
              "td",
              { colspan: 5, class: "text-secondary" },
              "No library objects. Load a model database or open a scenario."
            )
          )
    )
  );

  const selectedItems = [...state.selected]
    .map((id) => store.library("nodes").find((n) => n.id === id) || store.library("edges").find((e) => e.id === id))
    .filter(Boolean);
  const map = h("div");
  const left = h(
    "div",
    { class: "col-lg-5" },
    h(
      "div",
      { class: "row g-2 mb-2" },
      h(
        "div",
        { class: "col-6" },
        h("label", { class: "form-label small mb-0" }, "Scenario Type"),
        select(
          store.enums.scenarioTypes.map((type) => type.name),
          scenario.scenarioType,
          (value) => store.update((s) => (s.scenarioType = value))
        )
      ),
      h(
        "div",
        { class: "col-6 d-flex align-items-end" },
        h(
          "div",
          { class: "btn-group btn-group-sm w-100" },
          button(`Nodes (${network.nodes.length})`, () => {
            state.view = "nodes";
            state.type = "";
            render();
          }, isNodes ? "primary" : "outline-primary"),
          button(`Edges (${network.edges.length})`, () => {
            state.view = "edges";
            state.type = "";
            render();
          }, isNodes ? "outline-primary" : "primary")
        )
      )
    ),
    h(
      "div",
      { class: "row g-2 mb-2" },
      h(
        "div",
        { class: "col-6" },
        textInput(state.search, (value) => {
          state.search = value;
          renderTableOnly();
        }, { placeholder: "Search by name", id: "network-search" })
      ),
      h(
        "div",
        { class: "col-6" },
        select([["", "All types"], ...types], state.type, (value) => {
          state.type = value;
          render();
        })
      )
    ),
    h("div", { class: "sn-scroll border rounded", id: "network-table" }, table),
    h(
      "div",
      { class: "mt-2" },
      button("Select All", () => items.filter((i) => !included.has(i.id)).forEach((i) => toggle(i, false))),
      " ",
      button("Deselect All", () => {
        // edges first so that nodes are no longer used by them
        const sorted = [...items].sort((a, b) => Number(Boolean(b.origin)) - Number(Boolean(a.origin)));
        sorted.filter((i) => included.has(i.id) && !getUses(i.id).length).forEach((i) => toggle(i, true));
      })
    ),
    selectedItems.length === 1 ? details(selectedItems[0]) : null
  );
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      left,
      h(
        "div",
        { class: "col-lg-7" },
        map,
        h(
          "div",
          { class: "small text-secondary mt-1" },
          legend("#4cd964", "Surface"),
          legend("#ff9f43", "Orbital"),
          legend("#c792ea", "Lagrange"),
          " nodes · ",
          legend("#ff5a52", "Space"),
          legend("#4cd964", "Surface"),
          legend("#ffd43b", "Flight"),
          " edges"
        )
      )
    )
  );
  drawNetwork(map, network, {
    selected: state.selected,
    onSelect: (id) => {
      state.selected = new Set([id]);
      state.view = store.node(id) ? "nodes" : "edges";
      render();
    },
  });
}

function legend(color, label) {
  return h("span", { class: "me-2" }, h("span", { class: "sn-dot", style: { background: color } }), label);
}

// re-renders while keeping the focus in the search box
function renderTableOnly() {
  render();
  const input = document.getElementById("network-search");
  if (input) {
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  }
}
