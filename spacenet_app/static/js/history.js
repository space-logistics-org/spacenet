// Decodes the simulation history sent by the server: static information
// about each element and, at each time step, the elements which changed.
// Frames are rebuilt on demand as element states (the shape of the
// element states of the other endpoints), so that the element tree,
// details, and capacity bars display them unchanged.

/** Composes the state of an element from its information and change. */
function compose(info, change, contents) {
  const index = change.stateIndex ?? -1;
  const state = {
    id: info.id,
    name: info.name,
    type: info.type,
    templateId: info.templateId,
    icon: info.icon,
    classOfSupply: info.classOfSupply,
    environment: info.environment,
    cargoEnvironment: info.cargoEnvironment,
    isCarrier: info.isCarrier,
    isCrew: info.isCrew,
    isContainer: info.isContainer,
    states: info.states,
    stateTypes: info.stateTypes,
    stateIndex: index,
    state: index >= 0 ? info.states[index] : null,
    stateType: index >= 0 ? info.stateTypes[index] : null,
    mass: change.mass,
    totalMass: change.totalMass,
    volume: change.volume,
    cargoMass: change.cargoMass,
    maxCargoMass: info.maxCargoMass,
    cargoVolume: change.cargoVolume,
    maxCargoVolume: info.maxCargoVolume,
    crewSize: info.isCarrier ? change.crewSize : 0,
    maxCrewSize: info.isCarrier ? info.maxCrewSize : 0,
    resources: { ...change.resources },
    massByClassOfSupply: change.massByClassOfSupply,
    energy: change.energy ?? 0,
    energyCapacity: info.energyCapacity ?? 0,
    contents: info.isCarrier ? contents : [],
    fuelTanks: [],
    fuelName: null,
    fuelAmount: 0,
    maxFuelAmount: 0,
    isp: info.isCarrier ? info.isp : 0,
  };
  if (info.isCarrier) {
    info.fuelTanks.forEach((tank, i) => {
      const fuelName = change.fuelNames[i] ?? null;
      const amount = change.fuelAmounts[i] ?? 0;
      state.fuelTanks.push({ ...tank, fuelName, amount });
      if (fuelName !== null) state.resources[fuelName] = (state.resources[fuelName] ?? 0) + amount;
    });
    const primary = state.fuelTanks[0];
    if (primary) {
      state.fuelName = primary.fuelName;
      state.fuelAmount = primary.amount;
      state.maxFuelAmount = primary.maxAmount;
    }
  }
  return state;
}

/** Adds the masses at one time step, padding classes of supply first seen later. */
function addPoint(series, index, masses) {
  for (const key of new Set([...Object.keys(series), ...Object.keys(masses)])) {
    const values = (series[key] ||= new Array(index).fill(0));
    values.push(masses[key] ?? 0);
  }
}

function toSeries(times, series) {
  return Object.entries(series)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([classOfSupply, values]) => ({
      classOfSupply: Number(classOfSupply),
      points: values.map((mass, i) => [times[i], mass]),
    }));
}

/**
 * Creates a view of the history of a simulation result.
 *
 * @param {object} result the simulation analysis
 */
export function createHistory(result) {
  const { elements, frames } = result.history;
  const locations = result.locations;
  const times = frames.map((frame) => frame.time);
  // replays the changes up to a time step (moving forward from the last one)
  let cursor = -1;
  let current = new Map();
  function advance(index) {
    if (index < cursor) {
      cursor = -1;
      current = new Map();
    }
    while (cursor < index) {
      cursor += 1;
      const frame = frames[cursor];
      for (const element of frame.removed) current.delete(element);
      for (const change of frame.changes) current.set(change.element, change);
    }
    return current;
  }
  let massCache = null;

  return {
    length: frames.length,
    times,

    /** The elements at each location (by location id) at a time step. */
    frame(index) {
      const state = advance(index);
      const children = new Map();
      // element indices follow the order of elements within containers
      for (const element of [...state.keys()].sort((a, b) => a - b)) {
        const change = state.get(element);
        const parent = change.location !== null && change.location !== undefined
          ? `l${change.location}`
          : `e${change.container}`;
        if (!children.has(parent)) children.set(parent, []);
        children.get(parent).push(element);
      }
      const create = (element) =>
        compose(elements[element], state.get(element), (children.get(`e${element}`) ?? []).map(create));
      return {
        time: frames[index].time,
        locations: Object.fromEntries(
          locations.map((location, i) => [location.id, (children.get(`l${i}`) ?? []).map(create)])
        ),
      };
    },

    /**
     * The intervals in which each element existed at each location (of the
     * element or of its top-level carrier), in order of first appearance.
     */
    segments() {
      const open = new Map(); // element -> { location, start }
      const result = new Map(); // element -> segments
      const close = (element, end) => {
        const segment = open.get(element);
        if (!segment) return;
        if (!result.has(element)) result.set(element, []);
        result.get(element).push({ ...segment, end });
        open.delete(element);
      };
      frames.forEach((frame, index) => {
        const state = advance(index);
        const locationOf = (element) => {
          let change = state.get(element);
          for (let depth = 0; change && depth < 100; depth++) {
            if (change.location !== null && change.location !== undefined) return change.location;
            change = state.get(change.container);
          }
          return null;
        };
        for (const element of [...open.keys()]) {
          if (!state.has(element)) close(element, frame.time);
        }
        for (const element of state.keys()) {
          const location = locationOf(element);
          const segment = open.get(element);
          if (segment && segment.location === location) continue;
          close(element, frame.time);
          open.set(element, { location, start: frame.time });
          if (!result.has(element)) result.set(element, []);
        }
      });
      for (const element of [...open.keys()]) close(element, times.at(-1) ?? 0);
      return [...result.entries()].map(([element, segments]) => ({
        id: elements[element].id,
        name: elements[element].name,
        type: elements[element].type,
        isCrew: elements[element].isCrew,
        segments,
      }));
    },

    /**
     * Mass by class of supply over time of each location (top-level
     * elements) and of each element (including nested contents).
     */
    masses() {
      if (massCache) return massCache;
      const locationSeries = locations.map(() => ({}));
      const elementSeries = new Map();
      frames.forEach((_, index) => {
        const state = advance(index);
        const totals = locations.map(() => ({}));
        for (const [element, change] of state) {
          if (change.location !== null && change.location !== undefined) {
            const total = totals[change.location];
            for (const [key, mass] of Object.entries(change.massByClassOfSupply)) {
              total[key] = (total[key] ?? 0) + mass;
            }
          }
          if (!elementSeries.has(element)) elementSeries.set(element, {});
          const series = elementSeries.get(element);
          // pad the time steps before the element existed
          for (const values of Object.values(series)) {
            while (values.length < index) values.push(0);
          }
          addPoint(series, index, change.massByClassOfSupply);
        }
        locationSeries.forEach((series, i) => addPoint(series, index, totals[i]));
      });
      // pad the time steps after an element was removed
      for (const series of elementSeries.values()) {
        for (const values of Object.values(series)) {
          while (values.length < frames.length) values.push(0);
        }
      }
      massCache = {
        locations: locations.map((location, i) => ({
          id: location.id,
          name: location.name,
          type: null,
          series: toSeries(times, locationSeries[i]),
        })),
        elements: [...elementSeries.entries()]
          .map(([element, series]) => ({
            id: elements[element].id,
            name: elements[element].name,
            type: elements[element].type,
            series: toSeries(times, series),
          }))
          // by name (in code point order, as previously sorted by the server)
          .sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0)),
      };
      return massCache;
    },
  };
}
