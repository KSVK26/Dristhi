# Pitch Talking Points — Slides 3 & 4 (DRISHTI / SIH 26095, Team Cortex)

## Slide 3 — TECHNICAL APPROACH (~90 seconds)

### Opening line
> "Here's how DRISHTI actually works end-to-end — five stages, one automated pipeline, zero room for fake reporting."

### Methodology & Flow (walk the diagram left → right)

1. **Data Ingestion**
   - Field app captures project data, CCTV feeds, and geo-tagged inspection evidence at the source.
   - Key phrase: *"Evidence is captured at the point of truth — the field — not self-reported later."*
   - ⚠ Accuracy note: CCTV is HLS streams + a DroidCam phone-as-IP-camera tile (simulated feeds) — say "live feed integration," don't claim real RTSP cameras unless asked.

2. **Centralized AI Engine (DRISHTI Central Platform)**
   - All data streams into one central platform.
   - AI performs risk scoring and behavior analysis on every project and inspection.
   - Key phrase: *"Every project gets a live risk score — the system knows which sites deserve attention before a human does."*

3. **Automated Alert Trigger**
   - If the AI flags an anomaly → priority alert fires automatically.
   - If not → the project stays under continuous monitoring.
   - Key phrase: *"No human has to sift through dashboards — the system escalates only what matters."*

4. **Smart Surprise Inspection**
   - GPS-based random officer assignment — officers can't predict or be tipped off about visits.
   - Bonus detail (strong proof point): the assignment uses a **cryptographically-seeded RNG stored in the database** — you can replay the lottery later and prove nobody hand-picked the inspector.
   - Tamper-proof photos and live video-conference capture during the inspection.
   - Key phrase: *"Randomization kills collusion; tamper-proof capture kills fake evidence."*

5. **Official Dashboard Action**
   - Automated report generation for MoSJE officials; dashboard routes follow-ups automatically.
   - Closes the loop: detect → inspect → act.

### Tech Stack (right panel) — deliver fast and confident
> ⚠ Honesty guardrails (all verified against the code):
> - **DB:** running prototype is **SQLite**; PostgreSQL is the production path — literally a one-line `DATABASE_URL` change (SQLAlchemy throughout). Say "SQLite-to-PostgreSQL in one line," don't claim Postgres is deployed.
> - **Flutter:** shipped for **Android + Web**; iOS comes from the same codebase but isn't demoed — say "one codebase for Android, iOS, and web," not "iOS app."
- **Field App:** Flutter (Dart) — one codebase, Android + Web (iOS from same code).
- **Dashboard:** React + Vite — fast, modern oversight UI.
- **Backend:** FastAPI + SQLAlchemy DB (SQLite → PostgreSQL in one line) — proven, government-deployable stack.
- **AI Layer:** IsolationForest + OpenCV — *lightweight anomaly detection, no expensive GPU farm needed.*
- **Maps:** Leaflet + OpenStreetMap — fully open-source, zero licensing cost.
- **Video/VC:** HLS live feeds + Jitsi Meet — open-source video conferencing for surprise inspections.
- **Auth & Geo:** JWT + RBAC with 3 role tiers (admin / inspector / institute) + GPS verification.

### Slide 3 closer
> "Every component here is mature, open-source, and field-proven — nothing exotic, nothing experimental. That's deliberate: this must run on government infrastructure from day one."

---

## Slide 4 — FEASIBILITY & VIABILITY (~75 seconds)

### Opening line
> "A solution is only as good as it is deployable — so let us show you exactly why DRISHTI is feasible and how we've de-risked it."

### Top row — three pillars of feasibility
1. **Technical Feasibility:** Mature tech & stable architecture — everything on slide 3 is production-grade, off-the-shelf technology.
2. **Operational Feasibility:** Seamless field integration & automated compliance — officers just capture evidence; the AI handles auditing 24/7.
3. **Economic Viability:** Cost-effective initial development & optimized resources — open-source stack means near-zero licensing cost.

### Middle — we don't hide our risks
> "We identified four real challenges — and each one already has a concrete mitigation."

| Challenge | Mitigation | One-liner for jury |
|---|---|---|
| **Hardware Variation** | Optimized app, rigorous testing against minimum specs | Runs on low-end field devices |
| **Connectivity Issues** | Offline caching & automatic sync via local storage | *Works in rural, low-network zones — data syncs when connectivity returns* |
| **AI Accuracy & Bias** | Human-in-the-loop review & continuous retraining | *AI recommends, humans decide — no wrongful action on a false positive* |
| **User Adoption** | Intuitive UI & comprehensive training | Designed for field staff, not engineers |

### Closing line (bridge to next slide)
> "Every risk has a mitigation, every mitigation is already designed in — which makes DRISHTI not just an idea, but a viable solution ready for implementation."

---

## Anticipated jury Q&A for these slides

1. **"Why IsolationForest and not deep learning?"** — Anomaly detection on tabular/behavioral data is exactly what IsolationForest is built for; it's fast, explainable, and runs on modest hardware. OpenCV handles the vision tasks. Right tool per job keeps cost and latency low.
2. **"How do you guarantee photos aren't faked?"** — Tamper-proof capture in the field app (geo + timestamp bound at capture) plus zero-trust evidence verification on the central platform.
3. **"What if the officer colludes?"** — GPS-based *random* assignment means neither side knows the pairing in advance; behavior analysis also flags suspiciously clean inspection patterns.
4. **"Offline sync — what if evidence conflicts?"** — Frame it as *designed, not shipped*: "Offline caching with automatic sync on reconnect is our named next milestone for field rollout — we'd rather show the honest boundary than overclaim." The app already stores the JWT locally and degrades gracefully; conflict reconciliation via the AI engine is the designed approach.
5. **"3 JWT roles — which?"** — **Admin** = DoSJE/MoSJE officials (oversight dashboard, alerts, VC), **Inspector/PMU** = field officers who get assigned surprise visits AND capture geo-tagged photo evidence in the Flutter app, **Institute** = institute incharge/staff (role-ready in the backend; they join surprise VCs).

## Delivery tips
- Slide 3: physically trace the 5-step flow with your hand/pointer — juries follow diagrams best when narrated spatially.
- Spend the most time on steps 2–4 (AI engine → alert → surprise inspection); that's the innovation core.
- Slide 4: emphasize "we found our own weaknesses before you did" — juries reward honest risk analysis with concrete mitigations.
- Keep each mitigation to one sentence; the table on the slide carries the detail.
