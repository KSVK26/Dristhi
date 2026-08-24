# 👁️ drishti — Smart Real-Time Monitoring & Inspection Platform

**SIH 2026 · Problem Statement 26095 · Ministry of Social Justice & Empowerment (DoSJE)**

<p>
  <img src="dashboard/src/components/Logo.jsx" width="0" alt="">
  <i>lotus-eye brand: navy #0E1A2F · blue #2563EB</i>
</p>

A centralized monitoring system with three components:

| Component | Tech | Who uses it |
|---|---|---|
| `backend/` | Python FastAPI + SQLite + scikit-learn + OpenCV | (API for all apps) |
| `dashboard/` | React + Vite + Leaflet + Recharts + hls.js | DoSJE officials **and** PMU inspectors (role-based UI) |
| `mobile/drishti_app/` | Flutter (Android + Web) | PMU / inspection teams in the field |

## ✨ Features (mapped to PS requirements)

- **Live CCTV feed integration** → HLS streams + DroidCam phone-as-IP-camera tile
- **Random VC connectivity** → one-click Jitsi surprise rooms with Incharge/Staff/Beneficiaries
- **Real-time monitoring dashboard** → risk-coloured map pins, district/scheme filters, attendance charts
- **Mobile inspection module** → camera evidence + GPS geo-tagging + checklist
- **AI random inspection assignment** → seeded RNG (auditable fairness) weighted by distance
- **Geo-tagged reports & live evidence** → photo + GPS stored per report
- **AI anomaly & attendance analytics** → IsolationForest flags outlier institutes
- **Proxy detection** → OpenCV face detection on evidence (`possible_proxy` flag)
- **Notifications** → 🔔 bell + page; admins get high-risk/proxy/anomaly alerts,
  inspectors get assignment & VC alerts (15 s polling, mark-read)
- **Risk scoring** → every institute gets a 0–100 score that updates automatically

## 👥 Two role experiences (NGO portal = future scope)

### 👑 Admin — "DoSJE Command Center" (`admin / admin123`)
- 4 live stat cards: Institutes · High-risk · Open alerts · Evidence reports
- **Quick Actions**: 🤖 Run AI Anomaly Scan · 🎯 Assign Random Inspection · 📞 Start Surprise VC
- **Surprise VC panel** with join links · recent alerts feed
- District + Scheme filters on the Live Map · **CSV export** of the report register
- Can resolve alerts (lowers the institute's risk score)

### 🧭 Inspector — "PMU Field Ops" (`ravi / inspector123`)
- Stats: Tasks Assigned · Completed · Pending · proxy flags on own reports
- Task cards with **🧭 Navigate (Google Maps)**, checklist preview, SURPRISE chips
- **My Submissions** history with AI-flag outcomes (✔ verified / ⚠ possible proxy)
- Read-only map/CCTV/alerts/reports (controls show 🔒 hints)
- 🔔 notified instantly when an inspection is assigned or a VC goes live
- Evidence capture happens in the Flutter field app

Both roles get a **Profile page**: avatar, name, @username, account ID,
organization and a per-role permissions checklist.

## 🚀 Run it (3 terminals)

### 1. Backend (port 8000)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
python seed.py                    # creates demo data
python -m uvicorn main:app --reload --port 8000
```
Interactive API docs: http://localhost:8000/docs

### 2. Dashboard (port 5173)
```bash
cd dashboard
npm install
npm run dev
```
Open http://localhost:5173 — login `admin / admin123`

### 3. Flutter field app

**Option A — run in a browser (no Android SDK needed):**
```bash
cd mobile/drishti_app
flutter build web --release
python -m http.server 5174 --directory build/web
```
Open http://localhost:5174 — login `ravi / inspector123`

**Option B — run on Android** (requires Android Studio / SDK):
```bash
flutter run                       # emulator or USB phone
```
- Android emulator: backend URL is already `http://10.0.2.2:8000`
- Physical phone: edit `kApiBase` in `lib/main.dart` to your PC's WiFi IP

## 🎬 2-minute demo script

1. **Admin dashboard** → stat cards + click 🤖 **Run AI Anomaly Scan** → Dwarka flagged
2. Pick an institute → 🎯 **Assign Random Inspection** → nearest PMU officer chosen, audit seed shown
3. Open the **field app** (ravi) → 🔔 notification arrived → task visible with Navigate link
4. In the field app: *Capture Evidence* → take a photo → submit
5. No faces in photo? → **⚠ POSSIBLE PROXY** → admin's bell lights up 🚨
6. Admin → **Alerts** → resolve → risk score drops
7. **CCTV Feeds** → 3 live HLS streams (+ your phone via DroidCam)
8. 📞 **Start Surprise VC** → Jitsi room opens; inspectors notified too
9. **Reports → Export CSV** → transparency register download

## 🧪 Tests

```bash
cd backend && .venv\Scripts\python test_api.py      # full API flow (8 steps)
cd mobile/drishti_app && flutter analyze && flutter test
```

## 🔐 Demo accounts

| Username | Password | Role |
|---|---|---|
| admin | admin123 | DoSJE official (full control) |
| ravi / priya / arjun | inspector123 | PMU field inspectors |
| ngostaff | institute123 | NGO staff (future scope) |

## 📁 Structure

```
backend/    FastAPI app, models, JWT/RBAC auth, AI engine, notifications, e2e test
dashboard/  React dashboard — role-based UI, Logo/Layout components, 7 pages
mobile/     Flutter field app (tasks, capture evidence, VC)
docs/       planv0.md (original build plan) · planv1.md (v2 redesign plan) · SIH deck
```

All software used is free & open-source.

---

## 🛠️ Appendix — backend launch options & venv troubleshooting

### 1. Backend (port 8000) — alternative launchers

**Option A — one command (recommended):**
```powershell
.\backend\run.ps1
```
The script auto-creates `.venv` if missing, activates it, installs `requirements.txt` only when packages are absent, and starts uvicorn with `--reload` — no manual activation ever needed.

**Option B — VS Code:** open the repo in VS Code and press **F5** ("DRISHTI Backend" launch config). The workspace is preconfigured to always use `backend\.venv` — no manual activation.

**Option C — manual:**
```bash
cd backend
python -m venv .venv                 # only if .venv doesn't exist yet
.\.venv\Scripts\activate             # Windows  (source .venv/bin/activate on Linux/macOS)
python -m pip install -r requirements.txt
python seed.py                       # creates demo data
python -m uvicorn main:app --reload --port 8000
```
Interactive API docs: http://localhost:8000/docs

> **Tip:** prefer `python -m pip ...` over bare `pip`. Module-style invocation uses the interpreter directly and can never hit broken hardcoded paths inside venv launcher executables.

#### 🛠️ Backend venv troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Fatal error in launcher: Unable to create process using '"D:\...old path...\pip.exe"'` | venv was moved/copied; `.exe` launchers embed an absolute python path from creation time | `python -m pip install --upgrade --force-reinstall pip` (regenerates launchers) |
| `Unable to copy '...\venvlauncher.exe' to '.venv\Scripts\python.exe'` when creating a venv | a process is running from the venv (can't overwrite a running `python.exe`) or antivirus lock | stop all processes using `.venv`, close editors/terminals holding it, then retry |
| `[WinError 10013]` on uvicorn startup | port 8000 already held by a stale server instance (`Get-NetTCPConnection -LocalPort 8000`) | kill the holder: `Stop-Process -Id <PID> -Force`, then relaunch |
| Rebuilding from scratch | — | stop all processes → `Remove-Item -Recurse -Force .venv` → `python -m venv .venv` |
