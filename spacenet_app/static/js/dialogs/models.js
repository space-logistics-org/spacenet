// Dialog to browse, add, edit, copy, and delete the object models of the
// library: nodes, edges, resources, element templates, and demand models.
//
// Models of the scenario and new models are saved with the scenario; models
// which are only part of the loaded database are changed in the browser.

import { typeBadge } from "../components.js";
import { store } from "../store.js";
import {
  alertDialog,
  badge,
  button,
  clone,
  confirmDialog,
  fmt,
  h,
  openModal,
  select,
  textInput,
  uuid,
} from "../util.js";
import { newElement, openElementTemplate } from "./elementTemplate.js";
import {
  newDemandModel,
  newEdge,
  newNode,
  newResource,
  openDemandModelTemplate,
  openEdge,
  openNode,
  openResource,
} from "./modelEditors.js";

const nodeName = (id) => store.library("nodes").find((node) => node.id === id)?.name ?? "?";

/** Kinds of models with their editors and the columns which describe them. */
const KINDS = {
  nodes: {
    label: "Nodes",
    types: () => store.enums.nodeTypes,
    create: newNode,
    open: openNode,
    columns: [
      ["Type", (node) => node.type.replace(/ Node$/, "")],
      ["Body", (node) => (node.body2 ? `${node.body1}–${node.body2} L${node.lpNumber}` : node.body1)],
    ],
  },
  edges: {
    label: "Edges",
    types: () => store.enums.edgeTypes,
    create: newEdge,
    open: openEdge,
    columns: [
      ["Type", (edge) => edge.type.replace(/ Edge$/, "")],
      ["Origin", (edge) => nodeName(edge.origin)],
      ["Destination", (edge) => nodeName(edge.destination)],
    ],
  },
  resources: {
    label: "Resources",
    types: () => store.enums.resourceTypes,
    create: newResource,
    open: openResource,
    columns: [
      ["Type", (resource) => resource.type],
      ["Class of Supply", (resource) => store.className(resource.classOfSupply)],
      ["Units", (resource) => resource.units],
      ["Unit Mass", (resource) => `${fmt(resource.unitMass, 4)} kg`],
    ],
  },
  elements: {
    label: "Elements",
    types: () => store.enums.elementTypes,
    create: newElement,
    open: openElementTemplate,
    columns: [
      ["Type", (element) => typeBadge(element.type)],
      ["Class of Supply", (element) => store.className(element.classOfSupply ?? 0)],
      ["Mass", (element) => `${fmt(element.mass)} kg`],
    ],
  },
  demandModels: {
    label: "Demand Models",
    types: () => store.enums.demandModelTypes,
    create: newDemandModel,
    open: openDemandModelTemplate,
    columns: [
      ["Type", (model) => model.type],
      ["Description", (model) => model.description ?? ""],
    ],
  },
};

/**
 * Opens the editor of (a copy of) a model and saves the result. Resolves to
 * the saved model, or undefined if cancelled.
 */
export async function editModel(kind, model, { isNew = false } = {}) {
  const saved = await KINDS[kind].open(model, isNew);
  // accepting a model without changes does not change the scenario
  if (saved && (isNew || JSON.stringify(saved) !== JSON.stringify(model))) {
    store.saveModel(kind, saved);
  }
  return saved;
}

/** Opens the editor of a new model of a kind (and optionally a type). */
export function addModel(kind, type) {
  return editModel(kind, KINDS[kind].create(type || undefined), { isNew: true });
}

function copyOf(kind, model) {
  const copy = clone(model);
  copy.id = uuid();
  copy.name = `${model.name} (copy)`;
  // the copy of a location is empty
  if (kind === "nodes" || kind === "edges") copy.contents = [];
  for (const burn of copy.burns || []) burn.id = uuid();
  for (const state of copy.states || []) state.id = uuid();
  return copy;
}

/** Opens the dialog (optionally showing a kind of model). */
export function openModels(initial = "nodes") {
  const state = { kind: initial, search: "", type: "", selected: new Set() };
  const body = h("div");
  let rows = new Map();
  let actions = {};

  const selection = () =>
    store.library(state.kind).filter((model) => state.selected.has(model.id));

  function updateSelection() {
    for (const [id, row] of rows) row.classList.toggle("table-active", state.selected.has(id));
    const count = [...state.selected].filter((id) => rows.has(id)).length;
    actions.edit.disabled = count !== 1;
    actions.copy.disabled = count !== 1;
    actions.remove.disabled = count < 1;
  }

  async function edit(model) {
    await editModel(state.kind, model);
    render();
  }

  async function add(model) {
    const saved = await editModel(state.kind, model, { isNew: true });
    if (saved) state.selected = new Set([saved.id]);
    render();
  }

  async function remove() {
    const models = selection();
    const names = models.map((model) => model.name).join(", ");
    if (!(await confirmDialog("Delete Models", `Delete ${names}?`))) return;
    const blocked = [];
    for (const model of models) {
      const uses = store.modelUses(state.kind, model.id);
      if (uses.length) blocked.push([model, uses]);
      else store.removeModel(state.kind, model.id);
    }
    state.selected.clear();
    render();
    if (blocked.length) {
      alertDialog(
        "Cannot Delete",
        h(
          "div",
          {},
          "The following models are used and must be replaced before they are deleted:",
          h(
            "ul",
            { class: "mb-0" },
            blocked.map(([model, uses]) =>
              h(
                "li",
                {},
                h("strong", {}, model.name),
                ` is used by ${uses.slice(0, 5).join(", ")}`,
                uses.length > 5 ? ` and ${uses.length - 5} more` : ""
              )
            )
          )
        )
      );
    }
  }

  function render({ focusSearch = false } = {}) {
    const definition = KINDS[state.kind];
    const search = state.search.toLowerCase();
    const models = store
      .library(state.kind)
      .filter((model) => !state.type || model.type === state.type)
      .filter((model) => !search || model.name.toLowerCase().includes(search));

    rows = new Map();
    for (const model of models) {
      const row = h(
        "tr",
        {
          dataset: { id: model.id },
          onClick: (event) => {
            if (!event.ctrlKey && !event.metaKey) state.selected.clear();
            else if (state.selected.has(model.id)) {
              state.selected.delete(model.id);
              return updateSelection();
            }
            state.selected.add(model.id);
            return updateSelection();
          },
          onDblclick: () => edit(model),
        },
        h("td", {}, model.name),
        definition.columns.map(([, value]) => h("td", {}, value(model))),
        h(
          "td",
          {},
          store.owns(state.kind, model.id) ? badge("Scenario", "primary") : badge("Database")
        )
      );
      rows.set(model.id, row);
    }

    actions = {
      add: button("Add…", () => add(definition.create(state.type || undefined)), "primary", {
        "data-model": "add",
      }),
      edit: button("Edit…", () => edit(selection()[0]), "outline-secondary", { "data-model": "edit" }),
      copy: button("Copy…", () => add(copyOf(state.kind, selection()[0])), "outline-secondary", {
        "data-model": "copy",
      }),
      remove: button("Delete", remove, "outline-danger", { "data-model": "delete" }),
    };

    body.replaceChildren(
      h(
        "ul",
        { class: "nav nav-pills mb-2" },
        Object.entries(KINDS).map(([kind, item]) =>
          h(
            "li",
            { class: "nav-item" },
            h(
              "a",
              {
                class: `nav-link py-1 ${kind === state.kind ? "active" : ""}`,
                href: "#",
                dataset: { kind },
                onClick: (event) => {
                  event.preventDefault();
                  Object.assign(state, { kind, search: "", type: "", selected: new Set() });
                  render();
                },
              },
              `${item.label} (${store.library(kind).length})`
            )
          )
        )
      ),
      h(
        "div",
        { class: "row g-2 mb-2" },
        h(
          "div",
          { class: "col-md-4" },
          textInput(
            state.search,
            (value) => {
              state.search = value;
              render({ focusSearch: true });
            },
            { placeholder: "Search by name", "data-model": "search" }
          )
        ),
        h(
          "div",
          { class: "col-md-3" },
          select([["", "All types"], ...definition.types()], state.type, (value) => {
            state.type = value;
            render();
          })
        ),
        h(
          "div",
          { class: "col-md-5 text-end" },
          actions.add,
          " ",
          actions.edit,
          " ",
          actions.copy,
          " ",
          actions.remove
        )
      ),
      h(
        "div",
        { class: "sn-scroll border rounded" },
        h(
          "table",
          { class: "table table-sm table-hover sn-table mb-0" },
          h(
            "thead",
            {},
            h(
              "tr",
              {},
              h("th", {}, "Name"),
              definition.columns.map(([title]) => h("th", {}, title)),
              h("th", {}, "Source")
            )
          ),
          h(
            "tbody",
            {},
            [...rows.values()],
            models.length
              ? null
              : h(
                  "tr",
                  {},
                  h(
                    "td",
                    { colspan: definition.columns.length + 2, class: "text-secondary" },
                    "No models. Add a model or load a model database."
                  )
                )
          )
        )
      ),
      h(
        "div",
        { class: "small text-secondary mt-2" },
        "Models of the scenario (and new models) are saved with the scenario. Changes to models ",
        "of the database are kept in this browser until a database is loaded."
      )
    );
    updateSelection();
    if (focusSearch) {
      const input = body.querySelector('[data-model="search"]');
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);
    }
  }

  render();
  return openModal({
    title: "Models",
    size: "xl",
    body,
    footer: (control) => button("Close", () => control.close(), "primary"),
  }).closed;
}
