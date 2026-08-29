# DRISHTI Plan v5

> Changelog of everything that changed since planv4.
> Generated as part of the QA/security pass (2026-08-29, commits
> `c52eaaa` and `a502cfd`).

---

## 1. What changed since planv4

### 1.2 Explainable risk scores

- Refactored `ai_engine.py`: `risk_factors(db, institute) -> (score, factors)` is the new single source of truth; `compute_risk_score` derives from it. Same numbers, more explainable.
- New endpoint: `GET /institutes/{id}/risk-breakdown` returns:
  ```json
  {
    "institute_id": 1, "name": "Samarth …", "score": 30,
    "factors": [
      {"icon":"🚨","reason":"3 unresolved alert(s)","points":30,"detail":"proxy_suspect ×1 · …"}
    ],
    "hint": "Resolve the open alerts … to lower this score."
  }
  ```
- The endpoint also **recomputes and persists** the score so the returned
  number always matches `institutes.risk_score` (no drift).
- UI: a yellow "Why this score?" box renders under the risk badge in the
  Live Map side panel, with per-factor `+points` and a remediation hint.
- Tests: added step 3b to `test_api.py` (asserts breakdown score equals
  stored risk_score).

Commit `3024972`.

### 1.3 Google Maps link → lat/lng parser

- New `dashboard/src/utils/mapsLink.js` (pure JS, no API key) handles 6 link
  shapes: `?q=lat,lng`, `@lat,lng,zoom`, `?ll=lat,lng`, `!3dLAT!4dLNG`,
  bare `"lat, lng"`, and short-link detection.
- New backend endpoint `POST /utils/expand-maps-link` (admin-only) does
  a HEAD request with `HTTPRedirectHandler` to expand short links.
- Dashboard ➕ Add Institute form: new "📍 Paste a Google Maps link" row
  at the top with an "Extract coordinates" button that auto-fills lat/lng.

Commit `6c0ffe3`.

### 1.4 B16 live sync (Flutter)

- `tasks_screen.dart`: a 20-second `Timer.periodic` in `initState` calls
  `_load()` so newly assigned inspections show up in the inspector's
  task list without a manual refresh. `dispose()` cancels the timer.

Commit `6c0ffe3`.

### 1.5 Self-hosted CCTV with surveillance overlay

- Replaced external HLS test streams with 3 self-hosted mp4 loops in
  `dashboard/public/cctv/` (committed to repo so they can never die
  mid-demo):
  - `cam1-classroom.mp4` — students in a real classroom
  - `cam2-hallway.mp4` — hall/people walking
  - `cam3-corridor.mp4` — corridor
- `CctvGrid.jsx` rewrite: detects relative URL → renders plain
  `<video loop autoplay muted controls>` (no HLS); keeps DroidCam tile
  for a real phone feed.
- Surveillance overlay (CSS, no extra deps):
  - Pulsing red `● REC` dot in the top-left of every live tile
  - Live ticking `HH:MM:SS` clock next to it
  - `CAM 0X · <label>` tag in the bottom-left
  - Subtle scanlines + vignette over the whole tile for that "actual
    security-camera" feel
- DroidCam tile kept as camera #4 — for the live phone-feed wow moment

Commit `c986d2a`.

### 1.6 Deployment architecture (as built on Render)

```
GitHub (KSVK26/Dristhi)
   │
   │  auto-deploy on push to main
   │
   ├─→ Render "DRISHTI Dashboard"   (static, npm run build)
   │     env: VITE_API_URL = https://drishti-api-u0qf.onrender.com
   │     URL: https://drishti-dashboard.onrender.com
   │
   ├─→ Render "DRISHTI Backend"      (web service, uvicorn main:app)
   │     env: DATABASE_URL = postgresql://…pooler…@aws-0-ap-south-1…
   │     URL: https://drishti-api-u0qf.onrender.com
   │     Schema self-heals on every boot (`_ensure_schema_columns`).
   │
   └─→ Render "DRISHTI Field App"   (static, mobile/web_app/)
        env: (none, baked in via --dart-define at build time)
        URL: https://drishti-field-app.onrender.com
```

Database is Supabase (PostgreSQL) accessed via the session pooler
(`pooler.supabase.com:6543`, TLS required).

### 1.7 Security hardening v0.2.0

See `docs/SECURITY.md` for the full reference. Commit `c52eaaa` added:

- **JWT expiry + role-aware TTLs** (admin 8h, inspector 24h, institute 12h)
- **POST /auth/refresh** with grace window (1h post-expiry)
- **Login rate-limit**: 5 attempts/min per username, 60s lockout
- **Env-driven `JWT_SECRET`** (random fallback if unset)
- **Server-side MIME sniff** on photo upload (JPEG/PNG/WebP only) + 5 MB cap
- **Extension from MIME**, never from client filename
- **Photo integrity** (client-side SHA-256 form-field, re-hashed on
  server; mismatch → 400) — optional, server is source of truth
- **3 new Report columns**: `photo_sha256`, `captured_at`, `device_id`
- **5 HTTP security headers** (HSTS, X-Frame-Options DENY,
  X-Content-Type-Options nosniff, Referrer-Policy, CSP)
- **Env-driven CORS allowlist** (`CORS_ORIGINS`)

Verified live:
```
curl -I https://drishti-api-u0qf.onrender.com/
→ HTTP 200
→ Strict-Transport-Security: max-age=63072000; includeSubDomains
→ X-Frame-Options: DENY
→ X-Content-Type-Options: nosniff
→ Referrer-Policy: no-referrer
→ Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
```

### 1.8 Field-app server-URL fix

- `main.dart`: the `server_url` override from `SharedPreferences` is
  now only restored when `kIsWeb == false`. On web, the baked-in
  `kHostedApiBase` (from `--dart-define=DRISHTI_API=…`) is the
  single source of truth — a stale `localhost:8000` from a previous
  local test can never break the deployed app.
- New "↻ Reset to default" link under the Server address field
  wipes any persisted override (useful on physical phones).
- 5-stage documentation update: `MOBILE_TESTING_GUIDE.md` and
  `README.md` now show the two-build workflow.

Commit `c986d2a`.

---

## 2. What's NOT documented here (lives in its own file)

| Topic | File |
|---|---|
| Full security model + pen-test checklist | `docs/SECURITY.md`, `docs/SECURITY_QA.md` |
| 5-minute demo flow + talking points | `docs/DEMO_GUIDE.md` |
| Pre-deployment architecture | `docs/DEPLOYMENT_PLAN.md`, `docs/COMPLETE_EXPLANATION.md` |
| Iteration history (v1–v4) | `docs/planv1.md` → `docs/planv4.md` |

## 3. Two-build field-app workflow (the gotcha)

The Flutter field app builds **differently** depending on where it'll run.

| Where | Command | Resulting `kApiBase` |
|---|---|---|
| Local browser (`http://localhost:5174`) | `flutter build web --release` | `http://localhost:8000` |
| Physical phone (same WiFi) | `flutter build web --dart-define=DRISHTI_API=http://YOUR_PC_IP:8000` | baked-in URL |
| Hosted (Render, Netlify) | `flutter build web --release --dart-define=DRISHTI_API=https://drishti-api-u0qf.onrender.com` | `https://…u0qf…` |

Deploy to Render: copy the `build/web/` output to `mobile/web_app/`,
commit, push — the static-site Render service picks it up.

## 4. Known roadmap (not blockers)

- 2FA / TOTP for admin login
- Immutable audit log at the DB level (Postgres `REVOKE DELETE ON alerts`)
- Row-level security on Supabase
- Real CCTV encryption (today: self-hosted test loops; production: signed-HLS)
- Photo EXIF stripping before AI
- External SIEM stream (Wazuh / Splunk)
