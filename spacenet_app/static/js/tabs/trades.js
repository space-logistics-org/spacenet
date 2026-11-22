// Trades tab: varies fields of the scenario (a full-factorial or
// one-at-a-time design), simulates each case on the server, and compares the
// measures of effectiveness of the cases; and runs Monte Carlo reliability
// studies of random part failures.

import { api, ApiError } from "../api.js";
import { plot } from "../components.js";
import { store } from "../store.js";
import { button, clear, fmt, h, numberInput, select, textInput, toast } from "../util.js";

// categorical series colors in fixed order (validated palette)
const SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];

// collections of the scenario whose items have named numeric fields
const COLLECTIONS = [
  ["elementTemplates", "Element template"],
  ["instantiatedElements", "Element instance"],
  ["network/edges", "Edge"],
  ["network/nodes", "Node"],
  ["demandModels", "Demand model"],
  ["resourceList", "Resource"],
  ["configuration", "Configuration"],
];

const METRIC_LABELS = {
  errorCount: "Errors",
  warningCount: "Warnings",
  unsatisfiedDemandCount: "Unsatisfied demands",
  unsatisfiedDemandMass: "Unsatisfied demand mass (kg)",
  crewSurfaceDays: "Crew surface days",
  crewTime: "Crew time (crew-hours)",
  explorationCapability: "Exploration capability (kg-crew-days)",
  explorationMassDelivered: "Exploration mass delivered (kg)",
  launchMass: "Launch mass (kg)",
  upMassCapacityUtilization: "Up-mass capacity utilization",
  downMassCapacityUtilization: "Return-mass capacity utilization",
  relativeExplorationCapability: "Relative exploration capability",
  propellantBurnedMass: "Propellant burned (kg)",
  propellantBoiloffMass: "Propellant boiloff (kg)",
  propellantTransferLossMass: "Propellant transfer losses (kg)",
  energyDeficit: "Energy deficit (kWh)",
  campaignCost: "Campaign cost ($M)",
  isruOutputMass: "ISRU production (kg)",
  isruEnergy: "ISRU energy (kWh)",
};

const state = {
  variables: [],
  design: "Full Factorial",
  metric: "errorCount",
  result: null,
  running: false,
  reliability: { runs: 100, seed: 0, result: null, running: false, part: null },
};

let root;

export function init(container) {
  root = container;
  store.on("scenario", () => {
    state.variables = [];
    state.result = null;
    state.reliability.result = null;
    state.reliability.part = null;
  });
}

export function render() {
  if (!root || !store.scenario) return;
  draw();
}

// ------------------------------------------------------------- fields

/** Lists the numeric fields (dotted paths) of an object, excluding identifiers. */
function numericFields(value, prefix = "", depth = 0) {
  if (depth > 6 || value === null || value === undefined) return [];
  if (typeof value === "number") return [prefix];
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => numericFields(item, `${prefix}/${index}`, depth + 1));
  }
  if (typeof value === "object") {
    return Object.entries(value)
      .filter(([key]) => !["id", "templateId"].includes(key))
      .flatMap(([key, item]) => numericFields(item, `${prefix}/${key}`, depth + 1));
  }
  return [];
}

function collection(path) {
  return path.split("/").reduce((node, key) => node?.[key], store.scenario);
}

/** Options of the items of a collection (selected by name). */
function itemOptions(path) {
  const items = collection(path);
  if (!Array.isArray(items)) return [];
  return items.filter((item) => item.name).map((item) => [item.name, item.name]);
}

/** Options of the numeric fields of an item of a collection. */
function fieldOptions(variable) {
  const items = collection(variable.collection);
  const item = Array.isArray(items) ? items.find((candidate) => candidate.name === variable.item) : items;
  // include optional numeric fields which are not yet defined
  const optional = {
    elementTemplates: ["/unitCost", "/designLife"],
    "network/edges": ["/costPerTransport", "/minDepartureInterval"],
    "network/nodes": ["/illumination", "/maxNightDuration"],
  }[variable.collection] ?? [];
  return [...new Set([...numericFields(item ?? {}), ...optional])].map((path) => [path, path.slice(1)]);
}

function pathOf(variable) {
  if (variable.collection === "configuration") return `configuration${variable.field}`;
  return `${variable.collection}/name=${variable.item}${variable.field}`;
}

function currentValue(variable) {
  let node = store.scenario;
  for (const segment of pathOf(variable).split("/")) {
    if (node === undefined || node === null) return undefined;
    if (Array.isArray(node) && segment.includes("=")) {
      const [key, value] = segment.split("=");
      node = node.find((item) => String(item[key]) === value);
    } else {
      node = node[segment];
    }
  }
  return node;
}

function valuesOf(variable) {
  if (variable.mode === "list") {
    return variable.list
      .split(",")
      .map((text) => text.trim())
      .filter(Boolean)
      .map(Number)
      .filter((value) => Number.isFinite(value));
  }
  const steps = Math.max(1, Math.round(variable.steps ?? 1));
  if (steps === 1) return [variable.from];
  return Array.from({ length: steps }, (_, i) => variable.from + ((variable.to - variable.from) * i) / (steps - 1));
}

function newVariable() {
  const variable = {
    name: `x${state.variables.length + 1}`,
    collection: "elementTemplates",
    item: itemOptions("elementTemplates")[0]?.[0] ?? "",
    field: "",
    mode: "range",
    from: 0,
    to: 1,
    steps: 3,
    list: "",
  };
  variable.field = fieldOptions(variable)[0]?.[0] ?? "";
  seedRange(variable);
  return variable;
}

/** Sets the range of a variable around the current value of its field. */
function seedRange(variable) {
  const value = Number(currentValue(variable));
  if (Number.isFinite(value) && value !== 0) {
    variable.from = value * 0.8;
    variable.to = value * 1.2;
  } else {
    variable.from = 0;
    variable.to = 1;
  }
}

// --------------------------------------------------------------- run

async function run() {
  const study = {
    variables: state.variables.map((variable) => ({
      name: variable.name,
      path: pathOf(variable),
      values: valuesOf(variable),
    })),
    design: state.design,
    metrics: [],
  };
  state.running = true;
  draw();
  try {
    state.result = await api.runTrade(store.scenario, study);
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    toast(`The trade study could not run: ${error.message}`, "danger");
  } finally {
    state.running = false;
  }
  draw();
}

// -------------------------------------------------------------- draw

function variableRow(variable, index) {
  const refresh = () => draw();
  const collections = COLLECTIONS.map(([value, label]) => [value, label]);
  const items = variable.collection === "configuration" ? [] : itemOptions(variable.collection);
  const fields = fieldOptions(variable);
  return h(
    "div",
    { class: "card card-body py-2 mb-2" },
    h(
      "div",
      { class: "row g-2 align-items-end" },
      h(
        "div",
        { class: "col-md-1" },
        h("label", { class: "form-label small mb-0" }, "Name"),
        textInput(variable.name, (value) => (variable.name = value || `x${index + 1}`))
      ),
      h(
        "div",
        { class: "col-md-2" },
        h("label", { class: "form-label small mb-0" }, "Object"),
        select(collections, variable.collection, (value) => {
          variable.collection = value;
          variable.item = itemOptions(value)[0]?.[0] ?? "";
          variable.field = fieldOptions(variable)[0]?.[0] ?? "";
          seedRange(variable);
          refresh();
        })
      ),
      variable.collection === "configuration"
        ? null
        : h(
            "div",
            { class: "col-md-3" },
            h("label", { class: "form-label small mb-0" }, "Item"),
            select(items.length ? items : [["", "(none)"]], variable.item, (value) => {
              variable.item = value;
              variable.field = fieldOptions(variable)[0]?.[0] ?? "";
              seedRange(variable);
              refresh();
            })
          ),
      h(
        "div",
        { class: "col-md-3" },
        h("label", { class: "form-label small mb-0" }, "Field"),
        select(fields.length ? fields : [["", "(no numeric fields)"]], variable.field, (value) => {
          variable.field = value;
          seedRange(variable);
          refresh();
        })
      ),
      h(
        "div",
        { class: "col-md-3 text-end" },
        h("div", { class: "small text-secondary" }, `Current: ${fmt(currentValue(variable) ?? NaN, 4)}`),
        button("Remove", () => {
          state.variables.splice(index, 1);
          refresh();
        })
      )
    ),
    h(
      "div",
      { class: "row g-2 align-items-end mt-1" },
      h(
        "div",
        { class: "col-md-2" },
        h("label", { class: "form-label small mb-0" }, "Values"),
        select(
          [
            ["range", "Range"],
            ["list", "List"],
          ],
          variable.mode,
          (value) => {
            variable.mode = value;
            refresh();
          }
        )
      ),
      variable.mode === "list"
        ? h(
            "div",
            { class: "col-md-6" },
            h("label", { class: "form-label small mb-0" }, "Values (comma-separated)"),
            textInput(variable.list, (value) => (variable.list = value))
          )
        : [
            ["From", "from"],
            ["To", "to"],
            ["Steps", "steps"],
          ].map(([label, key]) =>
            h(
              "div",
              { class: "col-md-2" },
              h("label", { class: "form-label small mb-0" }, label),
              numberInput(variable[key], (value) => (variable[key] = value ?? 0), key === "steps" ? { min: 1, step: 1 } : {})
            )
          ),
      h(
        "div",
        { class: "col-md-2 small text-secondary" },
        `${valuesOf(variable).length} values`
      )
    ),
    h("div", { class: "small text-secondary mt-1 font-monospace" }, pathOf(variable))
  );
}

function caseCount() {
  if (!state.variables.length) return 0;
  const counts = state.variables.map((variable) => valuesOf(variable).length);
  return state.design === "Full Factorial"
    ? counts.reduce((product, count) => product * count, 1)
    : 1 + counts.reduce((sum, count) => sum + count, 0);
}

function draw() {
  const result = state.result;
  const chart = h("div", { class: "sn-chart", style: { height: "360px" } });
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-xl-6" },
        h("h6", {}, "Variables"),
        h(
          "div",
          { class: "form-text mb-2" },
          "Each variable sets a numeric field of the scenario to each of its values. Each case is " +
            "simulated with the variables set; other fields keep their values."
        ),
        state.variables.map(variableRow),
        h(
          "div",
          { class: "d-flex gap-2 align-items-center" },
          button("Add Variable", () => {
            state.variables.push(newVariable());
            draw();
          }),
          h(
            "div",
            { style: { width: "12rem" } },
            select(["Full Factorial", "One at a Time"], state.design, (value) => {
              state.design = value;
              draw();
            })
          ),
          h("span", { class: "small text-secondary" }, `${caseCount()} cases`),
          button(state.running ? "Running…" : "Run Trade Study", run, "primary", {
            disabled: state.running || !state.variables.length,
          })
        )
      ),
      h(
        "div",
        { class: "col-xl-6" },
        result
          ? [
              h(
                "div",
                { class: "row g-2 mb-1" },
                h(
                  "div",
                  { class: "col-md-8" },
                  h("label", { class: "form-label small mb-0" }, "Metric"),
                  select(
                    result.metrics.map((metric) => [metric, METRIC_LABELS[metric] ?? metric]),
                    state.metric,
                    (value) => {
                      state.metric = value;
                      draw();
                    }
                  )
                )
              ),
              chart,
            ]
          : h("div", { class: "sn-muted-box" }, "Define variables and run the trade study to compare its cases.")
      )
    ),
    ...(result ? [resultTable(result)] : []),
    reliabilitySection()
  );
  if (result) drawChart(chart, result);
  drawHistogram();
}

/** Line chart of the metric against the first variable (one line per value of the second). */
function drawChart(chart, result) {
  const [first, second] = result.variables;
  const metric = state.metric;
  const ok = result.cases.filter((item) => !item.error);
  const groups = new Map();
  for (const item of ok) {
    const key = second === undefined ? "" : String(item.values[second]);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  const traces = [...groups.entries()].slice(0, SERIES.length).map(([key, items], index) => {
    items.sort((a, b) => a.values[first] - b.values[first]);
    return {
      x: items.map((item) => item.values[first]),
      y: items.map((item) => item.metrics[metric]),
      name: second === undefined ? METRIC_LABELS[metric] ?? metric : `${second} = ${fmt(Number(key), 4)}`,
      mode: "lines+markers",
      line: { color: SERIES[index], width: 2 },
      marker: { size: 8, color: SERIES[index], line: { color: "#ffffff", width: 2 } },
      hovertemplate: `${first} = %{x:.4g}<br>%{y:,.4g}<extra></extra>`,
    };
  });
  plot(chart, traces, {
    xaxis: { title: { text: first } },
    yaxis: { title: { text: METRIC_LABELS[metric] ?? metric } },
    hovermode: "closest",
    showlegend: traces.length > 1,
  });
}

function resultTable(result) {
  return h(
    "div",
    { class: "mt-3" },
    h("h6", {}, `Cases (${result.cases.length})`),
    h(
      "div",
      { class: "table-responsive sn-scroll border rounded" },
      h(
        "table",
        { class: "table table-sm sn-table small mb-0" },
        h(
          "thead",
          {},
          h(
            "tr",
            {},
            h("th", {}, "#"),
            result.variables.map((name) => h("th", { class: "text-end" }, name)),
            result.metrics.map((metric) => h("th", { class: "text-end" }, METRIC_LABELS[metric] ?? metric))
          )
        ),
        h(
          "tbody",
          {},
          result.cases.map((item) =>
            h(
              "tr",
              { class: item.error || item.metrics.errorCount > 0 ? "table-warning" : "" },
              h("td", {}, item.index + 1),
              result.variables.map((name) => h("td", { class: "text-end" }, fmt(item.values[name], 4))),
              item.error
                ? h("td", { colspan: result.metrics.length, class: "text-danger" }, item.error)
                : result.metrics.map((metric) => h("td", { class: "text-end" }, fmt(item.metrics[metric], 2)))
            )
          )
        )
      )
    ),
    h("div", { class: "form-text" }, "Cases with simulation errors (e.g., insufficient delta-v) are highlighted.")
  );
}

// --------------------------------------------------------- reliability

let histogram = null; // chart element of the selected part

async function runReliability() {
  const reliability = state.reliability;
  reliability.running = true;
  draw();
  try {
    reliability.result = await api.runMonteCarlo(store.scenario, {
      runs: Math.max(1, Math.round(reliability.runs)),
      seed: Math.max(0, Math.round(reliability.seed)),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    toast(`The reliability study could not run: ${error.message}`, "danger");
  } finally {
    reliability.running = false;
  }
  draw();
}

/** Parts with a mean time to failure in the element templates of the scenario. */
function failingParts() {
  return (store.scenario.elementTemplates ?? []).flatMap((template) =>
    (template.parts ?? []).filter((part) => part.meanTimeToFailure).map((part) => [template, part])
  );
}

function reliabilitySection() {
  const reliability = state.reliability;
  const result = reliability.result;
  const parts = result?.parts ?? [];
  if (!parts.some((part) => part.part === reliability.part)) reliability.part = parts[0]?.part ?? null;
  histogram = parts.length ? h("div", { class: "sn-chart", style: { height: "280px" } }) : null;
  const count = failingParts().length;
  return h(
    "div",
    { class: "mt-4 pt-3 border-top" },
    h("h6", {}, "Monte Carlo Reliability"),
    h(
      "div",
      { class: "form-text mb-2" },
      "Simulates the scenario repeatedly with random failures of parts which define a mean time to failure " +
        "(each unit fails at a constant rate while its element is active, for its duty cycle). A failure " +
        "demands a spare at the location of the element; a shortfall is a failure without an available spare. " +
        `The element templates define ${count} failing part${count === 1 ? "" : "s"}.`
    ),
    h(
      "div",
      { class: "d-flex gap-2 align-items-end flex-wrap mb-2" },
      h(
        "div",
        { style: { width: "8rem" } },
        h("label", { class: "form-label small mb-0" }, "Runs"),
        numberInput(reliability.runs, (value) => (reliability.runs = value ?? 100), { min: 1, max: 1000 })
      ),
      h(
        "div",
        { style: { width: "8rem" } },
        h("label", { class: "form-label small mb-0" }, "Seed"),
        numberInput(reliability.seed, (value) => (reliability.seed = value ?? 0), { min: 0 })
      ),
      button(reliability.running ? "Running…" : "Run Monte Carlo", runReliability, "primary", {
        disabled: reliability.running || count === 0,
      })
    ),
    result
      ? h(
          "div",
          { class: "row g-3" },
          h(
            "div",
            { class: "col-xl-6" },
            h(
              "div",
              { class: "mb-2" },
              h("span", { class: "fs-5 fw-semibold me-2" }, `${fmt(100 * result.shortfallProbability, 1)}%`),
              h(
                "span",
                { class: "text-secondary small" },
                `of ${result.runs - result.failedRuns} runs exhaust the spares of at least one part` +
                  (result.failedRuns ? ` (${result.failedRuns} runs failed)` : "")
              )
            ),
            reliabilityTable(parts)
          ),
          h(
            "div",
            { class: "col-xl-6" },
            parts.length
              ? [
                  h(
                    "div",
                    { class: "row g-2 mb-1" },
                    h(
                      "div",
                      { class: "col-md-8" },
                      h("label", { class: "form-label small mb-0" }, "Part"),
                      select(
                        parts.map((part) => [part.part, part.part]),
                        reliability.part,
                        (value) => {
                          reliability.part = value;
                          draw();
                        }
                      )
                    )
                  ),
                  histogram,
                ]
              : h("div", { class: "sn-muted-box" }, "No parts operated during the simulation.")
          )
        )
      : null
  );
}

function reliabilityTable(parts) {
  const reliability = state.reliability;
  const cell = (value, warn = false) =>
    h("td", { class: `text-end ${warn ? "text-danger fw-semibold" : ""}` }, value);
  return h(
    "div",
    { class: "table-responsive" },
    h(
      "table",
      { class: "table table-sm sn-table small mb-0" },
      h(
        "thead",
        {},
        h(
          "tr",
          {},
          ["Part", "Expected", "Mean", "95th pct.", "Max", "P(shortfall)", "Mean shortfall"].map((label, i) =>
            h("th", { class: i > 0 ? "text-end" : "" }, label)
          )
        )
      ),
      h(
        "tbody",
        {},
        parts.map((part) =>
          h(
            "tr",
            {
              class: part.part === reliability.part ? "table-active" : "",
              style: { cursor: "pointer" },
              title: part.elements.join(", "),
              onClick: () => {
                reliability.part = part.part;
                draw();
              },
            },
            h("td", {}, part.part),
            cell(fmt(part.expected, 2)),
            cell(fmt(part.mean, 2)),
            cell(fmt(part.percentiles["95"], 0)),
            cell(fmt(part.max, 0)),
            cell(`${fmt(100 * part.shortfallProbability, 1)}%`, part.shortfallProbability > 0.05),
            cell(fmt(part.meanShortfall, 2))
          )
        )
      )
    ),
    h(
      "div",
      { class: "form-text" },
      "Failures per run. Expected is the mean of the failure distribution; shortfall probabilities above 5% are highlighted."
    )
  );
}

/** Bar chart of the number of runs by number of failures of the selected part. */
function drawHistogram() {
  const reliability = state.reliability;
  const part = reliability.result?.parts.find((item) => item.part === reliability.part);
  if (!histogram || !part) return;
  const total = part.histogram.reduce((sum, count) => sum + count, 0) || 1;
  plot(
    histogram,
    [
      {
        type: "bar",
        x: part.histogram.map((_, failures) => failures),
        y: part.histogram,
        customdata: part.histogram.map((count) => (100 * count) / total),
        name: part.part,
        marker: { color: SERIES[0], cornerradius: 4 },
        hovertemplate: "%{x} failures: %{y} runs (%{customdata:.1f}%)<extra></extra>",
      },
    ],
    {
      xaxis: { title: { text: `Failures of ${part.part}` }, dtick: 1 },
      yaxis: { title: { text: "Runs" }, rangemode: "tozero" },
      bargap: 0.2,
      showlegend: false,
    }
  );
}
