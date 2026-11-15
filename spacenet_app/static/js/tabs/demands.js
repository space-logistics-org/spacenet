// Demands tab: demands simulated by the server, aggregated to the transports
// which could supply them, and broken down by element, mission, and location.

import { api, ApiError, latest } from "../api.js";
import { checklist, COS_COLORS, cosName, dateOf, issueList, nodeAxisLayout, plot } from "../components.js";
import { store } from "../store.js";
import { button, checkbox, clear, download, fmt, h, numberInput, select, toast } from "../util.js";

const VIEWS = [
  ["network", "Supply Network"],
  ["feasibility", "Scenario Feasibility"],
  ["byElement", "Demands by Element"],
  ["byMission", "Demands by Mission"],
  ["byLocation", "Demands by Location"],
];

const DISPLAYS = [
  ["demandMass", "Transport Demands"],
  ["rawCapacity", "Raw Capacity"],
  ["remainingCapacity", "Remaining Capacity"],
  ["netCapacity", "Net Capacity"],
];

const state = {
  view: "network",
  options: { estimateContainerMasses: false, consumeExistingResources: false },
  display: "netCapacity",
  node: null,
  filters: {},
  smooth: false,
  delimiter: ",",
  analysis: null,
  error: null,
  stale: true,
};

let root;
const request = latest((signal) => api.analyzeDemands(store.scenario, state.options, signal));

export function init(container) {
  root = container;
  store.on("change", () => (state.stale = true));
  store.on("scenario", () => {
    state.analysis = null;
    state.filters = {};
    state.node = null;
  });
}

async function load() {
  state.stale = false;
  try {
    const analysis = await request();
    if (analysis === undefined) return;
    state.analysis = analysis;
    state.error = null;
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    state.error = error;
  }
  draw();
}

export function render({ shown } = {}) {
  if (!root || !store.scenario) return;
  if (state.stale || shown) load();
  else draw();
}

async function exportDemands(kind) {
  try {
    const { name, text } = await api.exportText(`demands/${kind}`, {
      scenario: store.scenario,
      options: state.options,
      delimiter: state.delimiter,
    });
    download(name, text, "text/csv");
  } catch (error) {
    toast(`Export failed: ${error.message}`, "danger");
  }
}

function draw() {
  const scenario = store.scenario;
  const configuration = scenario.configuration;
  const analysis = state.analysis;
  const setOption = (name, value) => {
    state.options[name] = value;
    load();
  };
  const controls = h(
    "div",
    { class: "col-lg-3" },
    h("h6", {}, "Demand Options"),
    h("label", { class: "form-label small mb-0" }, "Item Discretization"),
    select(store.enums.itemDiscretization, configuration.itemDiscretization, (value) =>
      store.update((s) => (s.configuration.itemDiscretization = value))
    ),
    h("label", { class: "form-label small mb-0 mt-2" }, "Item Aggregation (0: first demand, 1: unit demand)"),
    numberInput(
      configuration.itemAggregation,
      (value) => store.update((s) => (s.configuration.itemAggregation = Math.min(1, Math.max(0, value ?? 0)))),
      { min: 0, max: 1, step: 0.25, disabled: configuration.itemDiscretization === "None", dataset: { key: "aggregation" } }
    ),
    h(
      "div",
      { class: "mt-2" },
      checkbox("Scavenge spares", configuration.scavengeSpares, (value) =>
        store.update((s) => (s.configuration.scavengeSpares = value))
      )
    ),
    h("h6", { class: "mt-3" }, "Display Options"),
    checkbox("Estimate logistics container masses", state.options.estimateContainerMasses, (value) =>
      setOption("estimateContainerMasses", value)
    ),
    checkbox("Consume existing resources", state.options.consumeExistingResources, (value) =>
      setOption("consumeExistingResources", value)
    ),
    h("h6", { class: "mt-3" }, "Export Demands"),
    h(
      "div",
      { class: "input-group input-group-sm" },
      select(
        [
          [",", "Comma"],
          ["\t", "Tab"],
          [";", "Semicolon"],
        ],
        state.delimiter,
        (value) => (state.delimiter = value)
      ),
      button("Raw", () => exportDemands("raw")),
      button("Aggregated", () => exportDemands("aggregated"))
    ),
    analysis
      ? h(
          "div",
          { class: "small text-secondary mt-3" },
          h("div", {}, `Total demands: ${fmt(analysis.totalMass, 1)} kg`),
          analysis.unassignedMass
            ? h("div", { class: "text-danger" }, `Without a transport: ${fmt(analysis.unassignedMass, 1)} kg`)
            : null,
          h("div", {}, `${analysis.raw.demands.length} logged demands`)
        )
      : null,
    analysis?.issues?.length ? h("div", { class: "mt-2" }, issueList(analysis.issues)) : null
  );

  const chart = h("div", { class: "sn-chart" });
  const chartOptions = h("div", { class: "mt-1" });
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      controls,
      h(
        "div",
        { class: "col-lg-9" },
        h(
          "ul",
          { class: "nav nav-pills mb-1" },
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
                    state.view = key;
                    draw();
                  },
                },
                label
              )
            )
          )
        ),
        state.error
          ? h("div", { class: "alert alert-warning" }, `Demands cannot be simulated: ${state.error.message}`)
          : chart,
        chartOptions
      )
    )
  );
  if (!analysis || state.error) {
    if (!state.error) plot(chart, []);
    return;
  }
  if (state.view === "network") drawNetwork(chart, chartOptions, analysis);
  else if (state.view === "feasibility") drawFeasibility(chart, chartOptions, analysis);
  else drawSources(chart, chartOptions, analysis[state.view], state.view);
}

function drawNetwork(chart, options, analysis) {
  options.append(
    h(
      "div",
      { class: "row g-2 align-items-end" },
      h(
        "div",
        { class: "col-md-4" },
        h("label", { class: "form-label small mb-0" }, "Display"),
        select(DISPLAYS, state.display, (value) => {
          state.display = value;
          draw();
        })
      ),
      h(
        "div",
        { class: "col-md-8 small text-secondary" },
        "Lines are transports (green: positive, grey: zero, red: negative); circles are demands at arrivals."
      )
    )
  );
  const values = analysis.supplyEdges.map((edge) => Math.abs(edge[state.display]));
  const largest = Math.max(1, ...values);
  const traces = analysis.supplyEdges.map((edge) => {
    const value = edge[state.display];
    const color = value > 0 ? "#2ca02c" : value < 0 ? "#d62728" : "#adb5bd";
    return {
      x: [dateOf(edge.startTime), dateOf(edge.endTime)],
      y: [edge.origin.name, edge.destination.name],
      mode: "lines",
      line: { color, width: 2 + (10 * Math.abs(value)) / largest },
      name: edge.location.name,
      showlegend: false,
      hovertemplate: `${edge.location.name}<br>${DISPLAYS.find(([key]) => key === state.display)[1]}: ${fmt(value, 1)} kg<extra></extra>`,
    };
  });
  const points = analysis.supplyPoints.filter((point) => point.demandMass > 0);
  const largestPoint = Math.max(1, ...points.map((point) => point.demandMass));
  if (points.length) {
    traces.push({
      x: points.map((point) => dateOf(point.time)),
      y: points.map((point) => point.location.name),
      mode: "markers",
      marker: {
        color: "#1f77b4",
        opacity: 0.7,
        size: points.map((point) => 8 + (26 * point.demandMass) / largestPoint),
      },
      text: points.map((point) => `${fmt(point.demandMass, 1)} kg`),
      name: "Aggregated demands",
      hovertemplate: "%{y}<br>Demands: %{text}<extra></extra>",
    });
  }
  plot(chart, traces, nodeAxisLayout());
}

function drawFeasibility(chart, options, analysis) {
  const nodes = analysis.feasibility.map((item) => [item.location.id, item.location.name]);
  if (!nodes.some(([id]) => id === state.node)) state.node = nodes.at(-1)?.[0] ?? null;
  options.append(
    h(
      "div",
      { class: "row g-2" },
      h(
        "div",
        { class: "col-md-4" },
        h("label", { class: "form-label small mb-0" }, "Feasibility at Node"),
        select(nodes, state.node, (value) => {
          state.node = value;
          draw();
        })
      )
    )
  );
  const item = analysis.feasibility.find((candidate) => candidate.location.id === state.node);
  if (!item) {
    plot(chart, []);
    return;
  }
  const x = item.points.map((point) => dateOf(point.time));
  const series = [
    ["cumulativeRawCapacity", "Gross Capacity", "#7f7f7f"],
    ["cumulativeRemainingCapacity", "Net Capacity", "#2ca02c"],
    ["cumulativeDemandMass", "Estimated Demands", "#d62728"],
  ];
  plot(
    chart,
    series.map(([key, name, color]) => ({
      x,
      y: item.points.map((point) => point[key]),
      name,
      mode: "lines+markers",
      line: { shape: "hv", color },
    })),
    { xaxis: { type: "date" }, yaxis: { title: { text: "Cumulative mass (kg)" } } }
  );
}

function drawSources(chart, options, sources, key) {
  const redraw = () => drawSourceChart(chart, sources, key);
  const list = checklist(
    sources.map((source) => [source.id, source.name]),
    redraw,
    { selected: state.filters[key] ?? (sources[0] ? [sources[0].id] : []) }
  );
  state.filters[key] = list.selected;
  options.append(
    h(
      "div",
      { class: "row g-2" },
      h("div", { class: "col-md-6" }, list.element),
      h(
        "div",
        { class: "col-md-6" },
        checkbox("Smooth demands", state.smooth, (value) => {
          state.smooth = value;
          redraw();
        }),
        h(
          "div",
          { class: "small text-secondary" },
          "One selection shows cumulative demands over time; several selections are compared by class of supply."
        )
      )
    )
  );
  redraw();
}

function drawSourceChart(chart, sources, key) {
  const selected = sources.filter((source) => state.filters[key].has(source.id));
  if (selected.length === 1) {
    plot(
      chart,
      selected[0].series.map((series) => ({
        x: series.points.map((point) => dateOf(point[0])),
        y: series.points.map((point) => point[1]),
        name: cosName(series.classOfSupply),
        mode: "lines",
        line: { shape: state.smooth ? "linear" : "hv", color: COS_COLORS[series.classOfSupply] },
      })),
      { xaxis: { type: "date" }, yaxis: { title: { text: "Cumulative mass (kg)" } } }
    );
    return;
  }
  const classes = [...new Set(selected.flatMap((source) => Object.keys(source.massByClassOfSupply)))]
    .map(Number)
    .sort((a, b) => a - b);
  plot(
    chart,
    classes.map((classOfSupply) => ({
      type: "bar",
      x: selected.map((source) => source.name),
      y: selected.map((source) => source.massByClassOfSupply[classOfSupply] ?? 0),
      name: cosName(classOfSupply),
      marker: { color: COS_COLORS[classOfSupply] },
    })),
    { barmode: "stack", yaxis: { title: { text: "Mass (kg)" } } }
  );
}
