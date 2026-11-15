// Dialog to add or edit a demand model of a mission or of an element state.
// A demand model is an instance of a template; a new template is added to
// the scenario if none is chosen.

import { resourceTable, schemaForm } from "../components.js";
import { store } from "../store.js";
import { button, clone, h, openModal, select, textInput, uuid } from "../util.js";

const NEW = "";
const BASE_FIELDS = ["name", "type", "templateId", "demands"];

/**
 * Opens the dialog for a demand model instance ({type} for a new model).
 * Resolves to the instance, or undefined if cancelled.
 */
export function openDemandModel({ model }) {
  const isNew = !model.templateId;
  const type = model.type;
  const draft = { name: model.name ?? type, ...clone(model) };
  const templates = () => store.library("demandModels").filter((template) => template.type === type);
  let templateId = draft.templateId ?? templates()[0]?.id ?? NEW;
  // demands of a new template
  const newDemands = [];
  const usesDemands = type === "Timed Impulse" || type === "Rated";
  // schema of the parameters of other types (crew consumables, sparing by mass)
  const templateName = `${type.replace(/ /g, "")}DemandModel`;
  const parameters = () =>
    Object.keys(store.schema.$defs[`Inst${templateName}`].properties).filter(
      (name) => !BASE_FIELDS.includes(name)
    );
  const quantity = type === "Rated" ? "rate" : "amount";
  const quantityLabel = type === "Rated" ? "Rate (per day)" : "Amount";
  let override = Array.isArray(draft.demands);
  const body = h("div");

  function template() {
    return templates().find((item) => item.id === templateId);
  }

  function render() {
    const chosen = template();
    const options = [...templates().map((item) => [item.id, item.name]), [NEW, "(new demand model)"]];
    const parts = [
      h(
        "div",
        { class: "row g-2 mb-3" },
        h(
          "div",
          { class: "col-md-6" },
          h("label", { class: "form-label small mb-0" }, "Name"),
          textInput(draft.name, (value) => (draft.name = value))
        ),
        h(
          "div",
          { class: "col-md-6" },
          h("label", { class: "form-label small mb-0" }, "Template"),
          select(options, templateId, (value) => {
            templateId = value;
            render();
          })
        )
      ),
    ];
    if (usesDemands && !chosen) {
      parts.push(
        h("h6", {}, "Demands"),
        resourceTable(newDemands, () => {}, { quantity, label: quantityLabel })
      );
    } else if (usesDemands) {
      const overrideBox = h("input", {
        type: "checkbox",
        class: "form-check-input me-2",
        checked: override,
        onChange: () => {
          override = overrideBox.checked;
          draft.demands = override ? clone(draft.demands ?? chosen.demands ?? []) : undefined;
          render();
        },
      });
      parts.push(
        h("label", { class: "form-check-label mb-2" }, overrideBox, "Override the demands of the template"),
        override
          ? resourceTable(draft.demands, () => {}, { quantity, label: quantityLabel })
          : h(
              "ul",
              { class: "mb-0" },
              (chosen.demands ?? []).map((amount) =>
                h("li", {}, `${store.resourceLabel(amount)}: ${amount[quantity]}`)
              )
            )
      );
    } else {
      parts.push(
        h("h6", {}, "Parameters"),
        h(
          "div",
          { class: "small text-secondary mb-2" },
          "Empty parameters use the value of the template (shown as a placeholder)."
        ),
        schemaForm(store.schema.$defs[`Inst${templateName}`], draft, parameters(), null, {
          optional: true,
          placeholders: chosen ?? defaults(templateName),
        })
      );
    }
    body.replaceChildren(...parts);
  }

  function defaults(name) {
    const result = {};
    for (const [key, property] of Object.entries(store.schema.$defs[name].properties)) {
      if (property.default !== undefined) result[key] = property.default;
    }
    return result;
  }

  render();
  const control = openModal({
    title: `${isNew ? "Add" : "Edit"} ${type} Demand Model`,
    body,
    footer: (c) => [
      button("Cancel", () => c.close()),
      button(
        "OK",
        () => {
          if (templateId === NEW) {
            // a new template is added to the scenario
            const created = { id: uuid(), name: draft.name, type, description: "" };
            if (usesDemands) {
              created.demands = newDemands;
            } else {
              // the parameters define the new template (required ones default to none)
              const definition = store.schema.$defs[templateName];
              for (const name of parameters()) {
                if (draft[name] !== undefined && draft[name] !== null) created[name] = draft[name];
                else if (definition.required?.includes(name)) {
                  created[name] = definition.properties[name].type === "boolean" ? false : 0;
                }
                delete draft[name];
              }
            }
            store.update((scenario) => scenario.demandModels.push(created));
            templateId = created.id;
            delete draft.demands;
          } else {
            store.update(() => store.include("demandModels", templateId));
          }
          if (usesDemands && !override) delete draft.demands;
          c.close({ ...draft, type, templateId });
        },
        "primary"
      ),
    ],
  });
  return control.closed;
}
