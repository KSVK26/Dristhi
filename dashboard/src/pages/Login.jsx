// DRISHTI - Login page (JWT auth against the FastAPI backend)

import { useState } from "react";
import Logo from "../components/Logo.jsx";
import { api } from "../api.js";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const data = await api("/login", {
        method: "POST",
        body: { username, password },
      });
      localStorage.setItem("drishti_token", data.token);
      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo"><Logo size={58} /></div>
        <h1>DRISHTI</h1>
        <p className="muted">Smart Real-Time Monitoring & Inspection · DoSJE</p>

        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="error">{error}</p>}
        <button disabled={busy} type="submit">
          {busy ? "Signing in…" : "Sign In"}
        </button>

        <div className="hint">
          <b>Demo accounts</b>
          <span>admin / admin123 — Department official</span>
          <span>ravi / inspector123 — PMU field inspector</span>
        </div>
      </form>
    </div>
  );
}