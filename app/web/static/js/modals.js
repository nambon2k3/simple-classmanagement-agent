/** Create/edit class and student dialogs. */

import { api, apiUpload } from "./api.js";
import { refreshClasses, state } from "./state.js";
import { WEEKDAYS } from "./format.js";
import { actions, el, field, modal, toast } from "./ui.js";
import { navigate, render } from "./router.js";

export function openCreateClass() {
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
      navigate(`/classes/${created.classroom.id}/students`);
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

export function openAddStudent(className) {
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

export function openEditStudent(className) {
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

export function openEditClass(classId, current) {
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
    field("Class image (optional, up to 10 MB)", icon),
    actions(el("button", { class: "btn ghost", onclick: close }, "Cancel"), submit),
  );
}

export function openAddWeeklySlot(classId, onDone) {
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

export function openAddExtra(classId, onDone) {
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

export function openCancelTeachingDay(className, onConfirm) {
  const { body, close } = modal("Cancel teaching day");
  const confirmBtn = el("button", { class: "btn danger" }, "Mark all absent");
  confirmBtn.addEventListener("click", async () => {
    confirmBtn.disabled = true;
    try {
      await onConfirm();
      close();
    } catch (err) {
      toast(err.message, "error");
      confirmBtn.disabled = false;
    }
  });
  body.append(
    el(
      "p",
      { class: "warn-copy" },
      `Cancel today's class for ${className}? Every student will be marked absent. This cannot be undone from the dashboard.`,
    ),
    actions(el("button", { class: "btn ghost", onclick: close }, "Go back"), confirmBtn),
  );
}
