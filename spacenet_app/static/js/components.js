// Components shared by tabs and dialogs: resource tables, element trees,
// issue lists, generated forms, and charts.

import { store } from "./store.js";
import {
  addDays,
  badge,
  button,
  checkbox,
  clear,
  fmt,
  h,
  numberInput,
  select,
  textInput,
} from "./util.js";

// --------------------------------------------------------------- resources

/**
 * Creates an editable table of resource amounts (or rates). Rows are either
 * specific ({resource, amount}) or generic ({classOfSupply, environment, amount}).
 */
export function resourceTable(amounts, onChange, { quantity = "amount", label = "Amount" } = {}) {
  const body = h("tbody");
  const classes = store.enums.classesOfSupply.map((c) => [c.id, `${c.id} ${c.name}`]);

  function render() {
    clear(body);
    amounts.forEach((amount, index) => {
      const generic = !amount.resource;
      const resources = store.library("resources").map((r) => [r.id, r.name]);
      body.append(
        h(
          "tr",
          {},
          h(
            "td",
            {},
            select(["Generic", "Specific"], generic ? "Generic" : "Specific", (value) => {
              const value0 = amount[quantity] ?? 0;
              if (value === "Generic") {
                amounts[index] = {
                  classOfSupply: 2,
                  environment: "Unpressurized",
                  [quantity]: value0,
                };
              } else if (resources.length) {
                amounts[index] = { resource: resources[0][0], [quantity]: value0 };
                store.include("resources", resources[0][0]);
              }
              render();
              onChange();
            })
          ),
          h(
            "td",
            {},
            generic
              ? select(classes, amount.classOfSupply, (value) => {
                  amount.classOfSupply = Number(value);
                  onChange();
                })
              : select(resources, amount.resource, (value) => {
                  amount.resource = value;
                  store.include("resources", value);
                  onChange();
                })
          ),
          h(
            "td",
            {},
            generic
              ? select(store.enums.environments, amount.environment, (value) => {
                  amount.environment = value;
                  onChange();
                })
              : h("span", { class: "text-secondary small" }, store.resource(amount.resource)?.units ?? "")
          ),
          h(
            "td",
            {},
            numberInput(amount[quantity], (value) => {
              amount[quantity] = value ?? 0;
              onChange();
            })
          ),
          h(
            "td",
            {},
            button("×", () => {
              amounts.splice(index, 1);
              render();
              onChange();
            })
          )
        )
      );
    });
    if (!amounts.length) {
      body.append(h("tr", {}, h("td", { colspan: 5, class: "text-secondary" }, "None")));
    }
  }

  render();
  return h(
    "div",
    {},
    h(
      "table",
      { class: "table table-sm align-middle mb-1" },
      h(
        "thead",
        {},
        h("tr", {}, ["Type", "Resource", "Environment", label, ""].map((t) => h("th", {}, t)))
      ),
      body
    ),
    button("Add Resource", () => {
      amounts.push({ classOfSupply: 2, environment: "Unpressurized", [quantity]: 0 });
      render();
      onChange();
    })
  );
}

// ----------------------------------------------------------------- elements

/** Lists an element state and its (recursively) nested contents with depths. */
export function flatten(elements, depth = 0, parent = null, result = []) {
  for (const element of elements || []) {
    result.push({ element, depth, parent });
    flatten(element.contents, depth + 1, element, result);
  }
  return result;
}

const TYPE_KINDS = {
  "Human Agent": "info",
  "Robotic Agent": "info",
  "Propulsive Vehicle": "danger",
  "Surface Vehicle": "success",
  "Element Carrier": "primary",
  "Resource Container": "warning",
};

export function typeBadge(type) {
  return badge(type || "Element", TYPE_KINDS[type] || "secondary");
}

/**
 * Creates a tree of element states.
 *
 * Options:
 *   checked: Set of identifiers shown with (and changed by) checkboxes
 *   selected: identifier of the element shown as selected
 *   onSelect(element): makes rows selectable
 *   onChange(): called when a checkbox changes
 *   filter(element): limits which elements can be checked or selected
 *   detail(element): text shown after the element name
 */
export function elementTree(elements, options = {}) {
  const { checked, selected, onSelect, onChange, filter = () => true, detail } = options;

  function item(element) {
    const enabled = filter(element);
    const label = [
      h("span", { class: enabled ? "" : "text-secondary" }, element.name),
      " ",
      typeBadge(element.type),
      element.state ? h("span", { class: "text-secondary small ms-1" }, `(${element.state})`) : null,
      detail ? h("span", { class: "text-secondary small ms-1" }, detail(element)) : null,
    ];
    let row;
    if (checked && enabled) {
      row = h(
        "div",
        { class: "sn-tree-row" },
        checkbox(label, checked.has(element.id), (value) => {
          if (value) checked.add(element.id);
          else checked.delete(element.id);
          onChange?.();
        })
      );
    } else {
      row = h(
        "div",
        {
          class:
            "sn-tree-row" +
            (onSelect && enabled ? " selectable" : "") +
            (selected === element.id ? " selected" : ""),
          onClick: onSelect && enabled ? () => onSelect(element) : null,
        },
        label
      );
    }
    return h(
      "li",
      {},
      row,
      element.contents?.length ? h("ul", {}, element.contents.map(item)) : null
    );
  }

  if (!elements?.length) return h("div", { class: "text-secondary small" }, "No elements");
  return h("ul", { class: "sn-tree" }, elements.map(item));
}

/** Creates a description of an element state with capacity and fuel bars. */
export function elementDetails(element) {
  const { capacityBars } = elementBars(element);
  return h(
    "div",
    {},
    h("div", { class: "fw-semibold" }, element.name, " ", typeBadge(element.type)),
    h(
      "div",
      { class: "small text-secondary mb-1" },
      [
        element.state ? `State: ${element.state} (${element.stateType})` : null,
        `Mass: ${fmt(element.mass)} kg`,
        `Total mass: ${fmt(element.totalMass)} kg`,
        store.scenario.configuration.volumeConstrained ? `Volume: ${fmt(element.volume, 4)} m³` : null,
      ]
        .filter(Boolean)
        .join(" · ")
    ),
    capacityBars,
    Object.keys(element.resources || {}).length
      ? h(
          "div",
          { class: "small" },
          Object.entries(element.resources).map(([name, amount]) =>
            h("div", {}, `${name}: ${fmt(amount)}`)
          )
        )
      : null
  );
}

export function elementBars(element) {
  const bars = [];
  const bar = (label, value, maximum, units) => {
    const over = value - maximum > 1e-9;
    const percent = maximum > 0 ? Math.min(100, (100 * value) / maximum) : value > 0 ? 100 : 0;
    return h(
      "div",
      { class: "sn-bar mb-1" },
      h("div", { class: "small text-secondary" }, label),
      h(
        "div",
        { class: "progress" },
        h(
          "div",
          {
            class: `progress-bar ${over ? "bg-danger-subtle" : "bg-success-subtle"}`,
            style: { width: `${percent}%` },
          },
          `${fmt(value)} / ${fmt(maximum)} ${units}`
        )
      )
    );
  };
  if (element.isCarrier || element.isContainer) {
    bars.push(bar("Cargo mass", element.cargoMass, element.maxCargoMass, "kg"));
    if (store.scenario.configuration.volumeConstrained) {
      bars.push(bar("Cargo volume", element.cargoVolume, element.maxCargoVolume, "m³"));
    }
  }
  if (element.isCarrier && element.maxCrewSize > 0) {
    bars.push(bar("Crew", element.crewSize, element.maxCrewSize, ""));
  }
  for (const tank of element.fuelTanks ?? []) {
    if (tank.maxAmount > 0) {
      bars.push(bar(`${tank.label} (${tank.fuelName ?? "none"})`, tank.amount, tank.maxAmount, ""));
    }
  }
  return { capacityBars: bars };
}

// ------------------------------------------------------------------- issues

/** Creates a list of errors and warnings. */
export function issueList(issues, { onSelect = null, empty = "No errors" } = {}) {
  if (!issues?.length) return h("div", { class: "text-success small" }, empty);
  return h(
    "div",
    { class: "list-group list-group-flush" },
    issues.map((issue) => {
      const kind = issue.kind === "warning" ? "warning" : issue.kind === "demand" ? "info" : "danger";
      const mission =
        issue.missionIndex !== null && issue.missionIndex !== undefined
          ? store.scenario.missionList[issue.missionIndex]
          : null;
      const event =
        mission && issue.eventIndex !== null && issue.eventIndex !== undefined
          ? mission.events[issue.eventIndex]
          : null;
      const source = event?.name ?? issue.eventName ?? mission?.name ?? "";
      return h(
        "div",
        {
          class: `list-group-item list-group-item-${kind} sn-issue py-1` + (onSelect && mission ? " list-group-item-action" : ""),
          style: onSelect && mission ? { cursor: "pointer" } : null,
          onClick: onSelect && mission ? () => onSelect(issue) : null,
        },
        issue.time !== undefined && issue.kind !== "scenario"
          ? h("span", { class: "text-secondary me-2" }, `${fmt(issue.time)} d`)
          : null,
        source ? h("strong", { class: "me-1" }, `${source}:`) : null,
        issue.message
      );
    })
  );
}

// -------------------------------------------------------------------- forms

/**
 * Creates form controls for the properties of a JSON schema object.
 * Empty inputs remove the property when `optional` is set.
 */
export function schemaForm(definition, target, names, onChange, { optional = false, placeholders = {} } = {}) {
  const root = store.schema;
  const resolve = (property) => {
    let schema = property;
    if (schema.anyOf) schema = schema.anyOf.find((option) => option.type !== "null") || schema;
    if (schema.$ref) schema = root.$defs[schema.$ref.split("/").pop()];
    return schema;
  };
  return h(
    "div",
    { class: "row g-2" },
    names.map((name) => {
      const property = definition.properties[name];
      if (!property) return null;
      const schema = resolve(property);
      const title = property.title || name;
      const set = (value) => {
        if (optional && (value === null || value === "")) delete target[name];
        else target[name] = value;
        onChange?.();
      };
      let control;
      if (schema.type === "boolean") {
        control = checkbox(title, target[name] ?? placeholders[name], set);
        return h("div", { class: "col-md-6", title: property.description }, control);
      }
      if (schema.enum) {
        const options = optional ? [["", "(default)"], ...schema.enum] : schema.enum;
        control = select(options, target[name], (value) => set(value === "" ? null : value));
      } else if (schema.type === "number" || schema.type === "integer") {
        control = numberInput(target[name], set, {
          min: schema.minimum,
          max: schema.maximum,
          placeholder: placeholders[name] ?? "",
        });
      } else {
        control = textInput(target[name], set, { placeholder: placeholders[name] ?? "" });
      }
      return h(
        "div",
        { class: "col-md-6", title: property.description },
        h("label", { class: "form-label small mb-0" }, title),
        control
      );
    })
  );
}

// ------------------------------------------------------------------- charts

export const COS_COLORS = {
  0: "#7f7f7f",
  1: "#d62728",
  2: "#1f77b4",
  3: "#17becf",
  4: "#ff7f0e",
  5: "#8c564b",
  6: "#2ca02c",
  7: "#bcbd22",
  8: "#9467bd",
  9: "#e377c2",
  10: "#7f7f7f",
};

export const EVENT_COLORS = {
  "Create Elements": "#2ca02c",
  "Move Elements": "#ff7f0e",
  "Transfer Resources": "#ff7f0e",
  "Add Resources": "#8c564b",
  "Remove Elements": "#000000",
  "Consume Resources": "#1f77b4",
  "Reconfigure Element": "#e377c2",
  "Reconfigure Elements": "#e377c2",
  "Propulsive Burn": "#d62728",
  "Space Transport": "#d62728",
  "Surface Transport": "#2ca02c",
  "Flight Transport": "#e0a800",
  "Crewed Exploration": "#17becf",
  "Crewed EVA": "#17becf",
};

export function cosName(id) {
  const item = store.enums.classesOfSupply.find((c) => c.id === Number(id));
  return item ? `COS ${item.id}: ${item.name}` : `COS ${id}`;
}

/** Gets the date of a simulation time (days after the scenario start). */
export function dateOf(days) {
  return addDays(store.scenario.startDate, days).toISOString();
}

const LAYOUT = {
  margin: { l: 60, r: 20, t: 20, b: 40 },
  font: { size: 11 },
  legend: { orientation: "h", y: -0.15 },
  hovermode: "closest",
};

/** Draws a chart (replacing any chart in the element). */
export function plot(element, traces, layout = {}) {
  if (!traces.length) {
    Plotly.purge(element);
    clear(element).append(h("div", { class: "sn-muted-box mt-3" }, "No data to display"));
    return;
  }
  if (element.querySelector(".sn-muted-box")) clear(element);
  Plotly.react(
    element,
    traces,
    {
      ...LAYOUT,
      ...layout,
      xaxis: { ...(layout.xaxis || {}) },
      yaxis: { automargin: true, ...(layout.yaxis || {}) },
    },
    { responsive: true, displaylogo: false }
  );
}

/**
 * Creates the traces of a "bat chart": events of missions over time by node.
 * Transports are lines between nodes, explorations are horizontal spans, and
 * other events are markers.
 */
export function batTraces(missions, { missionFilter = null, typeFilter = null } = {}) {
  const lines = {};
  const points = {};
  for (const mission of missions) {
    if (missionFilter && !missionFilter.has(mission.index)) continue;
    for (const event of mission.events) {
      if (typeFilter && !typeFilter.has(event.type)) continue;
      const text = `${event.name}<br>${mission.name}`;
      const start = dateOf(event.time);
      const duration = event.duration ?? 0;
      if (event.origin && event.destination) {
        const line = (lines[event.type] ||= { x: [], y: [], text: [] });
        line.x.push(start, dateOf(event.time + duration), null);
        line.y.push(store.locationName(event.origin), store.locationName(event.destination), null);
        line.text.push(text, text, null);
      } else if (duration > 0 && store.node(event.location)) {
        const line = (lines[event.type] ||= { x: [], y: [], text: [] });
        line.x.push(start, dateOf(event.time + duration), null);
        line.y.push(store.locationName(event.location), store.locationName(event.location), null);
        line.text.push(text, text, null);
      } else if (store.node(event.location)) {
        const point = (points[event.type] ||= { x: [], y: [], text: [] });
        point.x.push(start);
        point.y.push(store.locationName(event.location));
        point.text.push(text);
      }
    }
  }
  const traces = [];
  for (const [type, line] of Object.entries(lines)) {
    traces.push({
      ...line,
      name: type,
      mode: "lines+markers",
      line: { color: EVENT_COLORS[type], width: 3 },
      marker: { size: 5 },
      hovertemplate: "%{text}<br>%{x}<extra></extra>",
    });
  }
  for (const [type, point] of Object.entries(points)) {
    traces.push({
      ...point,
      name: type,
      mode: "markers",
      marker: { color: EVENT_COLORS[type], size: 9, symbol: "square" },
      hovertemplate: "%{text}<br>%{x}<extra></extra>",
    });
  }
  return traces;
}

/** Layout of a chart with network nodes on the vertical axis. */
export function nodeAxisLayout() {
  return {
    yaxis: {
      type: "category",
      categoryorder: "array",
      categoryarray: store.scenario.network.nodes.map((node) => node.name),
      automargin: true,
    },
    xaxis: { type: "date" },
  };
}

/** Creates a checklist with "all" and "none" shortcuts; returns {element, selected}. */
export function checklist(items, onChange, { selected = null } = {}) {
  const set = new Set(selected ?? items.map(([value]) => value));
  const list = h("div", { class: "sn-scroll-sm border rounded p-2" });
  function render() {
    clear(list).append(
      ...items.map(([value, label]) =>
        checkbox(label, set.has(value), (checked) => {
          if (checked) set.add(value);
          else set.delete(value);
          onChange();
        })
      )
    );
  }
  render();
  const element = h(
    "div",
    {},
    h(
      "div",
      { class: "mb-1" },
      button("All", () => {
        items.forEach(([value]) => set.add(value));
        render();
        onChange();
      }),
      " ",
      button("None", () => {
        set.clear();
        render();
        onChange();
      })
    ),
    list
  );
  return { element, selected: set };
}
