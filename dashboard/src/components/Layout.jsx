// DRISHTI - app shell: left sidebar + top bar + content area.
// Sidebar mirrors the modern admin template; topbar has breadcrumbs,
// date, notification bell (with unread badge + dropdown) and user avatar.

import { useEffect, useRef, useState } from "react";
import Logo from "./Logo.jsx";
import { api } from "../api.js";

function Bell() {
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const load = () => api("/notifications").then(setItems).catch(() => {});
  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  // close dropdown when clicking outside
  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  async function markAll() {
    await api("/notifications/read-all", { method: "POST" }).catch(() => {});
    load();
  }

  const hasHigh = items.some((n) => n.severity === "high");

  return (
    <div className="bell-wrap" ref={ref}>
      <button className={"bell" + (hasHigh ? " pulse" : "")}
              onClick={() => setOpen(!open)} title="Notifications">
        🔔
        {items.length > 0 && <span className="bell-badge">{items.length}</span>}
      </button>
      {open && (
        <div className="bell-panel">
          <div className="bell-head">
            <b>Notifications</b>
            <button className="btn sm" disabled={!items.length} onClick={markAll}>Mark all read</button>
          </div>
          {items.length === 0 && <p className="muted bell-empty">🎉 All caught up!</p>}
          {items.slice(0, 8).map((n) => (
            <div key={n.id} className={"bell-item sev-" + n.severity}>
              <span className={"sev-dot " + n.severity} />
              <div>
                <div className="bell-msg">{n.message}</div>
                <small>{new Date(n.created_at).toLocaleString()}</small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Layout({ user, nav, tab, setTab, onLogout, children }) {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });
  const active = nav.find((n) => n.id === tab);
  const initials = user.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div className="shell">
      {/* ---------------- sidebar ---------------- */}
      <aside className="sidebar">
        <div className="side-brand">
          <Logo withWordmark />
        </div>

        <div className="side-role">
          <span className={"role-pill " + user.role}>
            {user.role === "admin" ? "👑 DoSJE Official" : "🧭 PMU Field Team"}
          </span>
        </div>

        <nav className="side-nav">
          {nav.map((n) => (
            <button key={n.id}
              className={"nav-item" + (tab === n.id ? " active" : "")}
              onClick={() => setTab(n.id)}>
              <span className="nav-ico">{n.icon}</span>{n.label}
              {n.badge && <span className="nav-badge">{n.badge}</span>}
            </button>
          ))}
        </nav>

        <div className="side-user">
          <div className="avatar">{initials}</div>
          <div className="side-user-meta">
            <b>{user.name}</b>
            <small>{user.role === "admin" ? "Department Official" : "Field Inspector"}</small>
          </div>
          <button className="logout" title="Logout" onClick={onLogout}>⏻</button>
        </div>
      </aside>

      {/* ---------------- main ---------------- */}
      <div className="main-col">
        <header className="topbar">
          <div className="crumbs">
            <span>drishti</span>
            <span className="crumb-sep">›</span>
            <b>{active ? active.label : "Dashboard"}</b>
          </div>
          <div className="top-right">
            <span className="top-date">{today}</span>
            <Bell />
            <div className="avatar avatar-sm">{initials}</div>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
