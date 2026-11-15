// Manifest tab: packs aggregated demands in containers and loads containers
// in the carriers of transports. Every operation is performed by the server
// which returns the updated manifest and a view of it.

import { api, ApiError, latest } from "../api.js";
import { store } from "../store.js";
import { badge, button, capacityBar, clear, download, fmt, h, redraw, select, toast } from "../util.js";

const state = {
  result: null, // {manifest, view, dropped}
  error: null,
  demands: new Set(), // keys of selected aggregated demands
  container: null, // identifier of the selected container
  edge: null, // key of the selected supply edge
  carrier: null, // identifier of the selected carrier
  stale: true,
  busy: false,
  level: "demands",
  delimiter: ",",
};

let root;
let applying = false;

const request = latest((signal, operation, params) =>
  api.manifest(operation, store.scenario, { ...params, selection: selection() }, signal)
);

function selection() {
  return {
    containerId: state.container,
    edgeKey: state.carrier ? state.edge : null,
    carrierId: state.carrier,
  };
}

export function init(container) {
  root = container;
  store.on("change", () => {
    if (!applying) state.stale = true;
  });
  store.on("scenario", () => {
    Object.assign(state, { result: null, container: null, edge: null, carrier: null });
    state.demands = new Set();
  });
}

export function render({ shown } = {}) {
  if (!root || !store.scenario) return;
  if (state.stale || shown) run("view");
  else redraw(root, draw);
}

/** Performs a manifest operation and stores the resulting manifest. */
async function run(operation, params = {}) {
  state.stale = false;
  state.busy = true;
  try {
    const result = await request(operation, params);
    if (result === undefined) return;
    state.result = result;
    state.error = null;
    // forget selections which no longer exist
    const view = result.view;
    if (!view.containers.some((c) => c.id === state.container)) state.container = null;
    if (!view.edges.some((e) => e.key === state.edge)) {
      state.edge = null;
      state.carrier = null;
    }
    const keys = new Set(view.demands.map((d) => d.key));
    state.demands = new Set([...state.demands].filter((key) => keys.has(key)));
    if (JSON.stringify(result.manifest) !== JSON.stringify(store.scenario.manifest)) {
      applying = true;
      try {
        store.update((scenario) => (scenario.manifest = result.manifest));
      } finally {
        applying = false;
      }
    }
    if (result.dropped.length && operation === "view") {
      toast(`${result.dropped.length} manifest entries no longer match the scenario and were dropped.`, "warning");
    }
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    state.error = error;
    if (operation !== "view") toast(error.message, "danger");
  } finally {
    state.busy = false;
  }
  redraw(root, draw);
}

const refresh = () => run("view");

async function exportManifest() {
  try {
    const { name, text } = await api.exportText("manifest", {
      scenario: store.scenario,
      level: state.level,
      delimiter: state.delimiter,
    });
    download(name, text, "text/csv");
  } catch (error) {
    toast(`Export failed: ${error.message}`, "danger");
  }
}

function draw() {
  if (state.error && !state.result) {
    clear(root).append(
      h("div", { class: "alert alert-warning" }, `The manifest cannot be built: ${state.error.message}`)
    );
    return;
  }
  if (!state.result) {
    clear(root).append(h("div", { class: "text-secondary" }, "Simulating demands…"));
    return;
  }
  const view = state.result.view;
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      h("div", { class: "col-lg-4" }, drawDemands(view)),
      h("div", { class: "col-lg-4" }, drawContainers(view)),
      h("div", { class: "col-lg-4" }, drawCarriers(view))
    )
  );
}

// ------------------------------------------------------------------ demands

function drawDemands(view) {
  const selected = view.demands.filter((demand) => state.demands.has(demand.key));
  const keys = selected.map((demand) => demand.key);
  return h(
    "div",
    {},
    h(
      "div",
      { class: "d-flex align-items-center mb-2" },
      h("h6", { class: "mb-0 me-auto" }, "Aggregated Demands"),
      button("Auto-Manifest", () => run("auto"), "primary"),
      h("span", { class: "me-1" }),
      button("Reset", () => run("reset"), "outline-danger")
    ),
    h(
      "div",
      { class: "small text-secondary mb-1" },
      `Packed ${fmt(view.packedMass, 1)} of ${fmt(view.totalMass, 1)} kg · ` +
        `${view.loadedContainerCount} of ${view.containers.length} containers loaded`
    ),
    h(
      "div",
      { class: "sn-scroll border rounded", dataset: { scroll: "demands" } },
      h(
        "table",
        { class: "table table-sm table-hover sn-table mb-0" },
        h("thead", {}, h("tr", {}, ["Supply Point", "Resource", "Amount", "Packed"].map((t) => h("th", {}, t)))),
        h(
          "tbody",
          {},
          view.demands.map((demand) =>
            h(
              "tr",
              {
                class:
                  (state.demands.has(demand.key) ? "table-active " : "") +
                  (demand.remainingAmount > 0 ? "" : "text-success"),
                onClick: (event) => {
                  if (!event.ctrlKey && !event.metaKey && !event.shiftKey) state.demands.clear();
                  if (state.demands.has(demand.key)) state.demands.delete(demand.key);
                  else state.demands.add(demand.key);
                  redraw(root, draw);
                },
              },
              h("td", {}, demand.pointLabel, demand.edgeKey ? [" ", badge("in transit", "info")] : null),
              h("td", {}, demand.resourceName, demand.canPack ? [" ", badge("fits", "success")] : null),
              h("td", { class: "text-end" }, `${fmt(demand.amount)} ${demand.units}`),
              h("td", { class: "text-end" }, fmt(demand.packedAmount))
            )
          ),
          view.demands.length
            ? null
            : h("tr", {}, h("td", { colspan: 4, class: "text-secondary" }, "The scenario has no unsatisfied demands."))
        )
      )
    ),
    h(
      "div",
      { class: "mt-2" },
      button("Pack", () => run("pack", { demandKeys: keys, containerId: state.container }), "outline-primary", {
        disabled: !selected.some((demand) => demand.canPack),
        title: "Pack the selected demands in the selected container",
      }),
      " ",
      button("Auto-Pack", () => run("auto-pack", { demandKeys: keys }), "outline-primary", {
        disabled: !selected.some((demand) => demand.canAutoPack),
      }),
      " ",
      button("Unpack", () => run("unpack", { demandKeys: keys }), "outline-secondary", {
        disabled: !selected.some((demand) => demand.canUnpack),
      }),
      " ",
      button("Select Unpacked", () => {
        state.demands = new Set(view.demands.filter((d) => d.remainingAmount > 0).map((d) => d.key));
        redraw(root, draw);
      })
    ),
    h("h6", { class: "mt-3" }, "Export Manifest"),
    h(
      "div",
      { class: "input-group input-group-sm" },
      select(
        [
          ["demands", "By packed demand"],
          ["containers", "By container"],
          ["carriers", "By carrier"],
          ["edges", "By transport"],
        ],
        state.level,
        (value) => (state.level = value)
      ),
      select(
        [
          [",", "Comma"],
          ["\t", "Tab"],
          [";", "Semicolon"],
        ],
        state.delimiter,
        (value) => (state.delimiter = value)
      ),
      button("Export", exportManifest)
    )
  );
}

// --------------------------------------------------------------- containers

function drawContainers(view) {
  const selected = view.containers.find((container) => container.id === state.container);
  const volume = store.scenario.configuration.volumeConstrained;
  const addMenu = h(
    "div",
    { class: "btn-group" },
    h(
      "button",
      { class: "btn btn-sm btn-outline-primary dropdown-toggle", "data-bs-toggle": "dropdown", type: "button" },
      "Add"
    ),
    h(
      "ul",
      { class: "dropdown-menu" },
      store.enums.containerTypes.map((type) =>
        h(
          "li",
          {},
          h(
            "a",
            {
              class: "dropdown-item",
              href: "#",
              onClick: (event) => {
                event.preventDefault();
                run("containers", { containerType: type });
              },
            },
            type
          )
        )
      )
    )
  );
  return h(
    "div",
    {},
    h(
      "div",
      { class: "d-flex align-items-center mb-2" },
      h("h6", { class: "mb-0 me-auto" }, "Logistics Containers"),
      addMenu,
      h("span", { class: "me-1" }),
      button("Remove", () => run("containers/remove", { containerIds: [state.container] }), "outline-danger", {
        disabled: !selected,
      })
    ),
    h(
      "div",
      { class: "sn-scroll-sm border rounded", dataset: { scroll: "containers" } },
      h(
        "table",
        { class: "table table-sm table-hover sn-table mb-0" },
        h("thead", {}, h("tr", {}, ["Container", "Supply Point", "Transport"].map((t) => h("th", {}, t)))),
        h(
          "tbody",
          {},
          view.containers.map((container) =>
            h(
              "tr",
              {
                class: container.id === state.container ? "table-active" : "",
                onClick: () => {
                  state.container = container.id === state.container ? null : container.id;
                  refresh();
                },
              },
              h("td", {}, container.name, container.canManifest ? [" ", badge("fits", "success")] : null),
              h("td", {}, container.pointLabel ?? ""),
              h(
                "td",
                {},
                container.edgeLabels.length
                  ? container.edgeLabels.join("; ")
                  : h("span", { class: "text-secondary" }, container.contents.length ? "not loaded" : "empty")
              )
            )
          ),
          view.containers.length
            ? null
            : h("tr", {}, h("td", { colspan: 3, class: "text-secondary" }, "Add a container or auto-pack demands."))
        )
      )
    ),
    selected
      ? h(
          "div",
          { class: "card card-body py-2 mt-2" },
          h(
            "div",
            { class: "fw-semibold" },
            selected.name,
            " ",
            badge(selected.containerType),
            " ",
            badge(selected.cargoEnvironment, "light")
          ),
          h(
            "div",
            { class: "small text-secondary mb-1" },
            `Mass ${fmt(selected.mass)} kg · Total ${fmt(selected.totalMass)} kg · Volume ${fmt(selected.volume, 4)} m³`
          ),
          capacityBar("Cargo mass", selected.cargoMass, selected.maxCargoMass),
          volume ? capacityBar("Cargo volume", selected.cargoVolume, selected.maxCargoVolume, "m³") : null,
          h(
            "table",
            { class: "table table-sm sn-table mb-1" },
            h(
              "tbody",
              {},
              selected.contents.map((item) =>
                h(
                  "tr",
                  {},
                  h("td", {}, item.pointLabel),
                  h("td", {}, item.resourceName),
                  h("td", { class: "text-end" }, `${fmt(item.amount)} ${item.units}`),
                  h(
                    "td",
                    { class: "text-end" },
                    button(
                      "Unpack",
                      () => run("unpack", { demandKeys: [item.demandKey], containerId: selected.id })
                    )
                  )
                )
              ),
              selected.contents.length ? null : h("tr", {}, h("td", { class: "text-secondary" }, "Empty"))
            )
          ),
          h(
            "div",
            {},
            button(
              "Load in Selected Carrier",
              () => run("load", { containerIds: [selected.id], edgeKey: state.edge, carrierId: state.carrier }),
              "outline-primary",
              { disabled: !selected.canManifest }
            ),
            " ",
            button("Unload", () => run("unload", { containerIds: [selected.id] }), "outline-secondary", {
              disabled: !selected.edgeKeys.length,
            })
          )
        )
      : h("div", { class: "small text-secondary mt-2" }, "Select a container to see its contents.")
  );
}

// ----------------------------------------------------------------- carriers

function drawCarriers(view) {
  const containers = Object.fromEntries(view.containers.map((container) => [container.id, container]));
  const volume = store.scenario.configuration.volumeConstrained;
  const loadable = view.containers.filter((container) => container.canManifest);
  return h(
    "div",
    {},
    h(
      "div",
      { class: "d-flex align-items-center mb-2" },
      h("h6", { class: "mb-0 me-auto" }, "Transports and Carriers"),
      button(
        `Load All That Fit (${loadable.length})`,
        () =>
          run("load", {
            containerIds: loadable.map((container) => container.id),
            edgeKey: state.edge,
            carrierId: state.carrier,
          }),
        "outline-primary",
        { disabled: !loadable.length }
      )
    ),
    h(
      "div",
      { class: "sn-scroll", dataset: { scroll: "carriers" } },
      view.edges.map((edge) =>
        h(
          "div",
          { class: "card mb-2" },
          h(
            "div",
            { class: "card-header py-1 small" },
            h("strong", {}, edge.label),
            edge.isFlight ? [" ", badge("flight", "warning")] : null,
            h("span", { class: "float-end text-secondary" }, `net ${fmt(edge.netCargoMass, 1)} kg`)
          ),
          h(
            "div",
            { class: "list-group list-group-flush" },
            edge.carriers.map((carrier) => {
              const active = state.edge === edge.key && state.carrier === carrier.id;
              return h(
                "div",
                {
                  class: "list-group-item list-group-item-action py-1" + (active ? " active" : ""),
                  style: { cursor: "pointer", paddingLeft: `${0.75 + carrier.depth}rem` },
                  onClick: () => {
                    if (active) {
                      state.edge = null;
                      state.carrier = null;
                    } else {
                      state.edge = edge.key;
                      state.carrier = carrier.id;
                    }
                    refresh();
                  },
                },
                h(
                  "div",
                  { class: "d-flex" },
                  h("span", { class: "me-auto" }, carrier.name),
                  h(
                    "span",
                    { class: "small" },
                    `${fmt(carrier.cargoMass, 1)} / ${fmt(carrier.maxCargoMass, 1)} kg`,
                    volume ? ` · ${fmt(carrier.cargoVolume, 3)} / ${fmt(carrier.maxCargoVolume, 3)} m³` : ""
                  )
                ),
                active && carrier.containers.length
                  ? h(
                      "div",
                      { class: "small mt-1" },
                      carrier.containers.map((id) =>
                        h(
                          "div",
                          { class: "d-flex align-items-center" },
                          h(
                            "span",
                            { class: "me-auto" },
                            `${containers[id]?.name ?? "?"} (${fmt(containers[id]?.totalMass, 1)} kg)`
                          ),
                          h(
                            "a",
                            {
                              href: "#",
                              class: "link-light",
                              onClick: (event) => {
                                event.preventDefault();
                                event.stopPropagation();
                                run("unload", { containerIds: [id], edgeKey: edge.key });
                              },
                            },
                            "unload"
                          )
                        )
                      )
                    )
                  : carrier.containers.length
                    ? h("div", { class: "small text-secondary" }, `${carrier.containers.length} containers`)
                    : null
              );
            }),
            edge.carriers.length ? null : h("div", { class: "list-group-item text-secondary py-1" }, "No carriers")
          )
        )
      ),
      view.edges.length ? null : h("div", { class: "sn-muted-box" }, "The scenario has no transports.")
    )
  );
}
