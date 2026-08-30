/** Tuition reports over a period. */

import { api } from "../api.js";
import { state } from "../state.js";
import { el, field, kpi, loading, setHeader, setMain, setContext } from "../ui.js";
import { PERIODS } from "../format.js";

export async function renderReports() {
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
        el(
          "div",
          { class: "att-tally", style: "margin-bottom:10px" },
          `${classSelect.value || "All classes"} \u00B7 ${report.range.label}`,
        ),
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
