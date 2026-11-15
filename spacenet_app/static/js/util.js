// Utilities shared by all modules: elements, formats, durations, and dates.

/**
 * Creates an element. Attributes starting with "on" are event listeners;
 * `class`, `style`, and `dataset` are assigned; boolean attributes are
 * set as properties. Children may be nodes, strings, or (nested) arrays.
 */
export function h(tag, attrs = {}, ...children) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key.startsWith("on") && typeof value === "function") {
      element.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (key === "class") {
      element.className = value;
    } else if (key === "dataset") {
      Object.assign(element.dataset, value);
    } else if (key === "style" && typeof value === "object") {
      Object.assign(element.style, value);
    } else if (
      ["checked", "disabled", "selected", "hidden", "value", "readOnly", "multiple"].includes(key)
    ) {
      element[key] = value;
    } else {
      element.setAttribute(key, value === true ? "" : value);
    }
  }
  append(element, children);
  return element;
}

function append(element, children) {
  for (const child of children) {
    if (child === null || child === undefined || child === false) continue;
    if (Array.isArray(child)) append(element, child);
    else element.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
}

/** Creates an SVG element. */
export function svg(tag, attrs = {}, ...children) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key.startsWith("on") && typeof value === "function") {
      element.addEventListener(key.slice(2).toLowerCase(), value);
    } else {
      element.setAttribute(key, value);
    }
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    element.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return element;
}

export function clear(element) {
  element.replaceChildren();
  return element;
}

/**
 * Redraws the contents of an element while keeping the keyboard focus (and
 * scroll positions) of controls identified by a `data-key` attribute.
 */
export function redraw(root, draw) {
  const focused = root.contains(document.activeElement) ? document.activeElement : null;
  const key = focused?.dataset?.key;
  let selection = null;
  try {
    selection = focused ? [focused.selectionStart, focused.selectionEnd] : null;
  } catch {
    selection = null;
  }
  const scrolls = {};
  for (const element of root.querySelectorAll("[data-scroll]")) {
    scrolls[element.dataset.scroll] = element.scrollTop;
  }
  draw();
  for (const element of root.querySelectorAll("[data-scroll]")) {
    if (scrolls[element.dataset.scroll]) element.scrollTop = scrolls[element.dataset.scroll];
  }
  if (!key) return;
  const target = root.querySelector(`[data-key="${CSS.escape(key)}"]`);
  if (!target) return;
  target.focus();
  try {
    if (selection && selection[0] !== null) target.setSelectionRange(selection[0], selection[1]);
  } catch {
    // not all input types support selections
  }
}

export function uuid() {
  return crypto.randomUUID();
}

export function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function debounce(callback, delay = 300) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => callback(...args), delay);
  };
}

/** Formats a number with a limited number of decimals. */
export function fmt(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "";
  if (!Number.isFinite(value)) return "∞";
  return Number(value).toLocaleString("en-US", { maximumFractionDigits: digits });
}

// ---------------------------------------------------------------- durations

const DURATION = /^(-)?P(?:(\d+(?:\.\d+)?)W)?(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$/;

/** Converts an ISO-8601 duration (or a number of seconds) to seconds. */
export function isoToSeconds(value) {
  if (value === null || value === undefined || value === "") return 0;
  if (typeof value === "number") return value;
  const match = DURATION.exec(value);
  if (!match) return Number(value) || 0;
  const [, sign, weeks, days, hours, minutes, seconds] = match;
  const total =
    Number(weeks || 0) * 604800 +
    Number(days || 0) * 86400 +
    Number(hours || 0) * 3600 +
    Number(minutes || 0) * 60 +
    Number(seconds || 0);
  return sign ? -total : total;
}

/** Converts seconds to an ISO-8601 duration with days, hours, minutes, and seconds. */
export function secondsToIso(total) {
  let seconds = Math.round(Math.abs(Number(total) || 0) * 1000) / 1000;
  const days = Math.floor(seconds / 86400);
  seconds -= days * 86400;
  const hours = Math.floor(seconds / 3600);
  seconds -= hours * 3600;
  const minutes = Math.floor(seconds / 60);
  seconds = Math.round((seconds - minutes * 60) * 1000) / 1000;
  let text = "P" + (days ? `${days}D` : "");
  if (hours || minutes || seconds || !days) {
    text += "T" + (hours ? `${hours}H` : "") + (minutes ? `${minutes}M` : "");
    if (seconds || (!hours && !minutes)) text += `${seconds}S`;
  }
  return (total < 0 ? "-" : "") + text;
}

export const isoToDays = (value) => isoToSeconds(value) / 86400;
export const daysToIso = (days) => secondsToIso(Number(days || 0) * 86400);
export const isoToHours = (value) => isoToSeconds(value) / 3600;
export const hoursToIso = (hours) => secondsToIso(Number(hours || 0) * 3600);

// -------------------------------------------------------------------- dates

/** Converts an ISO date to the value of a datetime-local input (in UTC). */
export function toInputDate(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toISOString().slice(0, 16);
}

/** Converts the value of a datetime-local input (in UTC) to an ISO date. */
export function fromInputDate(value) {
  if (!value) return null;
  const date = new Date(value.length === 16 ? `${value}:00Z` : `${value}Z`);
  return Number.isNaN(date.getTime()) ? null : date.toISOString().replace(".000Z", "Z");
}

/** Gets the date a number of days after an ISO date. */
export function addDays(iso, days) {
  return new Date(new Date(iso).getTime() + days * 86400000);
}

export function formatDate(date) {
  const value = date instanceof Date ? date : new Date(date);
  if (Number.isNaN(value.getTime())) return "";
  return value.toISOString().slice(0, 16).replace("T", " ");
}

// ------------------------------------------------------------------ widgets

/** Shows a transient message. */
export function toast(message, kind = "secondary") {
  const element = h(
    "div",
    { class: `toast align-items-center text-bg-${kind} border-0`, role: "alert" },
    h(
      "div",
      { class: "d-flex" },
      h("div", { class: "toast-body" }, message),
      h("button", {
        type: "button",
        class: "btn-close btn-close-white me-2 m-auto",
        "data-bs-dismiss": "toast",
      })
    )
  );
  document.getElementById("toasts").append(element);
  element.addEventListener("hidden.bs.toast", () => element.remove());
  new bootstrap.Toast(element, { delay: kind === "danger" ? 8000 : 3500 }).show();
}

/** Saves text as a file. */
export function download(name, text, type = "application/json") {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = h("a", { href: url, download: name });
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Creates a labeled capacity bar (red when over capacity). */
export function capacityBar(label, value, maximum, units = "kg") {
  const over = maximum !== null && value - maximum > 1e-9;
  const percent = maximum > 0 ? Math.min(100, (100 * value) / maximum) : value > 0 ? 100 : 0;
  return h(
    "div",
    { class: "sn-bar mb-1" },
    h("div", { class: "small text-secondary" }, label),
    h(
      "div",
      { class: "progress", role: "progressbar" },
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
}

/** Creates a small colored badge. */
export function badge(text, kind = "secondary") {
  return h("span", { class: `badge text-bg-${kind} sn-badge-type` }, text);
}

/** Creates a labeled form field in a column. */
export function field(label, control, { col = "col-md-6", help = null } = {}) {
  return h(
    "div",
    { class: col },
    h("label", { class: "form-label small mb-0" }, label),
    control,
    help && h("div", { class: "form-text mt-0" }, help)
  );
}

/** Creates a select from options given as values or [value, label] pairs. */
export function select(options, value, onChange, attrs = {}) {
  const element = h(
    "select",
    { class: "form-select form-select-sm", ...attrs, onChange: () => onChange(element.value) },
    options.map((option) => {
      const [optionValue, label] = Array.isArray(option) ? option : [option, option];
      return h(
        "option",
        { value: optionValue ?? "", selected: String(optionValue ?? "") === String(value ?? "") },
        label
      );
    })
  );
  return element;
}

/** Creates a number input which reports null when empty. */
export function numberInput(value, onChange, attrs = {}) {
  const element = h("input", {
    class: "form-control form-control-sm",
    type: "number",
    step: "any",
    value: value ?? "",
    ...attrs,
    onInput: () => onChange(element.value === "" ? null : Number(element.value)),
  });
  return element;
}

export function textInput(value, onChange, attrs = {}) {
  const element = h("input", {
    class: "form-control form-control-sm",
    value: value ?? "",
    ...attrs,
    onInput: () => onChange(element.value),
  });
  return element;
}

export function checkbox(label, checked, onChange, attrs = {}) {
  const id = `c-${uuid()}`;
  const input = h("input", {
    class: "form-check-input",
    type: "checkbox",
    id,
    checked: Boolean(checked),
    ...attrs,
    onChange: () => onChange(input.checked),
  });
  return h(
    "div",
    { class: "form-check" },
    input,
    h("label", { class: "form-check-label", for: id }, label)
  );
}

export function button(label, onClick, kind = "outline-secondary", attrs = {}) {
  return h(
    "button",
    { type: "button", class: `btn btn-sm btn-${kind}`, ...attrs, onClick },
    label
  );
}

/**
 * Shows a modal dialog and resolves when it is closed with the value passed
 * to `close` (undefined if dismissed).
 */
export function openModal({ title, body, footer = null, size = "lg", scrollable = true }) {
  let result;
  let resolve;
  const promise = new Promise((done) => (resolve = done));
  const titleElement = h("h5", { class: "modal-title" }, title);
  const footerElement = h("div", { class: "modal-footer" });
  const element = h(
    "div",
    { class: "modal", tabindex: "-1", "data-bs-backdrop": "static" },
    h(
      "div",
      {
        class: `modal-dialog modal-${size} ${scrollable ? "modal-dialog-scrollable" : ""}`,
      },
      h(
        "div",
        { class: "modal-content" },
        h(
          "div",
          { class: "modal-header py-2" },
          titleElement,
          h("button", { type: "button", class: "btn-close", "data-bs-dismiss": "modal" })
        ),
        h("div", { class: "modal-body" }, body),
        footerElement
      )
    )
  );
  document.getElementById("modal-root").append(element);
  // dialogs can open other dialogs: a focus trap would fight over the focus
  const modal = new bootstrap.Modal(element, { focus: false });
  const control = {
    element,
    footer: footerElement,
    setTitle: (text) => (titleElement.textContent = text),
    close: (value) => {
      result = value;
      modal.hide();
    },
    closed: promise,
  };
  if (typeof footer === "function") append(footerElement, [footer(control)].flat());
  else if (footer) append(footerElement, [footer].flat());
  element.addEventListener("hidden.bs.modal", () => {
    modal.dispose();
    element.remove();
    resolve(result);
  });
  modal.show();
  return control;
}

/** Asks for confirmation. */
export function confirmDialog(title, message) {
  const control = openModal({
    title,
    size: "md",
    body: h("div", {}, [message].flat()),
    footer: (c) => [
      button("Cancel", () => c.close(false)),
      button("OK", () => c.close(true), "primary"),
    ],
  });
  return control.closed.then((value) => value === true);
}

/** Shows a message. */
export function alertDialog(title, message) {
  return openModal({
    title,
    size: "md",
    body: h("div", {}, [message].flat()),
    footer: (c) => button("OK", () => c.close(), "primary"),
  }).closed;
}
