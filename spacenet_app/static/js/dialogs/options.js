// Scenario options dialog generated from the configuration schema.

import { schemaForm } from "../components.js";
import { store } from "../store.js";
import { button, clone, h, openModal } from "../util.js";

const GROUPS = [
  ["Numerical Precision", ["timePrecision", "demandPrecision", "massPrecision", "volumePrecision"]],
  ["Cargo Constraints", ["volumeConstrained", "environmentConstrained"]],
  ["Discrete Demands", ["itemDiscretization", "itemAggregation", "scavengeSpares"]],
  ["Simulation Detail", ["detailedExploration", "detailedEva", "timePhasedConsumables"]],
  ["Part Failures", ["partFailures", "randomSeed"]],
  [
    "Generic Packing Factors (kg of packing per kg)",
    [
      "genericPackingFactorGas",
      "genericPackingFactorLiquid",
      "genericPackingFactorPressurized",
      "genericPackingFactorUnpressurized",
    ],
  ],
];

export function openOptions() {
  const definition = store.schema.$defs.Configuration;
  const draft = clone(store.scenario.configuration);
  const grouped = new Set(GROUPS.flatMap(([, names]) => names));
  const containers = Object.keys(definition.properties).filter((name) => !grouped.has(name));
  const body = h(
    "div",
    {},
    [...GROUPS, ["Resource Containers", containers]].map(([title, names]) =>
      h(
        "div",
        { class: "mb-3" },
        h("h6", { class: "border-bottom pb-1" }, title),
        schemaForm(definition, draft, names)
      )
    )
  );
  openModal({
    title: "Scenario Options",
    body,
    footer: (control) => [
      button("Cancel", () => control.close()),
      button(
        "OK",
        () => {
          store.update((scenario) => (scenario.configuration = draft));
          control.close();
        },
        "primary"
      ),
    ],
  });
}
