/** Class details, schedule, and tuition status. */

import { api } from "../api.js";
import { refreshClasses, state } from "../state.js";
import { el, toast, table, loading, setHeader, setMain, setContext } from "../ui.js";
import { fmtDate } from "../format.js";
import { navigate } from "../router.js";
import { openEditClass, openAddWeeklySlot, openAddExtra } from "../modals.js";

export async function renderClassInfo() {
  const { classId, className } = state.view;
  setHeader("#", "class-info", className);
  const requested = new URLSearchParams(location.search).get("tab");
  const tabState = {
    active: ["details", "schedule", "tuition"].includes(requested) ? requested : "details",
  };

  const tabbar = el("div", { class: "tabs" });
  const panel = el("div", {});

  function selectTab(id) {
    tabState.active = id;
    const url = new URL(location.href);
    if (id === "details") url.searchParams.delete("tab");
    else url.searchParams.set("tab", id);
    history.replaceState({}, "", url.pathname + url.search);
    for (const t of tabbar.children) t.classList.toggle("active", t.dataset.id === id);
    panel.replaceChildren(loading());
    if (id === "details") renderDetailsTab(panel, classId, className);
    else if (id === "schedule") renderScheduleTab(panel, classId);
    else renderTuitionTab(panel, classId, className);
  }

  for (const [id, label] of [
    ["details", "Details"],
    ["schedule", "Schedule"],
    ["tuition", "Tuition"],
  ]) {
    const tab = el("button", { class: "tab", onclick: () => selectTab(id) }, label);
    tab.dataset.id = id;
    tabbar.append(tab);
  }

  setMain(
    el(
      "div",
      { class: "hero" },
      el("h1", {}, className),
      el("p", {}, "Class details, timetable and tuition status."),
    ),
    tabbar,
    panel,
  );
  selectTab(tabState.active);

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
      navigate("/");
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
        el(
          "button",
          { class: "btn primary", onclick: () => openEditClass(classId, info.classroom) },
          "Edit class",
        ),
      ),
    ),
    el(
      "div",
      { class: "card", style: "margin-top:16px" },
      el("h3", {}, "Danger zone"),
      el(
        "label",
        { class: "checkline" },
        deleteConfirm,
        "I understand this deletes students, attendance and tuition history",
      ),
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
        el(
          "button",
          {
            class: "btn primary",
            onclick: () => openAddWeeklySlot(classId, () => renderScheduleTab(panel, classId)),
          },
          "Add weekly slot",
        ),
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
        el(
          "button",
          {
            class: "btn primary",
            onclick: () => openAddExtra(classId, () => renderScheduleTab(panel, classId)),
          },
          "Add extra class",
        ),
      ),
    ),
  );
}

async function renderTuitionTab(panel, classId, className) {
  const rows = await api.get(`/api/tuition/status?class_id=${classId}`);
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
      el(
        "div",
        { class: "att-tally", style: "margin-top:12px" },
        "To mark tuition as paid, go to the Students page.",
      ),
    ),
  );
}
