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