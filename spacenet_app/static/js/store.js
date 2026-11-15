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

  /** Objects of a kind (nodes, edges, resources, elements, demandModels) of the scenario. */
  collection(kind) {
    const scenario = this.scenario;
    return {
      nodes: scenario.network.nodes,
      edges: scenario.network.edges,
      resources: scenario.resourceList,
      elements: scenario.elementTemplates,
      demandModels: scenario.demandModels,
    }[kind];
  },

  /** True, if an object is part of the scenario (rather than only of the database). */
  owns(kind, id) {
    return this.collection(kind).some((item) => item.id === id);
  },

  /** Library objects: those of the scenario followed by those of the database. */
  library(kind) {
    const own = this.collection(kind);
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
    const target = this.collection(kind);
    if (!id || target.some((item) => item.id === id)) return;
    const item = (this.database[kind] || []).find((candidate) => candidate.id === id);
    if (!item) return;
    target.push(clone(item));
    this.includeReferences(item);
  },

  /** Adds the database objects referenced (by unique identifier) by an object to the scenario. */
  includeReferences(item) {
    const text = JSON.stringify(item);
    for (const other of ["nodes", "resources", "demandModels", "elements"]) {
      for (const candidate of this.database[other] || []) {
        if (candidate.id !== item.id && text.includes(candidate.id)) {
          this.include(other, candidate.id);
        }
      }
    }
  },

  // -------------------------------------------------------------- models

  /**
   * Saves an added or edited object model. Objects of the scenario and new
   * objects are saved to the scenario; other objects are saved to the
   * database kept by the browser.
   */
  saveModel(kind, model) {
    const stored = this.database[kind] || [];
    const index = stored.findIndex((item) => item.id === model.id);
    if (index >= 0 && !this.owns(kind, model.id)) {
      stored[index] = model;
      this.setDatabase(this.database);
      return;
    }
    this.update(() => {
      const own = this.collection(kind);
      const position = own.findIndex((item) => item.id === model.id);
      if (position >= 0) own[position] = model;
      else own.push(model);
      this.includeReferences(model);
    });
  },

  /** Removes an object model from the scenario or (if it is not part of it) the database. */
  removeModel(kind, id) {
    if (this.owns(kind, id)) {
      this.update(() => {
        const own = this.collection(kind);
        own.splice(own.findIndex((item) => item.id === id), 1);
      });
    } else {
      this.database[kind] = (this.database[kind] || []).filter((item) => item.id !== id);
      this.setDatabase(this.database);
    }
  },

  /** Lists the objects which reference an object model (and prevent its removal). */
  modelUses(kind, id) {
    const uses = [];
    const check = (label, items) => {
      for (const item of items || []) {
        if (item.id !== id && JSON.stringify(item).includes(id)) uses.push(`${label} ${item.name}`);
      }
    };
    const labels = [
      ["Node", "nodes"],
      ["Edge", "edges"],
      ["Resource", "resources"],
      ["Element", "elements"],
      ["Demand model", "demandModels"],
    ];
    if (!this.owns(kind, id)) {
      for (const [label, other] of labels) check(label, this.database[other]);
      return uses;
    }
    const scenario = this.scenario;
    for (const [label, other] of labels) check(label, this.collection(other));
    check("Instantiated element", scenario.instantiatedElements);
    for (const mission of scenario.missionList) {
      const events = mission.events.filter((event) => JSON.stringify(event).includes(id));
      for (const event of events) uses.push(`Event ${event.name} (${mission.name})`);
      if (!events.length && JSON.stringify(mission).includes(id)) uses.push(`Mission ${mission.name}`);
    }
    if (this.location(id)?.contents?.length) uses.push("Initial elements");
    if (JSON.stringify(scenario.manifest).includes(id)) uses.push("Manifest");
    return uses;
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
