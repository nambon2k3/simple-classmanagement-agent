/** DOM helpers, toasts, and modals. */

export function el(tag, props, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key === "disabled") node.disabled = !!value;
    else if (key === "checked") node.checked = !!value;
    else if (key === "value") node.value = value;
    else if (key.startsWith("on") && typeof value === "function")
      node.addEventListener(key.slice(2).toLowerCase(), value);
    else node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

export const $ = (id) => document.getElementById(id);

export function toast(message, kind = "success") {
  const node = el("div", { class: `toast ${kind}` }, message);
  $("toast-root").append(node);
  setTimeout(() => node.remove(), 4200);
}

export function modal(title) {
  const overlay = el("div", { class: "modal-overlay" });
  const body = el("div", { class: "modal-body" });
  const box = el("div", { class: "modal" }, el("header", {}, title), body);
  overlay.append(box);
  const close = () => overlay.remove();
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  document.addEventListener("keydown", function onEsc(e) {
    if (e.key === "Escape") {
      close();
      document.removeEventListener("keydown", onEsc);
    }
  });
  $("modal-root").append(overlay);
  return { body, close };
}

export function actions(...buttons) {
  return el("div", { class: "modal-actions" }, ...buttons);
}

export function field(labelText, input) {
  return el("label", { class: "field" }, el("span", {}, labelText), input);
}

export function loading() {
  return el("div", { class: "loading" }, el("span", { class: "spinner" }), " Loading\u2026");
}

export function setHeader(glyph, title, subtitle, extra) {
  const header = $("main-header");
  header.replaceChildren(
    el("span", { class: "glyph" }, glyph),
    el("span", { class: "title" }, title),
    subtitle ? el("span", { class: "subtitle" }, subtitle) : null,
    el("span", { class: "spacer" }),
    extra || null,
  );
}

export function setMain(...nodes) {
  $("main-body").replaceChildren(...nodes);
}

export function setContext(label, ...nodes) {
  $("app").classList.remove("no-context");
  const ctx = $("context");
  ctx.replaceChildren(
    el("div", { class: "ctx-header" }, label),
    el("div", { class: "ctx-scroll" }, ...nodes),
  );
}

export function hideContext() {
  $("app").classList.add("no-context");
  $("context").replaceChildren();
}

export function kpi(label, value, hint) {
  return el(
    "div",
    { class: "kpi" },
    el("div", { class: "label" }, label),
    el("div", { class: "value" }, value),
    hint ? el("div", { class: "hint" }, hint) : null,
  );
}

export function table(columns, rows, emptyText) {
  if (!rows.length) return el("div", { class: "empty" }, emptyText || "Nothing to show.");
  const head = el("thead", {}, el("tr", {}, ...columns.map((c) => el("th", {}, c.label))));
  const body = el(
    "tbody",
    {},
    ...rows.map((row) => el("tr", {}, ...columns.map((c) => el("td", {}, c.render(row))))),
  );
  return el("table", {}, head, body);
}
