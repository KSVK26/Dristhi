# 👁️ DRISHTI — Smart Real-Time Monitoring & Inspection Platform

**SIH 2026 · Problem Statement 26095 · Ministry of Social Justice & Empowerment (DoSJE)**

A centralized monitoring system with three components:

| Component | Tech | Who uses it |
|---|---|---|
| `backend/` | Python FastAPI + SQLite + scikit-learn + OpenCV | (API for both apps) |
| `dashboard/` | React + Vite + Leaflet maps + Recharts + hls.js | DoSJE officials |
| `mobile/drishti_app/` | Flutter (Android) | PMU / inspection teams |

## ✨ Features (mapped to PS requirements)

- **Live CCTV feed integration** → HLS streams + DroidCam phone-as-IP-camera tile
- **Random VC connectivity** → one-click Jitsi surprise video-conference rooms
- **Real-time monitoring dashboard** → risk-coloured map pins, attendance charts, live alerts
- **Mobile inspection module** → camera evidence + GPS geo-tagging + checklist
- **AI random inspection assignment** → seeded RNG (auditable fairness) weighted by distance
- **Geo-tagged reports & live evidence** → photo + GPS stored per report
- **AI anomaly & attendance analytics** → IsolationForest flags outlier institutes
- **Proxy detection** → OpenCV face detection on evidence photos (`possible_proxy` flag)
- **Risk scoring** → every institute gets a 0–100 score that updates automatically

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

1. **Dashboard → Live Map**: click the red pin (Dwarka) → see attendance chart
2. Click **🤖 Run AI Anomaly Scan** → IsolationForest flags the anomalous institute
3. Click **🎯 Assign Random Inspection** → AI picks nearest PMU inspector, shows audit seed
4. **Flutter app**: login as `ravi` → task appears with map → *Capture Evidence*
5. Take any photo → submit → if no faces detected, app warns **⚠ POSSIBLE PROXY**
6. **Dashboard → Alerts**: proxy alert appeared → click *Mark Resolved* → risk score drops
7. **Dashboard → CCTV Feeds**: 3 live HLS streams (+ connect your phone via DroidCam)
8. Back on map pin → **📞 Start Surprise VC** → Jitsi room opens in browser

## 🧪 Tests

```bash
cd backend && .venv\Scripts\python test_api.py     # full API flow (8 steps)
cd mobile/drishti_app && flutter analyze && flutter test
```

## 🔐 Demo accounts

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Department official (full access) |
| ravi / priya / arjun | inspector123 | PMU field inspectors |
| ngostaff | institute123 | NGO staff |

## 📁 Structure

```
backend/    FastAPI app, models, JWT auth, AI engine, seeder, e2e test
dashboard/  React dashboard (map, CCTV grid, alerts, reports)
mobile/     Flutter field app (tasks, capture evidence, VC)
docs/       SIH presentation + build plan
```

All software used is free & open-source.