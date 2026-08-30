/** Formatting helpers. */

export function initials(name) {
  const compact = (name || "").replace(/\s+/g, "");
  return compact ? compact.slice(0, 2).toUpperCase() : "?";
}

export function fmtDate(iso) {
  if (!iso) return "\u2014";
  const value = iso.length === 10 ? iso + "T00:00:00" : iso;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

export function relTime(iso) {
  const then = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  const seconds = Math.floor((Date.now() - then.getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) {
    const m = Math.floor(seconds / 60);
    return `${m} minute${m > 1 ? "s" : ""} ago`;
  }
  if (seconds < 86400) {
    const h = Math.floor(seconds / 3600);
    return `${h} hour${h > 1 ? "s" : ""} ago`;
  }
  const days = Math.floor(seconds / 86400);
  if (days < 30) return `${days} day${days > 1 ? "s" : ""} ago`;
  return fmtDate(iso.slice(0, 10));
}

export function attendanceRate(summary) {
  if (!summary.total) return 0;
  return Math.round(((summary.present + summary.late) / summary.total) * 100);
}

export const WEEKDAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];
export const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];
export const PERIODS = [
  ["today", "Today"],
  ["yesterday", "Yesterday"],
  ["this_week", "This week"],
  ["last_week", "Last week"],
  ["this_month", "This month"],
  ["last_month", "Last month"],
  ["all_time", "All time"],
];
