/** Home dashboard: KPIs, today's classes, calendar, activity. */

import { api } from "../api.js";
import { state, classHref } from "../state.js";
import { el, $, kpi, setHeader, setMain, setContext, loading, toast } from "../ui.js";
import { initials, relTime, MONTHS } from "../format.js";
import { openCreateClass, openCancelTeachingDay } from "../modals.js";
import { render } from "../router.js";

export async function renderHome() {
  setHeader("#", "dashboard", "Overview of your classes");
  const [summary, activity, todayClasses] = await Promise.all([
    api.get("/api/dashboard/summary"),
    api.get("/api/activity"),
    api.get("/api/dashboard/today"),
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

  const todayCard = el(
    "div",
    { class: "card" },
    el("h3", {}, "Today's classes"),
    renderTodayClasses(todayClasses),
  );

  const calCard = el("div", { class: "card", id: "cal-card" });
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
    todayCard,
    el("div", { style: "height:16px" }),
    el("div", { class: "grid cols-2", style: "grid-template-columns: 2fr 1fr" }, calCard, activityCard),
    el("div", { style: "height:16px" }),
    createBtn,
  );

  await renderCalendar(calCard);

  setContext(
    "Classes",
    state.classes.length
      ? el(
          "div",
          {},
          ...state.classes.map((cls) =>
            el(
              "a",
              {
                class: "ctx-member",
                href: classHref(cls.id, "students"),
                "data-nav": "true",
              },
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

function formatSlot(slot) {
  return `${slot.start_time.slice(0, 5)}\u2013${slot.end_time.slice(0, 5)}`;
}

function renderTodayClasses(rows) {
  if (!rows.length) return el("div", { class: "empty" }, "No classes scheduled today.");
  return el("div", {}, ...rows.map(renderTodayRow));
}

function renderTodayRow(row) {
  let action;
  if (row.cancelled) {
    action = el("span", { class: "chip absent" }, "Cancelled");
  } else if (row.completed) {
    action = el("span", { class: "chip present" }, "Completed");
  } else if (!row.student_count) {
    action = el("span", { class: "chip neutral" }, "No students");
  } else {
    action = el(
      "div",
      { class: "today-class-actions" },
      el(
        "button",
        { class: "btn success", onclick: () => completeToday(row) },
        "Complete teaching day",
      ),
      el(
        "button",
        { class: "btn danger", onclick: () => confirmCancelToday(row) },
        "Mark as cancelled",
      ),
    );
  }
  return el(
    "div",
    { class: "today-class" },
    el("div", { class: "avatar", style: "border-radius:16px" }, initials(row.class_name)),
    el(
      "div",
      { class: "meta" },
      el(
        "a",
        {
          class: "name",
          href: classHref(row.class_id, "attendance"),
          "data-nav": "true",
        },
        row.class_name,
      ),
      el("div", { class: "when" }, row.slots.map(formatSlot).join(" \u00B7 ")),
    ),
    action,
  );
}

async function completeToday(row) {
  try {
    const res = await api.post("/api/attendance/complete-day", { class_id: row.class_id });
    toast(res.message);
    render();
  } catch (err) {
    toast(err.message, "error");
  }
}

function confirmCancelToday(row) {
  openCancelTeachingDay(row.class_name, async () => {
    const res = await api.post("/api/attendance/cancel-day", { class_id: row.class_id });
    toast(res.message);
    render();
  });
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
  const firstWeekday = (new Date(year, month - 1, 1).getDay() + 6) % 7;
  const lastDay = new Date(year, month, 0).getDate();
  const today = new Date();
  const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const grid = el("div", { class: "cal-grid" });
  for (const dow of ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    grid.append(el("div", { class: "cal-dow" }, dow));
  for (let i = 0; i < firstWeekday; i++) grid.append(el("div", { class: "cal-cell empty" }));
  for (let day = 1; day <= lastDay; day++) {
    const isToday =
      today.getFullYear() === year && today.getMonth() + 1 === month && today.getDate() === day;
    const events = byDay[day] || [];
    const isFuture = new Date(year, month - 1, day) > todayStart;
    let teachingClass = "";
    if (events.length) {
      if (events.every((item) => item.cancelled)) teachingClass = "teaching-cancelled";
      else if (events.every((item) => item.completed)) teachingClass = "teaching-done";
      else if (isFuture) teachingClass = "teaching-upcoming";
      else teachingClass = "teaching-pending";
    }
    const cell = el(
      "div",
      { class: `cal-cell ${isToday ? "today" : ""} ${teachingClass}`.trim() },
    );
    cell.append(el("div", { class: "cal-day" }, day));
    for (const item of events) {
      const start = item.start_time.slice(0, 5);
      const end = item.end_time.slice(0, 5);
      let statusClass = "pending";
      if (item.cancelled) statusClass = "cancelled";
      else if (item.completed) statusClass = "done";
      else if (isFuture) statusClass = "upcoming";
      cell.append(
        el(
          "div",
          {
            class: `cal-event ${item.kind === "extra" ? "extra" : ""} ${statusClass}`,
          },
          `${item.class_name} ${start}-${end}`,
        ),
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
  const card = $("cal-card");
  if (card) renderCalendar(card);
}
