// Client of the application programming interface. All analysis and
// simulation is performed by the server: requests carry the scenario.

export class ApiError extends Error {
  constructor(status, detail) {
    super(describe(detail) || `Request failed (${status})`);
    this.status = status;
    // list of {msg, loc?, missionIndex?, eventIndex?}
    this.detail = Array.isArray(detail) ? detail : [];
  }
}

function describe(detail) {
  if (typeof detail === "string") return detail;
  if (!Array.isArray(detail)) return "";
  return detail
    .slice(0, 5)
    .map((item) => {
      const location = (item.loc || []).filter((part) => part !== "body").join(" › ");
      return location ? `${location}: ${item.msg}` : item.msg;
    })
    .join("; ");
}

async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, options);
  if (!response.ok) {
    let detail = null;
    try {
      detail = (await response.json()).detail;
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(response.status, detail);
  }
  return response;
}

async function post(path, body, signal) {
  const response = await request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  return response.json();
}

/**
 * Wraps a request so that a new call cancels the previous call. The
 * returned promise of a cancelled call resolves to `undefined`.
 */
export function latest(send) {
  let controller = null;
  return async (...args) => {
    if (controller) controller.abort();
    controller = new AbortController();
    const { signal } = controller;
    try {
      return await send(signal, ...args);
    } catch (error) {
      if (error.name === "AbortError") return undefined;
      throw error;
    }
  };
}

export const api = {
  schema: async () => (await request("/meta/schema")).json(),
  enums: async () => (await request("/meta/enums")).json(),
  defaults: async () => (await request("/meta/defaults")).json(),

  validate: (scenario) => post("/scenario/validate", { scenario }),

  /** Validates a node, edge, resource, element template, or demand model. */
  validateModel: (kind, model) => post(`/library/${kind}/validate`, { model }),

  async loadDatabase(file) {
    const body = new FormData();
    body.append("upload", file);
    return (await request("/library/database", { method: "POST", body })).json();
  },

  analyzeMissions: (scenario, signal) => post("/missions/analyze", { scenario }, signal),

  eventState: (scenario, params, signal) => post("/events/state", { scenario, ...params }, signal),

  evaluateEvent: (scenario, params, signal) =>
    post("/events/evaluate", { scenario, ...params }, signal),

  analyzeDemands: (scenario, options, signal) =>
    post("/demands/analyze", { scenario, options }, signal),

  simulate: (scenario, signal) => post("/simulate", { scenario }, signal),

  manifest: (operation, scenario, params = {}, signal) =>
    post(`/manifest/${operation}`, { scenario, ...params }, signal),

  async exportText(path, body) {
    const response = await request(`/export/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const disposition = response.headers.get("Content-Disposition") || "";
    const match = /filename="([^"]+)"/.exec(disposition);
    return { name: match ? match[1] : "export.csv", text: await response.text() };
  },
};
