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
      const fuel = draft.fuel ?? null;
      const templateFuel = template.fuel ?? null;
      parts.push(
        h(
          "div",
          { class: "row g-2 mb-3" },
          type === "Propulsive Vehicle" ? number("Specific Impulse", "isp", "s") : number("Max Speed", "maxSpeed", "km/h"),
          number("Max Fuel", "maxFuel", "units"),
          h(
            "div",
            { class: "col-md-4" },
            h(
              "label",
              { class: "form-label small mb-0" },
              `Initial Fuel (${templateFuel ? store.resourceLabel(templateFuel) : "units"})`
            ),
            numberInput(
              fuel?.amount,
              (value) => {
                if (value === null) delete draft.fuel;
                else if (templateFuel) draft.fuel = { ...clone(templateFuel), amount: value };
              },
              { placeholder: templateFuel?.amount ?? "", min: 0, disabled: !templateFuel }
            )
          )
        )
      );
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
