/** Rail and channel sidebar as real links so F5 keeps the current page. */

import { el, $ } from "./ui.js";
import { initials } from "./format.js";
import { CLASS_CHANNELS, classHref, state } from "./state.js";

function railLink({ label, title, active, href, brand, cls }) {
  const hasImg = cls && cls.has_icon;
  const node = el("a", {
    class: `rail-btn ${brand ? "brand" : ""} ${active ? "active" : ""} ${hasImg ? "has-img" : ""}`,
    title: title || label,
    href: href || "#",
    "data-nav": href ? "true" : undefined,
  });
  if (brand) node.removeAttribute("data-nav");
  if (hasImg) {
    const img = el("img", { src: `/api/classes/${cls.id}/icon`, alt: cls.name });
    img.addEventListener("error", () => {
      img.remove();
      node.classList.remove("has-img");
      node.textContent = initials(cls.name);
    });
    node.append(img);
  } else {
    node.textContent = label;
  }
  return node;
}

function channelLink(href, id, label, glyph) {
  return el(
    "a",
    {
      class: `channel-item ${state.view.channel === id ? "active" : ""}`,
      href,
      "data-nav": "true",
    },
    el("span", { class: "glyph" }, glyph || "#"),
    label,
  );
}

export function renderRail() {
  const rail = $("rail");
  rail.replaceChildren();
  rail.append(railLink({ label: "CM", brand: true, title: "Class Management", href: "/" }));
  rail.append(el("div", { class: "rail-sep" }));
  rail.append(
    railLink({
      label: "\uD83C\uDFE0",
      title: "Home",
      href: "/",
      active: state.view.server === "home",
    }),
  );
  for (const cls of state.classes) {
    rail.append(
      railLink({
        label: initials(cls.name),
        title: cls.name,
        href: classHref(cls.id, "students"),
        active: state.view.server === "class" && state.view.classId === cls.id,
        cls,
      }),
    );
  }
  rail.append(el("div", { class: "rail-sep" }));
  rail.append(
    railLink({
      label: "AI",
      title: "AI chat",
      href: "/chat",
      active: state.view.server === "ai",
    }),
  );
}

export function renderChannels() {
  const panel = $("channels");
  panel.replaceChildren();
  const scroll = el("div", { class: "channels-scroll" });

  let headerText = "Home";
  if (state.view.server === "class") headerText = state.view.className;
  else if (state.view.server === "ai") headerText = "Assistant";

  if (state.view.server === "home") {
    scroll.append(el("div", { class: "channel-section" }, "Overview"));
    scroll.append(channelLink("/", "dashboard", "dashboard", "#"));
    scroll.append(el("div", { class: "channel-section" }, "Classes"));
    if (state.classes.length === 0) {
      scroll.append(el("div", { class: "empty" }, "No classes yet."));
    }
    for (const cls of state.classes) {
      scroll.append(
        el(
          "a",
          {
            class: "channel-item",
            href: classHref(cls.id, "students"),
            "data-nav": "true",
          },
          el("span", { class: "glyph" }, initials(cls.name)),
          cls.name,
        ),
      );
    }
  } else if (state.view.server === "class") {
    scroll.append(el("div", { class: "channel-section" }, "Channels"));
    for (const ch of CLASS_CHANNELS) {
      scroll.append(
        channelLink(classHref(state.view.classId, ch.id), ch.id, ch.label),
      );
    }
  } else if (state.view.server === "ai") {
    scroll.append(el("div", { class: "channel-section" }, "Assistant"));
    scroll.append(channelLink("/chat", "chat", "chat"));
  }

  const footer = el(
    "div",
    { class: "channels-footer" },
    el("div", { class: "avatar" }, initials(state.me ? state.me.display_name : "?")),
    el(
      "div",
      { class: "who" },
      el("b", {}, state.me ? state.me.display_name : "\u2014"),
      el("span", {}, "Administrator"),
    ),
  );

  panel.append(el("div", { class: "channels-header" }, headerText));
  panel.append(scroll);
  panel.append(footer);
}
