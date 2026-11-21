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
const STATE_DEMAND_MODELS = ["Timed Impulse", "Rated", "Sparing By Mass"];

export function newElement(type) {
  return { id: uuid(), type: type || "Element", name: "", description: "" };
}

function section(title, ...children) {
  return h("div", { class: "mb-3" }, h("h6", { class: "border-bottom pb-1" }, title), children);
}

// --------------------------------------------------------------------- fuel

function newTank() {
  return { maxAmount: 0, contents: { classOfSupply: 1, environment: "Unpressurized", amount: 0 } };
}

/**
 * Creates a fuel tank from the properties of a vehicle in the legacy format
 * (one fuel amount and capacity) which may remain in the browser database.
 */
function legacyTank(draft) {
  if (!draft.fuel) return newTank();
  const tank = { maxAmount: draft.maxFuel ?? draft.fuel.amount ?? 0, contents: draft.fuel };
  delete draft.fuel;
  delete draft.maxFuel;
  return tank;
}

/** Lists the fuel (and oxidizer) tanks of a vehicle. */
function fuelTanks(draft) {
  if (draft.type === "Surface Vehicle") return draft.fuelTank ? [draft.fuelTank] : [];
  if (draft.type !== "Propulsive Vehicle") return [];
  return (draft.propulsionSystems ?? [])
    .flatMap((system) => [system.fuelTank, system.oxidizerTank])
    .filter(Boolean);
}

/**
 * Creates controls to edit a fuel (or oxidizer) tank; controls are added
 * before its capacity and boiloff rate.
 */
function tankInput(tank, ...controls) {
  return tankEditor(tank, "Fuel", controls);
}

function tankEditor(tank, role, controls = []) {
  return [
    h(
      "div",
      { class: "row g-2 mb-2" },
      controls,
      numberField(`Max ${role} (units)`, tank, "maxAmount", { col: "col-md-3", min: 0 }),
      h(
        "div",
        {
          class: "col-md-3",
          title:
            "Fraction of the tank capacity lost per day, e.g., to cryogenic boiloff " +
            "(not applied on the surface of Earth). Instances which override the " +
            "propulsion systems do not inherit changes to this value.",
        },
        numberField("Boiloff (%/day)", tank, "boiloffRate", { col: "", min: 0, max: 100, scale: 0.01 })
      )
    ),
    h("div", { class: "mb-3" }, amountInput(tank.contents, (amount) => (tank.contents = amount), role)),
  ];
}

/**
 * Creates controls to make a propulsion system bipropellant: an oxidizer tank
 * (own or shared with another system) and an oxidizer-to-fuel mixture ratio.
 */
function oxidizerEditor(system, systems, render) {
  const bipropellant = Boolean(system.oxidizerTank || system.sharedOxidizerTank);
  const toggle = h(
    "label",
    { class: "form-check-label small mb-2 d-block" },
    h("input", {
      type: "checkbox",
      class: "form-check-input me-2",
      checked: bipropellant,
      onChange: () => {
        if (bipropellant) {
          // systems which shared the removed oxidizer tank take it over
          for (const other of systems) {
            if (other.sharedOxidizerTank !== system.type) continue;
            other.oxidizerTank = system.oxidizerTank ?? newTank();
            other.sharedOxidizerTank = null;
          }
          system.oxidizerTank = null;
          system.sharedOxidizerTank = null;
          system.mixtureRatio = null;
        } else {
          system.oxidizerTank = newTank();
          system.sharedOxidizerTank = null;
          system.mixtureRatio = system.mixtureRatio ?? 3.6;
        }
        render();
      },
    }),
    "Bipropellant (separate oxidizer tank)"
  );
  if (!bipropellant) return toggle;
  const shared = systems.some((other) => other.sharedOxidizerTank === system.type);
  const others = shared ? [] : systems.filter((other) => other !== system && other.oxidizerTank);
  const controls = [
    numberField("Mixture Ratio (O:F)", system, "mixtureRatio", { col: "col-md-3", min: 0 }),
    field(
      "Oxidizer Tank",
      select(
        [["", "Own oxidizer tank"], ...others.map((other) => [other.type, `Shared with ${other.type}`])],
        system.sharedOxidizerTank ?? "",
        (value) => {
          system.sharedOxidizerTank = value || null;
          system.oxidizerTank = value ? null : newTank();
          render();
        }
      ),
      { col: "col-md-3" }
    ),
  ];
  return [
    toggle,
    system.oxidizerTank
      ? tankEditor(system.oxidizerTank, "Oxidizer", controls)
      : h("div", { class: "row g-2 mb-3" }, controls),
  ];
}

/**
 * Creates controls to edit the propulsion systems of a propulsive vehicle:
 * one of each type with its own fuel tank or the fuel tank of another system.
 */
function propulsionEditor(draft) {
  const root = h("div");
  const types = store.enums.propulsionTypes;
  const order = (system) => types.findIndex((type) => type.id === system.type);
  function render() {
    const systems = draft.propulsionSystems;
    root.replaceChildren(
      ...types.map(({ id, name }) => {
        const system = systems.find((candidate) => candidate.type === id);
        const toggle = h("input", {
          type: "checkbox",
          class: "form-check-input me-2",
          checked: Boolean(system),
          onChange: () => {
            if (system) {
              draft.propulsionSystems = systems.filter((candidate) => candidate !== system);
              // systems which shared the removed fuel (oxidizer) tank take it over
              for (const other of draft.propulsionSystems) {
                if (other.sharedFuelTank === id) {
                  other.fuelTank = system.fuelTank ?? newTank();
                  other.sharedFuelTank = null;
                }
                if (other.sharedOxidizerTank === id) {
                  other.oxidizerTank = system.oxidizerTank ?? newTank();
                  other.sharedOxidizerTank = null;
                }
              }
            } else {
              systems.push({ type: id, isp: 0, fuelTank: newTank(), sharedFuelTank: null });
              systems.sort((a, b) => order(a) - order(b));
            }
            render();
          },
        });
        const title = h("label", { class: "form-check-label fw-semibold small" }, toggle, `${name} (${id})`);
        if (!system) return h("div", { class: "mb-2" }, title);
        // the fuel tank of another system can be shared if nothing shares this one
        const shared = systems.some((other) => other.sharedFuelTank === id);
        const others = shared ? [] : systems.filter((other) => other !== system && other.fuelTank);
        const controls = [
          numberField("Specific Impulse (s)", system, "isp", { col: "col-md-3", min: 0 }),
          field(
            "Fuel Tank",
            select(
              [["", "Own fuel tank"], ...others.map((other) => [other.type, `Shared with ${other.type}`])],
              system.sharedFuelTank ?? "",
              (value) => {
                system.sharedFuelTank = value || null;
                system.fuelTank = value ? null : newTank();
                render();
              }
            ),
            { col: "col-md-3" }
          ),
        ];
        return h(
          "div",
          { class: "mb-2" },
          title,
          system.fuelTank ? tankInput(system.fuelTank, ...controls) : h("div", { class: "row g-2 mb-3" }, controls),
          oxidizerEditor(system, draft.propulsionSystems, render)
        );
      })
    );
  }
  render();
  return root;
}

/** Creates controls to edit one resource amount (specific or generic). */
function amountInput(amount, replace, role = "Fuel") {
  const root = h("div", { class: "row g-2" });
  function render() {
    const generic = !amount.resource;
    const resources = store.library("resources").map((resource) => [resource.id, resource.name]);
    const controls = [
      field(
        `${role} Type`,
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
        `Initial ${role} (units)`,
        numberInput(amount.amount, (value) => (amount.amount = value ?? 0), { min: 0 }),
        { col: "col-md-3" }
      ),
    ];
    root.replaceChildren(...controls.flat());
  }
  render();
  return root;
}

// -------------------------------------------------------------------- power

/** Creates controls to edit the energy storage and grid connection of an element. */
function powerEditor(draft) {
  const root = h("div");
  function render() {
    const stored = Boolean(draft.energyStorage);
    root.replaceChildren(
      h(
        "div",
        { class: "row g-2 align-items-end" },
        h(
          "div",
          { class: "col-md-3" },
          h(
            "label",
            { class: "form-check-label small" },
            h("input", {
              type: "checkbox",
              class: "form-check-input me-2",
              checked: stored,
              onChange: () => {
                draft.energyStorage = stored ? null : { capacity: 0, charge: null };
                render();
              },
            }),
            "Energy storage"
          )
        ),
        stored
          ? [
              numberField("Capacity (kWh)", draft.energyStorage, "capacity", { col: "col-md-3", min: 0 }),
              h(
                "div",
                { class: "col-md-3", title: "Leave empty to start fully charged." },
                numberField("Initial Charge (kWh)", draft.energyStorage, "charge", { col: "", min: 0 })
              ),
            ]
          : null,
        h(
          "div",
          { class: "col-md-3" },
          h(
            "label",
            {
              class: "form-check-label small",
              title: "Shares power with the other grid-connected elements at a surface node.",
            },
            h("input", {
              type: "checkbox",
              class: "form-check-input me-2",
              checked: Boolean(draft.gridConnected),
              onChange: (event) => (draft.gridConnected = event.target.checked || null),
            }),
            "Grid connected"
          )
        )
      ),
      h(
        "div",
        { class: "form-text" },
        "Power generation and consumption are defined by the operational states below."
      )
    );
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
      section("Demand Models", models),
      section(
        "Power",
        h(
          "div",
          { class: "row g-2" },
          numberField("Consumption (kW)", draft, "powerConsumption", { col: "col-md-4", min: 0 }),
          numberField("Generation (kW)", draft, "powerGeneration", { col: "col-md-4", min: 0 }),
          field(
            "Generation Type",
            select(
              [
                ["", "Constant (e.g., fission)"],
                ["Solar", "Solar (scaled by illumination)"],
              ],
              draft.generationType ?? "",
              (value) => (draft.generationType = value || null)
            ),
            { col: "col-md-4" }
          )
        ),
        h(
          "div",
          { class: "form-text" },
          "Solar generation is the power when fully illuminated; it is scaled by the " +
            "illumination of the location. Elements share power with their contents " +
            "and, if grid connected, with other grid-connected elements at a surface node."
        )
      )
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
          h("tr", {}, ["Initial", "Name", "Type", "Demand Models", "Power", ""].map((title) => h("th", {}, title)))
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
                { class: "text-secondary text-nowrap" },
                [
                  state.powerConsumption ? `−${state.powerConsumption} kW` : null,
                  state.powerGeneration
                    ? `+${state.powerGeneration} kW${state.generationType === "Solar" ? " solar" : ""}`
                    : null,
                ]
                  .filter(Boolean)
                  .join(" ") || "None"
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
            : h("tr", {}, h("td", { colspan: 6, class: "text-secondary" }, "None"))
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
  if (type === "Propulsive Vehicle") {
    draft.propulsionSystems ||= [
      { type: "OMS", isp: draft.isp ?? 0, fuelTank: legacyTank(draft), sharedFuelTank: null },
    ];
    delete draft.isp;
    parts.push(section("Propulsion Systems", propulsionEditor(draft)));
  } else if (type === "Surface Vehicle") {
    draft.maxSpeed ??= 0;
    draft.fuelTank ||= legacyTank(draft);
    parts.push(
      section(
        "Mobility",
        h(
          "div",
          { class: "row g-2 mb-2" },
          numberField("Max Speed (km/h)", draft, "maxSpeed", { col: "col-md-3", min: 0 }),
          numberField("Fuel per km (units)", draft, "fuelConsumption", { col: "col-md-3", min: 0 }),
          numberField("Energy per km (kWh)", draft, "energyConsumption", { col: "col-md-3", min: 0 }),
          h(
            "div",
            { class: "col-md-3", title: "Longest traverse with crew aboard (e.g., EVA suit endurance). Empty if unlimited." },
            numberField("Max Crewed Traverse (h)", draft, "maxCrewedDuration", { col: "", min: 0 })
          ),
          h(
            "div",
            {
              class: "col-md-3",
              title:
                "Greatest distance the crew of an unpressurized rover may travel from a pressurized " +
                "safe haven at either end of a traverse. Empty if unlimited.",
            },
            numberField("Walk-Back Distance (km)", draft, "walkBackDistance", { col: "", min: 0 })
          )
        ),
        tankInput(draft.fuelTank)
      )
    );
  }
  parts.push(section("Power", powerEditor(draft)));
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
    check: (draft) => {
      if (draft.type === "Propulsive Vehicle" && !draft.propulsionSystems.length) {
        return "A propulsive vehicle requires a propulsion system.";
      }
      return fuelTanks(draft).some((tank) => tank.contents.amount > tank.maxAmount)
        ? "The initial fuel cannot exceed the maximum fuel."
        : null;
    },
  });
}
