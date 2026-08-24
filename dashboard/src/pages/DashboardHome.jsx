// DRISHTI - Role-aware home page.
//   admin     -> "DoSJE Command Center": stats, quick actions, VC panel, alerts
//   inspector -> "PMU Field Ops": my tasks, Google Maps links, submissions

import { useEffect, useState } from "react";
import { api } from "../api.js";

const CHECKLIST = [
  "Staff physically present?",
  "Beneficiaries visible on site?",
  "Records / registers available?",
  "Scheme activities running today?",
  "Facilities clean & usable?",
];

function StatCard({ icon, tint, label, value, sub }) {
  return (
    <div className="stat-card">
      <div className="stat-head">
        <span className={"stat-ico " + tint}>{icon}</span>
        <span className="stat-label">{label}</span>
      </div>
      <div className="stat-value">{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

export default function DashboardHome({ user, go }) {
  const [institutes, setInstitutes] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [reports, setReports] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [msg, setMsg] = useState("");
  const [pickInst, setPickInst] = useState("");

  const load = async () => {
    setInstitutes(await api("/institutes").catch(() => []));
    setAlerts(await api("/alerts").catch(() => []));
    setReports(await api("/reports").catch(() => []));
    if (user.role === "inspector") {
      setTasks(await api("/inspections/my").catch(() => []));
    }
  };
  useEffect(() => { load(); }, [user.role]);

  const highRisk = institutes.filter((i) => i.risk_score >= 70).length;
  const openAlerts = alerts.filter((a) => !a.resolved);
  const vcRooms = alerts
    .filter((a) => a.type === "vc_started")
    .map((a) => ({ ...a, url: a.message.match(/https:\S+)/)?.[0] }))
    .slice(0, 4);

  // ---------- admin quick actions ----------
  async function runScan() {
    setMsg("🤖 Running IsolationForest scan…");
    const r = await api("/analytics/run-anomaly", { method: "POST" })
      .catch(() => ({ flagged_count: 0, flagged: [] }));
    setMsg(r.flagged_count
      ? `🤖 AI flagged: ${r.flagged.map((f) => f.institute).join(", ")}`
      : "🤖 Scan complete — no anomalies found.");
    load();
  }
  async function assign() {
    if (!pickInst) return setMsg("⚠ Pick an institute first.");
    const r = await api("/inspections/assign-random",
      { method: "POST", body: { institute_id: Number(pickInst) } }).catch(() => null);
    setMsg(r ? `🎯 Assigned to ${r.assigned_to} (${r.distance_km} km) · audit seed ${r.assignment_seed}` : "❌ Assignment failed");
    load();
  }
  async function startVC() {
    if (!pickInst) return setMsg("⚠ Pick an institute first.");
    const r = await api("/vc/start",
      { method: "POST", body: { institute_id: Number(pickInst) } }).catch(() => null);
    setMsg(r ? `📞 VC room ready: ${r.url}` : "❌ Could not start VC");
    load();
  }

  const dateLine = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  }).toUpperCase();

  return (
    <div>
      <p className="eyebrow">{dateLine}</p>
      <h1 className="welcome">
        Welcome back, <span className="accent">{user.name.split(" ")[0]}</span>
      </h1>
      <p className="muted">
        {user.role === "admin"
          ? "Live oversight of every institute running under DoSJE schemes."
          : "Your inspection assignments and field submission history."}
      </p>
      {/* ---------- admin: quick actions ---------- */}
      {user.role === "admin" && (
        <div className="quick-actions card">
          <div className="qa-row">
            <button className="btn primary" onClick={runScan}>🤖 Run AI Anomaly Scan</button>
            <select value={pickInst} onChange={(e) => setPickInst(e.target.value)}>
              <option value="">— pick institute —</option>
              {institutes.map((i) => (
                <option key={i.id} value={i.id}>{i.name}</option>
              ))}
            </select>
            <button className="btn" onClick={assign}>🎯 Assign Inspection</button>
            <button className="btn" onClick={startVC}>📞 Start Surprise VC</button>
          </div>
          {msg && <div className="qa-msg">{msg}</div>}
        </div>
      )}

      {/* ---------- stat cards ---------- */}
      {user.role === "admin" ? (
        <div className="stat-grid">
          <StatCard icon="🏛️" tint="blue" label="Institutes monitored" value={institutes.length} sub="across all DoSJE schemes" />
          <StatCard icon="🚨" tint="red" label="High-risk institutes" value={highRisk} sub={highRisk ? "needs immediate oversight" : "all within limits"} />
          <StatCard icon="🔔" tint="amber" label="Open alerts" value={openAlerts.length} sub="awaiting resolution" />
          <StatCard icon="📋" tint="green" label="Evidence reports" value={reports.length} sub="geo-tagged submissions" />
        </div>
      ) : (
        <div className="stat-grid">
          <StatCard icon="🗂️" tint="blue" label="Tasks assigned" value={tasks.length} sub="lifetime assignments" />
          <StatCard icon="✅" tint="green" label="Completed" value={tasks.filter((t) => t.status === "completed").length} sub="evidence submitted" />
          <StatCard icon="⏳" tint="amber" label="Pending" value={tasks.filter((t) => t.status !== "completed").length} sub="action required" />
          <StatCard icon="⚠️" tint="red" label="Proxy flags on my reports"
            value={reports.filter((r) => tasks.some((t) => t.inspection_id === r.inspection_id) && r.ai_flags.length > 0).length}
            sub="re-visit with clear photos to clear them" />
        </div>
      )}

      {/* ---------- inspector: task cards ---------- */}
      {user.role === "inspector" && (
        <div className="card section">
          <h2 className="section-title">My Tasks</h2>
          <div className="banner">
            📱 Evidence capture (camera + GPS + checklist) happens in the <b>DRISHTI field app</b>.
            This dashboard mirrors your assignments.
          </div>
          {tasks.length === 0 && <p className="muted">No assignments yet — you'll be notified here and in the field app.</p>}
          {tasks.map((t) => {
            const done = t.status === "completed";
            return (
              <div key={t.inspection_id} className="task-row">
                <div className="task-info">
                  <b>{t.institute_name}</b>
                  <small>{t.scheme} · {t.district} {t.is_random && <span className="chip-surprise">SURPRISE</span>}</small>
                  <div className="checklist-preview">
                    {CHECKLIST.map((q) => <span key={q} className="check-q">☑ {q}</span>)}
                  </div>
                </div>
                <div className="task-actions">
                  <a className="btn sm" target="_blank" rel="noreferrer"
                     href={`https://www.google.com/maps?q=${t.lat},${t.lng}`}>
                    🧭 Navigate
                  </a>
                  <span className={"chip-status " + (done ? "ok" : "wait")}>
                    {done ? "✔ Completed" : "⏳ Pending"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ---------- admin: VC panel + recent alerts ---------- */}
      {user.role === "admin" && (
        <div className="two-col">
          <div className="card section">
            <h2 className="section-title">📞 Surprise VC Rooms</h2>
            {vcRooms.length === 0 && <p className="muted">No VC sessions yet — start one above.</p>}
            {vcRooms.map((v) => (
              <div key={v.id} className="vc-row">
                <span className="live-dot" />
                <span className="vc-text">{v.message.split(": ").slice(1).join(": ")}</span>
                {v.url && <a className="btn sm primary" href={v.url} target="_blank" rel="noreferrer">Join</a>}
              </div>
            ))}
          </div>
          <div className="card section">
            <h2 className="section-title">Recent Alerts</h2>
            {alerts.slice(0, 6).map((a) => (
              <div key={a.id} className={"mini-alert sev-" + a.severity + (a.resolved ? " done" : "")}>
                <span className={"sev-dot " + a.severity} />
                <span className="mini-msg">{a.message}</span>
              </div>
            ))}
            <button className="btn sm" onClick={() => go("alerts")}>View all →</button>
          </div>
        </div>
      )}

      {/* ---------- inspector: my submissions ---------- */}
      {user.role === "inspector" && (
        <div className="card section">
          <h2 className="section-title">My Submissions</h2>
          {reports.filter((r) => tasks.some((t) => t.inspection_id === r.inspection_id)).length === 0 && (
            <p className="muted">Nothing submitted yet.</p>
          )}
          {reports
            .filter((r) => tasks.some((t) => t.inspection_id === r.inspection_id))
            .map((r) => (
              <div key={r.id} className="task-row">
                <div className="task-info">
                  <b>{r.institute_name}</b>
                  <small>{new Date(r.created_at).toLocaleString()} · 📍 {r.geo_lat.toFixed(3)}, {r.geo_lng.toFixed(3)}</small>
                </div>
                {r.ai_flags.length === 0
                  ? <span className="chip-status ok">✔ AI verified</span>
                  : r.ai_flags.map((f) => <span key={f} className="chip-status bad">⚠ {f.replace(/_/g, " ")}</span>)}
              </div>
            ))}
        </div>
      )}


    </div>
  );
}
