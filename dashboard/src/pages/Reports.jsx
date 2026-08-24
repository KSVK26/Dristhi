// DRISHTI - Geo-tagged Inspection Reports
// Shows every evidence submission from the field app:
// photo, GPS location, checklist answers and AI flags (e.g. possible_proxy).

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { api, API_BASE } from "../api.js";

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    api("/reports").then(setReports).catch(console.error);
  }, []);

  return (
    <div>
      <div className="toolbar">
        <h2>📋 Field Inspection Reports</h2>
        <span className="muted">geo-tagged evidence with AI verification</span>
      </div>

      {reports.length === 0 && (
        <p className="muted">
          No reports yet — submit one from the Flutter field app.
        </p>
      )}

      <div className="report-list">
        {reports.map((r) => (
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

              {/* checklist answers */}
              <ul className="checklist">
                {Object.entries(r.checklist).map(([q, a]) => (
                  <li key={q}>{a === "yes" ? "✅" : "❌"} {q}</li>
                ))}
              </ul>

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
    </div>
  );
}