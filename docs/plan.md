# DRISHTI — Prototype Build Plan
**SIH 2026 · Problem Statement ID 26095**
*Smart Real-Time Monitoring & Inspection Mobile App (DoSJE / MoSJE)*

> Goal: A working end-to-end prototype in ~16–20 hours (1–2 days), 100% free tools, beginner-friendly code.
> Core principle wired into the app: **MONITOR → DETECT → VERIFY → REPORT → ACT**

---

## 1. Problem Summary

Develop a centralized mobile application for real-time monitoring, surprise inspections,
CCTV surveillance integration, and random inspection assignment for projects/institutes/NGOs
running under DoSJE schemes.

**Key features to demonstrate:**
- Live CCTV feed integration from projects/institutes
- Random Video Conferencing (VC) with Project Incharge / Staff / Beneficiaries
- Real-time monitoring dashboard for Department officials
- Mobile-based inspection module for PMU / Inspection Teams
- Random assignment of inspection duties through AI/automation
- Geo-tagged inspection reports and live evidence capture
- AI-based anomaly and attendance analytics

**Expected outcomes:** transparency & accountability, reduction in fake reporting/proxy
functioning, real-time monitoring, better inspection governance, citizen-centric delivery.

---

## 2. Tech Stack (Finalized — All Free)

| Layer | Choice | Why (beginner + free) |
|---|---|---|
| **Field App (mobile)** | **Flutter (Dart)** | One consistent widget model, friendly compiler errors, matches PPT stack verbatim |
| **Official Dashboard (web)** | **React + Vite** | Simplest modern web setup, hot reload |
| **Backend API** | **Python FastAPI** | Matches PPT slide 4; auto API docs at `/docs` |
| **Database** | **SQLite** via SQLAlchemy | Zero setup; upgrade path to PostgreSQL (mention in viva) |
| **Auth** | **JWT + 3 roles** (Admin, Inspector/PMU, Institute) | Implements RBAC box on PPT slide 4 |
| **Maps** | **flutter_map / Leaflet.js + OpenStreetMap tiles** | Free, no API key or billing (avoid Google Maps) |
| **Live CCTV feeds** | Simulated: public test HLS streams + **DroidCam / IP Webcam app** (phone → IP camera) | Demonstrates real feed integration without real cameras |
| **Video Conferencing** | **Jitsi Meet** (free, no account) | Drop-in VC room per institute — covers "Random VC connectivity" |
| **AI layer** | **scikit-learn IsolationForest** (anomaly/risk scoring) + **OpenCV face detection** (proxy-attendance check on photos) | Lightweight AI = innovation talking point |
| **Geo-evidence** | Phone GPS (`geolocator`) + timestamped photos (`image_picker`) uploaded to FastAPI | Covers geo-tagged reports |
| **Random assignment** | Weighted random algorithm (distance + workload + logged randomness seed) | Core PS feature, ~50 lines of code |
| **Deployment (demo day)** | Everything runs locally on one laptop + one phone; optional free hosting: Render (API), Vercel/Netlify (dashboard) | Zero cost |

---

## 3. Architecture (matches PPT Slide 4)

```
[Flutter Field App] ──┐                          ┌── [React Dashboard]
                      ├──► FastAPI Gateway ──────┤
[DroidCam CCTV] ──────┘          │                └── [Jitsi VC rooms]
                            SQLite DB
                                 │
                    AI Engine (FastAPI background):
                    • IsolationForest risk scoring
                    • Face-detection proxy check
                    • Random inspection assigner
```

Prototype workflow: **App → API Gateway → AI Engine → DB → Dashboard**

---

## 4. Folder Structure

```
SIH26095/
├─ backend/
│   ├─ main.py            # FastAPI app entry
│   ├─ models.py          # SQLAlchemy models
│   ├─ auth.py            # JWT + RBAC helpers
│   ├─ ai_engine.py       # anomaly detection + random assigner + face check
│   ├─ seed.py            # fake data generator
│   └─ routers/           # institutes, inspections, reports, alerts, cctv
├─ dashboard/             # React + Vite web dashboard
│   └─ src/pages/         # Login, MapView, CctvGrid, Alerts, Reports
├─ mobile/                # Flutter field app (drishti_app)
│   └─ lib/screens/       # login, my_tasks, capture_evidence, join_vc
└─ docs/
    ├─ plan.md            # this file
    └─ SIH presentation deck
```

---

## 5. Database Models

- `User(id, name, role[admin|inspector|institute], lat, lng, password_hash)`
- `Institute(id, name, district, scheme, lat, lng, risk_score)`
- `Inspection(id, institute_id, inspector_id, status, scheduled_at, is_random, assignment_seed)`
- `Report(id, inspection_id, geo_lat, geo_lng, photo_path, checklist_json, ai_flags, created_at)`
- `AttendanceLog(id, institute_id, date, expected, present, face_verified)` ← feeds anomaly AI
- `Alert(id, type, severity, message, resolved)`

## 6. Key API Endpoints

- `POST /login` — JWT auth
- `GET /institutes` — list with risk scores
- `GET /attendance/analytics/{institute_id}` — attendance history + anomaly flag
- `POST /inspections/assign-random` — AI assigns nearest suitable inspector
- `POST /reports` — multipart upload: photo + GPS + checklist
- `GET /reports` — dashboard view of submitted evidence
- `GET /alerts` — polling endpoint for live alerts
- `GET /cctv/streams` — stream URLs for CCTV grid

---

## 7. Step-by-Step Build Plan (~18 hours)

### PHASE 0 — Setup (Hour 0–1)
1. Install Node.js LTS, Python 3.11+, Flutter SDK (run `flutter doctor`, fix any issues).
2. Scaffold:
   - `npm create vite@latest dashboard`
   - `flutter create mobile/drishti_app`
   - `pip install fastapi uvicorn sqlalchemy python-jose passlib[bcrypt] scikit-learn opencv-python-headless pillow python-multipart`
3. Create folder structure above.

### PHASE 1 — Backend + Database (Hours 1–4)
1. Write models (Section 5), create tables.
2. Auth: register/login returning JWT; `get_current_user` dependency; role checks
   (`require_role("admin")`) → demonstrates RBAC.
3. Seed script: 6 institutes across districts, 3 inspectors, 30 days of fake attendance
   data (inject 2 anomalous institutes).
4. Implement endpoints (Section 6). Verify at `http://localhost:8000/docs`.

### PHASE 2 — Official Dashboard (Hours 4–8)
1. Login page → store JWT.
2. MapView (Leaflet): pins color-coded by risk score (green/yellow/red); click pin → side
   panel with attendance chart (Recharts) + "Trigger Random Inspection" button.
3. CCTV Grid: 2×3 tiles playing free HLS test streams + one DroidCam tile as "live site camera".
4. Random VC module: "Start Surprise VC" → creates Jitsi room
   `drishti-institute-{id}-{timestamp}`, shows join link, logs an alert.
5. Alerts panel: polls `/alerts` every 10s; red banner for high severity.
6. Reports table: view geo-tagged reports, open photo, mini-map of report location.

### PHASE 3 — Flutter Field App (Hours 8–12)
1. Packages: `http`, `geolocator`, `image_picker`, `flutter_map`, `shared_preferences`.
2. Screens:
   - **Login** — same JWT endpoint; store token in shared_preferences.
   - **My Tasks** — list of inspections assigned to logged-in inspector.
   - **Capture Evidence** — take photo (image_picker), grab GPS (geolocator),
     5-question yes/no checklist, upload multipart to `/reports`.
   - **Join VC** — open Jitsi room URL (webview or deep link).
3. Test on physical phone via USB (`flutter run`).

### PHASE 4 — AI Engine (Hours 12–15)
1. **Random assignment:** score each inspector = distance(institute↔officer) + workload;
   pick randomly among top-3 weighted candidates; **store the random seed** in DB →
   "prevents collusion / tamper-proof" talking point.
2. **Anomaly detection:** train IsolationForest on seeded attendance data; flag outlier
   institutes → auto-create Alert + bump risk_score.
3. **Proxy check (wow factor):** on report photo arrival, run OpenCV Haar-cascade face
   detection; if 0 faces in a beneficiary-verification photo → flag `possible_proxy`.
4. **Risk scoring:** combine anomaly score + overdue inspections + unresolved alerts →
   0–100 score driving map colors.

### PHASE 5 — Integration, Demo Script, Deck (Hours 15–18)
1. Full dry-run of golden demo flow (Section 8).
2. Fill remaining PPT slides:
   - Slide 3 (Technical Approach) = methodology flow from Section 3
   - Slide 5 (Feasibility) = all-free stack, offline-capable app, scales to PostgreSQL
   - Slide 6 (Impact) = maps to Expected Outcomes in Section 1
   - Slide 7 (References) = links already listed in deck
3. Record a 2-minute backup video of the demo.

---

## 8. Golden Demo Flow (for judges, ~4 min)

1. Admin logs into dashboard → sees map, all institutes green.
2. Clicks anomalous institute (red) → attendance graph dips → AI alert fired.
3. Clicks **"Assign Random Inspection"** → system picks nearest free inspector,
   shows seed-proof of fairness.
4. Switch to phone (inspector login) → task appears → captures geo-tagged photo →
   OpenCV verifies faces → submits report.
5. Back on dashboard: report + photo + GPS pin appear instantly; admin starts a
   surprise Jitsi VC with institute staff.
6. Close on the principle: *"We MONITOR continuously, DETECT with AI, VERIFY on ground,
   REPORT automatically, ACT in real time."*

---

## 9. Checkpoint Rule (time management)

If behind schedule at **Hour 8**:
- Drop native Flutter polish → keep screens minimal but functional.
- Simplify AI to the risk-score formula only (skip IsolationForest training).
Every PS feature remains demonstrable.

## 10. Free Test Resources

- HLS test streams: Mux test stream, Big Buck Bunny HLS
- DroidCam / IP Webcam (Android) → phone becomes IP camera
- Jitsi Meet: `https://meet.jit.si/<room-name>` — free, no signup
- OpenStreetMap tiles: free, no key
- References (from deck): socialjustice.gov.in, digitalindia.gov.in, uidai.gov.in,
  docs.ultralytics.com, webrtc.org, postgresql.org/docs, docs.opencv.org