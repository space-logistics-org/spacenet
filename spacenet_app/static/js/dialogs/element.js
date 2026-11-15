// Dialog to edit an instantiated element. Empty fields inherit the value of
// the element template (shown as a placeholder).

import { resourceTable } from "../components.js";
import { store } from "../store.js";
import { button, clone, h, numberInput, openModal, select, textInput } from "../util.js";

const CARRIERS = ["Element Carrier", "Propulsive Vehicle", "Surface Vehicle"];
const VEHICLES = ["Propulsive Vehicle", "Surface Vehicle"];

/** Opens the dialog; resolves to the edited instance, or undefined if cancelled. */
export function openElement(instance) {
  const draft = clone(instance);
  const template = store.template(draft.templateId) ?? {};
  const body = h("div");

  const number = (label, name, units = "") =>
    h(
      "div",
      { class: "col-md-4" },
      h("label", { class: "form-label small mb-0" }, units ? `${label} (${units})` : label),
      numberInput(
        draft[name],
        (value) => {
          if (value === null) delete draft[name];
          else draft[name] = value;
        },
        { placeholder: template[name] ?? "", min: 0 }
      )
    );

  function render() {
    const type = draft.type;
    const states = template.states ?? [];
    const parts = [
      h(
        "div",
        { class: "row g-2 mb-3" },
        h(
          "div",
          { class: "col-md-8" },
          h("label", { class: "form-label small mb-0" }, "Name"),
          textInput(draft.name, (value) => (draft.name = value))
        ),
        h(
          "div",
          { class: "col-md-4" },
          h("label", { class: "form-label small mb-0" }, "Template"),
          h("input", {
            class: "form-control form-control-sm",
            value: `${template.name ?? "?"} (${type})`,
            disabled: true,
          })
        ),
        h(
          "div",
          { class: "col-12" },
          h("label", { class: "form-label small mb-0" }, "Description"),
          textInput(
            draft.description,
            (value) => {
              if (value) draft.description = value;
              else delete draft.description;
            },
            { placeholder: template.description ?? "" }
          )
        )
      ),
      h(
        "div",
        { class: "row g-2 mb-3" },
        number("Mass", "mass", "kg"),
        number("Volume", "volume", "m³"),
        states.length
          ? h(
              "div",
              { class: "col-md-4" },
              h("label", { class: "form-label small mb-0" }, "Initial State"),
              select(
                [["", `(template: ${states[template.currentStateIndex ?? 0]?.name ?? "none"})`], ...states.map((state, index) => [index, `${state.name} (${state.type})`])],
                draft.currentStateIndex ?? "",
                (value) => {
                  if (value === "") delete draft.currentStateIndex;
                  else draft.currentStateIndex = Number(value);
                }
              )
            )
          : null
      ),
    ];
    if (type === "Human Agent" || type === "Robotic Agent") {
      parts.push(h("div", { class: "row g-2 mb-3" }, number("Active Time Fraction", "activeTimeFraction")));
    }
    if (CARRIERS.includes(type) || type === "Resource Container") {
      parts.push(
        h(
          "div",
          { class: "row g-2 mb-3" },
          number("Max Cargo Mass", "maxCargoMass", "kg"),
          number("Max Cargo Volume", "maxCargoVolume", "m³"),
          CARRIERS.includes(type) ? number("Max Crew", "maxCrew") : null
        )
      );
    }
    if (VEHICLES.includes(type)) {
      // the initial fuel of each fuel tank of the template can be replaced
      const fuel = (label, templateTank, tank, change) =>
        h(
          "div",
          { class: "col-md-4" },
          h(
            "label",
            { class: "form-label small mb-0" },
            `${label} (${store.resourceLabel(templateTank.contents)})`
          ),
          numberInput(
            tank && tank.contents.amount !== templateTank.contents.amount ? tank.contents.amount : null,
            (value) => change(value ?? templateTank.contents.amount),
            { placeholder: templateTank.contents.amount, min: 0, max: tank?.maxAmount ?? templateTank.maxAmount }
          )
        );
      const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
      if (type === "Propulsive Vehicle") {
        const templateSystems = template.propulsionSystems ?? [];
        const find = (systems, system) => (systems ?? []).find((other) => other.type === system.type);
        parts.push(
          h(
            "div",
            { class: "small text-secondary mb-1" },
            templateSystems
              .map(
                (system) =>
                  `${system.type}: ${system.isp} s` +
                  (system.sharedFuelTank ? ` (${system.sharedFuelTank} fuel tank)` : "")
              )
              .join(" · ")
          ),
          h(
            "div",
            { class: "row g-2 mb-3" },
            templateSystems
              .filter((system) => system.fuelTank)
              .map((system) =>
                fuel(
                  `Initial ${system.type} Fuel`,
                  system.fuelTank,
                  find(draft.propulsionSystems, system)?.fuelTank,
                  (amount) => {
                    const systems = draft.propulsionSystems ?? clone(templateSystems);
                    const tank = find(systems, system)?.fuelTank;
                    if (tank) tank.contents.amount = amount;
                    if (same(systems, templateSystems)) delete draft.propulsionSystems;
                    else draft.propulsionSystems = systems;
                  }
                )
              )
          )
        );
      } else {
        parts.push(
          h(
            "div",
            { class: "row g-2 mb-3" },
            number("Max Speed", "maxSpeed", "km/h"),
            template.fuelTank
              ? fuel("Initial Fuel", template.fuelTank, draft.fuelTank, (amount) => {
                  const tank = draft.fuelTank ?? clone(template.fuelTank);
                  tank.contents.amount = amount;
                  if (same(tank, template.fuelTank)) delete draft.fuelTank;
                  else draft.fuelTank = tank;
                })
              : null
          )
        );
      }
    }
    if (type === "Resource Container") {
      const override = Array.isArray(draft.contents);
      const box = h("input", {
        type: "checkbox",
        class: "form-check-input me-2",
        checked: override,
        onChange: () => {
          if (box.checked) draft.contents = clone(template.contents ?? []);
          else delete draft.contents;
          render();
        },
      });
      parts.push(
        h("h6", {}, "Contents"),
        h("label", { class: "form-check-label mb-2" }, box, "Override the contents of the template"),
        override
          ? resourceTable(draft.contents, () => {})
          : h(
              "ul",
              { class: "mb-0" },
              (template.contents ?? []).map((amount) =>
                h("li", {}, `${store.resourceLabel(amount)}: ${amount.amount}`)
              ),
              (template.contents ?? []).length ? null : h("li", { class: "text-secondary" }, "Empty")
            )
      );
    }
    body.replaceChildren(...parts);
  }

  render();
  return openModal({
    title: "Edit Element",
    body,
    footer: (control) => [
      button("Cancel", () => control.close()),
      button("OK", () => control.close(draft), "primary"),
    ],
  }).closed;
}
