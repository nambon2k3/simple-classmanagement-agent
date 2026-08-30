import { api } from "./api.js";

/** Shared dashboard state. The current screen is also stored in the URL. */

export const state = {
  me: null,
  classes: [],
  view: { server: "home", channel: "dashboard", classId: null, className: null },
  cal: { year: new Date().getFullYear(), month: new Date().getMonth() + 1 },
  chat: [],
};

export const CLASS_CHANNELS = [
  { id: "students", label: "students" },
  { id: "attendance", label: "attendance" },
  { id: "reports", label: "reports" },
  { id: "info", label: "class-info" },
];

export function classHref(classId, channel) {
  return `/classes/${classId}/${channel}`;
}

export async function refreshClasses() {
  state.classes = await api.get("/api/classes");
}
