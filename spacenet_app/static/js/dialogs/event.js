// Dialog to add or edit an event of a mission.
//
// The server simulates the scenario up to the time of the event so that
// the dialog offers the elements which are actually at the location, and
// evaluates each change of the draft event (errors, capacities, delta-v).

import { api, ApiError, latest } from "../api.js";
import { issueList } from "../components.js";
import { PANELS } from "../events/panels.js";
import { store } from "../store.js";
import {
  button,
  clone,
  daysToIso,
  debounce,
  fmt,
  h,
  isoToDays,
  numberInput,
  openModal,
  select,
  textInput,
} from "../util.js";

/**
 * Opens the dialog for a (copy of an) event of a mission. Resolves to the
 * saved event, or undefined if cancelled.
 */
export function openEventDialog({ mission, event, eventIndex }) {
  const missionIndex = store.scenario.missionList.indexOf(mission);
  const ctx = {
    mission,
    missionIndex,
    eventIndex,
    draft: event,
    // elements instantiated by the draft are only saved with the event
    instances: clone(store.scenario.instantiatedElements),
    state: null,
    evaluation: null,
    slots: [],
    scenario() {
      return { ...store.scenario, instantiatedElements: this.instances };
    },
    /** Element states at the location of the event (before the event). */
    here() {
      return this.state?.locations.find((l) => l.id === this.draft.location)?.elements ?? [];
    },
    /** Registers a function which displays the evaluation of the draft. */
    onEvaluation(show) {
      this.slots.push(show);
      if (this.evaluation) show(this.evaluation);
    },
    /** The draft changed: evaluate it. */
    changed() {
      evaluate();
    },
    /** The draft changed in a way which changes the controls shown. */
    refresh() {
      renderPanel();
      evaluate();
    },
  };

  const panel = h("div");
  const issues = h("div", { class: "mt-3" });
  const stateNote = h("div", { class: "small text-secondary mb-2" });
  let incomplete = null;

  const requestState = latest((signal) =>
    api.eventState(
      ctx.scenario(),
      {
        missionIndex,
        missionTime: ctx.draft.missionTime,
        priority: ctx.draft.priority,
        excludeEventIndex: eventIndex,
      },
      signal
    )
  );
  const requestEvaluation = latest((signal) =>
    api.evaluateEvent(ctx.scenario(), { missionIndex, eventIndex, event: ctx.draft }, signal)
  );

  async function loadState() {
    stateNote.textContent = "Pre-simulating…";
    try {
      const state = await requestState();
      if (state === undefined) return;
      ctx.state = state;
      stateNote.textContent = `State at day ${fmt(state.time, 3)} of the scenario, before this event.`;
    } catch (error) {
      if (!(error instanceof ApiError)) throw error;
      ctx.state = null;
      stateNote.textContent = `The scenario cannot be simulated: ${error.message}`;
    }
    ctx.refresh();
  }

  async function runEvaluation() {
    try {
      const evaluation = await requestEvaluation();
      if (evaluation === undefined) return undefined;
      ctx.evaluation = evaluation;
      incomplete = null;
      for (const show of ctx.slots) show(evaluation);
      issues.replaceChildren(
        h("h6", {}, "Evaluation"),
        issueList(evaluation.issues, { empty: "The event can be executed." })
      );
      return evaluation;
    } catch (error) {
      if (!(error instanceof ApiError)) throw error;
      incomplete = error;
      issues.replaceChildren(
        h("h6", {}, "Evaluation"),
        h("div", { class: "text-danger small" }, `The event is incomplete or invalid: ${error.message}`)
      );
      return null;
    }
  }

  const evaluate = debounce(runEvaluation, 250);
  const reloadState = debounce(loadState, 300);

  function renderPanel() {
    ctx.slots = [];
    panel.replaceChildren();
    const draw = PANELS[ctx.draft.type];
    if (draw) draw(ctx, panel);
  }

  const locations = [
    ...store.scenario.network.nodes.map((node) => [node.id, node.name]),
    ...store.scenario.network.edges.map((edge) => [edge.id, `${edge.name} (edge)`]),
  ];
  const header = h(
    "div",
    { class: "row g-2 mb-2" },
    h(
      "div",
      { class: "col-md-5" },
      h("label", { class: "form-label small mb-0" }, "Name"),
      textInput(ctx.draft.name, (value) => (ctx.draft.name = value))
    ),
    h(
      "div",
      { class: "col-md-3" },
      h("label", { class: "form-label small mb-0" }, "Location"),
      select(locations, ctx.draft.location, (value) => {
        ctx.draft.location = value;
        reloadState();
      })
    ),
    h(
      "div",
      { class: "col-md-2" },
      h("label", { class: "form-label small mb-0" }, "Time (days)"),
      numberInput(
        isoToDays(ctx.draft.missionTime),
        (value) => {
          ctx.draft.missionTime = daysToIso(Math.max(0, value ?? 0));
          reloadState();
        },
        { min: 0, step: store.scenario.configuration.timePrecision || "any" }
      )
    ),
    h(
      "div",
      { class: "col-md-2" },
      h("label", { class: "form-label small mb-0" }, "Priority"),
      select([1, 2, 3, 4, 5], ctx.draft.priority, (value) => {
        ctx.draft.priority = Number(value);
        reloadState();
      })
    )
  );

  const control = openModal({
    title: `${eventIndex === null ? "Add" : "Edit"} ${ctx.draft.type}`,
    size: "xl",
    body: h("div", {}, header, stateNote, panel, issues),
    footer: (c) => [
      button("Cancel", () => c.close()),
      button(
        "OK",
        async () => {
          // the draft must at least be a valid event
          const evaluation = await runEvaluation();
          if (!evaluation || incomplete) return;
          let saved;
          store.update((scenario) => {
            const events = scenario.missionList[missionIndex].events;
            saved = ctx.draft;
            if (eventIndex === null) events.push(saved);
            else events[eventIndex] = saved;
            events.sort(
              (a, b) =>
                isoToDays(a.missionTime) - isoToDays(b.missionTime) || a.priority - b.priority
            );
            scenario.instantiatedElements = ctx.instances;
            store.pruneInstances();
          });
          c.close(saved);
        },
        "primary"
      ),
    ],
  });
  renderPanel();
  loadState();
  return control.closed;
}
