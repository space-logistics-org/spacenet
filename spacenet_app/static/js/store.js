// Scenario store: the scenario being edited, the library of objects it can
// use, and the latest validation of its missions by the server.

import { api, ApiError, latest } from "./api.js";
import { clone, debounce } from "./util.js";

const SCENARIO_KEY = "spacenet.scenario";
const LIBRARY_KEY = "spacenet.library";

const listeners = {};

export const store = {
  /** Scenario being edited (as sent to and received from the server). */
  scenario: null,
  /** Model database loaded from a file: nodes, edges, resources, elements, demandModels. */
  database: { nodes: [], edges: [], resources: [], elements: [], demandModels: [] },
  /** Enumerations and JSON schema of scenarios. */
  enums: null,
  schema: null,
  /** Latest missions analysis (null until the scenario is first validated). */
  analysis: null,
  /** Error which prevents analysis of the scenario (ApiError or null). */
  problem: null,
  /** True, if the scenario has changes which were not saved to a file. */
  dirty: false,

  on(event, callback) {
    (listeners[event] ||= []).push(callback);
  },

  emit(event, ...args) {
    for (const callback of listeners[event] || []) callback(...args);
  },

  /** Changes the scenario and schedules its validation. */
  update(mutate) {
    mutate(this.scenario);
    this.dirty = true;
    this.emit("change");
    autosave();
    validate();
  },

  /** Replaces the scenario. */
  setScenario(scenario, { dirty = false } = {}) {
    this.scenario = scenario;
    this.scenario.manifest ||= { containers: [], loads: [] };
    this.scenario.manifest.containers ||= [];
    this.scenario.manifest.loads ||= [];
    this.analysis = null;
    this.problem = null;
    this.dirty = dirty;
    this.emit("scenario");
    this.emit("change");
    autosave();
    validateNow();
  },

  setDatabase(database) {
    this.database = { nodes: [], edges: [], resources: [], elements: [], demandModels: [], ...database };
    try {
      localStorage.setItem(LIBRARY_KEY, JSON.stringify(this.database));
    } catch {
      // the library is only kept for convenience
    }
    this.emit("change");
  },

  /** Restores the scenario and library saved by a previous session. */
  restore() {
    try {
      const database = JSON.parse(localStorage.getItem(LIBRARY_KEY));
      if (database) this.database = { ...this.database, ...database };
    } catch {
      // ignore
    }
    try {
      return JSON.parse(localStorage.getItem(SCENARIO_KEY));
    } catch {
      return null;
    }
  },

  // ------------------------------------------------------------- library

  /** Library objects: those of the scenario followed by those of the database. */
  library(kind) {
    const scenario = this.scenario;
    const own = {
      nodes: scenario.network.nodes,
      edges: scenario.network.edges,
      resources: scenario.resourceList,
      elements: scenario.elementTemplates,
      demandModels: scenario.demandModels,
    }[kind];
    // a database assigns new identifiers each time it is loaded, so objects
    // of the scenario also replace database objects with the same name
    const ids = new Set(own.map((item) => item.id));
    const names = new Set(own.map((item) => `${item.type}|${item.name}`));
    return [
      ...own,
      ...(this.database[kind] || []).filter(
        (item) => !ids.has(item.id) && !names.has(`${item.type}|${item.name}`)
      ),
    ];
  },

  node(id) {
    return this.scenario.network.nodes.find((node) => node.id === id);
  },

  edge(id) {
    return this.scenario.network.edges.find((edge) => edge.id === id);
  },

  location(id) {
    return this.node(id) || this.edge(id);
  },

  locationName(id) {
    return this.location(id)?.name ?? "?";
  },

  resource(id) {
    return this.library("resources").find((resource) => resource.id === id);
  },

  template(id) {
    return this.library("elements").find((template) => template.id === id);
  },

  instance(id) {
    return this.scenario.instantiatedElements.find((element) => element.id === id);
  },

  elementName(id) {
    return this.instance(id)?.name ?? "?";
  },

  className(id) {
    const item = this.enums.classesOfSupply.find((c) => c.id === Number(id));
    return item ? `${item.id} ${item.name}` : String(id);
  },

  /** Describes a resource amount (specific or generic). */
  resourceLabel(amount) {
    if (amount.resource) return this.resource(amount.resource)?.name ?? "?";
    return `Generic COS ${this.className(amount.classOfSupply)}`;
  },

  /**
   * Adds the library objects referenced by other objects of the scenario
   * (e.g., the template and resources of an added element) to the scenario.
   */
  include(kind, id) {
    const scenario = this.scenario;
    const target = {
      resources: scenario.resourceList,
      elements: scenario.elementTemplates,
      demandModels: scenario.demandModels,
    }[kind];
    if (!id || target.some((item) => item.id === id)) return;
    const item = (this.database[kind] || []).find((candidate) => candidate.id === id);
    if (!item) return;
    target.push(clone(item));
    // include objects referenced by unique identifier
    const text = JSON.stringify(item);
    for (const other of ["resources", "demandModels", "elements"]) {
      for (const candidate of this.database[other] || []) {
        if (candidate.id !== id && text.includes(candidate.id)) this.include(other, candidate.id);
      }
    }
  },

  /** Removes instantiated elements which are no longer referenced. */
  pruneInstances() {
    const scenario = this.scenario;
    const references = JSON.stringify([scenario.missionList, scenario.network]);
    let changed = true;
    while (changed) {
      changed = false;
      const contents = JSON.stringify(
        scenario.instantiatedElements.map((element) => element.contents || [])
      );
      const kept = scenario.instantiatedElements.filter(
        (element) => references.includes(element.id) || contents.includes(element.id)
      );
      if (kept.length < scenario.instantiatedElements.length) {
        scenario.instantiatedElements = kept;
        changed = true;
      }
    }
  },
};

const autosave = debounce(() => {
  try {
    localStorage.setItem(SCENARIO_KEY, JSON.stringify(store.scenario));
  } catch {
    // the saved copy is only kept for convenience
  }
}, 500);

const analyze = latest((signal, scenario) => api.analyzeMissions(scenario, signal));

async function validateNow() {
  const scenario = store.scenario;
  try {
    const analysis = await analyze(scenario);
    if (analysis === undefined || scenario !== store.scenario) return;
    store.analysis = analysis;
    store.problem = null;
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    store.problem = error;
  }
  store.emit("analysis");
}

const validate = debounce(validateNow, 400);

/** Gets the errors and warnings of an event from the latest analysis. */
export function eventIssues(missionIndex, eventIndex) {
  const event = store.analysis?.missions?.[missionIndex]?.events?.[eventIndex];
  return { errors: event?.errors ?? [], warnings: event?.warnings ?? [] };
}
