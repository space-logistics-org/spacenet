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
import { createHistory } from "../history.js";
import { drawNetwork } from "../networkMap.js";
import { store } from "../store.js";
import { button, checkbox, clear, download, fmt, formatDate, h, numberInput, select, toast } from "../util.js";

const VIEWS = [
  ["network", "Network History"],
  ["measures", "Measures History"],
  ["locations", "Location History"],
  ["elements", "Element History"],
  ["propellant", "Propellant"],
  ["flows", "Flows"],
  ["power", "Power"],
  ["isru", "ISRU"],
  ["cost", "Cost"],
  ["timeline", "Timeline"],
];

// categorical series colors in fixed order (validated for color vision
// deficiencies on the light surface; values are also shown in tables)
const SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"];

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
  history: null, // view of the history of the result (see history.js)
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
  propellantVehicle: null,
  powerGroup: null,
  isruProcess: null,
  flowResource: "",
  timelineCrew: false,
  tankers: {
    required: 1_200_000,
    tankerDelivery: 150_000,
    depotCapacity: 1_500_000,
    initial: 0,
    boiloffRate: 0.0005,
    intervalDays: 6,
    loiterDays: 1,
    transferLoss: 0.01,
  },
  sizing: null,
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
      history: null,
      error: null,
      outdated: false,
      frame: 0,
      location: null,
      element: null,
      locationFilter: null,
      historyLocation: null,
      historyElement: null,
      propellantVehicle: null,
      powerGroup: null,
      isruProcess: null,
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
    state.history = createHistory(result);
    state.frame = Math.min(state.frame, state.history.length - 1);
    state.locationFilter = null;
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    state.error = error;
    state.result = null;
    state.history = null;
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
  const frames = state.history.length;
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
  else if (state.view === "locations") drawMassHistory(content, state.history.masses().locations, "historyLocation", "Location");
  else if (state.view === "propellant") drawPropellant(content, result);
  else if (state.view === "power") drawPower(content, result);
  else if (state.view === "isru") drawISRU(content, result);
  else if (state.view === "flows") drawFlows(content, result);
  else if (state.view === "cost") drawCost(content, result);
  else if (state.view === "timeline") drawTimeline(content, result);
  else drawMassHistory(content, state.history.masses().elements, "historyElement", "Element");
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
    ["Propellant burned", fmt(values.propellantBurnedMass ?? 0, 0), "kg"],
    ["Propellant boiloff", fmt(values.propellantBoiloffMass ?? 0, 0), "kg"],
    ["Propellant transfer losses", fmt(values.propellantTransferLossMass ?? 0, 0), "kg"],
    ["Energy deficit", fmt(values.energyDeficit ?? 0, 0), "kWh"],
    ["ISRU production", fmt(values.isruOutputMass ?? 0, 0), "kg"],
    ["ISRU energy", fmt(values.isruEnergy ?? 0, 0), "kWh"],
    ["Campaign cost", fmt(values.campaignCost ?? 0, 0), "$M"],
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
  const frames = state.history.length;
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
  const snapshot = state.history.frame(state.frame);
  if (!snapshot) return;
  slider.value = state.frame;
  label.textContent =
    `${formatDate(dateOf(snapshot.time))} · day ${fmt(snapshot.time, 2)} · ` +
    `step ${state.frame + 1} of ${state.history.length}`;
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

// --------------------------------------------------------------- propellant

const BUDGET_COLUMNS = [
  ["loaded", "Loaded"],
  ["added", "Added"],
  ["transferredIn", "Transfer in"],
  ["transferredOut", "Transfer out"],
  ["transferLoss", "Transfer loss"],
  ["burned", "Burned"],
  ["boiloff", "Boiloff"],
  ["consumed", "Consumed"],
  ["residual", "Residual"],
];

// propellant losses which are compared across vehicles
const USES = [
  ["boiloff", "Boiloff"],
  ["transferLoss", "Transfer loss"],
];

/** Groups the tank histories and budgets of a propellant analysis by vehicle. */
function propellantVehicles(propellant) {
  const vehicles = new Map();
  for (const budget of propellant.budgets) {
    const vehicle = vehicles.get(budget.vehicleId) ?? {
      id: budget.vehicleId,
      name: budget.vehicleName,
      budgets: [],
      tanks: [],
      uses: Object.fromEntries(USES.map(([key]) => [key, 0])),
      transferred: 0,
    };
    vehicle.budgets.push(budget);
    for (const [key] of USES) vehicle.uses[key] += budget[key] * budget.unitMass;
    vehicle.transferred += (budget.transferredIn + budget.transferredOut) * budget.unitMass;
    vehicles.set(budget.vehicleId, vehicle);
  }
  for (const tank of propellant.tanks) vehicles.get(tank.vehicleId)?.tanks.push(tank);
  return [...vehicles.values()];
}

function drawPropellant(content, result) {
  frameParts = null;
  const propellant = result.propellant ?? { tanks: [], budgets: [], totals: {} };
  const vehicles = propellantVehicles(propellant).filter((vehicle) =>
    vehicle.budgets.some((budget) => budget.maxAmount > 0)
  );
  if (!vehicles.length) {
    content.append(h("div", { class: "sn-muted-box" }, "No vehicles with propellant tanks."));
    return;
  }
  if (!vehicles.some((vehicle) => vehicle.id === state.propellantVehicle)) {
    // default to the vehicle which receives the most propellant (e.g., a lander)
    const ranked = [...vehicles].sort((a, b) => b.transferred - a.transferred);
    state.propellantVehicle = ranked[0].id;
  }
  const vehicle = vehicles.find((item) => item.id === state.propellantVehicle);
  const levels = h("div", { class: "sn-chart" });
  const uses = h("div");
  content.append(
    h(
      "div",
      { class: "row g-2 mb-1" },
      h(
        "div",
        { class: "col-md-6" },
        h("label", { class: "form-label small mb-0" }, "Vehicle"),
        select(
          vehicles.map((item) => [item.id, item.name]),
          state.propellantVehicle,
          (value) => {
            state.propellantVehicle = value;
            draw();
          }
        )
      ),
      h(
        "div",
        { class: "col-md-6 d-flex align-items-end justify-content-end" },
        button("Export budgets (CSV)", exportPropellant)
      )
    ),
    h("h6", { class: "mt-2 mb-0" }, `Tank contents: ${vehicle.name}`),
    levels,
    budgetTable(vehicle),
    h("h6", { class: "mt-3" }, "Propellant losses by vehicle"),
    uses,
    tankerCard()
  );
  drawTankLevels(levels, vehicle);
  drawUses(uses, vehicles);
}

/** Line chart of the contents (kg) of each tank of a vehicle with its capacity. */
function drawTankLevels(chart, vehicle) {
  const traces = [];
  vehicle.tanks.forEach((tank, index) => {
    const color = SERIES[index % SERIES.length];
    const name = `${tank.tank} (${tank.resource ?? "empty"})`;
    const x = tank.points.map((point) => dateOf(point[0]));
    traces.push({
      x,
      y: tank.points.map((point) => point[1] * tank.unitMass),
      name,
      legendgroup: name,
      mode: "lines",
      line: { color, width: 2 },
      hovertemplate: `${name}: %{y:,.0f} kg<extra></extra>`,
    });
    if (x.length) {
      traces.push({
        x: [x[0], x[x.length - 1]],
        y: [tank.maxAmount * tank.unitMass, tank.maxAmount * tank.unitMass],
        name: `${name} capacity`,
        legendgroup: name,
        showlegend: false,
        mode: "lines",
        line: { color, width: 1, dash: "dash" },
        hovertemplate: `${name} capacity: %{y:,.0f} kg<extra></extra>`,
      });
    }
  });
  plot(chart, traces, {
    xaxis: { type: "date" },
    yaxis: { title: { text: "Contents (kg)" }, rangemode: "tozero" },
    hovermode: "x unified",
    showlegend: true,
  });
}

/** Table of the propellant budget (kg) of each tank of a vehicle. */
function budgetTable(vehicle) {
  const cell = (value) => h("td", { class: "text-end" }, fmt(value, 0));
  return h(
    "div",
    { class: "table-responsive" },
    h(
      "table",
      { class: "table table-sm sn-table small mb-0" },
      h(
        "thead",
        {},
        h("tr", {}, h("th", {}, "Tank (kg)"), BUDGET_COLUMNS.map(([, label]) => h("th", { class: "text-end" }, label)))
      ),
      h(
        "tbody",
        {},
        vehicle.budgets.map((budget) =>
          h(
            "tr",
            {},
            h("td", {}, `${budget.tank} (${budget.resource ?? "empty"})`),
            BUDGET_COLUMNS.map(([key]) => cell(budget[key] * budget.unitMass))
          )
        )
      )
    ),
    h(
      "div",
      { class: "form-text" },
      "Loaded + added + transfer in − transfer out − transfer loss − burned − boiloff − consumed = residual. " +
        "Boiloff is a fraction of the tank capacity per day (not applied on the surface of Earth)."
    )
  );
}

/** Horizontal stacked bars of the propellant lost by each vehicle. */
function drawUses(container, vehicles) {
  const limit = 15;
  const ranked = vehicles
    .map((vehicle) => ({ ...vehicle, total: USES.reduce((sum, [key]) => sum + vehicle.uses[key], 0) }))
    .filter((vehicle) => vehicle.total > 0)
    .sort((a, b) => b.total - a.total);
  const shown = ranked.slice(0, limit);
  const others = ranked.slice(limit);
  if (others.length) {
    shown.push({
      name: `Other (${others.length} vehicles)`,
      uses: Object.fromEntries(USES.map(([key]) => [key, others.reduce((sum, v) => sum + v.uses[key], 0)])),
    });
  }
  if (!shown.length) {
    container.replaceChildren(h("div", { class: "small text-secondary" }, "No boiloff or transfer losses."));
    return;
  }
  const chart = h("div", { style: { height: `${Math.max(160, 26 * shown.length + 70)}px` } });
  container.replaceChildren(chart);
  // largest at the top
  const names = shown.map((vehicle) => vehicle.name).reverse();
  plot(
    chart,
    USES.map(([key, label], index) => ({
      type: "bar",
      orientation: "h",
      name: label,
      y: names,
      x: [...shown].reverse().map((vehicle) => vehicle.uses[key]),
      marker: { color: SERIES[index], line: { color: "#ffffff", width: 1 } },
      hovertemplate: `%{y}<br>${label}: %{x:,.0f} kg<extra></extra>`,
    })),
    {
      barmode: "stack",
      bargap: 0.35,
      margin: { l: 20, r: 20, t: 10, b: 40 },
      xaxis: { title: { text: "Propellant mass lost (kg)" } },
      yaxis: { automargin: true },
      legend: { orientation: "h", y: 1.08, x: 0, traceorder: "normal" },
    }
  );
}

async function exportPropellant() {
  try {
    const { name, text } = await api.exportText("propellant", { scenario: store.scenario });
    download(name, text, "text/csv");
  } catch (error) {
    toast(`Export failed: ${error.message}`, "danger");
  }
}

/** Card to size a tanker campaign which aggregates propellant in a depot. */
function tankerCard() {
  const params = state.tankers;
  const output = h("div");
  const chart = h("div", { style: { height: "220px", display: "none" } });
  const input = (label, key, scale = 1, attrs = {}) =>
    h(
      "div",
      { class: "col-md-3" },
      h("label", { class: "form-label small mb-0" }, label),
      numberInput(params[key] === null ? null : params[key] / scale, (value) => {
        params[key] = value === null ? null : value * scale;
      }, { min: 0, ...attrs })
    );

  async function run() {
    try {
      state.sizing = await api.sizeTankers(params);
    } catch (error) {
      state.sizing = { error: error.message };
    }
    show();
  }

  function show() {
    const sizing = state.sizing;
    chart.style.display = sizing && !sizing.error ? "" : "none";
    if (!sizing) {
      output.replaceChildren();
      return;
    }
    if (sizing.error) {
      output.replaceChildren(h("div", { class: "alert alert-danger py-1 small" }, sizing.error));
      return;
    }
    output.replaceChildren(
      h(
        "div",
        { class: sizing.feasible ? "small" : "alert alert-warning py-1 small" },
        sizing.feasible
          ? h(
              "span",
              {},
              h("span", { class: "fw-semibold" }, `${sizing.flights} tanker flight${sizing.flights === 1 ? "" : "s"}`),
              ` deliver ${fmt(sizing.delivered, 0)} kg; ${fmt(sizing.boiloff, 0)} kg boils off and ` +
                `${fmt(sizing.transferLoss, 0)} kg is lost in transfer, leaving ${fmt(sizing.final, 0)} kg at departure.`
            )
          : `Infeasible: ${sizing.reason}`
      )
    );
    plot(
      chart,
      [
        {
          x: sizing.timeline.map((point) => point[0]),
          y: sizing.timeline.map((point) => point[1]),
          name: "Depot contents",
          mode: "lines+markers",
          marker: { size: 8, color: SERIES[0], line: { color: "#ffffff", width: 2 } },
          line: { color: SERIES[0], width: 2 },
          hovertemplate: "Day %{x:.1f}: %{y:,.0f} kg<extra></extra>",
        },
        {
          x: [0, sizing.timeline.at(-1)?.[0] ?? 0],
          y: [params.required, params.required],
          name: "Required",
          mode: "lines",
          line: { color: "#52514e", width: 1, dash: "dash" },
          hovertemplate: "Required: %{y:,.0f} kg<extra></extra>",
        },
      ],
      {
        margin: { l: 70, r: 20, t: 10, b: 40 },
        xaxis: { title: { text: "Days after the first tanker flight" } },
        yaxis: { title: { text: "Depot contents (kg)" }, rangemode: "tozero" },
        showlegend: true,
      }
    );
  }

  const card = h(
    "div",
    { class: "card mt-3" },
    h(
      "div",
      { class: "card-body py-2" },
      h("h6", { class: "card-title" }, "Tanker campaign sizing"),
      h(
        "div",
        { class: "form-text mb-2" },
        "Estimates the tanker flights needed to aggregate propellant in a depot, accounting for boiloff " +
          "between flights (a fraction of the depot capacity per day) and transfer losses. " +
          "Verify the estimate by simulating a scenario with that many flights."
      ),
      h(
        "div",
        { class: "row g-2 mb-2" },
        input("Required at departure (kg)", "required"),
        input("Delivery per flight (kg)", "tankerDelivery"),
        input("Depot capacity (kg)", "depotCapacity"),
        input("Initial contents (kg)", "initial"),
        input("Boiloff (%/day)", "boiloffRate", 0.01, { max: 100 }),
        input("Days between flights", "intervalDays"),
        input("Days before departure", "loiterDays"),
        input("Transfer loss (%)", "transferLoss", 0.01, { max: 99.9 })
      ),
      button("Size tanker campaign", run, "primary"),
      h("div", { class: "mt-2" }, output),
      chart
    )
  );
  // charts are drawn once the card is in the document (to size them)
  requestAnimationFrame(show);
  return card;
}

// -------------------------------------------------------------------- power

/** Describes where a power group was located (one location or a count). */
function placeOf(group) {
  const places = [...new Set(group.locationNames)];
  return places.length === 1 ? places[0] : `${places.length} locations`;
}

/** Step points (x, y) of values which are constant over each interval. */
function intervalSteps(group, key) {
  const x = [];
  const customdata = [];
  const y = [];
  group.starts.forEach((start, i) => {
    x.push(dateOf(start), dateOf(group.ends[i]));
    y.push(group[key][i], group[key][i]);
    customdata.push(group.locationNames[i], group.locationNames[i]);
  });
  return { x, y, customdata };
}

function drawPower(content, result) {
  frameParts = null;
  const groups = result.power?.groups ?? [];
  if (!groups.length) {
    content.append(
      h(
        "div",
        { class: "sn-muted-box" },
        "No elements generate, consume, or store power (define power in the operational states of element templates)."
      )
    );
    return;
  }
  const id = (group) => group.key;
  if (!groups.some((group) => id(group) === state.powerGroup)) {
    // default to the group with the largest deficit or consumption
    const ranked = [...groups].sort(
      (a, b) => b.totalDeficit - a.totalDeficit || b.totalConsumed - a.totalConsumed
    );
    state.powerGroup = id(ranked[0]);
  }
  const group = groups.find((item) => id(item) === state.powerGroup);
  const powerChart = h("div", { class: "sn-chart", style: { height: "260px" } });
  const energyChart = h("div", { class: "sn-chart", style: { height: "240px" } });
  content.append(
    h(
      "div",
      { class: "row g-2 mb-1" },
      h(
        "div",
        { class: "col-md-6" },
        h("label", { class: "form-label small mb-0" }, "Power group"),
        select(
          groups.map((item) => [id(item), `${item.name} (${placeOf(item)})`]),
          state.powerGroup,
          (value) => {
            state.powerGroup = value;
            draw();
          }
        )
      ),
      h(
        "div",
        { class: "col-md-6 small text-secondary d-flex align-items-end" },
        group.elements.join(", ")
      )
    ),
    h("h6", { class: "mt-2 mb-0" }, "Power (kW)"),
    powerChart,
    h("h6", { class: "mt-2 mb-0" }, "Stored energy (kWh)"),
    energyChart,
    h("h6", { class: "mt-3" }, "Power groups"),
    powerTable(groups, id),
    h(
      "div",
      { class: "form-text" },
      "Night need is the energy to supply the load (less constant generation) through the longest " +
        "night at a solar-powered site. It is flagged only for groups which stay at a site for a full " +
        "day-night cycle (29.5 days on the Moon); shorter stays can be scheduled in sunlight."
    )
  );
  const generation = intervalSteps(group, "generation");
  const consumption = intervalSteps(group, "consumption");
  plot(
    powerChart,
    [
      {
        ...generation,
        name: "Generation",
        mode: "lines",
        line: { color: SERIES[0], width: 2 },
        hovertemplate: "Generation: %{y:,.1f} kW at %{customdata}<extra></extra>",
      },
      {
        ...consumption,
        name: "Consumption",
        mode: "lines",
        line: { color: SERIES[1], width: 2 },
        hovertemplate: "Consumption: %{y:,.1f} kW<extra></extra>",
      },
    ],
    {
      xaxis: { type: "date" },
      yaxis: { title: { text: "Power (kW)" }, rangemode: "tozero" },
      hovermode: "x unified",
      showlegend: true,
    }
  );
  const ends = group.ends.map(dateOf);
  const energyTraces = [
    {
      x: ends,
      y: group.energy,
      name: "Stored energy",
      mode: "lines+markers",
      marker: { size: 8, color: SERIES[0], line: { color: "#ffffff", width: 2 } },
      line: { color: SERIES[0], width: 2 },
      hovertemplate: "Stored: %{y:,.1f} kWh<extra></extra>",
    },
    {
      x: ends,
      y: group.capacity,
      name: "Capacity",
      mode: "lines",
      line: { color: SERIES[0], width: 1, dash: "dash" },
      hovertemplate: "Capacity: %{y:,.1f} kWh<extra></extra>",
    },
  ];
  if (group.nightEnergy > 0) {
    energyTraces.push({
      x: [ends[0], ends.at(-1)],
      y: [group.nightEnergy, group.nightEnergy],
      name: "Required for the longest night",
      mode: "lines",
      line: { color: "#52514e", width: 1, dash: "dot" },
      hovertemplate: "Longest night: %{y:,.1f} kWh<extra></extra>",
    });
  }
  if (group.deficit.some((value) => value > 0)) {
    energyTraces.push({
      type: "bar",
      x: ends,
      y: group.deficit,
      name: "Deficit",
      marker: { color: SERIES[1] },
      hovertemplate: "Deficit: %{y:,.1f} kWh<extra></extra>",
    });
  }
  plot(energyChart, energyTraces, {
    xaxis: { type: "date" },
    yaxis: { title: { text: "Energy (kWh)" }, rangemode: "tozero" },
    hovermode: "x unified",
    showlegend: true,
  });
}

/** Table of the energy totals of each power group. */
function powerTable(groups, id) {
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
          ["Group", "Location", "Generated (kWh)", "Consumed (kWh)", "Deficit (kWh)", "Night need / storage (kWh)"].map(
            (label, i) => h("th", { class: i > 1 ? "text-end" : "" }, label)
          )
        )
      ),
      h(
        "tbody",
        {},
        groups.map((group) =>
          h(
            "tr",
            {
              class: id(group) === state.powerGroup ? "table-active" : "",
              style: { cursor: "pointer" },
              onClick: () => {
                state.powerGroup = id(group);
                draw();
              },
            },
            h("td", {}, group.name),
            h("td", {}, placeOf(group)),
            cell(fmt(group.totalGenerated, 0)),
            cell(fmt(group.totalConsumed, 0)),
            cell(fmt(group.totalDeficit, 0), group.totalDeficit > 0),
            group.nightEnergy > 0
              ? cell(
                  `${fmt(group.nightEnergy, 0)} / ${fmt(Math.max(...group.capacity), 0)}`,
                  group.nightShortfall
                )
              : cell("—")
          )
        )
      )
    )
  );
}

// -------------------------------------------------------------------- flows

// the basic Plotly bundle has no Sankey traces: the full bundle (same
// version) is loaded the first time the flows are drawn
const FULL_PLOTLY = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js";
let fullPlotly = null;

function loadFullPlotly() {
  if (window.Plotly?.PlotSchema?.get?.().traces?.sankey) return Promise.resolve();
  fullPlotly ??= new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = FULL_PLOTLY;
    script.onload = resolve;
    script.onerror = () => {
      fullPlotly = null;
      reject(new Error("The charting library could not be loaded."));
    };
    document.head.append(script);
  });
  return fullPlotly;
}

const SOURCES = ["Loaded", "Added", "Produced"];
const SINKS = ["Burned", "Boiloff", "Transfer Loss", "Consumed", "Residual"];

/** Color of a resource (in the order of the resources of the scenario). */
function resourceColors(links) {
  const names = [...new Set(links.map((link) => link.resource))];
  const order = (store.scenario.resourceList ?? []).map((resource) => resource.name);
  names.sort((a, b) => order.indexOf(a) - order.indexOf(b));
  return new Map(names.map((name, i) => [name, i < SERIES_FULL.length ? SERIES_FULL[i] : "#8a8984"]));
}

// categorical palette (validated; values are also shown in the table)
const SERIES_FULL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];

function alpha(hex, opacity) {
  const value = parseInt(hex.slice(1), 16);
  return `rgba(${(value >> 16) & 255}, ${(value >> 8) & 255}, ${value & 255}, ${opacity})`;
}

function drawFlows(content, result) {
  frameParts = null;
  const all = result.propellant?.links ?? [];
  if (!all.length) {
    content.append(h("div", { class: "sn-muted-box" }, "No vehicle tanks hold propellant during the simulation."));
    return;
  }
  const colors = resourceColors(all);
  if (state.flowResource && !colors.has(state.flowResource)) state.flowResource = "";
  const links = all.filter((link) => !state.flowResource || link.resource === state.flowResource);
  const chart = h("div", { class: "sn-chart", style: { height: "520px" } });
  content.append(
    h(
      "div",
      { class: "row g-2 mb-1" },
      h(
        "div",
        { class: "col-md-4" },
        h("label", { class: "form-label small mb-0" }, "Resource"),
        select([["", "All resources"], ...[...colors.keys()].map((name) => [name, name])], state.flowResource, (value) => {
          state.flowResource = value;
          draw();
        })
      ),
      h(
        "div",
        { class: "col-md-8 d-flex flex-wrap gap-3 align-items-end small" },
        [...colors.entries()]
          .filter(([name]) => !state.flowResource || name === state.flowResource)
          .map(([name, color]) =>
            h(
              "span",
              { class: "d-inline-flex align-items-center gap-1" },
              h("span", {
                style: { width: "12px", height: "12px", borderRadius: "2px", background: color, display: "inline-block" },
              }),
              name
            )
          )
      )
    ),
    h(
      "div",
      { class: "form-text mb-1" },
      "Propellant mass (t) loaded into, transferred between, and burned, lost, or left in vehicle tanks over the " +
        "campaign. Vehicles of the same name in different missions are combined (e.g., all tankers)."
    ),
    chart,
    h("h6", { class: "mt-3" }, "Flows"),
    flowTable(links, colors)
  );
  const nodes = [...new Set(links.flatMap((link) => [link.source, link.target]))];
  const index = new Map(nodes.map((name, i) => [name, i]));
  const nodeColor = (name) => (SOURCES.includes(name) || SINKS.includes(name) ? "#8a8984" : "#52514e");
  const traces = [
    {
      type: "sankey",
      arrangement: "snap",
      valueformat: ",.1f",
      valuesuffix: " t",
      node: {
        label: nodes,
        color: nodes.map(nodeColor),
        pad: 18,
        thickness: 14,
        line: { color: "#ffffff", width: 1 },
        hovertemplate: "%{label}: %{value:,.1f} t<extra></extra>",
      },
      link: {
        source: links.map((link) => index.get(link.source)),
        target: links.map((link) => index.get(link.target)),
        value: links.map((link) => link.mass / 1000),
        color: links.map((link) => alpha(colors.get(link.resource), 0.45)),
        customdata: links.map((link) => link.resource),
        hovertemplate: "%{source.label} → %{target.label}<br>%{customdata}: %{value:,.1f} t<extra></extra>",
      },
    },
  ];
  chart.append(h("div", { class: "sn-muted-box mt-3" }, "Loading the flow chart…"));
  loadFullPlotly()
    .then(() => {
      if (!chart.isConnected) return;
      clear(chart);
      Plotly.react(chart, traces, { margin: { l: 8, r: 8, t: 8, b: 8 }, font: { size: 12 } }, {
        responsive: true,
        displaylogo: false,
      });
    })
    .catch((error) => {
      clear(chart).append(h("div", { class: "sn-muted-box mt-3" }, error.message));
    });
}

/** Table of the flows (largest first). */
function flowTable(links, colors) {
  return h(
    "div",
    { class: "table-responsive sn-scroll border rounded", style: { maxHeight: "320px" } },
    h(
      "table",
      { class: "table table-sm sn-table small mb-0" },
      h(
        "thead",
        {},
        h(
          "tr",
          {},
          ["From", "To", "Resource", "Mass (t)"].map((label, i) => h("th", { class: i === 3 ? "text-end" : "" }, label))
        )
      ),
      h(
        "tbody",
        {},
        links.map((link) =>
          h(
            "tr",
            {},
            h("td", {}, link.source),
            h("td", {}, link.target),
            h(
              "td",
              {},
              h("span", {
                style: {
                  width: "10px",
                  height: "10px",
                  borderRadius: "2px",
                  background: colors.get(link.resource),
                  display: "inline-block",
                  marginRight: "6px",
                },
              }),
              link.resource
            ),
            h("td", { class: "text-end" }, fmt(link.mass / 1000, 1))
          )
        )
      )
    )
  );
}

// --------------------------------------------------------------------- ISRU

/** Formats the mass of each resource of a map {name: kg}. */
function massList(masses) {
  const entries = Object.entries(masses ?? {});
  return entries.length ? entries.map(([name, mass]) => `${name} ${fmt(mass, 0)}`).join(", ") : "—";
}

function drawISRU(content, result) {
  frameParts = null;
  const processes = result.isru?.processes ?? [];
  if (!processes.length) {
    content.append(
      h(
        "div",
        { class: "sn-muted-box" },
        "No ISRU processes operate (add an ISRU Process demand model to an operational state of an element template)."
      )
    );
    return;
  }
  if (!processes.some((item) => item.key === state.isruProcess)) state.isruProcess = processes[0].key;
  const process = processes.find((item) => item.key === state.isruProcess);
  const outputChart = h("div", { class: "sn-chart", style: { height: "260px" } });
  const rateChart = h("div", { class: "sn-chart", style: { height: "200px" } });
  content.append(
    h(
      "div",
      { class: "row g-2 mb-1" },
      h(
        "div",
        { class: "col-md-6" },
        h("label", { class: "form-label small mb-0" }, "Process"),
        select(
          processes.map((item) => [item.key, `${item.process} (${item.elementName})`]),
          state.isruProcess,
          (value) => {
            state.isruProcess = value;
            draw();
          }
        )
      ),
      h(
        "div",
        { class: "col-md-6 small text-secondary d-flex align-items-end" },
        process.specificEnergy != null
          ? `${fmt(process.specificEnergy, 1)} kWh per kg of ${Object.keys(process.outputs)[0]}`
          : ""
      )
    ),
    h("h6", { class: "mt-2 mb-0" }, "Cumulative production (kg)"),
    outputChart,
    h("h6", { class: "mt-2 mb-0" }, "Rate (% of full rate)"),
    rateChart,
    h("h6", { class: "mt-3" }, "ISRU processes"),
    isruTable(processes),
    h(
      "div",
      { class: "form-text" },
      "A process operates at the rate allowed by its inputs, the storage for its outputs, and the power " +
        "remaining in its power group after other consumption (without discharging energy storage). " +
        "Outputs are stored in the element itself or in tanks and containers which hold the resource."
    )
  );
  const start = dateOf(process.starts[0]);
  const ends = process.ends.map(dateOf);
  plot(
    outputChart,
    Object.entries(process.outputs).map(([name, masses], i) => ({
      x: [start, ...ends],
      y: [0, ...masses],
      name,
      mode: "lines",
      line: { color: SERIES[i % SERIES.length], width: 2 },
      hovertemplate: `${name}: %{y:,.0f} kg<extra></extra>`,
    })),
    {
      xaxis: { type: "date" },
      yaxis: { title: { text: "Mass (kg)" }, rangemode: "tozero" },
      hovermode: "x unified",
      showlegend: Object.keys(process.outputs).length > 1,
    }
  );
  const x = [];
  const y = [];
  const customdata = [];
  process.starts.forEach((value, i) => {
    const limit = process.limit[i] ? `limited by ${process.limit[i].toLowerCase()}` : "full rate";
    x.push(dateOf(value), dateOf(process.ends[i]));
    y.push(100 * process.rate[i], 100 * process.rate[i]);
    customdata.push(limit, limit);
  });
  plot(
    rateChart,
    [
      {
        x,
        y,
        customdata,
        name: "Rate",
        mode: "lines",
        line: { color: SERIES[0], width: 2 },
        hovertemplate: "Rate: %{y:.0f}% (%{customdata})<extra></extra>",
      },
    ],
    {
      xaxis: { type: "date" },
      yaxis: { title: { text: "Rate (%)" }, range: [0, 105] },
      hovermode: "x unified",
      showlegend: false,
    }
  );
}

/** Table of the totals of each ISRU process. */
function isruTable(processes) {
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
          [
            "Process",
            "Element",
            "Produced (kg)",
            "Consumed (kg)",
            "Energy (kWh)",
            "kWh/kg",
            "Full-rate / active (days)",
            "Limited by (days)",
          ].map((label, i) => h("th", { class: i > 3 && i < 7 ? "text-end" : "" }, label))
        )
      ),
      h(
        "tbody",
        {},
        processes.map((process) => {
          const limits = Object.entries(process.limits ?? {});
          return h(
            "tr",
            {
              class: process.key === state.isruProcess ? "table-active" : "",
              style: { cursor: "pointer" },
              onClick: () => {
                state.isruProcess = process.key;
                draw();
              },
            },
            h("td", {}, process.process),
            h("td", {}, process.elementName),
            h("td", {}, massList(process.totalOutputs)),
            h("td", {}, massList(process.totalInputs)),
            cell(fmt(process.totalEnergy, 0)),
            cell(process.specificEnergy != null ? fmt(process.specificEnergy, 1) : "—"),
            cell(
              `${fmt(process.operatingDays, 0)} / ${fmt(process.duration, 0)}`,
              process.operatingDays < 0.5 * process.duration
            ),
            h(
              "td",
              {},
              limits.length ? limits.map(([limit, days]) => `${limit} ${fmt(days, 0)}`).join(", ") : "—"
            )
          );
        })
      )
    )
  );
}

// --------------------------------------------------------------------- cost

const COST_CATEGORIES = ["Element", "Transport"];

function drawCost(content, result) {
  frameParts = null;
  const cost = result.cost ?? { items: [], byMission: {}, byYear: {}, byCategory: {}, total: 0 };
  if (!cost.items.length) {
    content.append(
      h(
        "div",
        { class: "sn-muted-box" },
        "No costs: define unit costs of element templates and costs per transport of edges."
      )
    );
    return;
  }
  const chart = h("div", { class: "sn-chart", style: { height: "300px" } });
  // every year in the range (including years without costs)
  const costYears = Object.keys(cost.byYear).map(Number);
  const years = [];
  for (let year = Math.min(...costYears); year <= Math.max(...costYears); year++) years.push(year);
  const amount = (year, category) =>
    cost.items
      .filter((item) => item.year === year && item.category === category)
      .reduce((sum, item) => sum + item.amount, 0);
  const rows = Object.entries(cost.byMission);
  content.append(
    h("h6", { class: "mb-0" }, `Cost by year (total $${fmt(cost.total, 0)}M, then-year)`),
    chart,
    h("h6", { class: "mt-3" }, "Cost by mission"),
    h(
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
            h("th", {}, "Mission"),
            COST_CATEGORIES.map((category) => h("th", { class: "text-end" }, `${category} ($M)`)),
            h("th", { class: "text-end" }, "Total ($M)")
          )
        ),
        h(
          "tbody",
          {},
          rows.map(([mission, total]) =>
            h(
              "tr",
              {},
              h("td", {}, mission),
              COST_CATEGORIES.map((category) =>
                h(
                  "td",
                  { class: "text-end" },
                  fmt(
                    cost.items
                      .filter((item) => (item.mission ?? "(none)") === mission && item.category === category)
                      .reduce((sum, item) => sum + item.amount, 0),
                    0
                  )
                )
              ),
              h("td", { class: "text-end fw-semibold" }, fmt(total, 0))
            )
          )
        )
      )
    ),
    h(
      "div",
      { class: "form-text" },
      "Element costs are incurred when elements are created (unit costs of templates or instances); transport " +
        "costs for each transport along an edge (e.g., launch services). Amounts are as defined (then-year " +
        "US dollars, not inflation-adjusted)."
    )
  );
  plot(
    chart,
    COST_CATEGORIES.map((category, index) => ({
      type: "bar",
      name: category,
      x: years.map(String),
      y: years.map((year) => amount(year, category)),
      marker: { color: SERIES[index], line: { color: "#ffffff", width: 1 } },
      hovertemplate: `%{x}: ${category} $%{y:,.0f}M<extra></extra>`,
    })),
    {
      barmode: "stack",
      xaxis: { type: "category", title: { text: "Year" } },
      yaxis: { title: { text: "Cost ($M)" }, rangemode: "tozero" },
      legend: { orientation: "h", y: 1.1, x: 0, traceorder: "normal" },
    }
  );
}

// ----------------------------------------------------------------- timeline

const TIMELINE_CATEGORIES = [
  ["transit", "In transit", SERIES[0]],
  ["space", "In space (orbit)", SERIES[1]],
  ["surface", "Surface (beyond Earth)", SERIES[2]],
  ["earth", "Earth surface", "#a3a29c"],
];

/** Categorizes a location of the simulation result for the timeline. */
function timelineCategory(result, index) {
  const location = result.locations[index];
  if (!location) return "earth";
  if (location.isEdge) return "transit";
  const node = store.scenario.network.nodes.find((item) => item.id === location.id);
  if (node?.type !== "Surface Node") return "space";
  return node.body1 === "Earth" ? "earth" : "surface";
}

function drawTimeline(content, result) {
  frameParts = null;
  const all = state.history.segments();
  const elements = all.filter((element) => state.timelineCrew || !element.isCrew);
  const names = elements.map((element) => element.name);
  const chart = h("div", { style: { height: `${Math.max(240, 18 * elements.length + 90)}px` } });
  content.append(
    h(
      "div",
      { class: "d-flex align-items-center mb-1" },
      h("h6", { class: "mb-0 me-auto" }, `Element timeline (${elements.length} elements)`),
      checkbox("Show crew members", state.timelineCrew, (value) => {
        state.timelineCrew = value;
        draw();
      })
    ),
    chart,
    h(
      "div",
      { class: "form-text" },
      "Each bar shows where an element (or its top-level carrier) is between recorded time steps."
    )
  );
  // one trace per location category with segments separated by gaps
  const traces = TIMELINE_CATEGORIES.map(([key, label, color]) => {
    const trace = {
      name: label,
      x: [],
      y: [],
      text: [],
      mode: "lines",
      line: { color, width: 10 },
      hovertemplate: "%{y}<br>%{text}<extra></extra>",
      connectgaps: false,
    };
    for (const element of elements) {
      for (const segment of element.segments) {
        if (timelineCategory(result, segment.location) !== key) continue;
        const where = result.locations[segment.location]?.name ?? "?";
        const span = `${where}: ${formatDate(dateOf(segment.start))} to ${formatDate(dateOf(segment.end))}`;
        trace.x.push(dateOf(segment.start), dateOf(segment.end), null);
        trace.y.push(element.name, element.name, null);
        trace.text.push(span, span, null);
      }
    }
    return trace;
  }).filter((trace) => trace.x.length);
  plot(chart, traces, {
    margin: { l: 20, r: 20, t: 10, b: 40 },
    xaxis: { type: "date" },
    yaxis: { automargin: true, autorange: "reversed", categoryorder: "array", categoryarray: names },
    hovermode: "closest",
    legend: { orientation: "h", y: 1.02, yanchor: "bottom", x: 0 },
    showlegend: true,
  });
}
