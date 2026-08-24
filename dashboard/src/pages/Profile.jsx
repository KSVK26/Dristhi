// DRISHTI - Profile page: account details + role permissions.

import { useEffect, useState } from "react";
import Logo from "../components/Logo.jsx";
import { api } from "../api.js";

const PERMISSIONS = {
  admin: [
    ["Run AI anomaly scans", true],
    ["Assign random inspections (auditable seed)", true],
    ["Start surprise VC rooms", true],
    ["Resolve alerts (lowers risk score)", true],
    ["View all CCTV feeds & reports", true],
    ["Submit field evidence", false],
  ],
  inspector: [
    ["Receive surprise inspection assignments", true],
    ["Submit geo-tagged photo evidence (field app)", true],
    ["Join surprise VC sessions", true],
    ["View map, CCTV, alerts & reports", true],
    ["Run AI scans / assign inspections", false],
    ["Resolve alerts", false],
  ],
};

export default function Profile({ user }) {
  const [me, setMe] = useState(user);
  const [compliance, setCompliance] = useState(null);

  useEffect(() => {
    api("/me").then(setMe).catch(() => {});
    if (user.role === "inspector") {
      // evidence-quality stats: completed tasks + clean-submission ratio
      Promise.all([api("/inspections/my"), api("/reports")])
        .then(([tasks, reports]) => {
          const myIds = tasks.map((t) => t.inspection_id);
          const mine = reports.filter((r) => myIds.includes(r.inspection_id));
          const done = tasks.filter((t) => t.status === "completed").length;
          const clean = mine.filter((r) => r.ai_flags.length === 0).length;
          setCompliance({
            done,
            submitted: mine.length,
            quality: mine.length ? Math.round((clean / mine.length) * 100) : 100,
          });
        })
        .catch(() => {});
    }
  }, [user.role]);

  const initials = me.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div className="profile-wrap">
      <div className="card profile-card">
        <div className="profile-top">
          <div className="avatar avatar-xl">{initials}</div>
          <div>
            <h1 className="welcome" style={{ fontSize: 26 }}>{me.name}</h1>
            <p className="muted">@{me.username}</p>
            <span className={"role-pill " + me.role}>
              {me.role === "admin" ? "DoSJE Official" : "PMU Field Inspector"}
            </span>
          </div>
        </div>

        <div className="detail-grid">
          <div className="detail"><small>Full name</small><b>{me.name}</b></div>
          <div className="detail"><small>Username</small><b>@{me.username}</b></div>
          <div className="detail"><small>Account ID</small><b>#{me.id}</b></div>
          <div className="detail"><small>Role</small><b>{me.role}</b></div>
          <div className="detail"><small>Organization</small><b>Dept. of Social Justice & Empowerment, MoSJE</b></div>
          <div className="detail"><small>Platform</small><b>DRISHTI v1.0 (SIH 26095)</b></div>
        </div>
      </div>

      {compliance && (
        <div className="card profile-card">
          <h2 className="section-title">📊 Field performance</h2>
          <div className="detail-grid" style={{ borderTop: "none", paddingTop: 0 }}>
            <div className="detail"><small>Inspections completed</small><b>{compliance.done}</b></div>
            <div className="detail"><small>Evidence reports submitted</small><b>{compliance.submitted}</b></div>
            <div className="detail"><small>Evidence quality (no proxy flags)</small><b>{compliance.quality}%</b></div>
          </div>
        </div>
      )}

      <div className="card profile-card">
        <h2 className="section-title">Your permissions</h2>
        <ul className="perm-list">
          {PERMISSIONS[me.role]?.map(([label, allowed]) => (
            <li key={label} className={allowed ? "yes" : "no"}>
              {allowed ? "✅" : "🔒"} {label}
            </li>
          ))}
        </ul>
      </div>

      <div className="card profile-card brand-line">
        <Logo withWordmark size={30} />
      </div>
    </div>
  );
}
