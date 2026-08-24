// DRISHTI - Live Alerts Panel
// Polls the backend every 10 seconds so new AI alerts appear automatically.
// Admin can resolve an alert, which also lowers the institute's risk score.

import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState("all");

  async function load() {
    try {
      setAlerts(await api("/alerts"));
    } catch (e) { console.error(e); }
  }

  // poll every 10s
  useEffect(() => {
    load();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, []);

  async function resolve(id) {
    await api(`/alerts/${id}/resolve`, { method: "POST" });
    load();
  }

  const shown = alerts.filter((a) =>
    filter === "all" ? true : filter === "open" ? !a.resolved : a.resolved
  );

  return (
    <div>
      <div className="toolbar">
        <h2>🚨 AI Alerts & Events</h2>
        <div className="filters">
          {["all", "open", "resolved"].map((f) => (
            <button key={f}
              className={"chip" + (filter === f ? " active" : "")}
              onClick={() => setFilter(f)}>
              {f}
            </button>
          ))}
          <span className="muted">auto-refreshes every 10s</span>
        </div>
      </div>

      <div className="alert-list">
        {shown.length === 0 && <p className="muted">No alerts in this view.</p>}
        {shown.map((a) => (
          <div key={a.id} className={`alert-card sev-${a.severity} ${a.resolved ? "resolved" : ""}`}>
            <div className="alert-head">
              <span className={`sev-tag ${a.severity}`}>{a.severity.toUpperCase()}</span>
              <b>{a.type.replace(/_/g, " ")}</b>
              <small>{new Date(a.created_at).toLocaleString()}</small>
            </div>
            <p>{a.message}</p>
            {!a.resolved && (
              <button onClick={() => resolve(a.id)}>✔ Mark Resolved</button>
            )}
            {a.resolved && <span className="muted">✔ Resolved</span>}
          </div>
        ))}
      </div>
    </div>
  );
}