// DRISHTI - MoSJE Oversight Dashboard (role-aware)
//   admin     -> Command Center (AI scans, assignments, VCs, alerts)
//   inspector -> Field Ops view (tasks, submissions; read-only elsewhere)
//   ngo/institute -> not in scope for the prototype (login still works)

import { useState } from "react";
import Login from "./pages/Login.jsx";
import Layout from "./components/Layout.jsx";
import DashboardHome from "./pages/DashboardHome.jsx";
import MapView from "./pages/MapView.jsx";
import CctvGrid from "./pages/CctvGrid.jsx";
import Alerts from "./pages/Alerts.jsx";
import Reports from "./pages/Reports.jsx";
import NotificationsPage from "./pages/NotificationsPage.jsx";
import Profile from "./pages/Profile.jsx";

// Sidebar navigation per role
const NAV = {
  admin: [
    { id: "home", label: "Dashboard", icon: "▦" },
    { id: "map", label: "Live Map", icon: "◉" },
    { id: "cctv", label: "CCTV Feeds", icon: "📹" },
    { id: "alerts", label: "Alerts", icon: "🚨" },
    { id: "reports", label: "Reports", icon: "📋" },
    { id: "notifs", label: "Notifications", icon: "🔔" },
    { id: "profile", label: "Profile", icon: "👤" },
  ],
  inspector: [
    { id: "home", label: "My Dashboard", icon: "▦" },
    { id: "map", label: "Live Map", icon: "◉" },
    { id: "cctv", label: "CCTV Feeds", icon: "📹" },
    { id: "alerts", label: "Alerts", icon: "🚨" },
    { id: "reports", label: "Reports", icon: "📋" },
    { id: "notifs", label: "Notifications", icon: "🔔" },
    { id: "profile", label: "Profile", icon: "👤" },
  ],
};

export default function App() {
  const [user, setUser] = useState(null); // {name, role, username, token}
  const [tab, setTab] = useState("home");

  if (!user) return <Login onLogin={setUser} />;

  return (
    <Layout user={user} nav={NAV[user.role] || NAV.inspector}
            tab={tab} setTab={setTab} onLogout={() => setUser(null)}>
      {tab === "home" && <DashboardHome user={user} go={setTab} />}
      {tab === "map" && <MapView user={user} />}
      {tab === "cctv" && <CctvGrid />}
      {tab === "alerts" && <Alerts user={user} />}
      {tab === "reports" && <Reports />}
      {tab === "notifs" && <NotificationsPage />}
      {tab === "profile" && <Profile user={user} />}
    </Layout>
  );
}
