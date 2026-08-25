# 📖 DRISHTI — The Complete Explanation
### Everything you need to understand, present, and defend our SIH 2026 solution
#### Problem Statement 26095 · Ministry of Social Justice & Empowerment (MoSJE)

> **How to use this document:** Read it top-to-bottom once. Before the pitch,
> re-read Sections 9 (slide mapping) and 10 (Q&A bank). If a judge asks anything,
> the answer is in here.

## 📑 Table of Contents

1. The Problem Statement — fully decoded
2. The Solution — DRISHTI explained
3. Architecture & data flows
4. Every technology — what, why, why free
5. Database design — every table explained
6. The AI — explained from zero
7. Security — auth, hashing, RBAC
8. Implementation walkthrough — every endpoint
9. Slide-by-slide PPT mapping
10. Judge Q&A bank — 50+ questions answered
11. Honest limitations & future scope
12. Glossary — every term

---

# 1 — The Problem Statement, fully decoded

## 1.1 The official text (what SIH gave us)

> **PS ID:** 26095
> **Title:** Smart Real-Time Monitoring & Inspection Mobile App
> **Organization:** Ministry of Social Justice and Empowerment (MoSJE)
> **Department:** Department of Social Justice and Empowerment (DoSJE)
> **Category:** Software

**Description (decoded line by line):**

| Official line | What it actually means |
|---|---|
| *"Develop a centralized mobile application"* | ONE system (not 20 disconnected spreadsheets and WhatsApp groups) that everyone logs into. "Centralized" = single source of truth. |
| *"real-time monitoring"* | Officials must see what's happening at institutes **right now** — not last month's paper report. |
| *"surprise inspections"* | Inspections must be **unannounced** — if an NGO knows you're coming Tuesday, they arrange everything for Tuesday. Surprise = you see reality. |
| *"CCTV surveillance integration"* | The system should show live camera feeds from institutes inside the app. |
| *"random inspection assignment"* | The computer picks WHO inspects WHICH institute — randomly — so officials can't always send their favourite inspector, and inspectors can't build cosy relationships with one NGO. |
| *"AI/automation"* | Use machine learning somewhere meaningful, not just forms. |

## 1.2 The real-world problem (why this PS exists)

To understand the solution, you must understand **how the fraud actually works today**:

**The setup:** MoSJE runs schemes for vulnerable groups — skill training for
Divyangjan (PM-DAKSH), elderly welfare awards (Vayoshreshtha), rehabilitation for
transgender persons (SMILE), drug de-addiction centres (NIRMYA). The ministry gives
**grants** to NGOs/institutes to run these programmes.

**How the money leaks (the fraud triangle):**

1. **Ghost beneficiaries** — An NGO claims to train 100 people but only 40 exist.
   Attendance registers are handwritten → easy to fake. 60 people's grant money
   disappears.

2. **Proxy functioning** — The NGO's *registered office* is real and looks great,
   but the *actual centre* in the village doesn't exist or is locked. When an
   inspection is announced, someone borrows a room and a few people for a day.

3. **Inspection collusion** — Inspections are announced in advance. Worse: the
   same 2–3 inspectors visit the same NGOs for years. Relationships form.
   A "satisfactory" report gets written from the office desk without visiting.

4. **The reporting gap** — By the time a paper inspection report travels from a
   district office to Delhi, months have passed. Nobody can cross-check it.

**What DoSJE asked SIH for:** a system that makes the above four fraud methods
impossible or extremely risky. Every feature in our app attacks one of them.

## 1.3 Stakeholders — and what each one gets

| Stakeholder | Who they are | What DRISHTI gives them |
|---|---|---|
| **DoSJE Divisions** | Ministry officials in Delhi who disburse grants | Live map + risk scores: know which NGOs to trust before releasing the next grant instalment |
| **PMU Teams** | Programme Management Unit — field staff who physically visit institutes | A phone app that tells them where to go, navigates them, and turns 1 hour of paperwork into a 5-minute evidence capture |
| **NGOs / Institutes** | Organisations receiving grants | Indirect: honest NGOs finally compete fairly — fraudulent ones can't undercut them with fake costs. Plus fewer repeat visits since digital evidence is accepted |
| **Beneficiaries** | Divyangjan trainees, elderly, transgender persons in programmes | Their attendance is actually counted and verified — the training they were promised actually happens |
| **State/District Authorities** | Regional offices | District + scheme filters: see only their jurisdiction in real time |

## 1.4 Expected outcomes — and how we achieve each

| PS expected outcome | How DRISHTI achieves it |
|---|---|
| **Improved transparency & accountability** | Every action is logged with timestamp + identity: who assigned (with audit seed), who inspected (with GPS), who resolved (with name). CSV export makes the whole register auditable. |
| **Reduction in fake reporting & proxy functioning** | Triple check: (1) photo taken live in-app, (2) GPS proves location, (3) OpenCV face detection proves humans present. Zero faces → automatic POSSIBLE_PROXY alert. |
| **Real-time monitoring of projects** | 10–15 s polling on dashboard; CCTV grid; attendance charts; live risk scores that change with events. |
| **Better inspection governance & compliance** | Seeded random assignment removes favouritism; the seed is stored and replayable to prove fairness. |
| **Enhanced citizen-centric service delivery** | If beneficiaries are physically present and counted, the schemes actually reach them — the ultimate goal. |

---

# 2 — The Solution: DRISHTI explained

## 2.1 The name

**DRISHTI (दृष्टि)** = "vision/sight" in Hindi. The logo is a **lotus eye** — the
lotus (national flower) + an eye (oversight). The ministry literally cannot *see*
its institutes today; we give it vision.

## 2.2 One-sentence pitch

> *"DRISHTI gives MoSJE real-time eyes on every institute, assigns inspections by
> auditable AI lottery, and verifies field evidence with GPS and computer vision —
> making proxy functioning and fake reporting detectable within minutes."*

## 2.3 Why THREE apps (judges always ask)

| App | Why it must be separate |
|---|---|
| **Web Dashboard** (React) | Officials sit at desks with big screens. They need maps, charts, grids of CCTV, tables of reports. A phone screen can't show a national map + 4 stat cards + alert feed at once. |
| **Field App** (Flutter) | Inspectors walk around with one hand. They need big buttons, camera integration, GPS — native mobile capabilities a website handles poorly. Flutter compiles to Android AND web from one codebase. |
| **Backend API** (FastAPI) | The single source of truth both apps share. Business logic (AI, risk scoring, RBAC) lives here once — not duplicated in two frontends. |

## 2.4 Requirement → feature mapping (the compliance table)

| PS requirement | DRISHTI implementation | Status |
|---|---|---|
| Centralized app | One FastAPI backend + one SQLite DB + JWT login for all roles | ✅ |
| Real-time monitoring | Dashboard: live map, 4 stat cards, 10 s alert polling, attendance charts | ✅ |
| CCTV integration | HLS stream grid (3 live streams) + DroidCam phone-as-IP-camera tile | ✅ |
| Surprise VC with Incharge/Staff/Beneficiaries | One-click Jitsi rooms, links pushed to inspectors | ✅ |
| Mobile inspection module (PMU) | Flutter: task list, camera, GPS, checklist, upload | ✅ |
| Random AI assignment | Seeded RNG weighted by distance + workload; seed stored for audit | ✅ |
| Geo-tagged reports & evidence | Multipart upload: photo + lat/lng + checklist JSON | ✅ |
| AI anomaly & attendance analytics | IsolationForest over 30-day attendance ratios | ✅ |
| Stakeholder coverage | Role-based access: admin / inspector (+ institute ready) | ✅ |

---

# 3 — Architecture & data flows

## 3.1 The big picture

```
┌─────────────────────┐         ┌─────────────────────┐
│  DASHBOARD (React)  │         │  FIELD APP (Flutter)│
│  officials, :5173   │         │  inspectors, phone  │
└──────────┬──────────┘         └──────────┬──────────┘
           │  HTTPS + JWT token            │  HTTPS + JWT token
           ▼                               ▼
     ┌─────────────────────────────────────────┐
     │        BACKEND API (FastAPI :8000)      │
     │  auth · RBAC · AI engine · risk scores  │
     │  notifications · file storage           │
     └───────────┬──────────────┬──────────────┘
                 ▼              ▼
         ┌────────────┐   ┌──────────────────┐
         │  SQLite DB │   │ uploads/ folder  │
         │ (drishti.db│   │ (evidence photos)│
         └────────────┘   └──────────────────┘
```

**Key point:** the frontends hold NO business logic. They only display what the
API returns. This means the AI, the rules, and the data live in ONE place.

## 3.2 Flow: Login (what happens when you press Sign In)

```
1. App sends:  POST /login  {username, password}
2. Backend loads the User row from SQLite
3. Backend hashes the typed password with PBKDF2-SHA256 (100,000 iterations,
   same salt as stored) and compares with the stored hash
4. Match? → Backend creates a JWT token containing:
      { sub: user_id, username, role }   signed with SECRET_KEY (HS256)
5. Token returns to the app → stored in localStorage (web) / SharedPreferences (phone)
6. EVERY later request sends:  Authorization: Bearer <token>
7. Backend decodes the token on every request → knows WHO you are and WHAT
   your role is → @require_role("admin") blocks unauthorised endpoints (403)
```

## 3.3 Flow: Random inspection assignment (the audit trail)

```
1. Admin clicks "Assign Inspection" →  POST /inspections/assign-random
2. Backend loads all inspectors + counts each one's open tasks
3. For each inspector: score = haversine_distance(km) + (open_tasks × 25)
      → nearest + least busy = best score
4. Keep the top-3 best candidates
5. Generate a cryptographically random 32-bit SEED (secrets.randbits)
6. numpy RNG seeded with it picks one of the top-3, weighted [3:2:1]
      → nearest is 3× more likely, but never certain
7. The SEED is saved on the Inspection row  ← THE AUDIT PROOF
8. Notifications created: one targeted to the inspector, one to admins
9. Frontend shows: "Assigned to X, Y km away, seed 1234567890"
```

**Why the seed matters (judge question!):** anyone can later take the stored
seed, re-run the same RNG code, and get the *same* winner. So the department can
prove: "we didn't cherry-pick — replay the seed yourself."

## 3.4 Flow: Evidence capture → AI proxy check

```
1. Inspector taps Capture → image_picker opens the phone camera (live only —
   no gallery pick in real use, so photos can't be borrowed)
2. geolocator grabs GPS → app shows lat/lng on screen
3. Inspector answers 5 yes/no checklist switches
   - Optional: tap **📷 Add photo proof** on any answer (uploads q0–q4 photos)
4. Submit → multipart/form-data POST /reports with:
      inspection_id, geo_lat, geo_lng, checklist (JSON),
      main photo + optional q0_photo…q4_photo per-answer proofs
5. Backend:
   a. verifies the inspection belongs to THIS inspector (403 otherwise)
   b. saves photo to uploads/report_<id>_<user>.jpg
   c. OpenCV decodes the image → grayscale → Haar cascade face detection
   d. face_count == 0  → flag "possible_proxy" + HIGH alert to admins
   e. compute_risk_score() recalculates the institute's 0–100 score
   f. if score ≥ 70 → deduplicated HIGH-RISK notification to admins
   g. inspection status → completed
6. Dashboard (polling) shows: new report card, new alert, new map colour
```

## 3.5 Flow: Notifications

```
Trigger events → Alert row created with routing fields:
  target_user_id  → notification for ONE person (e.g. assigned inspector)
  audience='admin'     → all admins see it
  audience='inspector' → all inspectors see it
  is_read=False until consumed

Apps poll GET /notifications every 10–15 s → badge count + list.
Mark read: POST /notifications/{id}/read or /read-all.
```

## 3.6 Flow: Risk score (the transparent formula)

```
score = 10 (base)
      + 20 × (unresolved HIGH alerts)      max +40
      + 10 × (unresolved MEDIUM alerts)
      + 10 × (overdue inspections)          max +30
      + up to 20 if average attendance < 90%
      clamped to 0–100
```

Worked example: an institute with 1 unresolved high alert (+20), 2 overdue
inspections (+20), and 80% average attendance (+20) = 10+20+20+20 = **70 → HIGH
RISK** → automatic admin notification.

**Why this formula (judge question!):** it's deliberately simple and explainable.
Every point is traceable to a real record in the database — no black box. A
registrar can compute it by hand.

---

# 4 — Every technology: what it is, why we chose it, what's the alternative

> The whole stack is **free and open-source** — total cost of software: **₹0**.
> This matters for a government deployment.

## 4.1 Backend

| Tech | What it is | Why we chose it | Alternatives we rejected |
|---|---|---|---|
| **Python + FastAPI** | Modern web framework; writes API endpoints as simple functions; auto-generates interactive docs at /docs | Fastest Python framework; automatic validation via type hints; the /docs page doubles as living documentation for judges | Django (too heavy for a prototype), Flask (no auto-docs, more boilerplate) |
| **Uvicorn** | The server that runs FastAPI | The standard companion; supports live reload during development | Gunicorn/Hypercorn |
| **SQLAlchemy** | Lets us talk to the database using Python classes instead of SQL strings | Prevents SQL-injection by design; switching databases later = changing one line | Raw SQL (injection risk), Django ORM (comes with Django) |
| **SQLite** | A complete database in ONE FILE (`drishti.db`) — no server to install | Zero setup = judges/teammates run it instantly. For production we'd swap to PostgreSQL (SQLAlchemy makes this a config change) | PostgreSQL/MySQL (need a server install — overkill for a 2-day prototype) |
| **PyJWT** | Creates and verifies JWT tokens (signed login tickets) | Industry standard, tiny | OAuth servers (way too heavy) |
| **hashlib PBKDF2** | Python's built-in password hashing (100,000 SHA-256 iterations with random salt) | Built into Python — zero dependencies; OWASP-approved algorithm | bcrypt (needs a C extension), plain hashes (never!) |
| **python-multipart** | Parses file uploads (the evidence photos) | Required by FastAPI for multipart forms | — |

## 4.2 The AI

| Tech | What it is | Why | Alternative |
|---|---|---|---|
| **scikit-learn IsolationForest** | Anomaly-detection algorithm: builds random "decision trees" that isolate each data point; points that get isolated in FEW steps are weird → outliers | Trains in <1 second on a laptop CPU; no GPU; explainable; perfect for tabular data like attendance ratios | Deep learning autoencoders (need GPUs + thousands of samples we don't have); simple thresholds (can't compare across institutes) |
| **OpenCV Haar cascade** | Face detection using light/dark rectangle patterns over the image; runs on CPU in milliseconds | Runs offline on any machine; no cloud, no API key, no cost; good enough to answer "are there humans here?" | MTCNN/MediaPipe (heavier, needs more setup); cloud vision APIs (cost money, send citizen photos to third parties — a privacy problem for government) |
| **numpy** | Math on arrays (attendance matrices, RNG) | Comes with scikit-learn anyway | — |
| **secrets.randbits** | Cryptographically secure random number | The assignment seed must be unpredictable AND reproducible | `random` module (predictable — a corrupt official could game it) |

## 4.3 Dashboard (React)

| Tech | What it is | Why |
|---|---|---|
| **React + Vite** | Component-based UI framework + instant dev server/build tool | Biggest talent pool; Vite builds in ~1.5 s; huge ecosystem |
| **Leaflet + OpenStreetMap** | Interactive maps with risk-coloured pins | **Completely free, no API key** (Google Maps charges money + needs billing + has usage limits) — critical for government |
| **Recharts** | Line/bar charts in React | Simple API for the 30-day attendance chart |
| **hls.js** | Plays HLS video streams (.m3u8) in browsers | That's the protocol real CCTV/IP cameras stream; we plug in free public streams to prove the integration works |
| **Jitsi Meet** | Free open-source video conferencing — we just create a room URL | Zero infrastructure: no WebRTC servers to run. Real deployment could self-host Jitsi on NIC servers |

## 4.4 Field app (Flutter)

| Tech | What it is | Why |
|---|---|---|
| **Flutter** | Google's UI toolkit — ONE Dart codebase → Android, iOS, and Web | Inspectors use Android; the ministry might want iOS; and we can demo in a browser without installing anything. One codebase = 3 platforms |
| **geolocator** | Flutter plugin for GPS position + permissions | Handles the Android permission flow for us |
| **image_picker** | Opens the native camera | Live camera only — evidence can't be an old gallery photo |
| **flutter_map + OpenStreetMap tiles** | Mini maps on task cards | Free, no API key |
| **shared_preferences** | Stores the JWT token + server address on the phone | Survives app restarts |
| **http** | REST calls to the backend | Standard |

## 4.5 Why this stack wins for government (judge answer)

- **₹0 software cost** — everything is open-source
- **Runs offline/on-premise** — citizen photos never leave government servers
  (critical for data-privacy compliance)
- **One-file database** for the pilot → one-line change to PostgreSQL for national scale
- **CPU-only AI** — no GPU budget needed, runs on a ₹20,000 machine

---

# 5 — Database design (every table, every column)

Six tables. Here's each one and *why every column exists*.

## 5.1 `users` — everyone who logs in

| Column | Type | Why it exists |
|---|---|---|
| id | int, primary key | unique reference everywhere else |
| username | str, unique | login handle |
| name | str | display name ("Ravi Kumar (PMU)") |
| role | str | **RBAC**: 'admin' / 'inspector' / 'institute' — decides what endpoints they may touch |
| password_hash | str | PBKDF2 hash, NEVER the plain password |
| lat, lng | float | inspector's last known position — used for nearest-officer assignment and distance display |

## 5.2 `institutes` — the monitored NGOs/centres

| Column | Why |
|---|---|
| name, district, scheme | identity + enables the map filters |
| lat, lng | map pin + haversine distance to inspectors |
| risk_score (0–100) | drives pin colour, HIGH-RISK notifications, and grant-scrutiny priority |
| contact_person, phone | for surprise-VC coordination |

## 5.3 `inspections` — assigned tasks

| Column | Why |
|---|---|
| institute_id, inspector_id | who goes where (foreign keys) |
| status | 'assigned' → 'in_progress' → 'completed' (the workflow) |
| is_random | TRUE = AI surprise assignment (shown as SURPRISE badge) |
| **assignment_seed** | ⭐ the stored RNG seed — the tamper-proof fairness proof |
| scheduled_at / completed_at | timestamps for the audit trail + "overdue" risk component |

## 5.4 `reports` — geo-tagged evidence

| Column | Why |
|---|---|
| inspection_id | which task this evidence closes |
| geo_lat, geo_lng | WHERE the photo was taken (rendered on a map) |
| photo_path | file under `uploads/` — served by the backend |
| checklist_json | the 5 yes/no answers, stored as JSON |
| ai_flags | 'possible_proxy', 'unreadable_image' — the AI verdict |
| created_at | when (audit trail) |

## 5.5 `attendance_logs` — AI input data

| Column | Why |
|---|---|
| institute_id, log_date | one row per institute per day |
| expected, present | the ratio present/expected is the AI's feature |
| face_verified | did CCTV/photo face-check pass that day (future CCTV analytics) |

## 5.6 `alerts` — events AND notifications (one table, two jobs)

| Column | Why |
|---|---|
| type | 'anomaly', 'proxy_suspect', 'high_risk', 'inspection_assigned', 'vc_started' |
| severity | low/medium/high → colours + risk-score weight |
| message | human-readable text shown in UI |
| institute_id | which institute (nullable) |
| resolved | admin handled it (lowers risk score) |
| audience | 'admin' / 'inspector' / NULL — role-based notification routing |
| target_user_id | direct notification to ONE user |
| is_read | notification consumed? |

> **Judge question — "why one table for alerts AND notifications?"**
> A: In a prototype, one table with routing columns is simpler and avoids
> duplication. In production we'd split into `events` (immutable log) and
> `notifications` (per-user delivery with read state) — we say this openly.

---

# 6 — The AI, explained from zero

## 6.1 IsolationForest — attendance anomaly detection

**The idea (no math needed):** imagine cutting a sheet of paper with random
straight lines, trying to isolate every dot on it. Normal dots clustered together
take MANY cuts to isolate. A dot sitting alone far away takes ONE cut.
IsolationForest does exactly this with random decision trees — **weird points are
easy to isolate**.

**Our specific setup:**
- **Input:** for each institute, 30 numbers = daily `present / expected` ratio
- **Training:** `IsolationForest(contamination=0.15, random_state=42)`
  - contamination=0.15 → "expect roughly 15% of institutes to be outliers"
  - random_state=42 → reproducible (same result every scan — auditable!)
- **Output:** label −1 (anomaly) or +1 (normal) per institute
- **On anomaly:** risk_score += 40, HIGH alert created, admins notified

**Judge Q: "Why not a neural network?"**
A: We have 6 institutes × 30 days = 180 data points. Neural networks need
thousands of samples and a GPU. IsolationForest is *designed* for small tabular
datasets, trains in under a second, and its decisions are explainable. Choosing
it is an engineering decision, not a limitation. When MoSJE has 10,000 institutes
of history, we can graduate to time-series models — the interface stays the same.

**Judge Q: "What does it actually catch?"**
A: Institutes whose attendance pattern deviates from the *group norm* — e.g.,
attendance that drops to 40% while every similar institute stays at 95%, or
suspiciously flat perfect attendance (a classic sign of fabricated registers).

---

## 6.2 Haar-cascade face detection — the proxy check

**The idea:** the Haar cascade slides thousands of simple light/dark rectangle
patterns over the image (eyes are darker than cheeks, nose bridge lighter than
eyes). Where many patterns match at once → a face. It's the classic, fast,
CPU-only face detector that ships **inside OpenCV** — no downloads, no cloud.

**Our logic (deliberately conservative):**

| faces found | verdict | action |
|---|---|---|
| 0 | `possible_proxy` | HIGH alert to admins, risk score bump |
| 1+ | pass | report marked AI-verified |
| image unreadable | `unreadable_image` | flagged for manual review |

**Judge Q: "What if the inspector photographs an empty room during a real
holiday?"**
A: The flag is **"possible proxy", not "guilty"**. It's a *trigger for human
review*, not a verdict. The admin sees it, can call the institute, and resolves
the alert — which we track (acknowledged_by / resolved). AI raises suspicion;
humans decide.

**Judge Q: "Can someone fool it with a printed photo of people?"**
A: A printed photo held in front of the camera *does* contain faces, so basic
Haar would pass it. Our defence-in-depth answer: (1) GPS must be near the
institute (geo-fence — future scope), (2) live camera capture only, (3) in
production we'd upgrade to **liveness detection** (blink/head-move checks) which
is a drop-in upgrade path we can name.

## 6.3 Seeded RNG — auditable fairness

**The problem it solves:** if assignment is a black box, a corrupt official can
re-run it until their "friendly" inspector wins.

**Our design:**
1. Score all inspectors: `distance_km + open_tasks × 25` (nearest, least busy = best)
2. Keep the **top 3**
3. Generate a 32-bit cryptographic seed (`secrets.randbits(32)`)
4. numpy RNG seeded with it picks from the top-3 with weights **3 : 2 : 1**
   (nearest is 3× likelier — efficiency matters — but never certain)
5. **Store the seed** on the inspection row

**The audit:** take the stored seed → re-run the exact code → the SAME winner
comes out → the draw was fair. This is called a *verifiable lottery*.

## 6.4 Risk scoring — full transparency

```
score = 10 (base)
      + 20 per unresolved HIGH alert   (capped +40)
      + 10 per unresolved MEDIUM alert
      + 10 per overdue inspection      (capped +30)
      + up to +20 for low average attendance (<90%)
      → clamped to 0..100
```

- ≥ 70 = HIGH RISK → automatic admin notification + red pin
- 40–69 = medium (orange pin)
- < 40 = low (green pin)
- Resolving alerts re-computes the score instantly (visible live on the demo!)

---

# 7 — Security: auth, hashing, RBAC

## 7.1 Passwords — PBKDF2-SHA256

- On signup/seed: `hash = PBKDF2-SHA256(password, random_16_byte_salt, 100_000 iterations)`
- Stored as: `100000$salt_hex$hash_hex`
- On login: same computation → constant-time comparison
- **We never store or log plain passwords.** Even we can't read them.
- 100,000 iterations = brute-forcing one password costs 100,000× more compute.

## 7.2 JWT — the session ticket

- After login, the backend signs a token: `{sub: user_id, username, role}`,
  algorithm HS256, 12-hour validity.
- Every request carries `Authorization: Bearer <token>`.
- The backend verifies the signature → **impossible to forge a role without the
  secret key**.
- Demo limitation (we admit it): the secret is hardcoded for the hackathon;
  production = environment variable + rotation.

## 7.3 RBAC — role-based access control

Enforced **on the backend**, not just hidden in the UI:

| Endpoint | Admin | Inspector |
|---|---|---|
| GET /institutes, /reports, /alerts, /cctv | ✅ | ✅ (read-only) |
| POST /analytics/run-anomaly | ✅ | ❌ 403 |
| POST /inspections/assign-random | ✅ | ❌ 403 |
| POST /vc/start | ✅ | ❌ 403 |
| POST /reports | ❌ 403 | ✅ |
| POST /inspections/{id}/start | ❌ | ✅ (own tasks only) |
| POST /alerts/{id}/resolve | ✅ | ❌ 403 |
| POST /alerts/{id}/acknowledge | ❌ | ✅ |

Ownership checks too: an inspector can only start/submit **their own** inspections
(`inspection.inspector_id != user.id → 403`). Tested and proven in our e2e suite.

## 7.4 Data privacy (the DPDP-Act answer)

- All citizen-adjacent data (photos, attendance) stays **on-premise**: SQLite file
  + local uploads folder. No third-party cloud receives anything.
- The only external service is **Jitsi meet.jit.si** for VC rooms (no citizen data
  stored); production would self-host Jitsi on NIC/MeghRaj government cloud.
- AI runs **locally** — no cloud vision APIs touching beneficiary photos.

---

# 8 — Implementation walkthrough (every endpoint, inside-out)

> Full list also lives at http://localhost:8000/docs (auto-generated by FastAPI).

## AUTH
| Endpoint | Inside |
|---|---|
| `POST /login` | find user → PBKDF2 verify → sign JWT {sub, username, role} → return token+role+name |
| `GET /me` | decode JWT → return id, name, role, username, GPS |

## MONITOR
| Endpoint | Inside |
|---|---|
| `GET /institutes` | all institutes → map pins (colour = risk_score) |
| `GET /institutes/{id}` | institute + its inspection history |
| `GET /attendance/analytics/{id}` | 30-day expected/present series → Recharts line chart |
| `GET /cctv/streams` | stream URL list (HLS demo streams + DroidCam placeholder) |

## DETECT
| Endpoint | Inside |
|---|---|
| `POST /analytics/run-anomaly` | **admin only.** IsolationForest over all institutes' 30-day ratios → anomalies get +40 risk & HIGH admin alert |
| `GET /alerts` | latest 50 events incl. acknowledged-by names |

## VERIFY
| Endpoint | Inside |
|---|---|
| `POST /inspections/assign-random` | **admin only.** score inspectors → top-3 → crypto seed → weighted pick → store seed → notify inspector + admins |
| `POST /inspections/{id}/start` | **inspector, own task.** status assigned → in_progress |
| `POST /vc/start` | **admin.** create Jitsi room name → notify admins + all inspectors |

## REPORT
| Endpoint | Inside |
|---|---|
| `POST /reports` | **inspector, own task.** multipart upload: main photo + GPS + checklist (+ optional q0–q4 per-answer photos) → save files → OpenCV face count → flags → risk recompute → HIGH-risk notification (deduped) → status completed → auto "📋 official report generated" admin alert |
| `GET /reports` | all reports w/ inspection_id + inspector_id + `question_photos` map (enables 📷 proof links and "my submissions" filter) |
| `GET /reports/{id}/document` | compiles the OFFICIAL INSPECTION REPORT live: letterhead, institute + inspector details, GPS + maps link, checklist with per-item photos, AI verdict, current risk score, audit seed if random assignment |

**Admin institute management:** `POST /institutes` (admin only) onboards a new
institute (name/district/scheme/GPS/contact); optional flag auto-generates 30
days of healthy attendance so charts and the AI scan work instantly. Powers the
"➕ Add Institute" form in the dashboard Quick Actions.

## ACT
| Endpoint | Inside |
|---|---|
| `POST /alerts/{id}/resolve` | **admin.** resolved=True → risk recompute |
| `POST /alerts/{id}/acknowledge` | **inspector.** acknowledged=True + acknowledged_by |

## NOTIFICATIONS
| Endpoint | Inside |
|---|---|
| `GET /notifications` | my unread: target_user_id==me OR (NULL target AND audience==my role) |
| `POST /notifications/{id}/read` | mark one |
| `POST /notifications/read-all` | mark all mine |

**Frontend polling:** dashboard bell 15 s, alerts page 10 s, field app alerts tab
15 s — chosen over WebSockets for hackathon simplicity; production upgrade path =
FastAPI WebSockets or SSE (we can name it).

---

# 9 — Slide-by-slide PPT mapping (what to SAY)

> Matches the **actual 7-slide deck** (SJB Institute format). Full per-slide
> script with verbatim lines: `docs/PRESENTATION_SCRIPT.md`. Deck slide 4 is
> intentionally skipped in the pitch.

| Deck slide | What we show/say |
|---|---|
| **1 — Title / PS details** | Read PS ID 26095, team, then the one-liner: "DRISHTI gives MoSJE real-time eyes on every institute." |
| **2 — DRISHTI (Proposed Solution)** | Walk the left column top-to-bottom (dashboard → AI hub → field app → analytics), then the middle column: each "How it addresses" box kills one fraud mode (compliance table 2.4: "nothing in the PS is unimplemented"). Right column = innovation: lightweight CPU AI, zero-trust evidence, unified ecosystem. |
| **3 — Technical Approach** | Narrate the five methodology stages left→right: data ingestion → centralized AI engine → automated alert trigger → smart surprise inspection → official dashboard action — this is the 12-step demo loop (TESTING_GUIDE section C). Tech-stack panel = Section 4 summary: FastAPI + React + Flutter + scikit-learn + OpenCV, all open-source, ₹0 licence cost, CPU-only AI. Architecture = Section 3.1: 2 frontends → 1 API → DB + files. |
| **4 — (skipped)** | Intentionally not part of the pitch. |
| **5 — Feasibility & Viability** | Top: technical / operational / economic feasibility (SQLite→PostgreSQL one-line change; stateless API → horizontal scaling; CPU AI → ₹20k machine; Jitsi self-host on NIC). Then each challenge → mitigation pair, honestly: offline caching & sync is a named roadmap item (Section 11); AI bias → human-in-the-loop; hardware → min-spec testing; adoption → three-tap UI. |
| **6 — Impact & Benefits** | Follow the 5-step chain (real-time monitoring → early anomaly detection → targeted surprise inspections → verified digital evidence → transparent welfare delivery), then stakeholders (PMU teams / NGOs & institutes / beneficiaries) and benefit boxes (public trust / fraud prevention / paperless scale — Section 1.4 outcome mapping). Close on the footer: "FROM report-based inspection TO evidence-based continuous verification." |
| **7 — References & Research** | Domain research (MoSJE + DoSJE scheme pages, Digital India, UIDAI) + engineering depth (OpenCV; Ultralytics and WebRTC evaluated for future versions; PostgreSQL scaling path). |

---

# 10 — Judge Q&A bank (50+ questions with model answers)

## Technical architecture

**Q1. Why did you build three separate apps instead of one?**
A: Different users, different contexts. Officials need map+charts+tables on a big
screen (web dashboard). Inspectors need camera+GPS+big buttons on the move
(Flutter). Both share ONE backend so business logic exists once. One codebase
(Flutter) even covers Android + iOS + web browser for the field.

**Q2. Why SQLite and not MySQL/PostgreSQL?**
A: For a hackathon prototype, SQLite means zero installation — the whole database
is one file, so anyone can run the project instantly. We used SQLAlchemy ORM, so
migrating to PostgreSQL for production is a single connection-string change. We
deliberately optimised for demonstrability without compromising the migration path.

**Q3. How does the mobile app talk to the backend?**
A: REST over HTTP with JSON. The app stores a JWT after login and sends it as a
Bearer token on every call. Multipart form-data for photo uploads.

**Q4. Is your data real-time?**
A: Yes for practical purposes — dashboards poll every 10–15 seconds, so new
alerts/evidence appear within one cycle. For sub-second push we'd add WebSockets
(FastAPI supports them natively) — a deliberate prototype simplification.

**Q5. What happens if two officials assign inspections at the same moment?**
A: Each request creates its own Inspection row with its own seed — both are valid,
both auditable. SQLite serialises writes; in production PostgreSQL row-locking and
unique constraints handle concurrency.

**Q6. How do you handle file storage for photos?**
A: Photos are saved to a local `uploads/` directory and served by the backend with
the JWT not required for the demo link. Production: S3-compatible object store
(MinIO on-prem) with signed URLs.

**Q7. What is your API documented with?**
A: FastAPI auto-generates OpenAPI docs at /docs — every endpoint is live-testable
from the browser. It's generated from the code, so it can never go stale.

**Q8. How does the phone know where the server is?**
A: The login screen has a configurable server-address field (remembered on the
device), so any phone can point at any deployment — emulator, LAN PC, or
production domain.

## AI / ML

**Q9. Explain your AI to a non-technical person.**
A: Two AIs. (1) The anomaly detector studies 30 days of attendance at every
institute and flags the one whose pattern looks abnormal compared to its peers —
like a teacher noticing one student's marks suddenly dropping. (2) The proxy
checker looks at the evidence photo and counts human faces; a "field visit" photo
with zero people is suspicious.

**Q10. Why IsolationForest and not linear regression or deep learning?**
A: IsolationForest is built for exactly our case: small tabular data, find
outliers, no labels needed, trains in <1 s, explainable. Deep learning needs
thousands of labelled samples and GPUs; regression predicts values, it doesn't
detect outliers. Right tool, right job.

**Q11. What is "contamination=0.15"?**
A: It tells the algorithm the expected proportion of outliers (~15%). It sets the
sensitivity of the boundary between normal and anomalous.

**Q12. How do you know your AI isn't giving false alarms?**
A: Two ways: the flag is "possible proxy" — a human (admin) reviews and resolves
it; and the seed + fixed random_state make every scan reproducible, so we can
audit why an institute was flagged by re-running it.

**Q13. How does face detection work?**
A: OpenCV's Haar cascade — thousands of simple light/dark rectangle patterns
slid across the image (eye region darker than cheeks, etc.). Where enough
patterns match, there's a face. Runs on CPU in milliseconds, fully offline.

**Q14. What if there are genuinely no beneficiaries in a photo but the visit is
real?**
A: The flag says "possible proxy" — it's a trigger for human review, not a
verdict. The admin calls the institute, verifies, and resolves the alert. We
track both the flag and the human decision.

**Q15. Could someone submit an old photo from their gallery?**
A: In the field app the capture is through the live camera (image_picker with
camera source). For stronger guarantees, production adds EXIF timestamp checks
and geo-fencing against the institute's coordinates.

**Q16. Where does the AI run — cloud or local?**
A: Fully local, on the CPU. No citizen photo ever leaves the government's server.
This is a privacy feature, not just a cost feature.

## Security & privacy

**Q17. How are passwords stored?**
A: PBKDF2-SHA256 with a random 16-byte salt and 100,000 iterations — OWASP-
recommended. We never store or log plain passwords; even the admin can't recover
them, only reset.

**Q18. What is a JWT and why use it?**
A: A signed ticket containing user id + role, valid 12 hours. The server verifies
the signature on every request — roles can't be forged without the secret key.
Stateless: no session table needed.

**Q19. How do you enforce who can do what?**
A: Backend-side RBAC decorators (`require_role`). Inspectors literally get HTTP
403 if they call admin endpoints — we demonstrate this in our test suite. UI
hiding alone is never trusted.

**Q20. Is this compliant with the DPDP Act?**
A: Designed to be: all personal data (photos, attendance) stays on-premise; AI
runs locally; no third-party cloud receives citizen data; access is role-restricted
and audited. Production adds consent capture and retention policies.

**Q21. What about the hardcoded secret key we can see in the code?**
A: Correct — that's a documented demo simplification. Production: environment
variable or vault, plus token rotation and refresh tokens.

**Q22. Can an inspector submit a report for someone else's inspection?**
A: No — the backend checks `inspection.inspector_id == current_user.id` and
returns 403 otherwise. Verified in our automated tests.

---

## Product & government fit

**Q23. How is this better than what MoSJE does today?**
A: Today: announced inspections, paper registers, WhatsApp photos (can be old or
borrowed), months-long reporting. DRISHTI: surprise + live camera + GPS + AI
verification + minutes-level dashboards. Every fraud vector has a counter-measure.

**Q24. NGOs will resist this. How do you handle adoption?**
A: Honest NGOs benefit most — they compete fairly and get faster grant processing
because verified digital evidence replaces repeated physical visits. Also, the
app is designed for inspectors, not NGOs — NGOs need do nothing.

**Q25. What about inspectors who aren't tech-savvy?**
A: The field app is deliberately minimal: login → task list → one capture screen
with three inputs (photo, auto-GPS, yes/no switches). No typing required.

**Q26. What if there's no internet at the institute (rural)?**
A: The prototype needs connectivity at submission. Roadmap: queue reports locally
and sync later (Flutter packages exist), plus offline map caching — stated
honestly as future scope. (This is exactly the "Offline Caching & Automatic
Sync" mitigation box on deck slide 5 — if a judge probes it, give this same
honest answer: capture is already decoupled from sync; queue-and-forward is
the first roadmap item.)

**Q26b. Your slide says offline caching — is it built or not?**
A: Be straight: photo capture is compressed and uploads as soon as the network
allows, but there is no local offline queue in the prototype yet. The
architecture supports it (capture and sync are already separate steps), and
it's the first roadmap item for field rollout. Overclaiming here would cost
more credibility than the gap itself.

**Q27. Can this scale to all of India?**
A: Yes architecturally: stateless FastAPI scales horizontally; PostgreSQL
replaces SQLite; object storage for photos; AI retrains per state. A one-state
pilot runs on a single ₹20k server.

**Q28. What's the running cost?**
A: Software ₹0 (open-source). Hardware: one modest server per state or MeghRaj
cloud. Jitsi self-hosted. Only real cost = maintenance staff.

**Q29. Who maintains it after the hackathon?**
A: Standard FastAPI/React/Flutter — any NIC or vendor team can maintain. We hand
over the repo with auto-generated API docs.

**Q30. What stops the ADMIN from misusing it?**
A: Every admin action is logged with identity + timestamp (assignments carry
audit seeds; resolutions attributed). CSV export enables third-party audit.
Production adds immutable audit logs and dual authorisation.

**Q31. Can this integrate real government CCTV?**
A: Yes — we already play HLS streams, the protocol most IP cameras/NVRs output.
Integration = pointing our stream list at the institute's RTSP-to-HLS gateway
(FFmpeg). Configuration, not new development.

**Q32. Why DroidCam in the demo?**
A: It turns a phone into an IP camera so we can show a REAL live feed on stage
without hardware. Production: institutes' existing CCTV replaces it.

## Process & team

**Q33. How did you divide the work?**
A: Backend / Dashboard / Field app — with the API contract designed first so all
three progressed in parallel. One member owned the AI engine end-to-end.

**Q34. What was your development process?**
A: API-contract-first, vertical slices (endpoint → frontend → test), automated
8-step e2e suite plus Flutter analyze/tests kept green throughout.

**Q35. What would you do differently?**
A: WebSockets instead of polling from day one, and geo-fencing earlier. Both are
known upgrade paths, not rewrites.

**Q36. Did you use paid APIs or pre-built solutions?**
A: None. AI, maps, video, auth — all open-source and self-hosted; only free
public demo streams.

**Q37. Hardest technical problem?**
A: (1) Provably-fair assignment — solved with a stored cryptographic seed making
the lottery replayable. (2) Making face detection meaningful without being a
verdict — solved by framing it as a human-review trigger.

---

## Deeper "what-if" questions (continued)

**Q38. What if an inspector spoofs their phone GPS?**
A: Prototype trusts OS GPS. Production: Android mock-location detection,
server-side geo-fence (reject evidence >500 m from institute), EXIF-GPS
cross-check. All three are named upgrade paths.

**Q39. What if an NGO bribes the inspector?**
A: Random assignment prevents long-term relationships; the stored seed exposes
manipulated draws; the AI proxy check is independent of the inspector's claim;
every action is attributed — collusion leaves a traceable chain.

**Q40. Two institutes at the same location?**
A: Pins overlap visually but are distinct records; filters and the reports list
disambiguate. Production adds slight display jitter.

**Q41. Who decided the risk-score weights?**
A: We did, transparently — and that's the point: policy (weights) is
configuration the department can tune, not hidden code.

**Q42. What does a new institute need before AI can watch it?**
A: ~10+ days of attendance history. Until then the rule-based risk score covers
it — the system degrades gracefully.

**Q43. Hindi / regional languages?**
A: Flutter and React both support localisation; UI strings are centralised —
translation task, not a code change.

**Q44. What happens to data when an NGO's grant is cancelled?**
A: Records retained for audit (never deleted); institute deactivated — stays in
history, leaves active rotation.

**Q45. Backups?**
A: Pilot: SQLite file copy. Production: PostgreSQL scheduled dumps +
object-storage replication.

**Q46. Does the dashboard work on phones?**
A: Responsive, yes — but the field app IS the mobile experience by design.

**Q47. What stops an inspector photographing a wall near their home?**
A: GPS is recorded and reviewed against the institute location. Production:
server-side geo-fence + EXIF checks — explicit roadmap.

**Q48. Why show acknowledged-by names on alerts?**
A: Accountability chain: flag → inspector acknowledged (seen) → official
resolved (acted). Three named humans per incident.

**Q49. What's tested automatically?**
A: 8-step e2e suite (login, RBAC 403s, AI scan, assignment, task retrieval,
evidence upload + proxy detection, VC, alerts) + Flutter analyze/widget tests —
all green.

**Q50. One more day — what would you add?**
A: Server-side geo-fencing, WebSocket push, and the NGO self-service portal.

## Rapid-fire one-liners

- **"Is the AI pre-trained?"** IsolationForest trains fresh on your data each
  scan; the face cascade ships pre-trained inside OpenCV.
- **"Offline mode?"** Roadmap: queue-and-sync.
- **"Push notifications?"** Roadmap: FCM; today in-app polling.
- **"Multi-tenant?"** District/scheme filters now; full multi-tenancy = schema work.
- **"Licence?"** Our code MIT-style; all dependencies open-source.
- **"The eye logo?"** DRISHTI = vision; lotus-eye = the nation watching its schemes.

---

# 11 — Honest limitations & future scope

| Limitation | Why | Future scope |
|---|---|---|
| Polling instead of push | Hackathon simplicity | WebSockets / FCM |
| No offline evidence queue | Needs sync engine | Flutter offline-first packages |
| Haar face detection is basic | CPU-only constraint | Liveness detection, MTCNN |
| No geo-fence yet | Time | Server-side radius check + EXIF |
| Single admin tier | Scope | District/state role hierarchy |
| NGO portal not built | Out of PS core | Compliance self-service view |
| Hardcoded JWT secret | Demo | Env vars + rotation |
| English UI | Time | i18n Hindi + regional |
| SQLite | Simplicity | PostgreSQL + replicas |

**How to present limitations:** "We know exactly where the prototype ends and
production begins — and every gap has a named, non-disruptive upgrade path."
Honesty here builds trust everywhere else.

---

# 12 — Glossary (every term, plain words)

| Term | Plain meaning |
|---|---|
| **API / endpoint** | A URL the app calls to get/send data, like `/login` |
| **JWT** | A signed digital ticket proving who you are; shown on every request |
| **RBAC** | Role-Based Access Control — permissions depend on your role |
| **PBKDF2** | A password-scrambling algorithm; one-way, slow by design |
| **Salt** | Random data mixed into a password before hashing so identical passwords look different |
| **ORM (SQLAlchemy)** | Translates Python classes into database tables/queries |
| **SQLite** | A whole database stored as one file |
| **IsolationForest** | AI that finds "weird" data points by how easily they get isolated |
| **contamination** | The share of data the AI expects to be abnormal |
| **Haar cascade** | OpenCV's pattern-based face detector |
| **Haversine** | Formula for distance between two GPS points on Earth |
| **HLS (.m3u8)** | Streaming video format used by CCTV/IP cameras |
| **DroidCam** | Free app turning a phone into a wireless camera |
| **Jitsi** | Free open-source video-conferencing (self-hostable) |
| **Seed (RNG)** | A number that makes random generation repeatable — our audit proof |
| **Risk score** | 0–100 number summarising how suspicious an institute is |
| **Polling** | Asking the server "anything new?" every few seconds |
| **WebSockets** | Server pushing data instantly (our future upgrade) |
| **CORS** | Browser rule about which websites may call an API |
| **Multipart upload** | Sending a file + form fields in one request |
| **Flutter / Dart** | Google's cross-platform app framework / its language |
| **React / Vite** | Web UI library / its fast build tool |
| **FastAPI / Uvicorn** | Python API framework / the server running it |
| **Geo-fence** | Virtual GPS boundary — "evidence must be within 500 m" |
| **EXIF** | Hidden metadata inside photos (time, GPS, device) |
| **Proxy functioning** | Pretending a scheme is running when it isn't |
| **PMU** | Programme Management Unit — the ministry's field team |

---

*End of the Complete Explanation. Read once, revise Sections 9–10 before the
pitch, and you can answer anything. — Team DRISHTI · SIH 2026 · PS 26095*
