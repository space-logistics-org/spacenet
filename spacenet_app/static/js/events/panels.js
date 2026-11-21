// Panels of the event dialog: one function per event type which draws the
// controls of a draft event. Capacities, durations, and delta-v shown by
// the panels are computed by the server (see dialogs/event.js).

import { elementBars, elementTree, flatten, resourceTable, typeBadge } from "../components.js";
import { openElement } from "../dialogs/element.js";
import { store } from "../store.js";
import {
  badge,
  button,
  daysToIso,
  fmt,
  h,
  hoursToIso,
  isoToDays,
  isoToHours,
  numberInput,
  select,
  textInput,
  uuid,
} from "../util.js";

const section = (title, ...children) =>
  h("div", { class: "mb-3" }, h("h6", { class: "border-bottom pb-1" }, title), children);

const labeled = (label, control, size = "col-md-4") =>
  h("div", { class: size }, h("label", { class: "form-label small mb-0" }, label), control);

/** Gets the name of an element from the simulated state or the scenario. */
function elementName(ctx, id) {
  for (const location of ctx.state?.locations ?? []) {
    const found = flatten(location.elements).find((item) => item.element.id === id);
    if (found) return found.element.name;
  }
  return ctx.instances.find((element) => element.id === id)?.name ?? "?";
}

function elementType(ctx, id) {
  return ctx.instances.find((element) => element.id === id)?.type ?? null;
}

/** Options of a select of the elements at the location (indented by nesting). */
function elementOptions(ctx, filter = () => true, current = null) {
  const options = flatten(ctx.here())
    .filter(({ element }) => filter(element))
    .map(({ element, depth }) => [element.id, `${"  ".repeat(depth)}${element.name}`]);
  if (current && !options.some(([id]) => id === current)) {
    options.unshift([current, `${elementName(ctx, current)} (not at this location)`]);
  }
  return [["", "(select)"], ...options];
}

/** A select which stores the chosen element in a property of the draft. */
function elementSelect(ctx, name, filter, { refresh = false } = {}) {
  return select(elementOptions(ctx, filter, ctx.draft[name]), ctx.draft[name], (value) => {
    if (value) ctx.draft[name] = value;
    else delete ctx.draft[name];
    if (refresh) ctx.refresh();
    else ctx.changed();
  });
}

/** A tree with checkboxes which stores the chosen elements in the draft. */
function elementChecklist(ctx, name = "elements", { topLevelOnly = false, refresh = false } = {}) {
  ctx.draft[name] ||= [];
  const elements = ctx.here();
  const checked = new Set(ctx.draft[name]);
  const present = new Set(flatten(elements).map(({ element }) => element.id));
  const missing = ctx.draft[name].filter((id) => !present.has(id));
  const top = new Set(elements.map((element) => element.id));
  return h(
    "div",
    {},
    elementTree(elements, {
      checked,
      filter: (element) => !topLevelOnly || top.has(element.id),
      onChange: () => {
        ctx.draft[name] = [...checked];
        if (refresh) ctx.refresh();
        else ctx.changed();
      },
    }),
    missing.length
      ? h(
          "div",
          { class: "text-danger small mt-1" },
          "Not at this location: ",
          missing.map((id) =>
            h(
              "span",
              { class: "me-2" },
              elementName(ctx, id),
              " ",
              h(
                "a",
                {
                  href: "#",
                  onClick: (event) => {
                    event.preventDefault();
                    ctx.draft[name] = ctx.draft[name].filter((other) => other !== id);
                    ctx.refresh();
                  },
                },
                "remove"
              )
            )
          )
        )
      : null
  );
}

/** A select of the location or a carrier at the location. */
function containerSelect(ctx, name = "container") {
  ctx.draft[name] ||= ctx.draft.location;
  const options = [
    [ctx.draft.location, `${store.locationName(ctx.draft.location)} (location)`],
    ...elementOptions(ctx, (element) => element.isCarrier).slice(1),
  ];
  // carriers created by this event can receive elements of a later event only
  if (!options.some(([id]) => id === ctx.draft[name])) {
    options.push([ctx.draft[name], `${elementName(ctx, ctx.draft[name])} (not at this location)`]);
  }
  return select(options, ctx.draft[name], (value) => {
    ctx.draft[name] = value;
    ctx.changed();
  });
}

/** Shows the capacity of the carrier or container which receives the event. */
function containerBars(ctx) {
  const element = h("div");
  ctx.onEvaluation((evaluation) => {
    element.replaceChildren(
      ...(evaluation.container
        ? [
            h("div", { class: "small fw-semibold" }, `${evaluation.container.name} after this event`),
            ...elementBars(evaluation.container).capacityBars,
          ]
        : [])
    );
  });
  return element;
}

const isResourceHolder = (element) => element.isContainer || element.maxFuelAmount > 0;

// ----------------------------------------------------------- element events

function createElements(ctx, panel) {
  const draft = ctx.draft;
  draft.elements ||= [];
  const filter = { search: "", type: "" };
  const library = h("div", { class: "sn-scroll-sm border rounded" });
  const prefix = ctx.mission.name.slice(0, 5);

  function nextName(base) {
    const names = new Set(ctx.instances.map((element) => element.name));
    if (!names.has(base)) return base;
    for (const letter of "ABCDEFGHIJKLMNOPQRSTUVWXYZ") {
      if (!names.has(`${base} ${letter}`)) return `${base} ${letter}`;
    }
    return `${base} ${names.size}`;
  }

  function add(template) {
    store.update(() => store.include("elements", template.id));
    const instance = {
      id: uuid(),
      type: template.type,
      templateId: template.id,
      name: nextName(`${prefix} | ${template.name}`),
    };
    ctx.instances.push(instance);
    draft.elements.push(instance.id);
    ctx.refresh();
  }

  function drawLibrary() {
    const search = filter.search.toLowerCase();
    const templates = store
      .library("elements")
      .filter((template) => !filter.type || template.type === filter.type)
      .filter((template) => !search || template.name.toLowerCase().includes(search));
    library.replaceChildren(
      h(
        "table",
        { class: "table table-sm table-hover sn-table mb-0" },
        h(
          "tbody",
          {},
          templates.map((template) =>
            h(
              "tr",
              { onDblclick: () => add(template) },
              h("td", {}, template.name),
              h("td", {}, typeBadge(template.type)),
              h("td", { class: "text-end" }, `${fmt(template.mass)} kg`),
              h("td", { class: "text-end" }, button("Add", () => add(template), "outline-primary"))
            )
          ),
          templates.length
            ? null
            : h("tr", {}, h("td", { class: "text-secondary" }, "No element templates. Load a model database."))
        )
      )
    );
  }

  const created = h(
    "ul",
    { class: "list-group list-group-flush" },
    draft.elements.map((id) => {
      const instance = ctx.instances.find((element) => element.id === id);
      return h(
        "li",
        { class: "list-group-item d-flex align-items-center py-1 px-0" },
        h("span", { class: "me-auto" }, instance?.name ?? "?", " ", typeBadge(instance?.type)),
        instance
          ? button("Edit", async () => {
              const result = await openElement(instance);
              if (result) {
                ctx.instances[ctx.instances.indexOf(instance)] = result;
                ctx.refresh();
              }
            })
          : null,
        h("span", { class: "me-1" }),
        button(
          "×",
          () => {
            draft.elements = draft.elements.filter((other) => other !== id);
            ctx.refresh();
          },
          "outline-danger"
        )
      );
    }),
    draft.elements.length ? null : h("li", { class: "list-group-item text-secondary px-0" }, "Add elements from the library.")
  );

  drawLibrary();
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-6" },
        section("Create In", containerSelect(ctx), h("div", { class: "mt-2" }, containerBars(ctx))),
        section("Elements", created)
      ),
      h(
        "div",
        { class: "col-lg-6" },
        section(
          "Element Library",
          h(
            "div",
            { class: "row g-2 mb-2" },
            h(
              "div",
              { class: "col-7" },
              textInput("", (value) => {
                filter.search = value;
                drawLibrary();
              }, { placeholder: "Search by name" })
            ),
            h(
              "div",
              { class: "col-5" },
              select([["", "All types"], ...store.enums.elementTypes], "", (value) => {
                filter.type = value;
                drawLibrary();
              })
            )
          ),
          library
        )
      )
    )
  );
}

function moveElements(ctx, panel) {
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h("div", { class: "col-lg-6" }, section("Elements", elementChecklist(ctx))),
      h(
        "div",
        { class: "col-lg-6" },
        section("Move To", containerSelect(ctx), h("div", { class: "mt-2" }, containerBars(ctx)))
      )
    )
  );
}

function removeElements(ctx, panel) {
  panel.append(section("Elements to Remove", elementChecklist(ctx)));
}

function reconfigureElement(ctx, panel) {
  const draft = ctx.draft;
  draft.stateIndex ??= 0;
  const element = flatten(ctx.here()).find((item) => item.element.id === draft.element)?.element;
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-6" },
        section(
          "Element",
          elementTree(ctx.here(), {
            selected: draft.element,
            filter: (candidate) => candidate.states.length > 0,
            onSelect: (candidate) => {
              draft.element = candidate.id;
              draft.stateIndex = Math.max(0, candidate.stateIndex);
              ctx.refresh();
            },
          })
        )
      ),
      h(
        "div",
        { class: "col-lg-6" },
        section(
          "State",
          h("div", { class: "small text-secondary mb-1" }, `Current state: ${element?.state ?? "none"}`),
          select(
            (element?.states ?? []).map((name, index) => [index, `${name} (${element.stateTypes[index]})`]),
            draft.stateIndex,
            (value) => {
              draft.stateIndex = Number(value);
              ctx.changed();
            },
            { disabled: !element }
          )
        )
      )
    )
  );
}

function reconfigureElements(ctx, panel) {
  const draft = ctx.draft;
  draft.stateType ||= "Active";
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h("div", { class: "col-lg-6" }, section("Elements", elementChecklist(ctx))),
      h(
        "div",
        { class: "col-lg-6" },
        section(
          "New State Type",
          select(store.enums.stateTypes, draft.stateType, (value) => {
            draft.stateType = value;
            ctx.changed();
          }),
          h(
            "div",
            { class: "form-text" },
            "Each element changes to its first state of this type."
          )
        )
      )
    )
  );
}

// ---------------------------------------------------------- resource events

function addResources(ctx, panel) {
  ctx.draft.resources ||= [];
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        section(
          "Resource Container",
          elementSelect(ctx, "container", isResourceHolder),
          h("div", { class: "mt-2" }, containerBars(ctx))
        )
      ),
      h("div", { class: "col-lg-7" }, section("Resources", resourceTable(ctx.draft.resources, ctx.changed)))
    )
  );
}

function consumeResources(ctx, panel) {
  ctx.draft.resources ||= [];
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h("div", { class: "col-lg-5" }, section("Demanding Element", elementSelect(ctx, "source"))),
      h("div", { class: "col-lg-7" }, section("Resources", resourceTable(ctx.draft.resources, ctx.changed)))
    )
  );
}

/**
 * A select of an integral tank of a vehicle (origin or destination of a
 * transfer) which defaults to the tanks which hold the transferred resources.
 */
function tankSelect(ctx, element, name) {
  if (element?.type !== "Propulsive Vehicle" || !element.fuelTanks?.length) {
    delete ctx.draft[name];
    return null;
  }
  const options = [
    ["", "(tanks holding the resources)"],
    ...element.fuelTanks.map((tank) => [tank.key, `${tank.label} tank (${tank.fuelName ?? "empty"})`]),
  ];
  return h(
    "div",
    { class: "mt-2" },
    h("label", { class: "form-label small mb-0" }, "Tank"),
    select(options, ctx.draft[name] ?? "", (value) => {
      if (value) ctx.draft[name] = value;
      else delete ctx.draft[name];
      ctx.changed();
    })
  );
}

/** A table of the transfers of an evaluated transfer event. */
function transferResults(ctx) {
  const element = h("div");
  ctx.onEvaluation((evaluation) => {
    const transfers = evaluation.transfers ?? [];
    element.replaceChildren(
      transfers.length
        ? h(
            "table",
            { class: "table table-sm small mb-0" },
            h(
              "thead",
              {},
              h(
                "tr",
                {},
                ["Resource", "To", "Removed", "Delivered", "Lost", "Remaining space"].map((label) =>
                  h("th", {}, label)
                )
              )
            ),
            h(
              "tbody",
              {},
              transfers.map((transfer) =>
                h(
                  "tr",
                  {},
                  h("td", {}, transfer.resourceName),
                  h("td", {}, transfer.destinationName),
                  h("td", {}, fmt(transfer.removed, 1)),
                  h("td", {}, fmt(transfer.delivered, 1)),
                  h("td", {}, fmt(transfer.lost, 1)),
                  h("td", {}, fmt(transfer.destinationSpace, 1))
                )
              )
            )
          )
        : h("div", { class: "small text-secondary" }, "No resources transferred.")
    );
  });
  return element;
}

function transferResources(ctx, panel) {
  ctx.draft.resources ||= [];
  const find = (id) => flatten(ctx.here()).find((item) => item.element.id === id)?.element;
  const origin = find(ctx.draft.originContainer);
  const destination = find(ctx.draft.destinationContainer);
  const mode = ctx.draft.transferMode ?? "Amount";
  const modeHelp = {
    Amount: "Transfers the listed resource amounts.",
    "Fill Destination":
      "Transfers as much as possible to fill the destination, using the listed resources or else all resources of the origin.",
    "Empty Origin":
      "Transfers as much as possible to empty the origin, using the listed resources or else all resources of the origin.",
  };
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        section(
          "Transfer From",
          elementSelect(ctx, "originContainer", isResourceHolder, { refresh: true }),
          tankSelect(ctx, origin, "originTank"),
          origin
            ? h(
                "div",
                { class: "small text-secondary mt-1" },
                Object.entries(origin.resources).map(([name, amount]) => h("div", {}, `${name}: ${fmt(amount)}`))
              )
            : null
        ),
        section(
          "Transfer To",
          elementSelect(ctx, "destinationContainer", isResourceHolder, { refresh: true }),
          tankSelect(ctx, destination, "destinationTank"),
          h("div", { class: "mt-2" }, containerBars(ctx))
        )
      ),
      h(
        "div",
        { class: "col-lg-7" },
        section(
          "Transfer",
          h(
            "div",
            { class: "row g-2" },
            labeled(
              "Mode",
              select(store.enums.transferModes ?? ["Amount"], mode, (value) => {
                if (value === "Amount") delete ctx.draft.transferMode;
                else ctx.draft.transferMode = value;
                ctx.refresh();
              }),
              "col-md-6"
            ),
            labeled(
              "Loss (%)",
              numberInput(
                ctx.draft.lossFraction ? ctx.draft.lossFraction * 100 : null,
                (value) => {
                  if (value) ctx.draft.lossFraction = value / 100;
                  else delete ctx.draft.lossFraction;
                  ctx.changed();
                },
                { min: 0, max: 99.9, placeholder: 0 }
              ),
              "col-md-3"
            )
          ),
          h("div", { class: "form-text" }, modeHelp[mode])
        ),
        section(
          mode === "Amount" ? "Resources" : "Resources (optional)",
          resourceTable(ctx.draft.resources, ctx.changed)
        ),
        section("Result", transferResults(ctx))
      )
    )
  );
}

// ------------------------------------------------------------------- burns

/**
 * Builds a sequence of burn (fire engine) and stage (discard element)
 * actions and shows the delta-v achieved as evaluated by the server.
 */
function burnSequence(ctx, actions, getBurn, elementIds) {
  const gauge = h("div");
  const list = h("ol", { class: "mb-2 ps-3" });
  const candidates = elementIds().map((id) => [id, elementName(ctx, id)]);
  let chosen = candidates[0]?.[0] ?? "";

  function drawList() {
    list.replaceChildren(
      ...actions.map((action, index) =>
        h(
          "li",
          {},
          badge(action.type, action.type === "Burn" ? "danger" : "dark"),
          " ",
          elementName(ctx, action.element),
          " ",
          h(
            "a",
            {
              href: "#",
              class: "small",
              onClick: (event) => {
                event.preventDefault();
                actions.splice(index, 1);
                drawList();
                ctx.changed();
              },
            },
            "remove"
          )
        )
      )
    );
    if (!actions.length) list.append(h("li", { class: "text-secondary" }, "No actions"));
  }

  const add = (type) => {
    if (!chosen) return;
    actions.push({ element: chosen, type });
    drawList();
    ctx.changed();
  };

  ctx.onEvaluation((evaluation) => {
    const burn = getBurn(evaluation);
    if (!burn) {
      gauge.replaceChildren();
      return;
    }
    const required = burn.deltaVRequired;
    const complete = burn.deltaVRemaining <= 1e-6;
    const percent = required > 0 ? Math.min(100, (100 * burn.deltaVAchieved) / required) : 100;
    const parts = [
      h(
        "div",
        { class: "sn-bar mb-1" },
        h(
          "div",
          { class: "progress" },
          h(
            "div",
            {
              class: `progress-bar ${complete ? "bg-success-subtle" : "bg-danger-subtle"}`,
              style: { width: `${percent}%` },
            },
            `${fmt(burn.deltaVAchieved, 1)} / ${fmt(required, 1)} m/s`
          )
        )
      ),
      h(
        "div",
        { class: "small text-secondary" },
        burn.executed
          ? `Stack mass: ${fmt(burn.stackMass, 1)} kg`
          : "Not executed (an earlier error stopped the transport)"
      ),
      burn.steps.length
        ? h(
            "table",
            { class: "table table-sm sn-table mb-0 mt-1" },
            h(
              "thead",
              {},
              h("tr", {}, ["Action", "Element", "Stack (kg)", "Δv (m/s)", "Fuel used", "Fuel left"].map((t) => h("th", {}, t)))
            ),
            h(
              "tbody",
              {},
              burn.steps.map((step) =>
                h(
                  "tr",
                  { class: step.message ? "table-danger" : "", title: step.message ?? "" },
                  h("td", {}, step.action),
                  h("td", {}, step.elementName),
                  h("td", {}, fmt(step.stackMass, 1)),
                  h("td", {}, step.action === "Burn" ? fmt(step.deltaVAchieved, 1) : ""),
                  h("td", {}, step.action === "Burn" ? fmt(step.fuelUsed, 1) : ""),
                  h("td", {}, step.action === "Burn" ? fmt(step.fuelRemaining, 1) : "")
                )
              )
            )
          )
        : null,
    ];
    gauge.replaceChildren(...parts.filter(Boolean));
  });

  drawList();
  return h(
    "div",
    {},
    list,
    h(
      "div",
      { class: "input-group input-group-sm mb-2" },
      select(candidates.length ? candidates : [["", "(select elements first)"]], chosen, (value) => (chosen = value)),
      button("Burn", () => {
        if (elementType(ctx, chosen) === "Propulsive Vehicle") add("Burn");
      }, "outline-danger", { title: "Fire the engine of a propulsive vehicle" }),
      button("Stage", () => add("Stage"), "outline-dark", { title: "Discard the element" }),
      button("Clear", () => {
        actions.length = 0;
        drawList();
        ctx.changed();
      })
    ),
    gauge
  );
}

function propulsiveBurn(ctx, panel) {
  const draft = ctx.draft;
  draft.elements ||= [];
  draft.burnStageSequence ||= [];
  const burns = store.scenario.network.edges.flatMap((edge) =>
    (edge.burns ?? []).map((burn, index) => [
      burn.id,
      `${edge.name}: burn ${index + 1} (${fmt(burn.deltaV)} m/s, ${burn.type ?? "OMS"})`,
    ])
  );
  draft.burn ||= burns[0]?.[0];
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        section(
          "Burn",
          select(burns.length ? burns : [["", "(no burns in the network)"]], draft.burn, (value) => {
            draft.burn = value;
            ctx.changed();
          })
        ),
        section("Elements", elementChecklist(ctx, "elements", { refresh: true }))
      ),
      h(
        "div",
        { class: "col-lg-7" },
        section(
          "Burn and Stage Sequence",
          burnSequence(ctx, draft.burnStageSequence, (evaluation) => evaluation.burns[0], () => draft.elements)
        )
      )
    )
  );
}

// -------------------------------------------------------------- transports

function edgeSelect(ctx, type, allowReverse = false) {
  const draft = ctx.draft;
  const edges = store.scenario.network.edges.filter(
    (edge) =>
      edge.type === type &&
      (edge.origin === draft.location || (allowReverse && edge.destination === draft.location))
  );
  if (!edges.some((edge) => edge.id === draft.edge)) draft.edge = edges[0]?.id;
  if (!draft.edge) delete draft.edge;
  const info = h("div", { class: "small text-secondary mt-1" });
  ctx.onEvaluation((evaluation) => {
    const transport = evaluation.transport;
    info.textContent = transport
      ? `Destination: ${store.locationName(transport.destination)} · Duration: ${
          transport.duration === null ? "infinite" : `${fmt(transport.duration, 3)} days`
        }`
      : "";
  });
  return h(
    "div",
    {},
    select(
      edges.length ? edges.map((edge) => [edge.id, edge.name]) : [["", `(no ${type.toLowerCase()} from this location)`]],
      draft.edge,
      (value) => {
        draft.edge = value;
        ctx.refresh();
      }
    ),
    info
  );
}

function spaceTransport(ctx, panel) {
  const draft = ctx.draft;
  draft.elements ||= [];
  draft.burnStageSequence ||= [];
  const edgeControl = edgeSelect(ctx, "Space Edge");
  const edge = store.edge(draft.edge);
  const burns = edge?.burns ?? [];
  // one sequence for each burn of the edge
  draft.burnStageSequence = burns.map(
    (burn) =>
      draft.burnStageSequence.find((sequence) => sequence.burn === burn.id) ?? {
        burn: burn.id,
        actions: [],
      }
  );
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        section("Trajectory", edgeControl),
        section("Elements", elementChecklist(ctx, "elements", { topLevelOnly: true, refresh: true }))
      ),
      h(
        "div",
        { class: "col-lg-7" },
        burns.map((burn, index) =>
          section(
            `Burn ${index + 1} (${burn.type ?? "OMS"}): ${fmt(burn.deltaV)} m/s at ${fmt(isoToDays(burn.time), 3)} days`,
            burnSequence(
              ctx,
              draft.burnStageSequence[index].actions,
              (evaluation) => evaluation.burns.find((result) => result.burnId === burn.id),
              () => draft.elements
            )
          )
        ),
        burns.length ? null : h("div", { class: "text-secondary" }, "Select a trajectory.")
      )
    )
  );
}

function flightTransport(ctx, panel) {
  ctx.draft.elements ||= [];
  const bars = h("div");
  ctx.onEvaluation((evaluation) => {
    const transport = evaluation.transport;
    bars.replaceChildren(
      ...(transport
        ? [
            elementBars({
              isCarrier: true,
              cargoMass: transport.cargoMass,
              maxCargoMass: transport.maxCargoMass,
              crewSize: transport.crewSize,
              maxCrewSize: Math.max(1, transport.maxCrewSize),
              cargoVolume: 0,
              maxCargoVolume: 0,
            }).capacityBars.filter((_, index) => index !== 1 || !store.scenario.configuration.volumeConstrained),
          ].flat()
        : [])
    );
  });
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        section("Flight", edgeSelect(ctx, "Flight Edge")),
        section("Flight Capacity", bars)
      ),
      h(
        "div",
        { class: "col-lg-7" },
        section("Elements", elementChecklist(ctx, "elements", { topLevelOnly: true }))
      )
    )
  );
}

function surfaceTransport(ctx, panel) {
  const draft = ctx.draft;
  draft.speed ??= 1;
  draft.dutyCycle ??= 1;
  const vehicle = flatten(ctx.here()).find((item) => item.element.id === draft.vehicle)?.element;
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h("div", { class: "col-lg-5" }, section("Surface Edge", edgeSelect(ctx, "Surface Edge", true))),
      h(
        "div",
        { class: "col-lg-7" },
        section(
          "Surface Vehicle",
          h(
            "div",
            { class: "row g-2" },
            labeled(
              "Vehicle",
              elementSelect(ctx, "vehicle", (element) => element.type === "Surface Vehicle", { refresh: true }),
              "col-md-6"
            ),
            labeled(
              "State During Transport",
              select(
                [["", "(no change)"], ...(vehicle?.states ?? []).map((name, index) => [index, name])],
                draft.transportState ?? "",
                (value) => {
                  if (value === "") delete draft.transportState;
                  else draft.transportState = Number(value);
                  ctx.changed();
                }
              ),
              "col-md-6"
            ),
            labeled(
              "Speed (m/s)",
              numberInput(draft.speed, (value) => {
                draft.speed = value ?? 0;
                ctx.changed();
              }, { min: 0 }),
              "col-md-6"
            ),
            labeled(
              "Duty Cycle (0 to 1)",
              numberInput(draft.dutyCycle, (value) => {
                draft.dutyCycle = value ?? 0;
                ctx.changed();
              }, { min: 0, max: 1, step: 0.05 }),
              "col-md-6"
            )
          )
        ),
        section("Traverse", traverseSummary(ctx))
      )
    )
  );
}

/** Summary of the distance, speed, fuel, and energy of an evaluated traverse. */
function traverseSummary(ctx) {
  const element = h("div", { class: "small" });
  ctx.onEvaluation(({ transport }) => {
    if (transport?.distance === null || transport?.distance === undefined) {
      element.replaceChildren(h("span", { class: "text-secondary" }, "Select an edge and a vehicle."));
      return;
    }
    const row = (label, value, warn = false) =>
      h("tr", {}, h("td", {}, label), h("td", { class: `text-end ${warn ? "text-danger fw-semibold" : ""}` }, value));
    const fast = transport.maxSpeed > 0 && transport.speed > transport.maxSpeed;
    element.replaceChildren(
      h(
        "table",
        { class: "table table-sm mb-0" },
        h(
          "tbody",
          {},
          row("Distance", `${fmt(transport.distance, 1)} km`),
          row(
            "Speed",
            `${fmt(transport.speed, 1)} km/h` + (transport.maxSpeed ? ` (max ${fmt(transport.maxSpeed, 1)})` : ""),
            fast
          ),
          transport.fuelRequired
            ? row(
                "Fuel",
                `${fmt(transport.fuelRequired, 1)} of ${fmt(transport.fuelAvailable, 1)} units`,
                transport.fuelRequired > transport.fuelAvailable
              )
            : null,
          transport.energyRequired
            ? row(
                "Energy",
                `${fmt(transport.energyRequired, 1)} of ${fmt(transport.energyAvailable, 1)} kWh`,
                transport.energyRequired > transport.energyAvailable
              )
            : null
        )
      )
    );
  });
  return element;
}

// ------------------------------------------------------------ crew events

function crewActivity(ctx, panel, isExploration) {
  const draft = ctx.draft;
  draft.evaDuration ||= "PT8H";
  draft.elementStates ||= [];
  draft.additionalDemands ||= [];
  if (isExploration) {
    draft.duration ||= "P7D";
    draft.evaPerWeek ??= 5;
  }
  const crew = flatten(ctx.here()).filter(({ element }) => element.isCrew);
  const included = (id) => draft.elementStates.find((item) => item.element === id);
  const table = h(
    "table",
    { class: "table table-sm align-middle mb-0" },
    h("thead", {}, h("tr", {}, ["EVA?", "Crew Member", "EVA State"].map((t) => h("th", {}, t)))),
    h(
      "tbody",
      {},
      crew.map(({ element }) => {
        const entry = included(element.id);
        return h(
          "tr",
          {},
          h(
            "td",
            {},
            h("input", {
              type: "checkbox",
              class: "form-check-input",
              checked: Boolean(entry),
              onChange: () => {
                if (entry) {
                  draft.elementStates = draft.elementStates.filter((item) => item !== entry);
                } else {
                  draft.elementStates.push({ element: element.id, stateIndex: -1 });
                }
                ctx.refresh();
              },
            })
          ),
          h("td", {}, element.name),
          h(
            "td",
            {},
            select(
              [[-1, "(no change)"], ...element.states.map((name, index) => [index, name])],
              entry?.stateIndex ?? -1,
              (value) => {
                if (entry) entry.stateIndex = Number(value);
                ctx.changed();
              },
              { disabled: !entry }
            )
          )
        );
      }),
      crew.length ? null : h("tr", {}, h("td", { colspan: 3, class: "text-secondary" }, "No crew members at this location"))
    )
  );
  panel.append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        section(
          isExploration ? "Exploration" : "Extra-Vehicular Activity",
          h(
            "div",
            { class: "row g-2" },
            isExploration
              ? [
                  labeled(
                    "Duration (days)",
                    numberInput(isoToDays(draft.duration), (value) => {
                      draft.duration = daysToIso(value ?? 0);
                      ctx.changed();
                    }, { min: 0 }),
                    "col-md-4"
                  ),
                  labeled(
                    "EVAs per Week",
                    numberInput(draft.evaPerWeek, (value) => {
                      draft.evaPerWeek = value ?? 0;
                      ctx.changed();
                    }, { min: 0, step: 1 }),
                    "col-md-4"
                  ),
                ]
              : null,
            labeled(
              "EVA Duration (hours)",
              numberInput(isoToHours(draft.evaDuration), (value) => {
                draft.evaDuration = hoursToIso(value ?? 0);
                ctx.changed();
              }, { min: 0 }),
              "col-md-4"
            )
          )
        ),
        section("Crew Location", elementSelect(ctx, "vehicle", (element) => element.isCarrier)),
        section("Crew", table)
      ),
      h(
        "div",
        { class: "col-lg-7" },
        section(
          "Additional Demands per EVA",
          resourceTable(draft.additionalDemands, ctx.changed)
        )
      )
    )
  );
}

export const PANELS = {
  "Create Elements": createElements,
  "Move Elements": moveElements,
  "Remove Elements": removeElements,
  "Reconfigure Element": reconfigureElement,
  "Reconfigure Elements": reconfigureElements,
  "Add Resources": addResources,
  "Consume Resources": consumeResources,
  "Transfer Resources": transferResources,
  "Propulsive Burn": propulsiveBurn,
  "Crewed EVA": (ctx, panel) => crewActivity(ctx, panel, false),
  "Crewed Exploration": (ctx, panel) => crewActivity(ctx, panel, true),
  "Flight Transport": flightTransport,
  "Surface Transport": surfaceTransport,
  "Space Transport": spaceTransport,
};
