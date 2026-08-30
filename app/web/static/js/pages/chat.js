/** AI assistant chat. */

import { api } from "../api.js";
import { state } from "../state.js";
import { el, toast, hideContext, setHeader, setMain } from "../ui.js";
import { initials } from "../format.js";

export async function renderChat() {
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
          el(
            "div",
            { class: `avatar ${m.role === "assistant" ? "bot" : ""}` },
            m.role === "assistant" ? "AI" : initials(state.me.display_name),
          ),
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
