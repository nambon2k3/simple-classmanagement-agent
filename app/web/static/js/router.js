/** Map the path to a view and render the matching page. */

import { el, setMain, loading, toast } from "./ui.js";
import { state } from "./state.js";
import { renderRail, renderChannels } from "./layout.js";
import { renderHome } from "./pages/home.js";
import { renderStudents } from "./pages/students.js";
import { renderAttendance } from "./pages/attendance.js";
import { renderReports } from "./pages/reports.js";
import { renderClassInfo } from "./pages/info.js";
import { renderChat } from "./pages/chat.js";

const PAGES = {
  dashboard: renderHome,
  students: renderStudents,
  attendance: renderAttendance,
  reports: renderReports,
  info: renderClassInfo,
  chat: renderChat,
};

export function parsePath(pathname) {
  const path = pathname.replace(/\/+$/, "") || "/";
  if (path === "/") return { server: "home", channel: "dashboard", classId: null };
  if (path === "/chat") return { server: "ai", channel: "chat", classId: null };
  const match = path.match(/^\/classes\/(\d+)\/(students|attendance|reports|info)$/);
  if (match) {
    return { server: "class", channel: match[2], classId: Number(match[1]) };
  }
  return { server: "home", channel: "dashboard", classId: null };
}

export function applyLocation() {
  const parsed = parsePath(location.pathname);
  state.view.server = parsed.server;
  state.view.channel = parsed.channel;
  state.view.classId = parsed.classId;
  if (parsed.classId != null) {
    const cls = state.classes.find((c) => c.id === parsed.classId);
    state.view.className = cls ? cls.name : null;
    if (!cls) {
      history.replaceState({}, "", "/");
      state.view.server = "home";
      state.view.channel = "dashboard";
      state.view.classId = null;
      state.view.className = null;
    }
  } else {
    state.view.className = null;
  }
}

export function navigate(path) {
  if (location.pathname === path) {
    render();
    return;
  }
  history.pushState({}, "", path);
  render();
}

export function render() {
  applyLocation();
  renderRail();
  renderChannels();
  const page = PAGES[state.view.channel] || renderHome;
  setMain(loading());
  Promise.resolve()
    .then(() => page())
    .catch((err) => {
      setMain(el("div", { class: "empty" }, err.message || "Something went wrong."));
      toast(err.message || "Something went wrong.", "error");
    });
}

export function startRouter() {
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[data-nav]");
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (link.target && link.target !== "_self") return;
    const href = link.getAttribute("href");
    if (!href || !href.startsWith("/")) return;
    event.preventDefault();
    navigate(href);
  });
  window.addEventListener("popstate", () => render());
  render();
}
