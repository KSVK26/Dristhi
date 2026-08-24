// DRISHTI - Notifications page: full list of my unread notifications.

import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function NotificationsPage() {
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(false);

  const load = () => api("/notifications").then(setItems).catch(() => {});
  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  async function markOne(id) {
    await api(`/notifications/${id}/read`, { method: "POST" }).catch(() => {});
    load();
  }
  async function markAll() {
    setBusy(true);
    await api("/notifications/read-all", { method: "POST" }).catch(() => {});
    setBusy(false);
    load();
  }

  return (
    <div className="notif-page">
      <div className="toolbar">
        <h2 className="section-title">🔔 Notifications</h2>
        <button className="btn sm" disabled={busy || items.length === 0} onClick={markAll}>
          Mark all read
        </button>
      </div>
      <p className="muted">Auto-refreshes every 15 s · {items.length} unread</p>

      {items.length === 0 && (
        <div className="card section"><p className="muted">🎉 All caught up — no unread notifications.</p></div>
      )}
      {items.map((n) => (
        <div key={n.id} className={`alert-card sev-${n.severity}`}>
          <div className="alert-head">
            <span className={`sev-tag ${n.severity}`}>{n.severity.toUpperCase()}</span>
            <b>{n.type.replace(/_/g, " ")}</b>
            <small>{new Date(n.created_at).toLocaleString()}</small>
          </div>
          <p>{n.message}</p>
          <button className="btn sm" onClick={() => markOne(n.id)}>Mark read</button>
        </div>
      ))}
    </div>
  );
}
