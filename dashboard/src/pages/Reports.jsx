// DRISHTI - Geo-tagged Inspection Reports
// Shows every evidence submission from the field app:
// photo, GPS location, checklist answers and AI flags (e.g. possible_proxy).

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { api, API_BASE } from "../api.js";

export default function Reports({ user }) {
  const [reports, setReports] = useState([]);
  const [openId, setOpenId] = useState(null);
  const [mineOnly, setMineOnly] = useState(false);
  const [myInspectionIds, setMyInspectionIds] = useState([]);
  const [doc, setDoc] = useState(null);          // auto-generated official report

  useEffect(() => {
    api("/reports").then(setReports).catch(console.error);
    if (user?.role === "inspector") {
      api("/inspections/my")
        .then((t) => setMyInspectionIds(t.map((x) => x.inspection_id)))
        .catch(() => {});
    }
  }, []);

  async function loadDocument(id) {
    setDoc(await api(`/reports/${id}/document`).catch(() => null));
  }

  const visible = mineOnly
    ? reports.filter((r) => myInspectionIds.includes(r.inspection_id))
    : reports;

  // Export the report register as CSV (transparency / compliance evidence)
  function exportCSV(list) {
    const rows = [["Report ID", "Institute", "Date", "Latitude", "Longitude", "AI Flags", "Checklist"]];
    list.forEach((r) => {
      rows.push([
        r.id, r.institute_name, new Date(r.created_at).toLocaleString(),
        r.geo_lat.toFixed(6), r.geo_lng.toFixed(6),
        r.ai_flags.join(" | ") || "verified",
        Object.entries(r.checklist).map(([q, a]) => `${q}: ${a}`).join("; "),
      ]);
    });
    const csv = rows.map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
    ).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `drishti_reports_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  }

  return (
    <div>
      <div className="toolbar">
        <h2 className="section-title">📋 Field Inspection Reports</h2>
        <div className="filters">
          {user?.role === "inspector" && (
            <button className={"chip" + (mineOnly ? " active" : "")}
                    onClick={() => setMineOnly(!mineOnly)}>
              my submissions only
            </button>
          )}
          <button className="btn" onClick={() => exportCSV(visible)} disabled={!visible.length}>
            ⬇ Export CSV
          </button>
        </div>
      </div>

      {visible.length === 0 && (
        <p className="muted">
          No reports in this view — submit one from the Flutter field app.
        </p>
      )}

      <div className="report-list">
        {visible.map((r) => (
          <div key={r.id} className="report-card">
            <img
              src={API_BASE + r.photo_url}
              alt="evidence"
              className="report-photo"
              onClick={() => setOpenId(openId === r.id ? null : r.id)}
            />
            <div className="report-body">
              <h3>{r.institute_name}</h3>
              <small>{new Date(r.created_at).toLocaleString()}</small>

              {/* AI flags */}
              <div className="flags">
                {r.ai_flags.length === 0 ? (
                  <span className="flag ok">✔ AI verified</span>
                ) : (
                  r.ai_flags.map((f) => (
                    <span key={f} className="flag bad">⚠ {f.replace(/_/g, " ")}</span>
                  ))
                )}
              </div>

              {/* checklist answers (+ per-answer photo proof) */}
              <ul className="checklist">
                {Object.entries(r.checklist).map(([q, a], i) => (
                  <li key={q}>
                    {a === "yes" || a === true ? "✅" : "❌"} {q}
                    {r.question_photos?.[String(i)] && (
                      <>{" "}
                        <a href={API_BASE + r.question_photos[String(i)]}
                           target="_blank" rel="noreferrer"
                           title="Photo proof for this answer">
                          📷 proof
                        </a>
                      </>
                    )}
                  </li>
                ))}
              </ul>

              <button className="btn sm primary" onClick={() => loadDocument(r.id)}>
                📄 Official Report
              </button>

              {/* mini map of where the photo was taken */}
              {openId === r.id && (
                <MapContainer
                  center={[r.geo_lat, r.geo_lng]} zoom={15}
                  style={{ height: 180, marginTop: 8 }}>
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  <CircleMarker center={[r.geo_lat, r.geo_lng]} radius={10}
                    pathOptions={{ color: "#1976d2", fillOpacity: 0.7 }}>
                    <Popup>Evidence captured here<br />{r.geo_lat.toFixed(5)}, {r.geo_lng.toFixed(5)}</Popup>
                  </CircleMarker>
                </MapContainer>
              )}
              <small className="muted">
                📍 GPS: {r.geo_lat.toFixed(5)}, {r.geo_lng.toFixed(5)} — click photo for map
              </small>
            </div>
          </div>
        ))}
      </div>

      {/* ---------- auto-generated OFFICIAL INSPECTION REPORT ---------- */}
      {doc && (
        <div className="modal-overlay" onClick={() => setDoc(null)}>
          <div className="print-doc" onClick={(e) => e.stopPropagation()}>
            <div className="doc-head">
              <h2>{doc.title}</h2>
              <p>{doc.authority}</p>
            </div>

            <table className="doc-meta">
              <tbody>
                <tr><td>Report ID</td><td><b>#{doc.report_id}</b></td>
                    <td>Inspection ID</td><td>#{doc.inspection_id}</td></tr>
                <tr><td>Institute</td><td colSpan={3}><b>{doc.institute.name}</b></td></tr>
                <tr><td>District / Scheme</td><td colSpan={3}>{doc.institute.district} · {doc.institute.scheme}</td></tr>
                <tr><td>Contact person</td><td>{doc.institute.contact_person || "—"} ({doc.institute.phone || "—"})</td>
                    <td>Risk score now</td><td><b>{doc.risk_score_now}/100</b></td></tr>
                <tr><td>Field inspector</td><td>{doc.inspector.name}</td>
                    <td>Captured at</td><td>{new Date(doc.captured_at).toLocaleString()}</td></tr>
                <tr><td>GPS location</td>
                    <td colSpan={3}>
                      📍 {doc.gps.lat.toFixed(5)}, {doc.gps.lng.toFixed(5)} —{" "}
                      <a href={doc.map_link} target="_blank" rel="noreferrer">open in Google Maps</a>
                    </td></tr>
                {doc.random_assignment && (
                  <tr><td>AI assignment</td>
                      <td colSpan={3}>Audit seed <code>{doc.random_assignment.audit_seed}</code> — replayable &amp; provably fair</td></tr>
                )}
              </tbody>
            </table>

            <img className="doc-mainphoto" src={API_BASE + doc.main_photo_url} alt="main evidence" />

            <h4>Compliance checklist (with per-item photo proof)</h4>
            <table className="doc-checklist">
              <tbody>
                {doc.checklist.map((c, i) => (
                  <tr key={i}>
                    <td className={c.answer === "Yes" ? "yes" : "no"}>{c.answer}</td>
                    <td>{c.question}</td>
                    <td>
                      {c.photo_url
                        ? <a href={API_BASE + c.photo_url} target="_blank" rel="noreferrer">
                            <img src={API_BASE + c.photo_url} alt="proof" style={{ height: 44, borderRadius: 6 }} />
                          </a>
                        : <span className="muted">no photo</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className={"doc-aibox " + (doc.ai_verification.flags.length ? "bad" : "ok")}>
              {doc.ai_verification.summary}
              {doc.ai_verification.flags.length > 0 &&
                ` (${doc.ai_verification.flags.join(", ")})`}
            </div>

            <div className="doc-signs">
              <div>_____________________<br />Field Inspector</div>
              <div>_____________________<br />Oversight Officer, DoSJE</div>
            </div>
            <small className="muted">Auto-generated by DRISHTI on {doc.generated_at}. Document ID: DR-{doc.report_id}-{doc.inspection_id}.</small>

            <div className="doc-actions no-print">
              <button className="btn primary" onClick={() => window.print()}>⬇ Save as PDF / Print</button>
              <button className="btn" onClick={() => setDoc(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}