// Simulation tab: runs the full simulation on the server and displays the
// errors, the network history, and the measures of effectiveness.

import { api, ApiError, latest } from "../api.js";
import {
  checklist,
  COS_COLORS,
  cosName,
  dateOf,
  elementDetails,
  elementTree,
  flatten,
  issueList,
  plot,
} from "../components.js";
import { drawNetwork } from "../networkMap.js";
import { store } from "../store.js";
import { button, checkbox, clear, fmt, formatDate, h, numberInput, select } from "../util.js";

const VIEWS = [
  ["network", "Network History"],
  ["measures", "Measures History"],
  ["locations", "Location History"],
  ["elements", "Element History"],
];

const MEASURES = [
  ["crewSurfaceDays", "Crew Surface Days", "crew-days"],
  ["crewTime", "Crew Time", "crew-hours"],
  ["launchMass", "Launch Mass", "kg"],
  ["explorationMassDelivered", "Exploration Mass Delivered", "kg"],
  ["upMassCapacityUtilization", "Up-Mass Capacity Utilization", "kg"],
  ["downMassCapacityUtilization", "Return-Mass Capacity Utilization", "kg"],
  ["explorationCapability", "Exploration Capability", "kg-crew-days"],
];

const state = {
  result: null,
  error: null,
  outdated: false,
  running: false,
  view: "network",
  frame: 0,
  playing: null,
  framesPerSecond: 4,
  location: null,
  element: null,
  measure: "crewSurfaceDays",
  linear: false,
  locationFilter: null,
  historyLocation: null,
  historyElement: null,
  showDemands: false,
};

let root;
let host; // { showTab }
const request = latest((signal) => api.simulate(store.scenario, signal));

export function init(container, options) {
  root = container;
  host = options;
  store.on("change", () => {
    if (state.result) state.outdated = true;
  });
  store.on("scenario", () => {
    stop();
    Object.assign(state, {
      result: null,
      error: null,
      outdated: false,
      frame: 0,
      location: null,
      element: null,
      locationFilter: null,
      historyLocation: null,
      historyElement: null,
    });
  });
}

export function render({ shown } = {}) {
  if (!root || !store.scenario) return;
  if (!shown && state.playing) return; // do not interrupt the animation
  draw();
}

async function simulate() {
  stop();
  state.running = true;
  draw();
  try {
    const result = await request();
    if (result === undefined) return;
    state.result = result;
    state.error = null;
    state.outdated = false;
    state.frame = Math.min(state.frame, result.networkHistory.length - 1);
    state.locationFilter = null;
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    state.error = error;
    state.result = null;
  } finally {
    state.running = false;
  }
  draw();
}

function stop() {
  if (state.playing) clearInterval(state.playing);
  state.playing = null;
}

function play() {
  const frames = state.result.networkHistory.length;
  if (state.frame >= frames - 1) state.frame = 0;
  state.playing = setInterval(() => {
    if (state.frame >= frames - 1) {
      stop();
      draw();
      return;
    }
    state.frame += 1;
    drawFrame();
  }, 1000 / Math.max(1, state.framesPerSecond));
  draw();
}

function draw() {
  const scenario = store.scenario;
  const configuration = scenario.configuration;
  const result = state.result;
  const issues = (result?.issues ?? []).filter((issue) => state.showDemands || issue.kind !== "demand");
  const left = h(
    "div",
    { class: "col-lg-3" },
    checkbox("Detailed explorations (generate EVA events)", configuration.detailedExploration, (value) =>
      store.update((s) => (s.configuration.detailedExploration = value))
    ),
    checkbox("Detailed EVAs (reconfigure and move elements)", configuration.detailedEva, (value) =>
      store.update((s) => (s.configuration.detailedEva = value))
    ),
    h(
      "div",
      { class: "my-2" },
      button(state.running ? "Simulating…" : "Simulate", simulate, "primary", { disabled: state.running })
    ),
    state.outdated
      ? h("div", { class: "alert alert-warning py-1 small" }, "The scenario changed since this simulation.")
      : null,
    state.error
      ? h("div", { class: "alert alert-danger py-1 small" }, `The scenario cannot be simulated: ${state.error.message}`)
      : null,
    result
      ? [
          h(
            "div",
            { class: "small mb-2" },
            `Completed with ${result.errorCount} error${result.errorCount === 1 ? "" : "s"} and ` +
              `${result.unsatisfiedDemandCount} unsatisfied demand${result.unsatisfiedDemandCount === 1 ? "" : "s"}.`
          ),
          totals(result.totals),
          h(
            "div",
            { class: "d-flex align-items-center mt-3" },
            h("h6", { class: "mb-0 me-auto" }, "Simulation Errors"),
            checkbox("Demands", state.showDemands, (value) => {
              state.showDemands = value;
              draw();
            })
          ),
          h(
            "div",
            { class: "sn-scroll-sm border rounded" },
            issueList(issues, {
              onSelect: async (issue) => {
                host.showTab("missions");
                const missions = await import("./missions.js");
                missions.editMission(issue.missionIndex, issue.eventIndex);
              },
            })
          ),
        ]
      : null
  );
  const content = h("div");
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      left,
      h(
        "div",
        { class: "col-lg-9" },
        h(
          "ul",
          { class: "nav nav-pills mb-2" },
          VIEWS.map(([key, label]) =>
            h(
              "li",
              { class: "nav-item" },
              h(
                "a",
                {
                  class: "nav-link py-1" + (state.view === key ? " active" : ""),
                  href: "#",
                  onClick: (event) => {
                    event.preventDefault();
                    stop();
                    state.view = key;
                    draw();
                  },
                },
                label
              )
            )
          )
        ),
        content
      )
    )
  );
  if (!result) {
    content.append(h("div", { class: "sn-muted-box" }, "Run the simulation to see its results."));
    return;
  }
  if (state.view === "network") drawHistory(content, result);
  else if (state.view === "measures") drawMeasures(content, result);
  else if (state.view === "locations") drawMassHistory(content, result.locationHistory, "historyLocation", "Location");
  else drawMassHistory(content, result.elementHistory, "historyElement", "Element");
}

function totals(values) {
  const rows = [
    ["Crew surface days", fmt(values.crewSurfaceDays, 1), "crew-days"],
    ["Crew time", fmt(values.crewTime, 0), "crew-hours"],
    ["Launch mass", fmt(values.launchMass, 0), "kg"],
    ["Exploration mass delivered", fmt(values.explorationMassDelivered, 0), "kg"],
    ["Up-mass capacity utilization", fmt(100 * values.upMassCapacityUtilization, 1), "%"],
    ["Return-mass capacity utilization", fmt(100 * values.downMassCapacityUtilization, 1), "%"],
    ["Exploration capability", fmt(values.explorationCapability, 0), "kg-crew-days"],
    ["Relative exploration capability", fmt(values.relativeExplorationCapability, 3), "(Apollo 17 = 1)"],
  ];
  return h(
    "table",
    { class: "table table-sm sn-table mb-0" },
    h(
      "tbody",
      {},
      rows.map(([label, value, units]) =>
        h("tr", {}, h("td", {}, label), h("td", { class: "text-end fw-semibold" }, value), h("td", { class: "text-secondary" }, units))
      )
    )
  );
}

// ---------------------------------------------------------- network history

let frameParts = null;

function drawHistory(content, result) {
  const frames = result.networkHistory.length;
  const map = h("div");
  const label = h("div", { class: "small text-secondary" });
  const details = h("div");
  const slider = h("input", {
    type: "range",
    class: "form-range",
    min: 0,
    max: frames - 1,
    step: 1,
    value: state.frame,
    onInput: () => {
      stop();
      state.frame = Number(slider.value);
      drawFrame();
    },
  });
  const step = (delta) => {
    stop();
    state.frame = Math.min(frames - 1, Math.max(0, state.frame + delta));
    draw();
  };
  frameParts = { map, label, details, slider, result };
  content.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-xl-8" },
        map,
        slider,
        h(
          "div",
          { class: "d-flex align-items-center gap-1" },
          button("⏮", () => step(-frames)),
          button("◀", () => step(-1)),
          state.playing
            ? button("⏸ Pause", () => {
                stop();
                draw();
              }, "primary")
            : button("▶ Play", play, "primary"),
          button("▶", () => step(1)),
          button("⏭", () => step(frames)),
          h("span", { class: "ms-3 small" }, "Frames per second"),
          h(
            "div",
            { style: { width: "5rem" } },
            numberInput(state.framesPerSecond, (value) => (state.framesPerSecond = Math.min(50, Math.max(1, value ?? 1))), {
              min: 1,
              max: 50,
              step: 1,
            })
          ),
          h("span", { class: "ms-auto" }, label)
        )
      ),
      h("div", { class: "col-xl-4" }, details)
    )
  );
  drawFrame();
}

function drawFrame() {
  if (!frameParts) return;
  const { map, label, details, slider, result } = frameParts;
  const snapshot = result.networkHistory[state.frame];
  if (!snapshot) return;
  slider.value = state.frame;
  label.textContent =
    `${formatDate(dateOf(snapshot.time))} · day ${fmt(snapshot.time, 2)} · ` +
    `step ${state.frame + 1} of ${result.networkHistory.length}`;
  const counts = {};
  for (const [id, elements] of Object.entries(snapshot.locations)) {
    if (elements.length) counts[id] = flatten(elements).length;
  }
  drawNetwork(map, store.scenario.network, {
    selected: new Set(state.location ? [state.location] : []),
    counts,
    onSelect: (id) => {
      state.location = id;
      state.element = null;
      drawFrame();
    },
  });
  const occupied = result.locations.filter((location) => snapshot.locations[location.id]?.length);
  if (!occupied.some((location) => location.id === state.location)) {
    state.location = occupied[0]?.id ?? null;
  }
  const elements = snapshot.locations[state.location] ?? [];
  const selected = flatten(elements).find((item) => item.element.id === state.element)?.element;
  details.replaceChildren(
    h("label", { class: "form-label small mb-0" }, "Elements at"),
    select(
      occupied.length ? occupied.map((location) => [location.id, location.name]) : [["", "(no elements)"]],
      state.location,
      (value) => {
        state.location = value;
        state.element = null;
        drawFrame();
      }
    ),
    h(
      "div",
      { class: "sn-scroll-sm border rounded p-2 my-2" },
      elementTree(elements, {
        selected: state.element,
        onSelect: (element) => {
          state.element = element.id;
          drawFrame();
        },
      })
    ),
    selected
      ? h("div", { class: "card card-body py-2" }, elementDetails(selected))
      : h("div", { class: "small text-secondary" }, "Select an element to see its state.")
  );
}

// ----------------------------------------------------------------- measures

function drawMeasures(content, result) {
  frameParts = null;
  const chart = h("div", { class: "sn-chart" });
  const info = h("div", { class: "small text-secondary" });
  const names = Object.fromEntries(result.locations.map((location) => [location.id, location.name]));
  const records = () => result.measures[state.measure] ?? [];
  const used = [...new Set(records().map((record) => record.location).filter(Boolean))];
  const list = checklist(
    used.map((id) => [id, names[id] ?? "?"]),
    () => update(),
    {}
  );

  function update() {
    const [, title, units] = MEASURES.find(([key]) => key === state.measure);
    const filtered = records()
      .filter((record) => !record.location || list.selected.has(record.location))
      .sort((a, b) => a.time - b.time);
    // records are accumulated over time for display
    const groups = {};
    for (const record of filtered) {
      const key = record.type ?? title;
      const group = (groups[key] ||= { x: [], y: [], total: 0 });
      group.total += record.amount;
      group.x.push(dateOf(record.time));
      group.y.push(group.total);
      if (record.capacity !== null && record.capacity !== undefined) {
        const capacity = (groups["Capacity"] ||= { x: [], y: [], total: 0 });
        capacity.total += record.capacity;
        capacity.x.push(dateOf(record.time));
        capacity.y.push(capacity.total);
      }
    }
    const traces = Object.entries(groups).map(([name, group]) => ({
      x: group.x,
      y: group.y,
      name,
      mode: "lines",
      line: { shape: state.linear ? "linear" : "hv" },
    }));
    plot(chart, traces, {
      xaxis: { type: "date" },
      yaxis: { title: { text: `Cumulative ${title} (${units})` } },
      showlegend: traces.length > 1,
    });
    const total = filtered.reduce((sum, record) => sum + record.amount, 0);
    info.textContent = `Filtered total: ${fmt(total, 1)} ${units} from ${filtered.length} records`;
  }

  content.append(
    h(
      "div",
      { class: "row g-3" },
      h("div", { class: "col-xl-9" }, chart, info),
      h(
        "div",
        { class: "col-xl-3" },
        h("label", { class: "form-label small mb-0" }, "Measure"),
        select(
          MEASURES.map(([key, title]) => [key, title]),
          state.measure,
          (value) => {
            state.measure = value;
            draw();
          }
        ),
        h(
          "div",
          { class: "my-2" },
          checkbox("Linearize data", state.linear, (value) => {
            state.linear = value;
            update();
          })
        ),
        h("div", { class: "small fw-semibold" }, "Locations"),
        list.element
      )
    )
  );
  update();
}

// ------------------------------------------------------------- mass history

function drawMassHistory(content, histories, key, label) {
  frameParts = null;
  const available = histories.filter((history) => history.series.length);
  if (!available.some((history) => history.id === state[key])) state[key] = available[0]?.id ?? null;
  const chart = h("div", { class: "sn-chart" });
  const history = available.find((item) => item.id === state[key]);
  content.append(
    h(
      "div",
      { class: "row g-2 mb-1" },
      h(
        "div",
        { class: "col-md-5" },
        h("label", { class: "form-label small mb-0" }, label),
        select(
          available.length ? available.map((item) => [item.id, item.name]) : [["", "(no mass by class of supply)"]],
          state[key],
          (value) => {
            state[key] = value;
            draw();
          }
        )
      ),
      h(
        "div",
        { class: "col-md-7 d-flex align-items-end" },
        checkbox("Linearize data", state.linear, (value) => {
          state.linear = value;
          draw();
        })
      )
    ),
    chart
  );
  plot(
    chart,
    (history?.series ?? []).map((series) => ({
      x: series.points.map((point) => dateOf(point[0])),
      y: series.points.map((point) => point[1]),
      name: cosName(series.classOfSupply),
      mode: "lines",
      stackgroup: "mass",
      line: { shape: state.linear ? "linear" : "hv", color: COS_COLORS[series.classOfSupply], width: 1 },
    })),
    { xaxis: { type: "date" }, yaxis: { title: { text: "Mass (kg)" } } }
  );
}
