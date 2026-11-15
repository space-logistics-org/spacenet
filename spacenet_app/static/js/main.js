// Entry point: loads the scenario, connects the header and menu, and
// switches between tabs.

import { api, ApiError } from "./api.js";
import { openOptions } from "./dialogs/options.js";
import { store } from "./store.js";
import * as demands from "./tabs/demands.js";
import * as manifest from "./tabs/manifest.js";
import * as missions from "./tabs/missions.js";
import * as network from "./tabs/network.js";
import * as simulation from "./tabs/simulation.js";
import { confirmDialog, download, fromInputDate, toast, toInputDate } from "./util.js";

const tabs = { network, missions, demands, manifest, simulation };
let active = "network";

const $ = (id) => document.getElementById(id);

function showTab(name, { force = false } = {}) {
  const scenario = store.scenario;
  if (!force && name !== "network" && !scenario.network.nodes.length) {
    toast("At least one network node is required.", "warning");
    name = "network";
  } else if (
    !force &&
    ["demands", "manifest", "simulation"].includes(name) &&
    !scenario.missionList.length
  ) {
    toast("At least one mission is required.", "warning");
    name = "missions";
  }
  active = name;
  for (const link of document.querySelectorAll("#tabs .nav-link")) {
    link.classList.toggle("active", link.dataset.tab === name);
  }
  for (const key of Object.keys(tabs)) $(`tab-${key}`).hidden = key !== name;
  if (location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
  tabs[name].render({ shown: true });
}

function renderHeader() {
  const scenario = store.scenario;
  const fields = {
    "scenario-name": scenario.name,
    "scenario-start": toInputDate(scenario.startDate),
    "scenario-author": scenario.createdBy,
    "scenario-description": scenario.description ?? "",
  };
  for (const [id, value] of Object.entries(fields)) {
    // do not disturb a field which is being edited
    if (document.activeElement !== $(id)) $(id).value = value;
  }
  document.title = `SpaceNet | ${scenario.name}`;
}

function renderStatus() {
  const problem = store.problem;
  const analysis = store.analysis;
  $("problem").hidden = !problem;
  if (problem) {
    $("problem").textContent = `The scenario cannot be analyzed until this is fixed: ${problem.message}`;
  }
  let text = "";
  if (analysis && !problem) {
    const errors = analysis.missions.reduce((sum, mission) => sum + mission.errorCount, 0);
    text = errors ? `${errors} mission error${errors === 1 ? "" : "s"}` : "No mission errors";
  }
  $("status").textContent = (store.dirty ? "Unsaved changes · " : "") + text;
}

function bindHeader() {
  const bind = (id, apply) =>
    $(id).addEventListener("input", () => store.update((scenario) => apply(scenario, $(id).value)));
  bind("scenario-name", (scenario, value) => (scenario.name = value));
  bind("scenario-author", (scenario, value) => (scenario.createdBy = value));
  bind("scenario-description", (scenario, value) => (scenario.description = value || null));
  bind("scenario-start", (scenario, value) => {
    const date = fromInputDate(value);
    if (date) scenario.startDate = date;
  });
}

async function confirmDiscard() {
  if (!store.dirty) return true;
  return confirmDialog("Unsaved Changes", "Discard the changes to the current scenario?");
}

async function openScenario(file) {
  try {
    const scenario = await api.validate(JSON.parse(await file.text()));
    store.setScenario(scenario);
    showTab(scenario.network.nodes.length ? "missions" : "network", { force: true });
    toast(`Opened ${file.name}`, "success");
  } catch (error) {
    toast(`Could not open ${file.name}: ${error.message}`, "danger");
  }
}

function bindMenu() {
  $("action-new").addEventListener("click", async () => {
    if (!(await confirmDiscard())) return;
    store.setScenario(await api.defaults());
    showTab("network", { force: true });
  });
  $("action-open").addEventListener("click", async () => {
    if (await confirmDiscard()) $("file-scenario").click();
  });
  $("file-scenario").addEventListener("change", async (event) => {
    const [file] = event.target.files;
    event.target.value = "";
    if (file) await openScenario(file);
  });
  $("action-save").addEventListener("click", () => {
    const scenario = store.scenario;
    const name = (scenario.name || "scenario").replace(/[^\w.-]+/g, "_");
    download(`${name}.json`, JSON.stringify(scenario, null, 2));
    store.dirty = false;
    renderStatus();
  });
  $("action-database").addEventListener("click", () => $("file-database").click());
  $("file-database").addEventListener("change", async (event) => {
    const [file] = event.target.files;
    event.target.value = "";
    if (!file) return;
    try {
      const database = await api.loadDatabase(file);
      store.setDatabase(database);
      toast(
        `Loaded ${database.nodes.length} nodes, ${database.edges.length} edges, ` +
          `${database.resources.length} resources, and ${database.elements.length} elements.`,
        "success"
      );
    } catch (error) {
      toast(`Could not load ${file.name}: ${error.message}`, "danger");
    }
  });
  $("action-options").addEventListener("click", openOptions);
}

async function start() {
  [store.enums, store.schema] = await Promise.all([api.enums(), api.schema()]);
  for (const [name, tab] of Object.entries(tabs)) tab.init($(`tab-${name}`), { showTab });
  bindHeader();
  bindMenu();
  store.on("change", () => {
    renderHeader();
    renderStatus();
    tabs[active].render({});
  });
  store.on("analysis", () => {
    renderStatus();
    tabs[active].render({ analysis: true });
  });
  for (const link of document.querySelectorAll("#tabs .nav-link")) {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      showTab(link.dataset.tab);
    });
  }
  window.addEventListener("beforeunload", (event) => {
    if (store.dirty) event.preventDefault();
  });

  // restore the scenario of the previous session if it is still valid
  let scenario = null;
  const saved = store.restore();
  if (saved) {
    try {
      scenario = await api.validate(saved);
    } catch (error) {
      if (!(error instanceof ApiError)) throw error;
      // keep an invalid scenario so it can be repaired
      scenario = error.detail.some((item) => item.type === "scenario_error") ? saved : null;
    }
  }
  store.setScenario(scenario || (await api.defaults()));
  const requested = location.hash.slice(1);
  showTab(tabs[requested] ? requested : "network");
}

start().catch((error) => {
  console.error(error);
  toast(`The application could not start: ${error.message}`, "danger");
});
