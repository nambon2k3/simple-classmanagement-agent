/** Dashboard boot: load the current user and classes, then start the router. */

import { api } from "./api.js";
import { refreshClasses, state } from "./state.js";
import { el } from "./ui.js";
import { startRouter } from "./router.js";

async function boot() {
  try {
    state.me = await api.get("/api/me");
    await refreshClasses();
  } catch (err) {
    document.body.append(el("div", { class: "toast error" }, err.message));
  }
  startRouter();
}

boot();
