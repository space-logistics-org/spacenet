// Dialogs to add or edit the object models of a library: nodes, edges,
// resources, and demand models (element templates: see elementTemplate.js).
// The server validates a model before it is accepted.

import { api, ApiError } from "../api.js";
import { resourceTable, schemaForm } from "../components.js";
import { store } from "../store.js";
import {
  button,
  clone,
  daysToIso,
  field,
  h,
  isoToDays,
  numberInput,
  openModal,
  select,
  textInput,
  uuid,
} from "../util.js";

// ------------------------------------------------------------------ helpers

/** Creates a labeled number input bound to a property (null when empty). */
export function numberField(label, target, name, { col = "col-md-4", scale = 1, ...attrs } = {}) {
  const value = target[name] === null || target[name] === undefined ? null : target[name] / scale;
  return field(
    label,
    numberInput(value, (input) => (target[name] = input === null ? null : input * scale), attrs),
    { col }
  );
}

/** Creates a labeled number input (days or hours) bound to a duration property. */
export function durationField(label, target, name, { col = "col-md-4", hours = false } = {}) {
  const factor = hours ? 24 : 1;
  const value = target[name] === null || target[name] === undefined ? null : isoToDays(target[name]) * factor;
  return field(
    label,
    numberInput(value, (input) => (target[name] = input === null ? null : daysToIso(input / factor)), {
      min: 0,
    }),
    { col }
  );
}

/** Creates a labeled select bound to a property. */
export function selectField(label, target, name, options, { col = "col-md-4", number = false, onChange } = {}) {
  return field(
    label,
    select(options, target[name], (value) => {
      target[name] = number ? Number(value) : value;
      onChange?.();
    }),
    { col }
  );
}

export function classOfSupplyOptions() {
  return store.enums.classesOfSupply.map((c) => [c.id, `${c.id} ${c.name}`]);
}

/** Gets the default value of a property of an object schema. */
export function schemaDefault(definition, name) {
  return store.schema.$defs[definition]?.properties?.[name]?.default;
}

function section(title, ...children) {
  return h("div", { class: "mb-3" }, h("h6", { class: "border-bottom pb-1" }, title), children);
}

/**
 * Opens a dialog to edit (a copy of) an object model. The type can only be
 * chosen for a new model. Resolves to the validated model, or undefined if
 * cancelled.
 *
 * Options:
 *   kind: kind of model (nodes, edges, resources, elements, demandModels)
 *   label: name of the kind of model shown in the title
 *   types: values of the `type` property
 *   draw(draft, redraw): creates the controls of the type-specific properties
 *   changeType(draft): removes properties which do not apply to a new type
 *   check(draft): returns a message if the model is not acceptable
 */
export function openEditor({ kind, label, model, isNew, types, draw, changeType, check, size = "lg" }) {
  const draft = clone(model);
  const problems = h("div", { class: "alert alert-danger py-2 small", hidden: true });
  const form = h("div");

  function redraw() {
    form.replaceChildren(
      h(
        "div",
        { class: "row g-2 mb-3" },
        field("Name", textInput(draft.name, (value) => (draft.name = value), { "data-model": "name" }), {
          col: "col-md-8",
        }),
        field(
          "Type",
          select(
            types,
            draft.type,
            (value) => {
              draft.type = value;
              changeType?.(draft);
              redraw();
            },
            { disabled: !isNew, "data-model": "type" }
          ),
          { col: "col-md-4" }
        ),
        field(
          "Description",
          textInput(draft.description, (value) => (draft.description = value), {
            "data-model": "description",
          }),
          { col: "col-12" }
        )
      ),
      h("div", {}, draw(draft, redraw))
    );
  }

  function show(messages) {
    problems.hidden = !messages.length;
    problems.replaceChildren(
      messages.length === 1
        ? messages[0]
        : h("ul", { class: "mb-0 ps-3" }, messages.map((message) => h("li", {}, message)))
    );
    if (messages.length) problems.scrollIntoView({ block: "nearest" });
  }

  async function accept(control) {
    draft.name = (draft.name ?? "").trim();
    const message = draft.name ? check?.(draft) : "A name is required.";
    if (message) return show([message]);
    try {
      control.close(await api.validateModel(kind, draft));
    } catch (error) {
      if (!(error instanceof ApiError)) throw error;
      const details = error.detail.map((item) => {
        const location = (item.loc || []).join(" › ");
        return location ? `${location}: ${item.msg}` : item.msg;
      });
      show(details.length ? details : [error.message]);
    }
    return undefined;
  }

  redraw();
  return openModal({
    title: `${isNew ? "Add" : "Edit"} ${label}`,
    size,
    body: h("div", {}, problems, form),
    footer: (control) => [
      button("Cancel", () => control.close()),
      button("OK", () => accept(control), "primary", { "data-model": "ok" }),
    ],
  }).closed;
}

// -------------------------------------------------------------------- nodes

function scenarioBodies() {
  const type = store.enums.scenarioTypes.find((item) => item.name === store.scenario.scenarioType);
  return type?.bodies ?? store.enums.bodies;
}

export function newNode(type) {
  return { id: uuid(), type: type || "Surface Node", name: "", description: "" };
}

function drawNode(draft) {
  const bodies = store.enums.bodies;
  if (draft.type === "Lagrange Node") {
    // by default, the point of the first two bodies of the scenario (e.g., Earth and Moon)
    const [major, minor] = scenarioBodies();
    draft.body1 ??= major ?? bodies[0];
    draft.body2 ??= minor ?? bodies.find((body) => body !== draft.body1);
    draft.lpNumber ??= 1;
    return h(
      "div",
      { class: "row g-2" },
      selectField("Major Body", draft, "body1", bodies),
      selectField("Minor Body", draft, "body2", bodies),
      selectField("Lagrange Point", draft, "lpNumber", [1, 2, 3, 4, 5], { number: true })
    );
  }
  draft.body1 ??= scenarioBodies().at(-1) ?? bodies[0];
  if (draft.type === "Surface Node") {
    draft.latitude ??= 0;
    draft.longitude ??= 0;
    return h(
      "div",
      { class: "row g-2" },
      selectField("Body", draft, "body1", bodies),
      numberField("Latitude (°)", draft, "latitude", { min: -90, max: 90 }),
      numberField("Longitude (°)", draft, "longitude", { min: -180, max: 180 }),
      numberField("Illumination (%)", draft, "illumination", { min: 0, max: 100, scale: 0.01 }),
      numberField("Longest Night (h)", draft, "maxNightDuration", { min: 0 }),
      h(
        "div",
        { class: "col-12 form-text" },
        "Illumination is the average fraction of time in sunlight (default 100%); " +
          "solar-powered elements must store enough energy to survive the longest night."
      )
    );
  }
  draft.apoapsis ??= 0;
  draft.periapsis ??= 0;
  draft.inclination ??= 0;
  return h(
    "div",
    { class: "row g-2" },
    selectField("Body", draft, "body1", bodies, { col: "col-md-3" }),
    numberField("Apoapsis (km)", draft, "apoapsis", { col: "col-md-3", min: 0 }),
    numberField("Periapsis (km)", draft, "periapsis", { col: "col-md-3", min: 0 }),
    numberField("Inclination (°)", draft, "inclination", { col: "col-md-3", min: 0, max: 180 })
  );
}

export function openNode(model, isNew) {
  return openEditor({
    kind: "nodes",
    label: "Node",
    model,
    isNew,
    types: store.enums.nodeTypes,
    draw: drawNode,
    // the default bodies depend on the type
    changeType: (draft) => {
      delete draft.body1;
      delete draft.body2;
    },
    check: (draft) =>
      draft.type === "Orbital Node" && draft.periapsis > draft.apoapsis
        ? "The periapsis cannot exceed the apoapsis."
        : draft.type === "Lagrange Node" && draft.body1 === draft.body2
          ? "The major and minor bodies must differ."
          : null,
  });
}

// -------------------------------------------------------------------- edges

export function newEdge(type) {
  return { id: uuid(), type: type || "Space Edge", name: "", description: "" };
}

function burnTable(burns) {
  const body = h("tbody");
  function render() {
    body.replaceChildren(
      ...burns.map((burn, index) =>
        h(
          "tr",
          {},
          h("td", {}, numberInput(isoToDays(burn.time), (value) => (burn.time = daysToIso(value ?? 0)), { min: 0 })),
          h("td", {}, numberInput(burn.deltaV, (value) => (burn.deltaV = value), { min: 0 })),
          h(
            "td",
            {},
            select(
              store.enums.propulsionTypes.map((type) => [type.id, type.id]),
              (burn.type ??= "OMS"),
              (value) => (burn.type = value)
            )
          ),
          h(
            "td",
            { class: "text-end" },
            button("×", () => {
              burns.splice(index, 1);
              render();
            })
          )
        )
      )
    );
    if (!burns.length) body.append(h("tr", {}, h("td", { colspan: 4, class: "text-secondary" }, "None")));
  }
  render();
  return h(
    "div",
    {},
    h(
      "table",
      { class: "table table-sm align-middle mb-1" },
      h("thead", {}, h("tr", {}, ["Time (days)", "Delta-V (m/s)", "Propulsion", ""].map((title) => h("th", {}, title)))),
      body
    ),
    button("Add Burn", () => {
      burns.push({ id: uuid(), time: burns.at(-1)?.time ?? daysToIso(0), deltaV: 0, type: "OMS" });
      render();
    })
  );
}

function drawEdge(draft) {
  const nodes = store.library("nodes").map((node) => [node.id, node.name]);
  if (!nodes.length) {
    return h("div", { class: "sn-muted-box" }, "An edge connects two nodes: add a node first.");
  }
  if (!nodes.some(([id]) => id === draft.origin)) draft.origin = nodes[0][0];
  if (!nodes.some(([id]) => id === draft.destination)) draft.destination = nodes.at(-1)[0];
  const parts = [
    h(
      "div",
      { class: "row g-2 mb-3" },
      selectField("Origin", draft, "origin", nodes, { col: "col-md-6" }),
      selectField("Destination", draft, "destination", nodes, { col: "col-md-6" })
    ),
  ];
  if (draft.type === "Surface Edge") {
    draft.distance ??= 0;
    parts.push(
      h("div", { class: "row g-2" }, numberField("Distance (km)", draft, "distance", { min: 0, scale: 1000 }))
    );
  } else if (draft.type === "Flight Edge") {
    draft.duration ??= daysToIso(0);
    draft.maxCrew ??= 0;
    draft.maxCargo ??= 0;
    parts.push(
      h(
        "div",
        { class: "row g-2" },
        durationField("Duration (days)", draft, "duration"),
        numberField("Max Crew", draft, "maxCrew", { min: 0, step: 1 }),
        numberField("Max Cargo (kg)", draft, "maxCargo", { min: 0 })
      )
    );
  } else {
    draft.duration ??= daysToIso(0);
    draft.burns ||= [];
    parts.push(
      h("div", { class: "row g-2 mb-3" }, durationField("Duration (days)", draft, "duration")),
      section("Burns", burnTable(draft.burns))
    );
  }
  parts.push(
    h(
      "div",
      { class: "row g-2 mt-1" },
      numberField("Cost per Transport ($M)", draft, "costPerTransport", { min: 0 }),
      numberField("Min. Departure Interval (days)", draft, "minDepartureInterval", { min: 0 }),
      h(
        "div",
        { class: "col-12 form-text" },
        "The cost of each transport along the edge (e.g., a launch service or ground operations) and the " +
          "shortest time between departures (e.g., the launch cadence of a pad); empty if none."
      )
    )
  );
  return parts;
}

export function openEdge(model, isNew) {
  return openEditor({
    kind: "edges",
    label: "Edge",
    model,
    isNew,
    types: store.enums.edgeTypes,
    draw: drawEdge,
    check: (draft) => {
      if (!draft.origin || !draft.destination) return "An origin and a destination are required.";
      if (draft.type !== "Flight Edge" && draft.origin === draft.destination) {
        return "The origin and the destination must differ.";
      }
      const late = (draft.burns || []).some((burn) => isoToDays(burn.time) > isoToDays(draft.duration));
      return draft.type === "Space Edge" && late ? "Burns cannot occur after the duration of the edge." : null;
    },
  });
}

// ---------------------------------------------------------------- resources

export function newResource(type) {
  return { id: uuid(), type: type || store.enums.resourceTypes[0], name: "", description: "" };
}

function drawResource(draft) {
  draft.classOfSupply ??= 0;
  draft.environment ??= "Unpressurized";
  draft.units ??= "kg";
  draft.unitMass ??= 1;
  draft.unitVolume ??= 0;
  draft.packingFactor ??= 0;
  return h(
    "div",
    { class: "row g-2" },
    selectField("Class of Supply", draft, "classOfSupply", classOfSupplyOptions(), {
      col: "col-md-8",
      number: true,
    }),
    selectField("Environment", draft, "environment", store.enums.environments),
    field("Units", textInput(draft.units, (value) => (draft.units = value)), { col: "col-md-3" }),
    numberField("Unit Mass (kg)", draft, "unitMass", { col: "col-md-3", min: 0 }),
    numberField("Unit Volume (m³)", draft, "unitVolume", { col: "col-md-3", min: 0 }),
    numberField("Packing Factor", draft, "packingFactor", { col: "col-md-3", min: 0 })
  );
}

export function openResource(model, isNew) {
  return openEditor({
    kind: "resources",
    label: "Resource",
    model,
    isNew,
    types: store.enums.resourceTypes,
    draw: drawResource,
  });
}

// ------------------------------------------------------------ demand models

const DEMAND_FIELDS = ["id", "name", "type", "description", "demands"];

export function newDemandModel(type) {
  return { id: uuid(), type: type || "Timed Impulse", name: "", description: "" };
}

function drawDemandModel(draft) {
  if (draft.type === "Timed Impulse" || draft.type === "Rated") {
    const rated = draft.type === "Rated";
    draft.demands ||= [];
    return section(
      "Demands",
      resourceTable(draft.demands, () => {}, {
        quantity: rated ? "rate" : "amount",
        label: rated ? "Rate (per day)" : "Amount",
      })
    );
  }
  const name = `${draft.type.replace(/ /g, "")}DemandModel`;
  const definition = store.schema.$defs[name];
  const names = Object.keys(definition.properties).filter((key) => !DEMAND_FIELDS.includes(key));
  const defaults = {};
  for (const key of names) {
    const value = definition.properties[key].default;
    if (value !== undefined) defaults[key] = value;
    // properties without a default are required
    else draft[key] ??= definition.properties[key].type === "boolean" ? false : 0;
  }
  return section(
    "Parameters",
    h(
      "div",
      { class: "small text-secondary mb-2" },
      "Empty parameters use the default value (shown as a placeholder)."
    ),
    schemaForm(definition, draft, names, null, { optional: true, placeholders: defaults })
  );
}

export function openDemandModelTemplate(model, isNew) {
  return openEditor({
    kind: "demandModels",
    label: "Demand Model",
    model,
    isNew,
    types: store.enums.demandModelTypes,
    draw: drawDemandModel,
    changeType: (draft) => {
      for (const key of Object.keys(draft)) {
        if (key === "demands" || !DEMAND_FIELDS.includes(key)) delete draft[key];
      }
    },
  });
}
