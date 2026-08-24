// DRISHTI - Inspector "My Tasks" workspace.
// Filter chips (All / Pending / Completed / Surprise), distance per task,
// start-inspection flow, Google Maps navigation, offline hint banner.

import { useEffect, useState } from "react";
import { api, haversineKm } from "../api.js";

export default function TasksPage({ user, onChanged }) {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState("all");
  const [me, setMe] = useState(null);
  const [busy, setBusy] = useState(null);

  const load = async () => {
    setTasks(await api("/inspections/my").catch(() => []));
  };
  useEffect(() => {
    load();
    api("/me").then(setMe).catch(() => {});
  }, []);

  async function startTask(id) {
    setBusy(id);
    await api(`/inspections/${id}/start`, { method: "POST" }).catch(() => {});
    setBusy(null);
    load();
    onChanged?.();
  }

  const withDist = tasks.map((t) => ({
    ...t,
    km: me ? haversineKm(me.lat, me.lng, t.lat, t.lng) : null,
  }));
  const shown = withDist
    .filter((t) =>
      filter === "all" ? true :
      filter === "pending" ? t.status === "assigned" :
      filter === "progress" ? t.status === "in_progress" :
      filter === "completed" ? t.status === "completed" :
      filter === "surprise" ? t.is_random : true)
    .sort((a, b) => (a.km ?? 999) - (b.km ?? 999));

  const chips = ["all", "pending", "progress", "completed", "surprise"];

  return (
    <div>
      <div className="toolbar">
        <h2 className="section-title">🗂️ My Tasks</h2>
        <div className="filters">
          {chips.map((f) => (
            <button key={f} className={"chip" + (filter === f ? " active" : "")}
                    onClick={() => setFilter(f)}>{f}</button>
          ))}
        </div>
      </div>

      <div className="banner">
        📶 No internet at site? Evidence captures in the <b>DRISHTI field app</b> and
        syncs when you're back online.
      </div>

      {shown.length === 0 && (
        <div className="card section"><p className="muted">No tasks in this view.</p></div>
      )}

      {shown.map((t) => {
        const done = t.status === "completed";
        const progress = t.status === "in_progress";
        return (
          <div key={t.inspection_id} className="card section task-card">
            <div className="task-row" style={{ borderBottom: "none", padding: 0 }}>
              <div className="task-info">
                <b>{t.institute_name}
                  {t.is_random && <span className="chip-surprise">SURPRISE</span>}
                </b>
                <small>{t.scheme} · {t.district}
                  {t.km != null && <> · 📍 {t.km.toFixed(1)} km away</>}
                </small>
              </div>
              <div className="task-actions">
                <a className="btn sm" target="_blank" rel="noreferrer"
                   href={`https://www.google.com/maps?q=${t.lat},${t.lng}`}>🧭 Navigate</a>
                {!done && !progress && (
                  <button className="btn sm primary" disabled={busy === t.inspection_id}
                          onClick={() => startTask(t.inspection_id)}>
                    {busy === t.inspection_id ? "…" : "▶ Start"}
                  </button>
                )}
                <span className={"chip-status " + (done ? "ok" : progress ? "prog" : "wait")}>
                  {done ? "✔ Completed" : progress ? "🔄 In progress" : "⏳ Assigned"}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
