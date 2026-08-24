// DRISHTI dashboard - tiny helper for talking to the FastAPI backend.
// Every request automatically carries the JWT token saved at login.

const API = "http://localhost:8000";

export function getToken() {
  return localStorage.getItem("drishti_token");
}

export async function api(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${getToken()}`,
      // NOTE: don't set Content-Type for FormData (browser sets it + boundary)
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
    },
    body: options.body instanceof FormData ? options.body : JSON.stringify(options.body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

export const API_BASE = API;

// Great-circle distance between two GPS points (km) — used to show
// "X km away" on inspector task cards.
export function haversineKm(lat1, lng1, lat2, lng2) {
  const r = 6371, toRad = (d) => (d * Math.PI) / 180;
  const p1 = toRad(lat1), p2 = toRad(lat2);
  const dp = toRad(lat2 - lat1), dl = toRad(lng2 - lng1);
  const a = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * r * Math.asin(Math.sqrt(a));
}
