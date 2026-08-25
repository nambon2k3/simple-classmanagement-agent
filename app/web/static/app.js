"use strict";

/* Class-management dashboard: a dependency-free single-page app that renders a
 * Discord-style workspace and talks to the FastAPI JSON API under /api. */

// --------------------------------------------------------------- DOM helpers

function el(tag, props, ...children) {
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

const $ = (id) => document.getElementById(id);

// --------------------------------------------------------------- API client

async function apiFetch(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = text;
  }
  if (!res.ok) {
    const err = new Error(errorMessage(data, res.status));
    err.data = data;
    throw err;
  }
  return data;
}

function errorMessage(data, status) {
  if (data && data.message) return data.message;
  if (data && typeof data.detail === "string") return data.detail;
  if (data && Array.isArray(data.detail))
    return data.detail.map((d) => d.msg || String(d)).join("; ");
  if (typeof data === "string" && data) return data;
  return `Request failed (${status})`;
}

async function apiUpload(path, file) {
  const res = await fetch(path, { method: "POST", body: file });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = text;
  }
  if (!res.ok) throw new Error(errorMessage(data, res.status));
  return data;
}

const api = {
  get: (p) => apiFetch("GET", p),
  post: (p, b) => apiFetch("POST", p, b === undefined ? {} : b),
};

// --------------------------------------------------------------- formatting

const STATUSES = [
  { v: "present", e: "\u2705", l: "Present" },
  { v: "absent", e: "\u274C", l: "Absent" },
  { v: "late", e: "\uD83D\uDFE1", l: "Late" },
  { v: "excused", e: "\uD83D\uDCDD", l: "Excused" },
];
const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const PERIODS = [
  ["today", "Today"],
  ["yesterday", "Yesterday"],
  ["this_week", "This week"],
  ["last_week", "Last week"],
  ["this_month", "This month"],
  ["last_month", "Last month"],
  ["all_time", "All time"],
];

function initials(name) {
  const compact = (name || "").replace(/\s+/g, "");
  return compact ? compact.slice(0, 2).toUpperCase() : "?";
}

function fmtDate(iso) {
  if (!iso) return "\u2014";
  const value = iso.length === 10 ? iso + "T00:00:00" : iso;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

function relTime(iso) {
  const then = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  const seconds = Math.floor((Date.now() - then.getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) {
    const m = Math.floor(seconds / 60);
    return `${m} minute${m > 1 ? "s" : ""} ago`;
  }
  if (seconds < 86400) {
    const h = Math.floor(seconds / 3600);
    return `${h} hour${h > 1 ? "s" : ""} ago`;
  }
  const days = Math.floor(seconds / 86400);
  if (days < 30) return `${days} day${days > 1 ? "s" : ""} ago`;
  return fmtDate(iso.slice(0, 10));
}

function attendanceRate(summary) {
  if (!summary.total) return 0;
  return Math.round(((summary.present + summary.late) / summary.total) * 100);
}

// --------------------------------------------------------------- feedback UI

function toast(message, kind = "success") {
  const node = el("div", { class: `toast ${kind}` }, message);
  $("toast-root").append(node);
  setTimeout(() => node.remove(), 4200);
}

function modal(title) {
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

function actions(...buttons) {
  return el("div", { class: "modal-actions" }, ...buttons);
}

function field(labelText, input) {
  return el("label", { class: "field" }, el("span", {}, labelText), input);
}

function loading() {
  return el("div", { class: "loading" }, el("span", { class: "spinner" }), " Loading\u2026");
}

// --------------------------------------------------------------- app state

const state = {
  me: null,
  classes: [],
  view: { server: "home", channel: "dashboard", classId: null, className: null },
  cal: { year: new Date().getFullYear(), month: new Date().getMonth() + 1 },
  chat: [],
};

const CLASS_CHANNELS = [
  { id: "students", label: "students" },
  { id: "attendance", label: "attendance" },
  { id: "reports", label: "reports" },
  { id: "class-info", label: "class-info" },
];

async function refreshClasses() {
  state.classes = await api.get("/api/classes");
}

function currentClass() {
  return state.classes.find((c) => c.id === state.view.classId) || null;
}

// --------------------------------------------------------------- navigation

function goHome() {
  state.view = { server: "home", channel: "dashboard", classId: null, className: null };
  render();
}

function goAi() {
  state.view = { server: "ai", channel: "chat", classId: null, className: null };
  render();
}

function selectClass(cls) {
  state.view = { server: "class", channel: "students", classId: cls.id, className: cls.name };
  render();
}

function setChannel(channel) {
  state.view.channel = channel;
  render();
}

// --------------------------------------------------------------- rail

function railButton({ label, title, active, onClick, brand, cls }) {
  const btn = el("button", {
    class: `rail-btn ${brand ? "brand" : ""} ${active ? "active" : ""}`,
    title: title || label,
    onclick: onClick,
  });
  if (cls && cls.has_icon) {
    const img = el("img", { src: `/api/classes/${cls.id}/icon`, alt: cls.name });
    img.addEventListener("error", () => {
      img.remove();
      btn.textContent = initials(cls.name);
    });
    btn.append(img);
  } else {
    btn.textContent = label;
  }
  return btn;
}

function renderRail() {
  const rail = $("rail");
  rail.replaceChildren();
  rail.append(railButton({ label: "CM", brand: true, title: "Class Management" }));
  rail.append(el("div", { class: "rail-sep" }));
  rail.append(
    railButton({
      label: "\uD83C\uDFE0",
      title: "Home",
      active: state.view.server === "home",
      onClick: goHome,
    }),
  );
  for (const cls of state.classes) {
    rail.append(
      railButton({
        label: initials(cls.name),
        title: cls.name,
        active: state.view.server === "class" && state.view.classId === cls.id,
        onClick: () => selectClass(cls),
        cls,
      }),
    );
  }
  rail.append(el("div", { class: "rail-sep" }));
  rail.append(
    railButton({
      label: "AI",
      title: "AI chat",
      active: state.view.server === "ai",
      onClick: goAi,
    }),
  );
}

// --------------------------------------------------------------- channels

function channelItem(id, label, glyph) {
  return el(
    "button",
    {
      class: `channel-item ${state.view.channel === id ? "active" : ""}`,
      onclick: () => setChannel(id),
    },
    el("span", { class: "glyph" }, glyph || "#"),
    label,
  );
}

function renderChannels() {
  const panel = $("channels");
  panel.replaceChildren();
  const scroll = el("div", { class: "channels-scroll" });

  let headerText = "Home";
  if (state.view.server === "class") headerText = state.view.className;
  else if (state.view.server === "ai") headerText = "Assistant";

  if (state.view.server === "home") {
    scroll.append(el("div", { class: "channel-section" }, "Overview"));
    scroll.append(channelItem("dashboard", "dashboard", "#"));
    scroll.append(el("div", { class: "channel-section" }, "Classes"));
    if (state.classes.length === 0) {
      scroll.append(el("div", { class: "empty" }, "No classes yet."));
    }
    for (const cls of state.classes) {
      scroll.append(
        el(
          "button",
          { class: "channel-item", onclick: () => selectClass(cls) },
          el("span", { class: "glyph" }, initials(cls.name)),
          cls.name,
        ),
      );
    }
  } else if (state.view.server === "class") {
    scroll.append(el("div", { class: "channel-section" }, "Channels"));
    for (const ch of CLASS_CHANNELS) scroll.append(channelItem(ch.id, ch.label));
  } else if (state.view.server === "ai") {
    scroll.append(el("div", { class: "channel-section" }, "Assistant"));
    scroll.append(channelItem("chat", "chat"));
  }

  const footer = el(
    "div",
    { class: "channels-footer" },
    el("div", { class: "avatar" }, initials(state.me ? state.me.display_name : "?")),
    el(
      "div",
      { class: "who" },
      el("b", {}, state.me ? state.me.display_name : "\u2014"),
      el("span", {}, "Administrator"),
    ),
  );

  panel.append(el("div", { class: "channels-header" }, headerText));
  panel.append(scroll);
  panel.append(footer);
}

// --------------------------------------------------------------- main scaffold

function setHeader(glyph, title, subtitle, extra) {
  const header = $("main-header");
  header.replaceChildren(
    el("span", { class: "glyph" }, glyph),
    el("span", { class: "title" }, title),
    subtitle ? el("span", { class: "subtitle" }, subtitle) : null,
    el("span", { class: "spacer" }),
    extra || null,
  );
}

function setMain(...nodes) {
  $("main-body").replaceChildren(...nodes);
}

function setContext(label, ...nodes) {
  $("app").classList.remove("no-context");
  const ctx = $("context");
  ctx.replaceChildren(
    el("div", { class: "ctx-header" }, label),
    el("div", { class: "ctx-scroll" }, ...nodes),
  );
}

function hideContext() {
  $("app").classList.add("no-context");
  $("context").replaceChildren();
}

function kpi(label, value, hint) {
  return el(
    "div",
    { class: "kpi" },
    el("div", { class: "label" }, label),
    el("div", { class: "value" }, value),
    hint ? el("div", { class: "hint" }, hint) : null,
  );
}

function table(columns, rows, emptyText) {
  if (!rows.length) return el("div", { class: "empty" }, emptyText || "Nothing to show.");
  const head = el("thead", {}, el("tr", {}, ...columns.map((c) => el("th", {}, c.label))));
  const body = el(
    "tbody",
    {},
    ...rows.map((row) => el("tr", {}, ...columns.map((c) => el("td", {}, c.render(row))))),
  );
  return el("table", {}, head, body);
}

// --------------------------------------------------------------- router

const PAGES = {
  dashboard: renderDashboard,
  students: renderStudents,
  attendance: renderAttendance,
  reports: renderReports,
  "class-info": renderClassInfo,
  chat: renderChat,
};

function render() {
  renderRail();
  renderChannels();
  const page = PAGES[state.view.channel] || renderDashboard;
  setMain(loading());
  Promise.resolve()
    .then(() => page())
    .catch((err) => {
      setMain(el("div", { class: "empty" }, err.message || "Something went wrong."));
      toast(err.message || "Something went wrong.", "error");
    });
}

// --------------------------------------------------------------- dashboard

async function renderDashboard() {
  setHeader("#", "dashboard", "Overview of your classes");
  const [summary, activity] = await Promise.all([
    api.get("/api/dashboard/summary"),
    api.get("/api/activity"),
  ]);

  const createBtn = el(
    "button",
    { class: "btn primary", onclick: openCreateClass },
    "Create a class",
  );

  const kpis = el(
    "div",
    { class: "grid cols-2" },
    kpi("Tuition not yet", summary.formatted_not_yet, "Unpaid present days"),
    kpi("Tuition completed", summary.formatted_completed, "Marked paid"),
  );

  const calCard = el("div", { class: "card" });
  const activityCard = el(
    "div",
    { class: "card" },
    el("h3", {}, "Recent activity"),
    renderActivity(activity),
  );

  setMain(
    el(
      "div",
      { class: "hero" },
      el("h1", {}, "Home"),
      el("p", {}, "Pick a class in the left rail to open its students, attendance and settings."),
    ),
    kpis,
    el("div", { style: "height:16px" }),
    el("div", { class: "grid cols-2", style: "grid-template-columns: 2fr 1fr" }, calCard, activityCard),
    el("div", { style: "height:16px" }),
    createBtn,
  );

  await renderCalendar(calCard);

  // Context: class directory with student counts.
  setContext(
    "Classes",
    state.classes.length
      ? el(
          "div",
          {},
          ...state.classes.map((cls) =>
            el(
              "div",
              { class: "ctx-member", onclick: () => selectClass(cls), style: "cursor:pointer" },
              el("div", { class: "avatar", style: "border-radius:16px" }, initials(cls.name)),
              el(
                "div",
                {},
                el("div", { class: "name" }, cls.name),
                el("div", { class: "code" }, `${cls.student_count} students`),
              ),
            ),
          ),
        )
      : el("div", { class: "empty" }, "No classes yet."),
  );
}

function renderActivity(entries) {
  if (!entries.length) return el("div", { class: "empty" }, "No activity yet.");
  return el(
    "div",
    {},
    ...entries.map((e) =>
      el(
        "div",
        { class: "activity" },
        el("div", { class: "mark" }, e.badge),
        el(
          "div",
          {},
          el("div", { class: "text" }, e.text),
          el("div", { class: "when" }, relTime(e.occurred_at)),
        ),
      ),
    ),
  );
}

async function renderCalendar(card) {
  const { year, month } = state.cal;
  card.replaceChildren(
    el(
      "div",
      { class: "cal-head" },
      el("button", {
        class: "btn ghost small",
        html: "&larr;",
        onclick: () => {
          shiftMonth(-1);
        },
      }),
      el("div", { class: "month" }, `${MONTHS[month - 1]} ${year}`),
      el("button", {
        class: "btn ghost small",
        html: "&rarr;",
        onclick: () => {
          shiftMonth(1);
        },
      }),
    ),
    loading(),
  );
  const occurrences = await api.get(`/api/schedule/month?year=${year}&month=${month}`);
  const byDay = {};
  for (const item of occurrences) {
    const d = new Date(item.session_date + "T00:00:00");
    if (d.getFullYear() === year && d.getMonth() + 1 === month)
      (byDay[d.getDate()] = byDay[d.getDate()] || []).push(item);
  }
  const firstWeekday = (new Date(year, month - 1, 1).getDay() + 6) % 7; // Monday=0
  const lastDay = new Date(year, month, 0).getDate();
  const today = new Date();
  const grid = el("div", { class: "cal-grid" });
  for (const dow of ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    grid.append(el("div", { class: "cal-dow" }, dow));
  for (let i = 0; i < firstWeekday; i++) grid.append(el("div", { class: "cal-cell empty" }));
  for (let day = 1; day <= lastDay; day++) {
    const isToday =
      today.getFullYear() === year && today.getMonth() + 1 === month && today.getDate() === day;
    const cell = el("div", { class: `cal-cell ${isToday ? "today" : ""}` });
    cell.append(el("div", { class: "cal-day" }, day));
    for (const item of byDay[day] || []) {
      const start = item.start_time.slice(0, 5);
      const end = item.end_time.slice(0, 5);
      cell.append(
        el("div", { class: `cal-event ${item.kind === "extra" ? "extra" : ""}` }, `${item.class_name} ${start}-${end}`),
      );
    }
    grid.append(cell);
  }
  card.replaceChildren(card.firstChild, grid);
}

function shiftMonth(delta) {
  let { year, month } = state.cal;
  month += delta;
  if (month < 1) {
    month = 12;
    year -= 1;
  } else if (month > 12) {
    month = 1;
    year += 1;
  }
  state.cal = { year, month };
  const card = $("main-body").querySelector(".card");
  if (card) renderCalendar(card);
}

// --------------------------------------------------------------- students

async function renderStudents() {
  const className = state.view.className;
  setHeader("#", "students", className);
  const students = await api.get(`/api/students?class_name=${encodeURIComponent(className)}`);

  const toolbar = el(
    "div",
    { class: "row", style: "margin-bottom:16px" },
    el("button", { class: "btn primary", onclick: () => openAddStudent(className) }, "Add student"),
    el("button", { class: "btn ghost", onclick: () => openEditStudent(className) }, "Update / remove"),
  );

  const searchInput = el("input", { placeholder: "Name or student ID", type: "text" });
  const searchResult = el("div", {});
  const searchBox = el(
    "div",
    { class: "card", style: "margin-top:16px" },
    el("h3", {}, "Search"),
    el(
      "div",
      { class: "row" },
      el("div", { style: "flex:1" }, searchInput),
      el(
        "button",
        {
          class: "btn",
          onclick: async () => {
            const query = searchInput.value.trim();
            if (!query) return;
            try {
              const rows = await api.post("/api/students/search", { query, class_name: null });
              searchResult.replaceChildren(studentTable(rows, "No students matched that search."));
            } catch (err) {
              toast(err.message, "error");
            }
          },
        },
        "Search",
      ),
    ),
    searchResult,
  );

  setMain(
    el(
      "div",
      { class: "hero" },
      el("h1", {}, "Students"),
      el("p", {}, `Roster for ${className}. Student IDs are unique within the class.`),
    ),
    toolbar,
    el("div", { class: "card" }, el("h3", {}, "Roster"), studentTable(students, `${className} has no students yet.`)),
    searchBox,
  );

  // Context: member list, Discord-style.
  setContext(
    `Members \u2014 ${students.length}`,
    students.length
      ? el(
          "div",
          {},
          ...students.map((s) =>
            el(
              "div",
              { class: "ctx-member" },
              el("div", { class: "avatar" }, initials(s.full_name)),
              el(
                "div",
                {},
                el("div", { class: "name" }, s.full_name),
                el("div", { class: "code" }, s.student_code),
              ),
            ),
          ),
        )
      : el("div", { class: "empty" }, "No members yet."),
  );
}

function studentTable(students, emptyText) {
  return table(
    [
      { label: "Code", render: (s) => el("span", { class: "mono" }, s.student_code) },
      { label: "Name", render: (s) => s.full_name },
      { label: "Email", render: (s) => s.email || "\u2014" },
      { label: "Phone", render: (s) => s.phone || "\u2014" },
    ],
    students,
    emptyText,
  );
}

// --------------------------------------------------------------- attendance

async function renderAttendance() {
  const { className, classId } = state.view;
  setHeader("#", "attendance", className);
  const data = await api.get(`/api/attendance/today?class_name=${encodeURIComponent(className)}`);
  const session = data.session;
  const students = data.students;
  const taking = session && session.status === "open";

  const body = el("div", {});
  body.append(
    el(
      "div",
      { class: "hero" },
      el("h1", {}, "Attendance"),
      el("p", {}, "Today's list. Online means present, offline means absent."),
    ),
  );

  if (!taking) {
    // A completed session can be updated at any time, so opening it always
    // reopens it rather than asking the teacher to opt in first.
    const controls = el("div", { class: "row", style: "margin-bottom:14px" });
    controls.append(
      el(
        "button",
        {
          class: "btn primary",
          onclick: async () => {
            try {
              const res = await api.post("/api/attendance/start", {
                class_name: className,
                reopen: !!session,
              });
              toast(res.message);
              render();
            } catch (err) {
              toast(err.message, "error");
            }
          },
        },
        session ? "Update attendance" : "Take attendance",
      ),
    );
    body.append(controls);
  }

  body.append(el("div", { class: "att-tally", style: "margin-bottom:6px" }, `Today \u00B7 ${fmtDate(new Date().toISOString().slice(0, 10))}`));
  const rosterCard = el("div", { class: "card" });
  const statusById = {};
  if (session) for (const e of session.entries) statusById[e.student_id] = e.status;

  if (!students.length) {
    rosterCard.append(el("div", { class: "empty" }, "This class has no students yet."));
  } else {
    for (const student of students) {
      const status = statusById[student.id];
      const online = status === "present" || status === "late";
      const row = el(
        "div",
        { class: "presence" },
        el("span", { class: `signal ${online ? "online" : "offline"}` }),
        el(
          "div",
          {},
          el("div", { class: "name" }, student.full_name),
          el("span", { class: "mono" }, student.student_code),
        ),
        el("span", { class: "spacer" }),
      );
      if (taking) {
        const checkbox = el("input", { type: "checkbox", checked: online });
        const sw = el("label", { class: "switch" }, checkbox, el("span", { class: "slider" }));
        checkbox.addEventListener("change", async () => {
          try {
            await api.post("/api/attendance/mark", {
              session_id: session.session_id,
              student_id: student.id,
              status: checkbox.checked ? "present" : "absent",
            });
            render();
          } catch (err) {
            toast(err.message, "error");
            render();
          }
        });
        row.append(sw);
      }
      rosterCard.append(row);
    }
    if (taking) {
      rosterCard.append(
        el(
          "div",
          { style: "margin-top:14px" },
          el(
            "button",
            {
              class: "btn primary",
              onclick: async () => {
                try {
                  const res = await api.post("/api/attendance/finish", {
                    session_id: session.session_id,
                    default_status: "absent",
                  });
                  toast(res.message);
                  render();
                } catch (err) {
                  toast(err.message, "error");
                }
              },
            },
            "Finish attendance",
          ),
        ),
      );
    }
  }
  body.append(rosterCard);

  // Since the last tuition payment.
  body.append(el("h3", { style: "margin:22px 0 10px" }, "Since the last tuition payment"));
  const sinceCard = el("div", { class: "card" }, loading());
  body.append(sinceCard);
  setMain(body);

  const since = await api.get(`/api/attendance/since-payment?class_id=${classId}`);
  renderSincePayment(sinceCard, since);

  // Context: today's session summary + legend.
  const summary = session ? session.summary : null;
  setContext(
    "Today",
    summary
      ? el(
          "div",
          {},
          el("div", { class: "grid cols-2" },
            kpi("Present", summary.present),
            kpi("Absent", summary.absent),
            kpi("Late", summary.late),
            kpi("Unmarked", summary.unmarked),
          ),
          el("div", { class: "ctx-group-label" }, "Attendance rate"),
          el("div", { style: "font-size:1.6rem;font-weight:700" }, `${attendanceRate(summary)}%`),
        )
      : el("div", { class: "empty" }, "No session today yet."),
  );
}

function renderSincePayment(card, summary) {
  if (!summary.students.length) {
    card.replaceChildren(el("div", { class: "empty" }, "No students to summarise yet."));
    return;
  }
  const nodes = [
    el(
      "div",
      { class: "grid cols-3" },
      kpi("Days attended", summary.total_present, "Across all students"),
      kpi("Days missed", summary.total_absent, "Across all students"),
      kpi("Class days", summary.session_days, "Since the last payment"),
    ),
    el(
      "div",
      { class: "legend" },
      el("span", {}, el("span", { class: "dot present" }), "Present"),
      el("span", {}, el("span", { class: "dot absent" }), "Absent"),
      el("span", {}, el("span", { class: "dot none" }), "Not marked"),
    ),
  ];
  for (const student of summary.students) {
    const dots = el("div", { class: "att-dots" });
    if (student.marks.length) {
      for (const mark of student.marks) {
        const cls = !mark.recorded ? "none" : mark.attended ? "present" : "absent";
        dots.append(el("span", { class: `dot ${cls}`, title: fmtDate(mark.session_date) }));
      }
    } else {
      dots.append(el("span", { class: "att-tally" }, "Nothing outstanding."));
    }
    const since = student.paid_through ? `paid through ${fmtDate(student.paid_through)}` : "never paid";
    nodes.push(
      el(
        "div",
        { class: "att-row" },
        el(
          "div",
          { class: "att-who" },
          el("div", { class: "name" }, student.full_name),
          el("span", { class: "mono" }, student.student_code),
          " ",
          el("span", { class: "att-tally" }, `\u00B7 ${since}`),
        ),
        dots,
        el(
          "div",
          { class: "att-tally" },
          `${student.present_days} present \u00B7 ${student.absent_days} absent \u00B7 ${student.formatted_unpaid}`,
        ),
      ),
    );
  }
  card.replaceChildren(...nodes);
}

// --------------------------------------------------------------- reports

async function renderReports() {
  const className = state.view.className;
  setHeader("#", "reports", className);

  const classSelect = el(
    "select",
    {},
    el("option", { value: "" }, "All classes"),
    ...state.classes.map((c) => el("option", { value: c.name }, c.name)),
  );
  classSelect.value = className;
  const periodSelect = el("select", {}, ...PERIODS.map(([v, l]) => el("option", { value: v }, l)));
  periodSelect.value = "this_month";

  const result = el("div", { style: "margin-top:16px" }, loading());

  async function run() {
    result.replaceChildren(loading());
    const params = new URLSearchParams({ period: periodSelect.value });
    if (classSelect.value) params.set("class_name", classSelect.value);
    try {
      const report = await api.get(`/api/reports/tuition?${params.toString()}`);
      result.replaceChildren(
        el("div", { class: "att-tally", style: "margin-bottom:10px" }, `${classSelect.value || "All classes"} \u00B7 ${report.range.label}`),
        el(
          "div",
          { class: "grid cols-2" },
          kpi("Total earned", report.formatted_total, "Billed from attended days"),
          kpi("Total days", report.teaching_days, "Completed teaching days"),
        ),
      );
      renderReportsContext(report);
    } catch (err) {
      result.replaceChildren(el("div", { class: "empty" }, err.message));
    }
  }
  classSelect.addEventListener("change", run);
  periodSelect.addEventListener("change", run);

  setMain(
    el(
      "div",
      { class: "hero" },
      el("h1", {}, "Reports"),
      el("p", {}, "Money earned and days taught over a period."),
    ),
    el(
      "div",
      { class: "row" },
      el("div", { style: "flex:1" }, field("Class", classSelect)),
      el("div", { style: "flex:1" }, field("Period", periodSelect)),
    ),
    result,
  );
  await run();
}

function renderReportsContext(report) {
  setContext(
    "Breakdown",
    report.classes && report.classes.length
      ? el(
          "div",
          {},
          ...report.classes.map((c) =>
            el(
              "div",
              { class: "ctx-member" },
              el(
                "div",
                {},
                el("div", { class: "name" }, c.class_name),
                el("div", { class: "code" }, `${c.teaching_days} days \u00B7 ${c.formatted_total}`),
              ),
            ),
          ),
        )
      : el("div", { class: "empty" }, "No classes in range."),
  );
}

// --------------------------------------------------------------- class info

async function renderClassInfo() {
  const { classId, className } = state.view;
  setHeader("#", "class-info", className);
  const tabState = { active: "details" };

  const tabbar = el("div", { class: "tabs" });
  const panel = el("div", {});

  function selectTab(id) {
    tabState.active = id;
    for (const t of tabbar.children) t.classList.toggle("active", t.dataset.id === id);
    panel.replaceChildren(loading());
    if (id === "details") renderDetailsTab(panel, classId, className);
    else if (id === "schedule") renderScheduleTab(panel, classId);
    else renderTuitionTab(panel, classId, className);
  }

  for (const [id, label] of [["details", "Details"], ["schedule", "Schedule"], ["tuition", "Tuition"]]) {
    const tab = el("button", { class: "tab", onclick: () => selectTab(id) }, label);
    tab.dataset.id = id;
    tabbar.append(tab);
  }

  setMain(
    el("div", { class: "hero" }, el("h1", {}, className), el("p", {}, "Class details, timetable and tuition status.")),
    tabbar,
    panel,
  );
  selectTab("details");

  const info = await api.get(`/api/classes/${encodeURIComponent(className)}/info`);
  setContext(
    "About",
    el(
      "div",
      {},
      el("div", { class: "ctx-group-label" }, "Students"),
      el("div", {}, String(info.classroom.student_count)),
      el("div", { class: "ctx-group-label" }, "Daily tuition"),
      el("div", {}, info.formatted_daily_tuition_fee),
      el("div", { class: "ctx-group-label" }, "Sessions recorded"),
      el("div", {}, String(info.total_sessions)),
      el("div", { class: "ctx-group-label" }, "Description"),
      el("div", {}, info.classroom.description || "\u2014"),
    ),
  );
}

async function renderDetailsTab(panel, classId, className) {
  const info = await api.get(`/api/classes/${encodeURIComponent(className)}/info`);
  const deleteConfirm = el("input", { type: "checkbox" });
  const deleteBtn = el("button", { class: "btn danger", disabled: true }, "Delete class");
  deleteConfirm.addEventListener("change", () => (deleteBtn.disabled = !deleteConfirm.checked));
  deleteBtn.addEventListener("click", async () => {
    try {
      const res = await api.post("/api/classes/delete", { name: className, confirm: true });
      toast(res.message);
      await refreshClasses();
      goHome();
    } catch (err) {
      toast(err.message, "error");
    }
  });

  panel.replaceChildren(
    el(
      "div",
      { class: "card" },
      el("p", {}, el("b", {}, "Students: "), String(info.classroom.student_count)),
      el("p", {}, el("b", {}, "Daily tuition: "), info.formatted_daily_tuition_fee),
      el("p", {}, el("b", {}, "Description: "), info.classroom.description || "\u2014"),
      el(
        "div",
        { style: "margin-top:12px" },
        el("button", { class: "btn primary", onclick: () => openEditClass(classId, info.classroom) }, "Edit class"),
      ),
    ),
    el(
      "div",
      { class: "card", style: "margin-top:16px" },
      el("h3", {}, "Danger zone"),
      el("label", { class: "checkline" }, deleteConfirm, "I understand this deletes students, attendance and tuition history"),
      deleteBtn,
    ),
  );
}

async function renderScheduleTab(panel, classId) {
  const data = await api.get(`/api/schedule?class_id=${classId}`);
  const rulesTable = table(
    [
      { label: "Day", render: (r) => r.weekday_label },
      { label: "Start", render: (r) => r.start_time.slice(0, 5) },
      { label: "End", render: (r) => r.end_time.slice(0, 5) },
      {
        label: "",
        render: (r) =>
          el(
            "button",
            {
              class: "btn ghost small",
              onclick: async () => {
                try {
                  await api.post("/api/schedule/rule/remove", { class_id: classId, rule_id: r.id });
                  toast("Weekly slot removed.");
                  renderScheduleTab(panel, classId);
                } catch (err) {
                  toast(err.message, "error");
                }
              },
            },
            "Remove",
          ),
      },
    ],
    data.rules,
    "No weekly slots yet.",
  );

  const extrasTable = table(
    [
      { label: "Date", render: (e) => fmtDate(e.session_date) },
      { label: "Start", render: (e) => e.start_time.slice(0, 5) },
      { label: "End", render: (e) => e.end_time.slice(0, 5) },
      { label: "Note", render: (e) => e.note || "\u2014" },
    ],
    data.extras,
    "No extra classes yet.",
  );

  panel.replaceChildren(
    el(
      "div",
      { class: "card" },
      el("h3", {}, "Weekly timetable"),
      rulesTable,
      el(
        "div",
        { style: "margin-top:12px" },
        el("button", { class: "btn primary", onclick: () => openAddWeeklySlot(classId, () => renderScheduleTab(panel, classId)) }, "Add weekly slot"),
      ),
    ),
    el(
      "div",
      { class: "card", style: "margin-top:16px" },
      el("h3", {}, "Extra classes"),
      extrasTable,
      el(
        "div",
        { style: "margin-top:12px" },
        el("button", { class: "btn primary", onclick: () => openAddExtra(classId, () => renderScheduleTab(panel, classId)) }, "Add extra class"),
      ),
    ),
  );
}

async function renderTuitionTab(panel, classId, className) {
  const rows = await api.get(`/api/tuition/status?class_id=${classId}`);
  const outstanding = rows.filter((r) => r.unpaid_days);
  panel.replaceChildren(
    el(
      "div",
      { class: "card" },
      table(
        [
          { label: "Code", render: (r) => el("span", { class: "mono" }, r.student_code) },
          { label: "Name", render: (r) => r.full_name },
          { label: "Unpaid days", render: (r) => String(r.unpaid_days) },
          { label: "Amount owed", render: (r) => r.formatted_unpaid },
          {
            label: "Status",
            render: (r) =>
              el("span", { class: `chip ${r.unpaid_days ? "absent" : "present"}` }, r.status),
          },
        ],
        rows,
        `No students in ${className}.`,
      ),
      outstanding.length
        ? el(
            "div",
            { style: "margin-top:12px" },
            el(
              "button",
              { class: "btn primary", onclick: () => openMarkTuition(classId, outstanding, () => renderTuitionTab(panel, classId, className)) },
              "Mark tuition completed",
            ),
          )
        : null,
    ),
  );
}

// --------------------------------------------------------------- chat

async function renderChat() {
  hideContext();
  setHeader("#", "chat", state.me && state.me.groq_enabled ? state.me.groq_model : "assistant");

  if (state.me && !state.me.groq_enabled) {
    setMain(
      el(
        "div",
        { class: "empty" },
        "GROQ_API_KEY is not set, so the assistant is unavailable. The rest of the dashboard still works without it.",
      ),
    );
    return;
  }

  const scroll = el("div", { class: "chat-scroll" });
  const input = el("input", { placeholder: "Ask the assistant\u2026", type: "text" });
  const sendBtn = el("button", { class: "btn primary" }, "Send");

  function drawMessages() {
    scroll.replaceChildren();
    if (!state.chat.length) {
      scroll.append(
        el("div", { class: "empty" }, "Ask in plain language, or start with an example."),
        el(
          "div",
          { class: "examples" },
          ...[
            "Create class SE401 with tuition fee 50000",
            "Add Nguyen Van A (SE001) to SE401",
            "Take attendance for SE401",
            "Who was absent this week?",
          ].map((ex) => el("button", { class: "example", onclick: () => submit(ex) }, ex)),
        ),
      );
      return;
    }
    for (const m of state.chat) {
      scroll.append(
        el(
          "div",
          { class: "msg" },
          el("div", { class: `avatar ${m.role === "assistant" ? "bot" : ""}` }, m.role === "assistant" ? "AI" : initials(state.me.display_name)),
          el(
            "div",
            {},
            el("div", { class: "who" }, m.role === "assistant" ? "Assistant" : "You"),
            el("div", { class: "body" }, m.content),
          ),
        ),
      );
    }
    scroll.scrollTop = scroll.scrollHeight;
  }

  async function submit(text) {
    const message = (text || "").trim();
    if (!message) return;
    state.chat.push({ role: "user", content: message });
    input.value = "";
    drawMessages();
    sendBtn.disabled = true;
    sendBtn.replaceChildren(el("span", { class: "spinner" }));
    try {
      const res = await api.post("/api/chat", { message });
      state.chat.push({ role: "assistant", content: res.reply });
    } catch (err) {
      state.chat.pop();
      toast(err.message, "error");
    } finally {
      sendBtn.disabled = false;
      sendBtn.textContent = "Send";
      drawMessages();
    }
  }

  sendBtn.addEventListener("click", () => submit(input.value));
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submit(input.value);
  });

  setMain(
    el(
      "div",
      { class: "chat-wrap" },
      el(
        "div",
        { class: "hero" },
        el("h1", {}, "AI chat"),
        el("p", {}, "The model only calls tools; it never writes to the database itself."),
      ),
      scroll,
      el("div", { class: "chat-input" }, input, sendBtn),
    ),
  );
  drawMessages();
  input.focus();
}

// --------------------------------------------------------------- modals

function openCreateClass() {
  const { body, close } = modal("Create a class");
  const name = el("input", { placeholder: "SE401", type: "text" });
  const description = el("input", { type: "text" });
  const fee = el("input", { type: "number", min: "0", step: "1000", value: "0" });
  const roster = el("input", { type: "file", accept: ".xlsx,.xlsm,.csv" });
  const submit = el("button", { class: "btn primary" }, "Create class");
  submit.addEventListener("click", async () => {
    if (!name.value.trim()) return toast("Please enter a class name.", "warning");
    submit.disabled = true;
    try {
      const created = await api.post("/api/classes", {
        name: name.value.trim(),
        description: description.value.trim() || null,
        daily_tuition_fee: parseInt(fee.value || "0", 10),
      });
      let message = created.message;
      const file = roster.files[0];
      if (file) {
        const q = new URLSearchParams({ filename: file.name, class_name: created.classroom.name });
        const imported = await apiUpload(`/api/classes/${created.classroom.id}/roster?${q}`, file);
        message += " " + imported.message;
        for (const problem of imported.skipped || []) toast(problem, "warning");
      }
      await refreshClasses();
      close();
      toast(message);
      selectClass(created.classroom);
    } catch (err) {
      toast(err.message, "error");
      submit.disabled = false;
    }
  });
  body.append(
    field("Class name", name),
    field("Description (optional)", description),
    field("Daily tuition (VND)", fee),
    field("Student list (optional .xlsx/.csv)", roster),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit),
  );
}

function openAddStudent(className) {
  const { body, close } = modal("Add student");
  const fullName = el("input", { placeholder: "Nguyen Van A", type: "text" });
  const code = el("input", { placeholder: "SE001", type: "text" });
  const email = el("input", { type: "text" });
  const phone = el("input", { type: "text" });
  const note = el("input", { type: "text" });
  const submit = el("button", { class: "btn primary" }, "Add student");
  submit.addEventListener("click", async () => {
    submit.disabled = true;
    try {
      const res = await api.post("/api/students", {
        class_name: className,
        full_name: fullName.value,
        student_code: code.value,
        email: email.value.trim() || null,
        phone: phone.value.trim() || null,
        note: note.value.trim() || null,
      });
      close();
      toast(res.message);
      render();
    } catch (err) {
      toast(err.message, "error");
      submit.disabled = false;
    }
  });
  body.append(
    field("Full name", fullName),
    field("Student ID", code),
    field("Email (optional)", email),
    field("Phone (optional)", phone),
    field("Note (optional)", note),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit),
  );
}

function openEditStudent(className) {
  const { body, close } = modal("Update or remove a student");
  const ref = el("input", { placeholder: "SE001 or Nguyen Van A", type: "text" });
  const newName = el("input", { type: "text" });
  const newCode = el("input", { type: "text" });
  const email = el("input", { type: "text" });
  const phone = el("input", { type: "text" });
  const note = el("input", { type: "text" });
  const removeConfirm = el("input", { type: "checkbox" });
  const removeBtn = el("button", { class: "btn danger", disabled: true }, "Remove student");
  removeConfirm.addEventListener("change", () => (removeBtn.disabled = !removeConfirm.checked));

  const saveBtn = el("button", { class: "btn primary" }, "Save changes");
  saveBtn.addEventListener("click", async () => {
    if (!ref.value.trim()) return toast("Please identify the student.", "warning");
    try {
      const res = await api.post("/api/students/update", {
        student: ref.value.trim(),
        class_name: className,
        new_full_name: newName.value.trim() || null,
        new_student_code: newCode.value.trim() || null,
        email: email.value.trim() || null,
        phone: phone.value.trim() || null,
        note: note.value.trim() || null,
      });
      close();
      toast(res.message);
      render();
    } catch (err) {
      toast(err.message, "error");
    }
  });
  removeBtn.addEventListener("click", async () => {
    if (!ref.value.trim()) return toast("Please identify the student.", "warning");
    try {
      const res = await api.post("/api/students/remove", {
        student: ref.value.trim(),
        class_name: className,
        confirm: true,
      });
      close();
      toast(res.message);
      render();
    } catch (err) {
      toast(err.message, "error");
    }
  });

  body.append(
    field("Student ID or name", ref),
    field("New full name (optional)", newName),
    field("New student ID (optional)", newCode),
    field("Email (optional)", email),
    field("Phone (optional)", phone),
    field("Note (optional)", note),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), saveBtn),
    el("hr", { style: "border:0;border-top:1px solid var(--divider);margin:16px 0" }),
    el("label", { class: "checkline" }, removeConfirm, "I understand this also deletes their attendance history"),
    removeBtn,
  );
}

function openEditClass(classId, current) {
  const { body, close } = modal("Edit class");
  const name = el("input", { type: "text", value: current.name });
  const description = el("textarea", {}, current.description || "");
  const fee = el("input", { type: "number", min: "0", step: "1000", value: String(current.daily_tuition_fee) });
  const icon = el("input", { type: "file", accept: "image/*" });
  const submit = el("button", { class: "btn primary" }, "Save changes");
  submit.addEventListener("click", async () => {
    const newName = name.value.trim();
    if (!newName) return toast("Please enter a name.", "warning");
    submit.disabled = true;
    try {
      let savedName = current.name;
      if (newName !== current.name) {
        const res = await api.post("/api/classes/rename", { current_name: current.name, new_name: newName });
        savedName = res.classroom.name;
      }
      const newDescription = description.value.trim();
      if ((newDescription || null) !== (current.description || null))
        await api.post(`/api/classes/${classId}/description`, { description: newDescription || null });
      const newFee = parseInt(fee.value || "0", 10);
      if (newFee !== current.daily_tuition_fee)
        await api.post("/api/classes/fee", { class_name: savedName, daily_tuition_fee: newFee });
      const file = icon.files[0];
      if (file) {
        const q = new URLSearchParams({ filename: file.name });
        await apiUpload(`/api/classes/${classId}/icon?${q}`, file);
      }
      await refreshClasses();
      close();
      toast(`${savedName} updated.`);
      state.view.className = savedName;
      render();
    } catch (err) {
      toast(err.message, "error");
      submit.disabled = false;
    }
  });
  body.append(
    field("Class name", name),
    field("Description", description),
    field("Daily tuition (VND)", fee),
    field("Class icon (optional)", icon),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit),
  );
}

function openAddWeeklySlot(classId, onDone) {
  const { body, close } = modal("Add weekly slot");
  const weekday = el("select", {}, ...WEEKDAYS.map((label, i) => el("option", { value: String(i) }, label)));
  const start = el("input", { type: "time", value: "18:00" });
  const end = el("input", { type: "time", value: "20:00" });
  const submit = el("button", { class: "btn primary" }, "Add slot");
  submit.addEventListener("click", async () => {
    try {
      await api.post("/api/schedule/rule", {
        class_id: classId,
        weekday: parseInt(weekday.value, 10),
        start_time: start.value,
        end_time: end.value,
      });
      close();
      toast("Weekly slot added.");
      onDone();
    } catch (err) {
      toast(err.message, "error");
    }
  });
  body.append(
    field("Weekday", weekday),
    field("Start", start),
    field("End", end),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit),
  );
}

function openAddExtra(classId, onDone) {
  const { body, close } = modal("Add extra class");
  const day = el("input", { type: "date", value: new Date().toISOString().slice(0, 10) });
  const start = el("input", { type: "time", value: "18:00" });
  const end = el("input", { type: "time", value: "20:00" });
  const note = el("input", { type: "text" });
  const submit = el("button", { class: "btn primary" }, "Add class");
  submit.addEventListener("click", async () => {
    try {
      await api.post("/api/schedule/extra", {
        class_id: classId,
        session_date: day.value,
        start_time: start.value,
        end_time: end.value,
        note: note.value.trim() || null,
      });
      close();
      toast("Extra class added.");
      onDone();
    } catch (err) {
      toast(err.message, "error");
    }
  });
  body.append(
    field("Date", day),
    field("Start time", start),
    field("End time", end),
    field("Note (optional)", note),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit),
  );
}

function openMarkTuition(classId, outstanding, onDone) {
  const { body, close } = modal("Mark tuition completed");
  const select = el(
    "select",
    {},
    ...outstanding.map((r) =>
      el("option", { value: String(r.student_id) }, `${r.full_name} (${r.student_code}) \u00B7 ${r.formatted_unpaid}`),
    ),
  );
  const submit = el("button", { class: "btn primary" }, "Mark completed");
  submit.addEventListener("click", async () => {
    try {
      const res = await api.post("/api/tuition/mark-completed", {
        class_id: classId,
        student_id: parseInt(select.value, 10),
      });
      close();
      toast(res.message);
      onDone();
    } catch (err) {
      toast(err.message, "error");
    }
  });
  body.append(field("Student", select), actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit));
}

// --------------------------------------------------------------- boot

async function boot() {
  try {
    state.me = await api.get("/api/me");
    await refreshClasses();
  } catch (err) {
    document.body.append(el("div", { class: "toast error" }, err.message));
  }
  render();
}

boot();
