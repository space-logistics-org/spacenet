// Missions tab: the list of missions with charts of their events and the
// editor of one mission and its events.

import { api } from "../api.js";
import { batTraces, checklist, dateOf, issueList, nodeAxisLayout, plot } from "../components.js";
import { openDemandModel } from "../dialogs/demandModel.js";
import { openEventDialog } from "../dialogs/event.js";
import { store } from "../store.js";
import {
  addDays,
  badge,
  button,
  clear,
  clone,
  confirmDialog,
  daysToIso,
  fmt,
  formatDate,
  fromInputDate,
  h,
  isoToDays,
  redraw,
  select,
  textInput,
  toInputDate,
  uuid,
} from "../util.js";

const state = {
  mission: null, // mission being edited
  selectedMission: null,
  selectedEvent: null,
  chart: "process",
  missionFilter: null,
  typeFilter: null,
  elementFilter: null,
};

let root;

export function init(container) {
  root = container;
  store.on("scenario", () => {
    Object.assign(state, {
      mission: null,
      selectedMission: null,
      selectedEvent: null,
      missionFilter: null,
      typeFilter: null,
      elementFilter: null,
    });
  });
}

export function render() {
  if (!root || !store.scenario) return;
  const missions = store.scenario.missionList;
  if (state.mission && !missions.includes(state.mission)) state.mission = null;
  redraw(root, () => (state.mission ? drawMission() : drawList()));
}

/** Opens the editor of a mission (optionally selecting one of its events). */
export function editMission(missionIndex, eventIndex = null) {
  state.mission = store.scenario.missionList[missionIndex] ?? null;
  state.selectedEvent = state.mission?.events[eventIndex] ?? null;
  render();
}

const analysisOf = (mission) =>
  store.analysis?.missions?.[store.scenario.missionList.indexOf(mission)] ?? null;

function sortMissions(scenario) {
  scenario.missionList.sort((a, b) => new Date(a.startDate) - new Date(b.startDate));
}

// ------------------------------------------------------------ mission list

function addMission() {
  store.update((scenario) => {
    const previous = scenario.missionList.at(-1);
    const summary = previous ? analysisOf(previous) : null;
    const mission = {
      name: `Mission ${scenario.missionList.length + 1}`,
      startDate: previous
        ? addDays(previous.startDate, summary?.duration ?? 0).toISOString().replace(".000Z", "Z")
        : scenario.startDate,
      events: [],
      demandModels: [],
      origin: previous?.origin ?? scenario.network.nodes[0].id,
      destination: previous?.destination ?? scenario.network.nodes.at(-1).id,
      returnOrigin: previous?.returnOrigin ?? null,
      returnDestination: previous?.returnDestination ?? null,
    };
    scenario.missionList.push(mission);
    sortMissions(scenario);
    state.selectedMission = mission;
    state.mission = mission;
  });
}

function copyMission(mission) {
  store.update((scenario) => {
    // elements created by the mission are copied with new identifiers
    const created = new Set(
      mission.events.filter((e) => e.type === "Create Elements").flatMap((e) => e.elements)
    );
    let text = JSON.stringify(mission);
    const instances = scenario.instantiatedElements.filter((element) => created.has(element.id));
    let instancesText = JSON.stringify(instances);
    for (const id of created) {
      const copy = uuid();
      text = text.replaceAll(id, copy);
      instancesText = instancesText.replaceAll(id, copy);
    }
    const copy = JSON.parse(text);
    copy.name = `${mission.name} (Copy)`;
    const start = new Date(mission.startDate);
    start.setUTCMonth(start.getUTCMonth() + 1);
    copy.startDate = start.toISOString().replace(".000Z", "Z");
    scenario.instantiatedElements.push(...JSON.parse(instancesText));
    scenario.missionList.push(copy);
    sortMissions(scenario);
    state.selectedMission = copy;
  });
}

async function removeMission(mission) {
  if (!(await confirmDialog("Remove Mission", `Remove ${mission.name} and its events?`))) return;
  store.update((scenario) => {
    scenario.missionList = scenario.missionList.filter((other) => other !== mission);
    store.pruneInstances();
    state.selectedMission = null;
  });
}

function drawList() {
  const scenario = store.scenario;
  const missions = scenario.missionList;
  const selected = missions.includes(state.selectedMission) ? state.selectedMission : null;
  const table = h(
    "table",
    { class: "table table-sm table-hover sn-table mb-0" },
    h("thead", {}, h("tr", {}, ["#", "Start Date", "Mission", "Events", ""].map((t) => h("th", {}, t)))),
    h(
      "tbody",
      {},
      missions.map((mission, index) => {
        const summary = analysisOf(mission);
        return h(
          "tr",
          {
            class: mission === selected ? "table-active" : "",
            onClick: () => {
              state.selectedMission = mission;
              render();
            },
            onDblclick: () => editMission(index),
          },
          h("td", {}, index + 1),
          h("td", {}, formatDate(mission.startDate)),
          h("td", {}, mission.name),
          h("td", {}, mission.events.length),
          h(
            "td",
            {},
            summary?.errorCount ? badge(`${summary.errorCount} errors`, "danger") : null,
            " ",
            summary?.warningCount ? badge(`${summary.warningCount} warnings`, "warning") : null
          )
        );
      }),
      missions.length
        ? null
        : h("tr", {}, h("td", { colspan: 5, class: "text-secondary" }, "No missions. Add a mission to begin."))
    )
  );
  const chart = h("div", { class: "sn-chart" });
  const options = h("div");
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-5" },
        h(
          "div",
          { class: "mb-2" },
          button("Add", addMission, "primary"),
          " ",
          button("Edit", () => editMission(missions.indexOf(selected)), "outline-secondary", { disabled: !selected }),
          " ",
          button("Copy", () => copyMission(selected), "outline-secondary", { disabled: !selected }),
          " ",
          button("Remove", () => removeMission(selected), "outline-danger", { disabled: !selected })
        ),
        h("div", { class: "sn-scroll border rounded", dataset: { scroll: "missions" } }, table),
        h("h6", { class: "mt-3" }, "Errors and Warnings"),
        h(
          "div",
          { class: "sn-scroll-sm border rounded", dataset: { scroll: "issues" } },
          issueList(store.analysis?.issues ?? [], {
            onSelect: (issue) => editMission(issue.missionIndex, issue.eventIndex),
          })
        )
      ),
      h(
        "div",
        { class: "col-lg-7" },
        h(
          "ul",
          { class: "nav nav-pills nav-fill mb-1" },
          [
            ["process", "Process Bat Chart"],
            ["element", "Element Bat Chart"],
          ].map(([key, label]) =>
            h(
              "li",
              { class: "nav-item" },
              h(
                "a",
                {
                  class: "nav-link py-1" + (state.chart === key ? " active" : ""),
                  href: "#",
                  onClick: (event) => {
                    event.preventDefault();
                    state.chart = key;
                    render();
                  },
                },
                label
              )
            )
          )
        ),
        chart,
        h("details", { class: "mt-1" }, h("summary", { class: "small" }, "Chart Options"), options)
      )
    )
  );
  drawChart(chart, options);
}

function drawChart(chart, options) {
  const analysis = store.analysis;
  if (!analysis || store.problem) {
    plot(chart, []);
    return;
  }
  const update = () => drawTraces(chart, analysis);
  if (state.chart === "process") {
    const missionList = checklist(
      analysis.missions.map((mission) => [mission.index, mission.name]),
      update,
      { selected: state.missionFilter }
    );
    const typeList = checklist(
      store.enums.eventTypes.map((type) => [type, type]),
      update,
      { selected: state.typeFilter }
    );
    state.missionFilter = missionList.selected;
    state.typeFilter = typeList.selected;
    options.append(
      h(
        "div",
        { class: "row g-2" },
        h("div", { class: "col-6" }, h("div", { class: "small fw-semibold" }, "Missions"), missionList.element),
        h("div", { class: "col-6" }, h("div", { class: "small fw-semibold" }, "Event Types"), typeList.element)
      )
    );
  } else {
    const elementList = checklist(
      analysis.elementHistory.map((history) => [history.element.id, history.element.name]),
      update,
      { selected: state.elementFilter }
    );
    state.elementFilter = elementList.selected;
    options.append(h("div", { class: "small fw-semibold" }, "Elements"), elementList.element);
  }
  update();
}

function drawTraces(chart, analysis) {
  if (state.chart === "process") {
    plot(
      chart,
      batTraces(analysis.missions, { missionFilter: state.missionFilter, typeFilter: state.typeFilter }),
      nodeAxisLayout()
    );
    return;
  }
  // the location of each element over time; transits connect two nodes
  const traces = [];
  for (const history of analysis.elementHistory) {
    if (!state.elementFilter.has(history.element.id)) continue;
    const x = [];
    const y = [];
    for (const segment of history.segments) {
      if (!store.node(segment.location)) continue;
      x.push(dateOf(segment.startTime), dateOf(segment.endTime));
      y.push(store.locationName(segment.location), store.locationName(segment.location));
    }
    if (x.length) {
      traces.push({ x, y, name: history.element.name, mode: "lines+markers", marker: { size: 4 } });
    }
  }
  plot(chart, traces, { ...nodeAxisLayout(), showlegend: traces.length <= 20 });
}

// ---------------------------------------------------------- mission editor

async function addEvent(mission, type) {
  const scenario = store.scenario;
  const missionIndex = scenario.missionList.indexOf(mission);
  const previous = mission.events.includes(state.selectedEvent)
    ? state.selectedEvent
    : mission.events.at(-1);
  let next = { missionTime: 0, priority: 1, location: mission.origin };
  if (previous) {
    next = {
      missionTime: isoToDays(previous.missionTime),
      priority: Math.min(5, previous.priority + 1),
      location: previous.location,
    };
    try {
      // the server suggests the time and location which follow the event
      const evaluation = await api.evaluateEvent(scenario, {
        missionIndex,
        eventIndex: mission.events.indexOf(previous),
        event: previous,
      });
      next = evaluation.next;
    } catch {
      // keep the default suggestion
    }
  }
  if (!store.location(next.location)) next.location = scenario.network.nodes[0].id;
  const draft = {
    name: `${mission.name.slice(0, 5)} | ${type}`,
    type,
    priority: next.priority,
    missionTime: daysToIso(next.missionTime),
    location: next.location,
  };
  const event = await openEventDialog({ mission, event: draft, eventIndex: null });
  if (event) state.selectedEvent = event;
  render();
}

async function editEvent(mission, event) {
  const result = await openEventDialog({
    mission,
    event: clone(event),
    eventIndex: mission.events.indexOf(event),
  });
  if (result) state.selectedEvent = result;
  render();
}

async function removeEvent(mission, event) {
  if (!(await confirmDialog("Remove Event", `Remove ${event.name}?`))) return;
  store.update(() => {
    mission.events = mission.events.filter((other) => other !== event);
    store.pruneInstances();
    state.selectedEvent = null;
  });
}

function drawMission() {
  const scenario = store.scenario;
  const mission = state.mission;
  const missionIndex = scenario.missionList.indexOf(mission);
  const summary = analysisOf(mission);
  const nodes = scenario.network.nodes.map((node) => [node.id, node.name]);
  const optionalNodes = [["", "(none)"], ...nodes];
  const selected = mission.events.includes(state.selectedEvent) ? state.selectedEvent : null;
  const set = (apply) => store.update(() => apply(mission));
  const col = (label, control, size = "col-md-6") =>
    h("div", { class: size }, h("label", { class: "form-label small mb-0" }, label), control);

  const startInput = h("input", {
    class: "form-control form-control-sm",
    type: "datetime-local",
    value: toInputDate(mission.startDate),
    dataset: { key: "mission-start" },
    onChange: () => {
      const date = fromInputDate(startInput.value);
      if (date) {
        store.update((s) => {
          mission.startDate = date;
          sortMissions(s);
        });
      }
    },
  });

  const eventsTable = h(
    "table",
    { class: "table table-sm table-hover sn-table mb-0" },
    h("thead", {}, h("tr", {}, ["Time (d)", "Priority", "Type", "Event", ""].map((t) => h("th", {}, t)))),
    h(
      "tbody",
      {},
      mission.events.map((event, index) => {
        const info = summary?.events?.[index];
        return h(
          "tr",
          {
            class: event === selected ? "table-active" : "",
            title: [...(info?.errors ?? []), ...(info?.warnings ?? [])].join("\n"),
            onClick: () => {
              state.selectedEvent = event;
              render();
            },
            onDblclick: () => editEvent(mission, event),
          },
          h("td", {}, fmt(isoToDays(event.missionTime), 3)),
          h("td", {}, event.priority),
          h("td", {}, event.type),
          h("td", {}, event.name),
          h(
            "td",
            {},
            info?.errors?.length ? badge("error", "danger") : null,
            " ",
            info?.warnings?.length ? badge("warning", "warning") : null
          )
        );
      }),
      mission.events.length
        ? null
        : h("tr", {}, h("td", { colspan: 5, class: "text-secondary" }, "No events. Add an event to begin."))
    )
  );

  const addMenu = h(
    "div",
    { class: "btn-group" },
    h(
      "button",
      { class: "btn btn-sm btn-primary dropdown-toggle", "data-bs-toggle": "dropdown", type: "button" },
      "Add Event"
    ),
    h(
      "ul",
      { class: "dropdown-menu" },
      store.enums.eventTypes.map((type) =>
        h(
          "li",
          {},
          h(
            "a",
            {
              class: "dropdown-item",
              href: "#",
              onClick: (e) => {
                e.preventDefault();
                addEvent(mission, type);
              },
            },
            type
          )
        )
      )
    )
  );

  const modelTypes = ["Timed Impulse", "Rated", "Crew Consumables"];
  const models = h(
    "div",
    {},
    h(
      "ul",
      { class: "list-group list-group-flush mb-1" },
      mission.demandModels.map((model, index) =>
        h(
          "li",
          { class: "list-group-item d-flex align-items-center py-1 px-0" },
          h("span", { class: "me-auto" }, model.name, " ", badge(model.type)),
          button("Edit", async () => {
            const result = await openDemandModel({ model: clone(model), missionIndex });
            if (result) set((m) => (m.demandModels[index] = result));
          }),
          h("span", { class: "me-1" }),
          button("×", () => set((m) => m.demandModels.splice(index, 1)), "outline-danger")
        )
      ),
      mission.demandModels.length ? null : h("li", { class: "list-group-item text-secondary px-0 py-1" }, "None")
    ),
    h(
      "div",
      { class: "btn-group" },
      h(
        "button",
        { class: "btn btn-sm btn-outline-secondary dropdown-toggle", "data-bs-toggle": "dropdown", type: "button" },
        "Add Demand Model"
      ),
      h(
        "ul",
        { class: "dropdown-menu" },
        modelTypes.map((type) =>
          h(
            "li",
            {},
            h(
              "a",
              {
                class: "dropdown-item",
                href: "#",
                onClick: async (e) => {
                  e.preventDefault();
                  const result = await openDemandModel({ model: { type }, missionIndex });
                  if (result) set((m) => m.demandModels.push(result));
                },
              },
              type
            )
          )
        )
      )
    )
  );

  const chart = h("div", { class: "sn-chart" });
  clear(root).append(
    h(
      "div",
      { class: "row g-3" },
      h(
        "div",
        { class: "col-lg-6" },
        h(
          "div",
          { class: "d-flex align-items-center mb-2" },
          button("‹ All Missions", () => {
            state.mission = null;
            render();
          }),
          h("h6", { class: "mb-0 ms-3" }, `Mission ${missionIndex + 1}`),
          summary
            ? h(
                "span",
                { class: "ms-3 small text-secondary" },
                `Duration ${fmt(summary.duration)} days · Crew ${summary.crewSize}`
              )
            : null
        ),
        h(
          "div",
          { class: "row g-2 mb-2" },
          col("Name", textInput(mission.name, (value) => set((m) => (m.name = value)), { dataset: { key: "mission-name" } })),
          col("Start Date (UTC)", startInput),
          col("Departure From", select(nodes, mission.origin, (value) => set((m) => (m.origin = value))), "col-md-3"),
          col("Departure To", select(nodes, mission.destination, (value) => set((m) => (m.destination = value))), "col-md-3"),
          col(
            "Return From",
            select(optionalNodes, mission.returnOrigin, (value) => set((m) => (m.returnOrigin = value || null))),
            "col-md-3"
          ),
          col(
            "Return To",
            select(optionalNodes, mission.returnDestination, (value) => set((m) => (m.returnDestination = value || null))),
            "col-md-3"
          )
        ),
        h("h6", {}, "Mission Demand Models"),
        models,
        h("h6", { class: "mt-3" }, "Events"),
        h(
          "div",
          { class: "mb-2" },
          addMenu,
          " ",
          button("Edit", () => editEvent(mission, selected), "outline-secondary", { disabled: !selected }),
          " ",
          button("Remove", () => removeEvent(mission, selected), "outline-danger", { disabled: !selected })
        ),
        h("div", { class: "sn-scroll border rounded", dataset: { scroll: "events" } }, eventsTable),
        selected && summary?.events?.[mission.events.indexOf(selected)]
          ? h(
              "div",
              { class: "mt-2" },
              [...summary.events[mission.events.indexOf(selected)].errors].map((message) =>
                h("div", { class: "text-danger small" }, message)
              ),
              [...summary.events[mission.events.indexOf(selected)].warnings].map((message) =>
                h("div", { class: "text-warning-emphasis small" }, message)
              )
            )
          : null
      ),
      h("div", { class: "col-lg-6" }, chart)
    )
  );
  plot(
    chart,
    summary && !store.problem ? batTraces([summary]) : [],
    nodeAxisLayout()
  );
}
