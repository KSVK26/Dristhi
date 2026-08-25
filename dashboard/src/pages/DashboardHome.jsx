// DRISHTI - Role-aware home page.
//   admin     -> "DoSJE Command Center": stats, quick actions, VC panel, alerts
//   inspector -> "PMU Field Ops": my tasks, Google Maps links, submissions

import { useEffect, useState } from "react";
import { api, haversineKm } from "../api.js";

const CHECKLIST = [
  "Staff physically present?",
  "Beneficiaries visible on site?",
  "Records / registers available?",
  "Scheme activities running today?",
  "Facilities clean & usable?",
];

// Blank template for the admin "➕ Add Institute" form.
const EMPTY_INST = {
  name: "", district: "", scheme: "", lat: "", lng: "",
  contact_person: "", phone: "", generate_attendance: true,
};

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
  const [me, setMe] = useState(null);
  const [msg, setMsg] = useState("");
  const [pickInst, setPickInst] = useState("");
  const [showAddInst, setShowAddInst] = useState(false);
  const [newInst, setNewInst] = useState(EMPTY_INST);
  const setField = (key) => (e) =>
    setNewInst((f) => ({
      ...f,
      [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value,
    }));

  const load = async () => {
    setInstitutes(await api("/institutes").catch(() => []));
    setAlerts(await api("/alerts").catch(() => []));
    setReports(await api("/reports").catch(() => []));
    if (user.role === "inspector") {
      setTasks(await api("/inspections/my").catch(() => []));
      setMe(await api("/me").catch(() => null));
    }
  };
  useEffect(() => { load(); }, [user.role]);

  const highRisk = institutes.filter((i) => i.risk_score >= 70).length;
  const openAlerts = alerts.filter((a) => !a.resolved);
  const vcRooms = alerts
    .filter((a) => a.type === "vc_started")
    .map((a) => ({ ...a, url: a.message.split(" ").find((w) => w.startsWith("https://")) }))
    .slice(0, 4);

  // ---------- inspector derived data ----------
  const myReports = reports.filter((r) =>
    tasks.some((t) => t.inspection_id === r.inspection_id));
  const doneTasks = tasks.filter((t) => t.status === "completed");
  const weekAgo = Date.now() - 7 * 864e5;
  const doneThisWeek = doneTasks.filter(
    (t) => new Date(t.scheduled_at).getTime() > weekAgo).length;
  const withDist = tasks.map((t) => ({
    ...t, km: me ? haversineKm(me.lat, me.lng, t.lat, t.lng) : null }));
  const nextUp = withDist
    .filter((t) => t.status !== "completed")
    .sort((a, b) => (a.km ?? 999) - (b.km ?? 999))[0];

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
  async function addInstitute(e) {
    e.preventDefault();
    const r = await api("/institutes", {
      method: "POST",
      body: { ...newInst, lat: parseFloat(newInst.lat), lng: parseFloat(newInst.lng) },
    }).catch((err) => ({ error: err.message }));
    if (!r || r.error) {
      return setMsg("❌ Could not add institute" + (r?.error ? `: ${r.error}` : ""));
    }
    setMsg(`🏛️ ${r.name} added` +
      (r.attendance_generated ? ` · ${r.attendance_generated} days of attendance seeded` : ""));
    setNewInst(EMPTY_INST);
    setShowAddInst(false);
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
            <button className="btn" onClick={() => setShowAddInst((s) => !s)}>
              ➕ Add Institute
            </button>
          </div>
          {showAddInst && (
            <form className="add-inst" onSubmit={addInstitute}>
              <div className="add-inst-grid">
                <input required placeholder="Institute name *" value={newInst.name} onChange={setField("name")} />
                <input required placeholder="District *" value={newInst.district} onChange={setField("district")} />
                <input required placeholder="DoSJE scheme *" value={newInst.scheme} onChange={setField("scheme")} />
                <input required placeholder="Latitude * e.g. 28.61" inputMode="decimal" value={newInst.lat} onChange={setField("lat")} />
                <input required placeholder="Longitude * e.g. 77.20" inputMode="decimal" value={newInst.lng} onChange={setField("lng")} />
                <input placeholder="Contact person" value={newInst.contact_person} onChange={setField("contact_person")} />
                <input placeholder="Phone" value={newInst.phone} onChange={setField("phone")} />
              </div>
              <div className="add-inst-foot">
                <label>
                  <input type="checkbox" checked={newInst.generate_attendance}
                         onChange={setField("generate_attendance")} />{" "}
                  Generate 30 days of sample attendance (AI scan &amp; charts work instantly)
                </label>
                <button className="btn primary sm" type="submit">Save institute</button>
              </div>
            </form>
          )}
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
          <StatCard icon="⏳" tint="amber" label="Pending tasks"
            value={tasks.filter((t) => t.status !== "completed").length}
            sub="action required" />
          <StatCard icon="✅" tint="green" label="Completed" value={doneTasks.length}
            sub="evidence submitted" />
          <StatCard icon="📅" tint="blue" label="Completed this week" value={doneThisWeek}
            sub="last 7 days" />
          <StatCard icon="⚠️" tint="red" label="Proxy flags on my reports"
            value={myReports.filter((r) => r.ai_flags.length > 0).length}
            sub="re-visit with clear photos to clear them" />
        </div>
      )}

      {/* ---------- inspector: next-up hero + activity ---------- */}
      {user.role === "inspector" && (
        <>
          <div className="card section nextup">
            <h2 className="section-title">🧭 Next up — nearest pending task</h2>
            {!nextUp ? (
              <p className="muted">🎉 Nothing pending — new assignments will appear here.</p>
            ) : (
              <div className="nextup-body">
                <div className="nextup-info">
                  <b>{nextUp.institute_name}
                    {nextUp.is_random && <span className="chip-surprise">SURPRISE</span>}
                  </b>
                  <small>{nextUp.scheme} · {nextUp.district}
                    {nextUp.km != null && <> · 📍 {nextUp.km.toFixed(1)} km away</>}
                  </small>
                  <div className="checklist-preview">
                    {CHECKLIST.map((q) => <span key={q} className="check-q">☑ {q}</span>)}
                  </div>
                </div>
                <div className="task-actions">
                  <a className="btn primary" target="_blank" rel="noreferrer"
                     href={`https://www.google.com/maps?q=${nextUp.lat},${nextUp.lng}`}>
                    🧭 Navigate
                  </a>
                  <button className="btn" onClick={() => go("tasks")}>All tasks →</button>
                </div>
              </div>
            )}
            <div className="banner" style={{ marginTop: 14 }}>
              📱 Evidence capture (camera + GPS + checklist) happens in the <b>DRISHTI field app</b>.
            </div>
          </div>

          <div className="card section">
            <h2 className="section-title">Recent activity</h2>
            {myReports.length === 0 && <p className="muted">No submissions yet.</p>}
            {myReports.slice(0, 3).map((r) => (
              <div key={r.id} className="mini-alert">
                <span className={"sev-dot " + (r.ai_flags.length ? "high" : "low")} />
                <span className="mini-msg">
                  {r.ai_flags.length
                    ? `⚠ Proxy flag at ${r.institute_name}`
                    : `✔ Verified submission at ${r.institute_name}`}
                  <small> · {new Date(r.created_at).toLocaleDateString()}</small>
                </span>
              </div>
            ))}
          </div>
        </>
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

      {/* inspector submission history now lives in Reports ("My submissions only") */}


    </div>
  );
}
