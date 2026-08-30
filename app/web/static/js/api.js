/** Fetch helpers for the dashboard JSON API. */

function errorMessage(data, status) {
  if (data && data.message) return data.message;
  if (data && typeof data.detail === "string") return data.detail;
  if (data && Array.isArray(data.detail))
    return data.detail.map((d) => d.msg || String(d)).join("; ");
  if (typeof data === "string" && data) return data;
  return `Request failed (${status})`;
}

async function apiFetch(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = text;
  }
  if (!res.ok) {
    const err = new Error(errorMessage(data, res.status));
    err.data = data;
    throw err;
  }
  return data;
}

export async function apiUpload(path, file) {
  const res = await fetch(path, { method: "POST", body: file });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = text;
  }
  if (!res.ok) throw new Error(errorMessage(data, res.status));
  return data;
}

export const api = {
  get: (p) => apiFetch("GET", p),
  post: (p, b) => apiFetch("POST", p, b === undefined ? {} : b),
};
