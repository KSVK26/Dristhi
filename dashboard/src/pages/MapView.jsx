// DRISHTI - Live Monitoring Map
// Leaflet + OpenStreetMap (free, no API key).
// - Pins are colour-coded by AI risk score: green <40, amber <70, red >=70
// - Click a pin -> side panel with attendance chart + action buttons:
//     "Assign Random Inspection"  (seeded RNG on the backend)
//     "Start Surprise VC"         (Jitsi room)

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { api } from "../api.js";
import "leaflet/dist/leaflet.css";

function riskColor(score) {
  if (score >= 70) return "#e53935"; // red
  if (score >= 40) return "#fb8c00"; // amber
  return "#43a047";                  // green
}

export default function MapView({ user }) {
  const [institutes, setInstitutes] = useState([]);
  const [selected, setSelected] = useState(null);   // clicked institute
  const [attendance, setAttendance] = useState([]); // its 30-day series
  const [message, setMessage] = useState("");
  const [fDistrict, setFDistrict] = useState("All");
  const [fScheme, setFScheme] = useState("All");
  const [myTasks, setMyTasks] = useState([]);       // inspector: own assignments

  async function load() {
    setInstitutes(await api("/institutes"));
  }
  useEffect(() => {
    load();
    if (user.role === "inspector") {
      api("/inspections/my").then(setMyTasks).catch(() => {});
    }
  }, []);

  const districts = ["All", ...new Set(institutes.map((i) => i.district))];
  const schemes = ["All", ...new Set(institutes.map((i) => i.scheme))];
  const visible = institutes.filter(
    (i) => (fDistrict === "All" || i.district === fDistrict) &&
           (fScheme === "All" || i.scheme === fScheme)
  );

  async function openInstitute(inst) {
    setSelected(inst);
    setAttendance(await api(`/attendance/analytics/${inst.id}`));
  }

  async function assignRandom() {
    try {
      const r = await api("/inspections/assign-random", {
        method: "POST",
        body: { institute_id: selected.id },
      });
      setMessage(
        `✅ Surprise inspection assigned to ${r.assigned_to} ` +
        `(${r.distance_km} km away). Audit seed: ${r.assignment_seed}`
      );
      load(); // refresh risk colours
    } catch (e) { setMessage("❌ " + e.message); }
  }

  async function startVC() {
    try {
      const r = await api("/vc/start", {
        method: "POST",
        body: { institute_id: selected.id },
      });
      setMessage(`📞 Surprise VC room ready: ${r.url}`);
    } catch (e) { setMessage("❌ " + e.message); }
  }

  async function runAI() {
    try {
      const r = await api("/analytics/run-anomaly", { method: "POST" });
      setMessage(r.flagged_count
        ? `🤖 AI flagged ${r.flagged_count} institute(s): ` +
          r.flagged.map((f) => f.institute).join(", ")
        : "🤖 AI scan complete — no anomalies found.");
      load();
    } catch (e) { setMessage("❌ " + e.message); }
  }

  return (
    <div className="map-layout">
      {/* ---------------- map ---------------- */}
      <div className="map-side">
        <div className="toolbar">
          <button className="btn primary" onClick={runAI}>🤖 Run AI Anomaly Scan</button>
          <div className="map-filters">
            <select value={fDistrict} onChange={(e) => setFDistrict(e.target.value)}>
              {districts.map((d) => <option key={d}>{d === "All" ? "All districts" : d}</option>)}
            </select>
            <select value={fScheme} onChange={(e) => setFScheme(e.target.value)}>
              {schemes.map((s) => <option key={s}>{s === "All" ? "All schemes" : s}</option>)}
            </select>
          </div>
          <span className="muted">
            {visible.length} of {institutes.length} institutes
          </span>
        </div>
        <MapContainer center={[28.62, 77.1]} zoom={10} className="leaflet-map">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                     attribution="© OpenStreetMap" />
          {visible.map((i) => (
            <CircleMarker key={i.id}
              center={[i.lat, i.lng]} radius={14}
              pathOptions={{ color: riskColor(i.risk_score), fillColor: riskColor(i.risk_score), fillOpacity: 0.75 }}
              eventHandlers={{ click: () => openInstitute(i) }}>
              <Popup>{i.name}<br />Risk score: {i.risk_score}</Popup>
            </CircleMarker>
          ))}
        </MapContainer>
        {message && <div className="toast">{message}</div>}
      </div>

      {/* ---------------- side panel ---------------- */}
      <aside className="panel">
        {!selected ? (
          <p className="muted">👈 Click any pin to inspect an institute.</p>
        ) : (
          <>
            <h2>{selected.name}</h2>
            <p className="muted">{selected.scheme} · {selected.district}</p>
            <p>Contact: {selected.contact_person} · {selected.phone}</p>

            <div className={"risk-badge " +
                (selected.risk_score >= 70 ? "high" : selected.risk_score >= 40 ? "mid" : "low")}>
              Risk Score: {selected.risk_score}/100
            </div>

            {/* ---------- inspector context for this institute ---------- */}
            {user.role === "inspector" && (() => {
              const mine = myTasks.filter((t) => t.institute_id === selected.id);
              const open = mine.find((t) => t.status !== "completed");
              const done = [...mine].reverse().find((t) => t.status === "completed");
              return (
                <>
                  {open && (
                    <div className="banner">
                      🗂️ You have a {open.status === "in_progress" ? "task in progress" : "task assigned"} here
                      {open.is_random && " (SURPRISE)"}
                    </div>
                  )}
                  {!open && done && (
                    <div className="banner ok-banner">
                      ✔ You inspected this on {new Date(done.scheduled_at).toLocaleDateString()}
                    </div>
                  )}
                  <div className="actions">
                    <a className="btn primary" target="_blank" rel="noreferrer"
                       href={`https://www.google.com/maps?q=${selected.lat},${selected.lng}`}>
                      🧭 Navigate
                    </a>
                  </div>
                </>
              );
            })()}

            <h3>30-Day Attendance (AI-monitored)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={attendance}>
                <XAxis dataKey="date" tick={{ fontSize: 9 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="expected" stroke="#888" dot={false} name="Expected" />
                <Line type="monotone" dataKey="present" stroke="#1976d2" dot={false} name="Present" />
              </LineChart>
            </ResponsiveContainer>

            {user.role === "admin" && (
              <div className="actions">
                <button className="btn primary" onClick={assignRandom}>
                  🎯 Assign Random Inspection
                </button>
                <button className="btn" onClick={startVC}>📞 Start Surprise VC</button>
              </div>
            )}
          </>
        )}
      </aside>
    </div>
  );
}