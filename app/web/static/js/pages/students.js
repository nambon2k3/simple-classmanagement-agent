/** Class roster with attendance since last payment. */

import { api } from "../api.js";
import { state } from "../state.js";
import { el, toast, table, setHeader, setMain, setContext } from "../ui.js";
import { initials } from "../format.js";
import { render } from "../router.js";
import { openAddStudent, openEditStudent } from "../modals.js";

export async function renderStudents() {
  const { className, classId } = state.view;
  setHeader("#", "students", className);
  const [students, since] = await Promise.all([
    api.get(`/api/students?class_name=${encodeURIComponent(className)}`),
    api.get(`/api/attendance/since-payment?class_id=${classId}`),
  ]);
  const sinceByStudent = {};
  for (const row of since.students) sinceByStudent[row.student_id] = row;

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
    el(
      "div",
      { class: "card" },
      el("h3", {}, "Roster"),
      studentTuitionTable(students, sinceByStudent, classId, `${className} has no students yet.`),
    ),
    searchBox,
  );

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

function studentTuitionTable(students, sinceByStudent, classId, emptyText) {
  return table(
    [
      { label: "Code", render: (s) => el("span", { class: "mono" }, s.student_code) },
      { label: "Name", render: (s) => s.full_name },
      {
        label: "Attendance",
        render: (s) => {
          const info = sinceByStudent[s.id];
          if (!info) return "\u2014";
          return el(
            "span",
            {},
            el("span", { class: "chip present", style: "margin-right:4px" }, `${info.present_days} present`),
            el("span", { class: "chip absent" }, `${info.absent_days} absent`),
          );
        },
      },
      {
        label: "Unpaid",
        render: (s) => {
          const info = sinceByStudent[s.id];
          if (!info) return "\u2014";
          return info.formatted_unpaid;
        },
      },
      {
        label: "",
        render: (s) => {
          const info = sinceByStudent[s.id];
          if (!info || !info.unpaid_vnd) return el("span", { class: "chip present" }, "Paid");
          const btn = el(
            "button",
            {
              class: "btn success small",
              onclick: async (e) => {
                e.stopPropagation();
                btn.disabled = true;
                try {
                  const res = await api.post("/api/tuition/mark-completed", {
                    class_id: classId,
                    student_id: s.id,
                  });
                  toast(res.message);
                  render();
                } catch (err) {
                  toast(err.message, "error");
                  btn.disabled = false;
                }
              },
            },
            "Mark paid",
          );
          return btn;
        },
      },
    ],
    students,
    emptyText,
  );
}
