// Dialog to add or edit an element template: its sizing, the properties of
// its type, its operational states (with demand models), and its parts.

import { resourceTable, typeBadge } from "../components.js";
import { store } from "../store.js";
import {
  button,
  clone,
  field,
  h,
  hoursToIso,
  isoToHours,
  numberInput,
  openModal,
  select,
  textInput,
  uuid,
} from "../util.js";
import { openDemandModel } from "./demandModel.js";
import {
  classOfSupplyOptions,
  numberField,
  openEditor,
  schemaDefault,
  selectField,
} from "./modelEditors.js";

const AGENTS = ["Human Agent", "Robotic Agent"];
const CARRIERS = ["Element Carrier", "Propulsive Vehicle", "Surface Vehicle"];
const VEHICLES = ["Propulsive Vehicle", "Surface Vehicle"];
const STATE_DEMAND_MODELS = ["Timed Impulse", "Rated", "Sparing By Mass"];

export function newElement(type) {
  return { id: uuid(), type: type || "Element", name: "", description: "" };
}

function section(title, ...children) {
  return h("div", { class: "mb-3" }, h("h6", { class: "border-bottom pb-1" }, title), children);
}

// --------------------------------------------------------------------- fuel

/** Creates controls to edit one resource amount (specific or generic). */
function amountInput(amount, replace) {
  const root = h("div", { class: "row g-2" });
  function render() {
    const generic = !amount.resource;
    const resources = store.library("resources").map((resource) => [resource.id, resource.name]);
    const controls = [
      field(
        "Fuel Type",
        select(["Generic", "Specific"], generic ? "Generic" : "Specific", (value) => {
          const quantity = amount.amount ?? 0;
          if (value === "Generic") {
            amount = { classOfSupply: 1, environment: "Unpressurized", amount: quantity };
          } else if (resources.length) {
            amount = { resource: resources[0][0], amount: quantity };
          }
          replace(amount);
          render();
        }),
        { col: "col-md-3" }
      ),
      generic
        ? [
            field(
              "Class of Supply",
              select(classOfSupplyOptions(), amount.classOfSupply, (value) => (amount.classOfSupply = Number(value))),
              { col: "col-md-4" }
            ),
            field(
              "Environment",
              select(store.enums.environments, amount.environment, (value) => (amount.environment = value)),
              { col: "col-md-2" }
            ),
          ]
        : field(
            "Resource",
            select(resources, amount.resource, (value) => (amount.resource = value)),
            { col: "col-md-6" }
          ),
      field(
        "Initial Fuel (units)",
        numberInput(amount.amount, (value) => (amount.amount = value ?? 0), { min: 0 }),
        { col: "col-md-3" }
      ),
    ];
    root.replaceChildren(...controls.flat());
  }
  render();
  return root;
}

// ------------------------------------------------------------------- states

/** Opens the dialog of a state; resolves to the edited state or undefined. */
function openState(state, isNew) {
  const draft = clone(state);
  draft.demandModels ||= [];
  const models = h("div");

  async function edit(index, type) {
    const model = index === null ? { type } : draft.demandModels[index];
    const saved = await openDemandModel({ model });
    if (!saved) return;
    if (index === null) draft.demandModels.push(saved);
    else draft.demandModels[index] = saved;
    render();
  }

  function render() {
    const adder = select(STATE_DEMAND_MODELS, STATE_DEMAND_MODELS[1], () => {}, {
      style: { width: "auto" },
      class: "form-select form-select-sm d-inline-block me-1",
    });
    models.replaceChildren(
      h(
        "table",
        { class: "table table-sm align-middle mb-1" },
        h(
          "tbody",
          {},
          draft.demandModels.map((model, index) =>
            h(
              "tr",
              {},
              h("td", {}, model.name),
              h("td", { class: "text-secondary" }, model.type),
              h(
                "td",
                { class: "text-end" },
                button("Edit", () => edit(index)),
                " ",
                button("×", () => {
                  draft.demandModels.splice(index, 1);
                  render();
                })
              )
            )
          ),
          draft.demandModels.length
            ? null
            : h("tr", {}, h("td", { colspan: 3, class: "text-secondary" }, "None"))
        )
      ),
      adder,
      button("Add Demand Model", () => edit(null, adder.value))
    );
  }

  render();
  return openModal({
    title: `${isNew ? "Add" : "Edit"} State`,
    body: h(
      "div",
      {},
      h(
        "div",
        { class: "row g-2 mb-3" },
        field("Name", textInput(draft.name, (value) => (draft.name = value)), { col: "col-md-8" }),
        field("Type", select(store.enums.stateTypes, draft.type, (value) => (draft.type = value)), {
          col: "col-md-4",
        }),
        field(
          "Description",
          textInput(draft.description, (value) => (draft.description = value || null)),
          { col: "col-12" }
        )
      ),
      section("Demand Models", models)
    ),
    footer: (control) => [
      button("Cancel", () => control.close()),
      button(
        "OK",
        () => {
          draft.name = (draft.name ?? "").trim() || draft.type;
          control.close(draft);
        },
        "primary"
      ),
    ],
  }).closed;
}

function stateTable(draft) {
  const root = h("div");

  async function edit(index) {
    const isNew = index === null;
    const state = isNew
      ? { id: uuid(), name: "", type: store.enums.stateTypes[0], demandModels: [] }
      : draft.states[index];
    const saved = await openState(state, isNew);
    if (!saved) return;
    if (isNew) draft.states.push(saved);
    else draft.states[index] = saved;
    // the first state is the initial state unless another is chosen
    if (draft.states.length === 1) draft.currentStateIndex = 0;
    render();
  }

  function remove(index) {
    draft.states.splice(index, 1);
    const current = draft.currentStateIndex;
    if (!draft.states.length) draft.currentStateIndex = null;
    else if (current === index) draft.currentStateIndex = 0;
    else if (current > index) draft.currentStateIndex = current - 1;
    render();
  }

  function render() {
    const group = `state-${uuid()}`;
    root.replaceChildren(
      h(
        "table",
        { class: "table table-sm align-middle mb-1" },
        h(
          "thead",
          {},
          h("tr", {}, ["Initial", "Name", "Type", "Demand Models", ""].map((title) => h("th", {}, title)))
        ),
        h(
          "tbody",
          {},
          draft.states.map((state, index) =>
            h(
              "tr",
              {},
              h(
                "td",
                {},
                h("input", {
                  type: "radio",
                  class: "form-check-input",
                  name: group,
                  checked: draft.currentStateIndex === index,
                  onChange: () => (draft.currentStateIndex = index),
                })
              ),
              h("td", {}, state.name),
              h("td", {}, state.type),
              h(
                "td",
                { class: "text-secondary" },
                (state.demandModels ?? []).map((model) => model.name).join(", ") || "None"
              ),
              h(
                "td",
                { class: "text-end text-nowrap" },
                button("Edit", () => edit(index)),
                " ",
                button("×", () => remove(index))
              )
            )
          ),
          draft.states.length
            ? null
            : h("tr", {}, h("td", { colspan: 5, class: "text-secondary" }, "None"))
        )
      ),
      button("Add State", () => edit(null), "outline-secondary", { "data-model": "add-state" })
    );
  }

  render();
  return root;
}

// -------------------------------------------------------------------- parts

function partTable(parts) {
  const root = h("div");
  function render() {
    const resources = store.library("resources").map((resource) => [resource.id, resource.name]);
    const hours = (part, name) =>
      numberInput(
        part[name] === null || part[name] === undefined ? null : isoToHours(part[name]),
        (value) => (part[name] = value === null ? null : hoursToIso(value)),
        { min: 0 }
      );
    root.replaceChildren(
      h(
        "table",
        { class: "table table-sm align-middle mb-1" },
        h(
          "thead",
          {},
          h(
            "tr",
            {},
            [
              "Resource",
              "Quantity",
              "Duty Cycle",
              "Time to Failure (h)",
              "Time to Repair (h)",
              "Mass to Repair (kg)",
              "",
            ].map((title) => h("th", {}, title))
          )
        ),
        h(
          "tbody",
          {},
          parts.map((part, index) =>
            h(
              "tr",
              {},
              h("td", {}, select(resources, part.resource, (value) => (part.resource = value))),
              h("td", {}, numberInput(part.quantity, (value) => (part.quantity = value ?? 1), { min: 1 })),
              h(
                "td",
                {},
                numberInput(part.dutyCycle, (value) => (part.dutyCycle = value ?? 1), { min: 0, max: 1 })
              ),
              h("td", {}, hours(part, "meanTimeToFailure")),
              h("td", {}, hours(part, "meanTimeToRepair")),
              h("td", {}, numberInput(part.massToRepair, (value) => (part.massToRepair = value), { min: 0 })),
              h(
                "td",
                { class: "text-end" },
                button("×", () => {
                  parts.splice(index, 1);
                  render();
                })
              )
            )
          ),
          parts.length ? null : h("tr", {}, h("td", { colspan: 7, class: "text-secondary" }, "None"))
        )
      ),
      resources.length
        ? button("Add Part", () => {
            parts.push({ resource: resources[0][0], quantity: 1, dutyCycle: 1 });
            render();
          })
        : h("span", { class: "small text-secondary" }, "A part is a resource: add a resource first.")
    );
  }
  render();
  return root;
}

// ----------------------------------------------------------------- contents

/** Creates a list of the element templates nested in a carrier template. */
function contentsList(draft) {
  const root = h("div");
  function render() {
    const templates = store.library("elements").filter((template) => template.id !== draft.id);
    const adder = select(
      templates.map((template) => [template.id, `${template.name} (${template.type})`]),
      templates[0]?.id,
      () => {},
      { style: { width: "auto", maxWidth: "70%" }, class: "form-select form-select-sm d-inline-block me-1" }
    );
    root.replaceChildren(
      h(
        "ul",
        { class: "list-unstyled mb-1" },
        draft.contents.map((id, index) => {
          const template = store.template(id);
          return h(
            "li",
            { class: "mb-1" },
            button("×", () => {
              draft.contents.splice(index, 1);
              render();
            }),
            " ",
            template?.name ?? "?",
            " ",
            typeBadge(template?.type)
          );
        }),
        draft.contents.length ? null : h("li", { class: "text-secondary" }, "None")
      ),
      h(
        "div",
        { hidden: !templates.length },
        adder,
        button("Add Element", () => {
          draft.contents.push(adder.value);
          render();
        })
      )
    );
  }
  render();
  return root;
}

// ------------------------------------------------------------------- dialog

function drawElement(draft) {
  const type = draft.type;
  const definition = type.replace(/ /g, "");
  draft.classOfSupply ??= schemaDefault(definition, "classOfSupply") ?? 0;
  draft.environment ??= schemaDefault(definition, "environment") ?? "Unpressurized";
  draft.mass ??= 0;
  draft.volume ??= 0;
  draft.accommodationMass ??= 0;
  draft.states ||= [];
  draft.parts ||= [];
  const parts = [
    h(
      "div",
      { class: "row g-2 mb-3" },
      selectField("Class of Supply", draft, "classOfSupply", classOfSupplyOptions(), {
        col: "col-md-8",
        number: true,
      }),
      selectField("Environment", draft, "environment", store.enums.environments),
      numberField("Mass (kg)", draft, "mass", { min: 0 }),
      numberField("Volume (m³)", draft, "volume", { min: 0 }),
      numberField("Accommodation Mass (kg)", draft, "accommodationMass", { min: 0 })
    ),
  ];
  if (AGENTS.includes(type)) {
    draft.activeTimeFraction ??= 1;
    parts.push(
      h(
        "div",
        { class: "row g-2 mb-3" },
        numberField("Active Time Fraction", draft, "activeTimeFraction", { min: 0, max: 1 })
      )
    );
  }
  if (CARRIERS.includes(type) || type === "Resource Container") {
    draft.cargoEnvironment ??= schemaDefault(definition, "cargoEnvironment") ?? "Unpressurized";
    draft.contents ||= [];
    if (CARRIERS.includes(type)) draft.maxCrew ??= 0;
    parts.push(
      h(
        "div",
        { class: "row g-2 mb-3" },
        numberField("Max Cargo Mass (kg)", draft, "maxCargoMass", { col: "col-md-3", min: 0 }),
        numberField("Max Cargo Volume (m³)", draft, "maxCargoVolume", { col: "col-md-3", min: 0 }),
        selectField("Cargo Environment", draft, "cargoEnvironment", store.enums.environments, {
          col: "col-md-3",
        }),
        CARRIERS.includes(type)
          ? numberField("Max Crew", draft, "maxCrew", { col: "col-md-3", min: 0, step: 1 })
          : null
      )
    );
  }
  if (VEHICLES.includes(type)) {
    draft.maxFuel ??= 0;
    draft.fuel ||= { classOfSupply: 1, environment: "Unpressurized", amount: 0 };
    if (type === "Propulsive Vehicle") draft.isp ??= 0;
    else draft.maxSpeed ??= 0;
    parts.push(
      h(
        "div",
        { class: "row g-2 mb-2" },
        type === "Propulsive Vehicle"
          ? numberField("Specific Impulse (s)", draft, "isp", { col: "col-md-3", min: 0 })
          : numberField("Max Speed (km/h)", draft, "maxSpeed", { col: "col-md-3", min: 0 }),
        numberField("Max Fuel (units)", draft, "maxFuel", { col: "col-md-3", min: 0 })
      ),
      h("div", { class: "mb-3" }, amountInput(draft.fuel, (amount) => (draft.fuel = amount)))
    );
  }
  if (type === "Resource Container") {
    parts.push(section("Contents", resourceTable(draft.contents, () => {})));
  } else if (CARRIERS.includes(type)) {
    parts.push(section("Contents (elements created with the carrier)", contentsList(draft)));
  }
  parts.push(section("States", stateTable(draft)), section("Parts", partTable(draft.parts)));
  return parts;
}

export function openElementTemplate(model, isNew) {
  return openEditor({
    kind: "elements",
    label: "Element",
    model,
    isNew,
    size: "xl",
    types: store.enums.elementTypes,
    draw: drawElement,
    // contents are elements for carriers and resources for containers
    changeType: (draft) => delete draft.contents,
    check: (draft) =>
      VEHICLES.includes(draft.type) && draft.fuel.amount > draft.maxFuel
        ? "The initial fuel cannot exceed the maximum fuel."
        : null,
  });
}
