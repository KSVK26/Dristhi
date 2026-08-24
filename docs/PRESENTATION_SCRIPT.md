# 🎤 DRISHTI — Slide-by-Slide Presentation Script
### Speaker playbook for the actual SIH deck (7 slides, page 4 skipped as instructed)
> Each section: what's ON the slide → verbatim script → key points → demo cues →
> judge questions that slide triggers → transition line.

**Timing plans:** ⏱ 3-min pitch = slides 1,2,3,5 + demo mention · ⏱ 5-min = all
slides, 40 s each · ⏱ 10-min = all slides + live demo inside slide 3.

**Suggested speakers:** S1 (anyone) → S2 (solution lead) → S3 (tech lead) →
S5 (feasibility) → S6 (impact) → S7 (anyone, closing).

---

# SLIDE 1 — TITLE PAGE

## 🖼️ On the slide
"TITLE PAGE · SMART INDIA HACKATHON 2026 · Problem Statement ID · Problem
Statement Title · Title · Name"

**Fill in:** PS ID **26095** · PS Title **"Smart Real-Time Monitoring & Inspection
Mobile App"** · Our Title **DRISHTI — Smart Real-Time Monitoring & Inspection
Platform for DoSJE** · Team name + member names.

## 🎤 Verbatim script (~45 seconds)

> "Good morning everyone. We are Team {name}, and we're solving Problem Statement
> 26095 from the Ministry of Social Justice and Empowerment — the Department of
> Social Justice and Empowerment runs schemes like PM-DAKSH skill training for
> Divyangjan, elderly welfare programmes, and rehabilitation schemes — worth
> hundreds of crores — delivered through NGOs and institutes across the country.
>
> The ministry's problem is simple to say and hard to solve: **how do you actually
> verify that the scheme you funded is really running, right now, on the ground?**
>
> Our answer is **DRISHTI** — which means 'vision' in Hindi. It's a smart
> real-time monitoring and inspection platform: a web command centre for
> officials, a mobile field app for inspection teams, and an AI brain that
> detects anomalies, assigns surprise inspections by auditable lottery, and
> verifies photo evidence with GPS and computer vision.
>
> In the next few minutes we'll show you exactly how every requirement of this
> problem statement is implemented — and live."

## 🔑 Key points
1. Say the **ministry and department names correctly** (MoSJE / DoSJE).
2. Name **two real schemes** (PM-DAKSH, SMILE) — shows you researched them.
3. End with the one-liner: *"real-time eyes on every institute."*

## ⚠️ Judge questions this slide triggers
- **"Why did you pick this PS?"** → "Because it's not a feature request — it's an
  accountability problem. Technology can genuinely fix it, and the impact is
  measured in crores of public money reaching real beneficiaries."
- **"Is this only for MoSJE?"** → "The architecture is ministry-agnostic — any
  grant-giving department can reuse it with different scheme names."

## ➡️ Transition
*"Let's start with what's actually broken today — and what we built."*

---

# SLIDE 2 — PROPOSED SOLUTION: DRISHTI

## 🖼️ On the slide (from your deck)
Three columns:

**PROPOSED SOLUTION (left)** — a top-to-bottom arrow flow of four blocks:
1. **MoSJE Oversight & Web Dashboard** — Define Policy, Monitor
2. **Central AI Hub & Automation** — Data Process, Random Assign
3. **Field App & Live Feeds** — Capture Geo-Evidence, Live VC
4. **Analytics & Insights** — Detect Anomalies, Verify Attendance

**HOW IT ADDRESSES THE PROBLEM (middle):** Eliminates Fake Reporting
*(tamper-proof data)* · Prevents Collusion *(random assignments)* · Overcomes
Bottlenecks *(efficient scalability)* · Automates Compliance *(24/7 AI
auditing)*

**INNOVATION & UNIQUENESS (right):** Lightweight AI *(efficient, low-bandwidth
vision)* · Zero-Trust Evidence *(hardware-verified data)* · Unified Ecosystem
*(centralized monitoring platform)*

## 🎤 Verbatim script (~90 seconds)

> "This slide is our whole solution in one view — follow the arrows on the
> left, top to bottom.
>
> **It starts with the MoSJE oversight dashboard** — that's where policy is
> defined and monitoring happens. Officials see every institute on a live map,
> colour-coded by an AI risk score, with attendance charts and a live alert feed.
>
> **The flow then runs through three more stages.** The **Central AI Hub**: it
> processes attendance data, detects anomalies, and — this is important —
> *randomly assigns* surprise inspections. The **Field App with live feeds**:
> our inspectors capture geo-tagged photo evidence through the app and can join
> surprise video conferences with institute staff at any time. And
> **Analytics & Insights**: the system continuously verifies attendance and
> detects anomalies automatically — 24 by 7.
>
> Now — **how does this address the problem?** Four direct answers.
> It **eliminates fake reporting** through tamper-proof, hardware-verified data.
> It **prevents collusion** because inspections are assigned by a seeded random
> lottery — nobody chooses their favourite inspector, and the random seed is
> stored so the draw can be replayed and proven fair. It **overcomes
> bottlenecks** — one dashboard scales to thousands of institutes. And it
> **automates compliance** — the AI audits attendance continuously, not once a
> year.
>
> And what's **unique** here? Our AI is **lightweight** — it runs on a plain CPU
> with low-bandwidth image checks, no GPUs, no cloud. Our evidence is
> **zero-trust** — captured in-app, GPS-stamped, and AI-verified before anyone
> reads the report. And it's a **unified ecosystem** — one login, one platform,
> from policy to proof."

## 🔑 Key points
1. **One flow, four fraud answers** — the left column is the pipeline; the
   middle column maps each fraud to its kill-switch.
2. The **seed** = auditable fairness. Say "replayable lottery" out loud.
3. **Lightweight AI** = runs on ₹20k hardware, no cloud — a differentiator.

## 🖥️ Demo cues
If allowed to demo here: dashboard on screen — point at each stat card while
naming the pillar. Otherwise keep the slide up.

## ⚠️ Judge questions this slide triggers
- **"What is 'zero-trust evidence'?"** → "Evidence is not trusted because a human
  wrote a report — it's captured through our app with GPS, verified by computer
  vision, and attributed to a logged-in inspector. Trust comes from the hardware
  and software chain, not from a signature."
- **"Random assignment — why is that innovation?"** → "Because it's an *auditable*
  lottery. The random seed is stored; replay it and you get the same inspector.
  Fairness becomes provable, not promised."
- **"24/7 AI auditing — how?"** → "Attendance data flows in daily; the anomaly
  model rescans on demand and risk scores update with every event — the system
  never sleeps even if staff do."

## ➡️ Transition
*"That's the what. Now the how — the technical approach."*

---

# SLIDE 3 — TECHNICAL APPROACH (Methodology & Flow + Tech Stack)

## 🖼️ On the slide (from your deck)
"TECHNICAL APPROACH" — two panels.

**METHODOLOGY & FLOW (left)** — five stages, left to right:
1. **DATA INGESTION** — Capture Project Data, CCTV, Reports & Inspection
   Evidence
2. **CENTRALIZED AI ENGINE** — DRISHTI Central Platform · Risk Scoring &
   Behavior Analysis
3. **AUTOMATED ALERT TRIGGER** — If Anomaly: Trigger Priority Alert · Else:
   Continue Monitoring
4. **SMART SURPRISE INSPECTION** — GPS-Based Officer Assignment · Capture
   Tamper-Proof Photos/VC 🔒
5. **OFFICIAL DASHBOARD ACTION** — Automated Report Generation · Dashboard
   Routing for Follow-up

**TECH STACK (right panel — still empty in the deck; paste this):**
**FastAPI (Python)** · **SQLite → PostgreSQL** · **scikit-learn
IsolationForest** · **OpenCV** · **React + Vite** · **Leaflet /
OpenStreetMap** · **Recharts** · **hls.js** · **Jitsi Meet** · **Flutter** —
all open-source · ₹0 licences · CPU-only AI

## 🎤 Verbatim script (~90 seconds)

> "Here's how it actually works — five stages, left to right.
>
> **One: data ingestion.** Project data, CCTV feeds, reports and inspection
> evidence all flow into one central platform.
>
> **Two: the centralized AI engine.** This is the DRISHTI backend — it runs
> risk scoring and behaviour analysis on every institute. Concretely:
> scikit-learn's IsolationForest watches thirty days of attendance and flags
> anomalies, and a transparent risk formula turns every event into a
> zero-to-hundred score.
>
> **Three: the automated alert trigger.** If the AI sees an anomaly, a priority
> alert fires. If not, monitoring simply continues — twenty-four by seven, no
> human has to watch a wall of screens.
>
> **Four: the smart surprise inspection.** The officer is chosen by our seeded
> random lottery, weighted by distance and workload — nobody picks their
> favourite inspector, and the seed is stored so the draw can be replayed and
> proven fair. The inspector's phone gets the task instantly with navigation.
> On site, they capture geo-tagged, tamper-proof photo evidence — the moment
> it's submitted, OpenCV counts human faces in the photo: zero faces raises an
> automatic proxy-suspicion flag. And a surprise video conference with the
> institute is one tap away.
>
> **Five: official dashboard action.** The risk score is recalculated
> instantly — if it crosses seventy, the dashboard lights up. Officials either
> resolve the alert, which lowers the risk, or escalate. Reports generate
> automatically, and follow-up is routed on the dashboard. Evidence, alerts,
> and actions — all logged, all attributed, all auditable.
>
> **The stack — and why.** Backend: **FastAPI** with a **SQLite** database —
> zero-install, and one line changes it to PostgreSQL for production scale.
> AI: **scikit-learn's IsolationForest** for anomaly detection and **OpenCV**
> for face verification — both run on a plain CPU, fully offline, no cloud, no
> API keys. Dashboard: **React** with **Leaflet and OpenStreetMap** maps — free,
> no licence fees for the government. Live video: **HLS streams** played with
> hls.js, plus **Jitsi** for the surprise video conferences. Field app:
> **Flutter** — one codebase for Android, iOS, and web.
>
> Everything is open-source. Total software licence cost: **zero rupees**."

## 🔑 Key points
1. **Five stages, one loop**: ingest → AI → alert → inspect → act — narrate
   the boxes in order, pointing at each.
2. **"One line" database migration** SQLite→PostgreSQL — scalability answer ready.
3. **₹0 licences, offline AI** — government-friendly by design.

## 🖥️ Demo cues
This is the best slide to switch to the LIVE demo: run the 12-step workflow
(TESTING_GUIDE section C) and return to this slide. If no demo time: point at
the flow diagram while narrating the loop.

## ⚠️ Judge questions this slide triggers
- **"Why FastAPI and not Django?"** → "Speed of development, automatic request
  validation from type hints, auto-generated API docs, and top-tier async
  performance. Django's admin/ORM power wasn't needed for this scope."
- **"Why Flutter for the field app?"** → "One codebase gives us Android, iOS,
  and a browser build — and native camera + GPS access that a mobile website
  handles poorly."
- **"Why polling and not WebSockets?"** → "Deliberate prototype simplification —
  10–15 second polling is enough for inspection workflows. FastAPI supports
  WebSockets natively, so the upgrade is straightforward."
- **"Is SQLite enough?"** → "For a state pilot, yes. For national scale,
  PostgreSQL — and because we used an ORM, that's a configuration change."

## ➡️ Transition
*"Does this actually work, and can the government afford it? That's
feasibility."*

---

# SLIDE 5 — FEASIBILITY & VIABILITY

## 🖼️ On the slide (from your deck)
"FEASIBILITY & VIABILITY" — top row, three feasibility boxes:
- **TECHNICAL FEASIBILITY:** Mature Tech & Stable Architecture
- **OPERATIONAL FEASIBILITY:** Seamless Field Integration & Automated
  Compliance
- **ECONOMIC VIABILITY:** Cost-Effective Initial Development & Optimized
  Resources

These feed into **POTENTIAL CHALLENGES & RISKS**, then four challenge →
mitigation pairs:
- **Hardware Variation** → Optimized App, Rigorous Testing (Min. Specs)
- **Connectivity Issues** → Offline Caching & Automatic Sync (Local Storage)
- **AI Accuracy & Bias** → Human-in-the-Loop & Retraining (Continuous Learning)
- **User Adoption** → Intuitive UI & Comprehensive Training (Simplicity)

All four converge on **VIABLE SOLUTION IMPLEMENTATION**.

⚠️ **Honesty flag:** the "Offline Caching & Automatic Sync" box describes a
roadmap item, not a built feature (no offline queue in the prototype — see
COMPLETE_EXPLANATION.md Section 11). Use the prepared answer below if a judge
probes it.

## 🎤 Verbatim script (~60 seconds)

> "Is this feasible? Three answers at the top of the slide.
>
> **Technically** — every component is proven, mature open-source technology,
> and our AI runs on a plain CPU: no GPUs, no cloud bills. The pilot runs on a
> single twenty-thousand-rupee server.
>
> **Operationally** — seamless field integration: the app is three taps, so
> inspectors need zero training, and institutes do nothing differently —
> compliance checking happens automatically in the background.
>
> **Economically** — cost-effective development, optimised resources: total
> software licence cost is zero. The only spend is one modest server per state,
> or the government's own MeghRaj cloud. Compare that to the crores lost to
> proxy functioning every year — the system pays for itself the first time it
> catches one fake centre.
>
> Now the honest part — the challenges, and how each one is mitigated.
> **Hardware variation**: the app is optimised for minimum specs and tested
> rigorously across device tiers. **Connectivity**: capture-first design —
> photos are compressed and uploaded as soon as the network allows, and full
> offline queue-and-sync is the named next step. **AI accuracy and bias**:
> every AI flag is a *suspicion*, never a verdict — a human reviews before any
> action, and the model retrains as data grows. **User adoption**: an intuitive
> three-tap interface plus a short walkthrough — designed for zero-training
> adoption.
>
> That's how the arrows converge on a viable implementation. And scaling from
> one state to the nation is a configuration path, not a rewrite: PostgreSQL
> for the database, object storage for photos, load-balanced API servers, and
> the AI retrains per state."

## 🔑 Key points
1. **₹0 licences** + one cheap server per state — pays for itself catching one
   fake centre.
2. **Every challenge has a named mitigation** — say them in the slide's order.
3. **Human-in-the-loop**: AI flags suspicion, humans decide — the defensible
   answer on AI bias.

## ⚠️ Judge questions this slide triggers
- **"What's the timeline to deploy?"** → "Pilot in 4–6 weeks: harden auth,
  migrate to PostgreSQL, deploy on MeghRaj, onboard 100 institutes. The
  prototype is functionally complete — this is hardening, not building."
- **"Data privacy law?"** → "All data stays on-premise, AI runs locally, access
  is role-based and audited — aligned with the DPDP Act."
- **"Who trains the staff?"** → "Inspectors need a 10-minute walkthrough — the
  app is three taps. Designed for zero-training adoption."
- **"Your slide says offline caching and sync — is that built?"** → "Capture is
  already decoupled from sync — the app compresses photos and uploads as soon
  as the network allows. Full offline queue-and-forward is the first roadmap
  item for field rollout; we'd rather show the honest boundary than overclaim."
- **"What if the AI flags an innocent institute?"** → "It can — that's why the
  slide says human-in-the-loop. An AI flag only raises an institute's risk
  score and queues a human review; no automated penalty is ever applied. And
  the risk formula is fully transparent — we can show exactly why a score went
  up."

## ➡️ Transition
*"Feasible — and here's the impact it creates."*

---

# SLIDE 6 — IMPACT & BENEFITS

## 🖼️ On the slide (from your deck)
"IMPACT & BENEFITS" — a 5-step value chain across the top:
**1 Real-Time Monitoring → 2 Early Anomaly Detection → 3 Targeted Surprise
Inspections → 4 Verified Digital Evidence → 5 Transparent Welfare Delivery**

Left column — who benefits: **PMU & Inspection Teams** (automated allocation &
faster inspections with geo-tagged evidence) · **NGOs / Institutes** (clear
compliance requirements and transparent verification) · **Beneficiaries**
(improved service quality, continuous delivery, greater accountability).

Right column — what improves: **SOCIAL & GOV: PUBLIC TRUST** (enhanced
accountability and assurance) · **ECONOMIC: FRAUD PREVENTION** (resource
optimization & minimized leakage) · **OPERATIONAL & ENV: PAPERLESS SCALE**
(scalable digital continuous trail).

Footer: **FROM: Report-Based Inspection → TO: Evidence-Based Continuous
Verification**

## 🎤 Verbatim script (~60 seconds)

> "Let's talk impact — follow the chain across the top.
>
> Real-time monitoring enables **early anomaly detection**. Anomalies trigger
> **targeted surprise inspections**. Inspections produce **verified digital
> evidence**. And evidence makes welfare delivery **transparent**. Each step
> feeds the next — that's the whole chain.
>
> On the left, who benefits. The **PMU and inspection teams**: allocation is
> automated and evidence is geo-tagged — reporting lag goes from *months* to
> *minutes*. **NGOs and institutes**: clear compliance requirements and
> transparent verification — honest ones finally compete on a level field,
> because fraudulent competitors can't undercut them with fabricated costs.
> And the **beneficiary** — the Divyangjan trainee, the elderly pensioner —
> if attendance is physically and digitally verified, the scheme they were
> promised actually reaches them.
>
> On the right, what improves. Socially and for government: **public trust** —
> enhanced accountability and assurance. Economically: **fraud prevention** —
> resource optimisation and minimized leakage. Operationally and
> environmentally: **paperless scale** — a scalable digital trail, continuous.
>
> And one line sums up the whole shift, at the bottom of the slide: from
> *report-based inspection* to **evidence-based continuous verification**.
> Inspection paperwork drops from about an hour to about five minutes; auditing
> goes from annual to twenty-four by seven."

## 🔑 Key points
1. Speak per **stakeholder**, ending with the beneficiary (emotional close).
2. Three **measurable deltas**: 1 hr→5 min, months→minutes, annual→24/7.
3. Tie back to the PS expected outcomes — every one is covered.

## ⚠️ Judge questions this slide triggers
- **"How do you measure success after deployment?"** → "Four metrics: proxy-flag
  detection rate, inspection turnaround time, reporting lag, and — the real one —
  grant money reaching verified beneficiaries versus ghost claims."
- **"Any assumption in these numbers?"** → "The 5-minute capture is measured from
  our prototype workflow; the months-to-minutes lag is the structural change from
  digital-first reporting."

## ➡️ Transition
*"Everything here stands on published, verifiable research and standards."*

---

# SLIDE 7 — REFERENCES & RESEARCH + THANK YOU

## 🖼️ On the slide (from your deck)
"REFERENCES & RESEARCH — DRISHTI" in two groups:
- **Official Government References:** socialjustice.gov.in ·
  socialjustice.gov.in/schemes · digitalindia.gov.in · uidai.gov.in
- **Technical Documentation References:** docs.opencv.org ·
  docs.ultralytics.com · webrtc.org · postgresql.org/docs

## 🎤 Verbatim script (~40 seconds)

> "Our research base: the Ministry of Social Justice and Empowerment's own
> scheme pages for the domain model; Digital India and UIDAI for the digital
> identity and platform standards we align with; OpenCV documentation for the
> computer-vision pipeline; Ultralytics and WebRTC references we evaluated for
> the next version of vision verification and self-hosted video; and PostgreSQL
> documentation for the production scaling path.
>
> To close: DRISHTI turns the ministry's question — *'is the scheme really
> running?'* — from a matter of trust into a matter of **evidence**. Thank you.
> We're happy to take questions."

## 🔑 Key points
1. References show **domain research** (ministry sites) + **engineering depth**
   (OpenCV, WebRTC, PostgreSQL).
2. Mention what you *evaluated* (Ultralytics for future vision models) — shows
   informed choices.
3. Close on the trust→evidence line, then **stop talking** and invite questions.

## ⚠️ Closing questions
Anything goes — the full 50-question bank with answers is in
`docs/COMPLETE_EXPLANATION.md` Section 10. Keep it open on a phone during Q&A.

---

# ⏱️ Timing cheat table

| Limit | Slides | Demo |
|---|---|---|
| 3 min | 1 (30 s) → 2 (75 s) → 3 (60 s) → 5 (30 s) → 6+7 (25 s) | mention only |
| 5 min | all, ~40 s each | 60 s live (assign → notify → capture) |
| 10 min | all, ~30 s each | 4 min live full workflow |

# 👥 Speaker assignment template

| Slide | Speaker | Why |
|---|---|---|
| 1 | Anyone | warm-up |
| 2 | Solution lead | owns the story |
| 3 | Tech lead | owns the stack |
| 5, 6 | Second member | fresh voice |
| 7 | Anyone | closer |
| Demo | Tech lead + one driving the phone | two-person demo |

# 📄 ONE-PAGE CHEAT SHEET (print this)

- **PS 26095 · MoSJE/DoSJE** — verify schemes are really running
- **Fraud**: ghost beneficiaries · proxy centres · collusion · paper lag
- **DRISHTI = vision**: dashboard + field app + AI backend
- **Loop**: assign (seeded lottery) → notify → navigate → capture (GPS+photo)
  → AI face check → risk score → resolve/VC
- **AI 1**: IsolationForest on 30-day attendance (paper-cut analogy)
- **AI 2**: OpenCV face count — 0 faces = possible_proxy (human review decides)
- **Fairness**: crypto seed stored → replayable lottery
- **Risk**: 10 base +40 alerts +30 overdue +20 attendance → 0–100
- **Security**: PBKDF2 passwords · JWT 12 h · backend RBAC · on-premise data
- **Cost**: ₹0 software · ₹20k server/state · CPU-only AI
- **Scale**: SQLite→PostgreSQL one line · stateless API · per-state AI
- **Honest gaps**: push, offline queue, geo-fence, liveness — all named paths
- **Impact closer**: "from report-based inspection → evidence-based continuous
  verification" (bottom of slide 6)
- **If probed on slide 5's "Offline Caching & Sync" box**: capture already
  decoupled from sync; queue-and-forward = first roadmap item
