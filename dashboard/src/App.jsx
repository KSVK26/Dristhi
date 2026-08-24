// DRISHTI - MoSJE Oversight & Web Dashboard
// Simple state-based navigation (no router needed for a prototype):
//   not logged in  -> <Login />
//   logged in      -> tabs: Live Map | CCTV | Alerts | Reports

import { useState } from "react";
import Login from "./pages/Login.jsx";
import MapView from "./pages/MapView.jsx";
import CctvGrid from "./pages/CctvGrid.jsx";
import Alerts from "./pages/Alerts.jsx";
import Reports from "./pages/Reports.jsx";

const TABS = [
  { id: "map", label: "🗺️ Live Map" },
  { id: "cctv", label: "📹 CCTV Feeds" },
  { id: "alerts", label: "🚨 Alerts" },
  { id: "reports", label: "📋 Reports" },
];

export default function App() {
  const [user, setUser] = useState(null); // {name, role, token}
  const [tab, setTab] = useState("map");

  if (!user) return <Login onLogin={setUser} />;

  return (
    <div className="app">
      {/* ---------- top bar ---------- */}
      <header className="topbar">
        <div className="brand">
          <span className="logo">👁️</span>
          <div>
            <h1>DRISHTI</h1>
            <small>MoSJE Oversight & Monitoring Dashboard</small>
          </div>
        </div>
        <nav>
          {TABS.map((t) => (
            <button
              key={t.id}
              className={"tab" + (tab === t.id ? " active" : "")}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
        <div className="userbox">
          <span>{user.name}</span>
          <small>{user.role}</small>
          <button onClick={() => setUser(null)}>Logout</button>
        </div>
      </header>

      {/* ---------- active page ---------- */}
      <main>
        {tab === "map" && <MapView user={user} />}
        {tab === "cctv" && <CctvGrid />}
        {tab === "alerts" && <Alerts />}
        {tab === "reports" && <Reports />}
      </main>
    </div>
  );
}