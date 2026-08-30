/** Today's attendance roll-call. */

import { api } from "../api.js";
import { state } from "../state.js";
import { el, toast, kpi, setHeader, setMain, setContext } from "../ui.js";
import { fmtDate, attendanceRate } from "../format.js";
import { render } from "../router.js";

export async function renderAttendance() {
  const { className } = state.view;
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

  body.append(
    el(
      "div",
      { class: "att-tally", style: "margin-bottom:6px" },
      `Today \u00B7 ${fmtDate(new Date().toISOString().slice(0, 10))}`,
    ),
  );
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
  setMain(body);

  const summary = session ? session.summary : null;
  setContext(
    "Today",
    summary
      ? el(
          "div",
          {},
          el(
            "div",
            { class: "grid cols-2" },
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
