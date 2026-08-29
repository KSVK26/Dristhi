# DRISHTI — Demo Guide

> The exact runbook for the live demo. Read once, then follow it.
> If you only have 5 minutes before the judges arrive, jump to
> **§4 Golden Flow**.

---

## 1. URLs (live, public)

| Service | URL | Account |
|---|---|---|
| Dashboard | https://drishti-dashboard.onrender.com | `admin / admin123` |
| Field app | https://drishti-field-app.onrender.com | `ravi / inspector123` |
| Backend docs | https://drishti-api-u0qf.onrender.com/docs | (Swagger UI) |

> **⚠️ Free-tier reminder:** the backend sleeps after ~15 min idle.
> Hit `https://drishti-api-u0qf.onrender.com/` **once 2 min before
> demo** to wake it (cold start = ~50s). If a button "doesn't work" the
> first time you click, just click again.

## 2. T-minus checklist (run this the night before)

```bash
# 1. Code is on the right SHA
cd D:\Projects\SIH\SIH26095
git status            # → nothing to commit
git log --oneline -3  # → top commit should be a502cfd or later
```

- [ ] All 3 services return HTTP 200 (curl each)
- [ ] No errors in the latest commit
- [ ] Demo accounts still work
- [ ] At least 3 reports exist in the DB (so the Reports tab isn't empty)

## 3. T-minus 5 minutes

1. Open `https://drishti-api-u0qf.onrender.com/` in a tab → wake the backend
2. Open `https://drishti-dashboard.onrender.com/` in a tab → login as `admin / admin123`
3. Open `https://drishti-field-app.onrender.com/` in a separate window/tab → login as `ravi / inspector123`
4. Have `docs/SECURITY_QA.md` open in a third tab — judges can probe, you can run the proofs live

## 4. The 5-minute Golden Flow

Each step has a **what to say** and **what to click**. Time budget: 5 minutes total.

### Step 1 — Login (10s)
- **Say:** "DRISHTI is a centralized monitoring platform with two apps. Admins see this dashboard, PMU inspectors use the field app on their phones."
- **Click:** already on the dashboard → already logged in. (If you logged out, use `admin / admin123`.)

### Step 2 — Live Map & explainable risk (45s) ⭐
- **Say:** "Every dot is an institute. Colour is the AI risk score — green is healthy, red needs attention. The score is **explainable**: click any pin to see exactly why it's high."
- **Click:** any red pin. The side panel shows:
  - Risk Score: NN/100
  - **Why this score?** panel: bullet list of contributing factors, each with `+points`
  - A 30-day attendance chart
- **If asked "can the score be gamed?":** every factor is a *real* DB event (alert, inspection, attendance log) — there's no knob an admin can twist to lower it without fixing the cause.

### Step 3 — AI Anomaly Scan (20s)
- **Say:** "IsolationForest on 30 days of attendance per institute. Outliers get flagged automatically — we don't need a human to spot them."
- **Click:** the **🤖 Run AI Anomaly Scan** button in the toolbar. A toast appears with flagged institutes.
- **Demo note:** if no institutes are flagged, the scan is still working — toast says "no anomalies found", which is itself a useful result.

### Step 4 — Assign Random Inspection (30s) ⭐
- **Say:** "Surprise inspections prevent collusion. An inspector can't pre-arrange with the institute if the assignment is *random* and *auditable*."
- **Click:** (1) pick an institute from the dropdown, (2) **🎯 Assign Random Inspection**. The response shows: the inspector's name, distance, and the **audit seed** — anyone can replay that seed and reproduce the choice.
- **If asked "what if a corrupt admin changes the seed?":** the seed is stored on the row before assignment, so tampering is detectable.

### Step 5 — Inspector sees it live (20s) ⭐
- **Switch to the field-app tab.**
- **Say:** "Watch — without me refreshing, the new task appears on the inspector's phone within 20 seconds. This is the live cross-device sync judges specifically asked for."
- Wait 20s → the new task card appears.
- **If it doesn't appear instantly:** the live sync polls every 20s, so wait or hit refresh.

### Step 6 — Capture evidence (60s)
- **Click:** the new task → **Capture Evidence**
- **Say:** "Five yes/no questions about physical presence + a photo. The photo is hashed client-side and re-verified server-side. Zero faces in the photo triggers an automatic POSSIBLE_PROXY alert."
- **Click:** tap the photo box → browser will offer file upload (web) or camera (phone). Pick any photo of a person. Toggle a few answers. Tap **Submit Geo-Tagged Report**.
- **What you'll see:** ✅ Report Submitted dialog. If the photo has no human face, you'll see ⚠ AI Flag Raised instead — that one is more dramatic on stage.

### Step 7 — Dashboard sees it + risk drops (30s) ⭐
- **Switch to the dashboard tab.**
- **Click:** Alerts. The proxy_suspect or inspection_completed event appears at the top.
- **Click:** Mark Resolved → the risk score visibly drops on the map pin.
- **Say:** "Closing the loop: the same data, on two devices, reconciled in seconds. No paperwork, no call to the institute, no back-and-forth on WhatsApp."

### Step 8 — Reports gallery + CSV (30s)
- **Click:** **Reports** tab.
- **Say:** "Every evidence photo is geo-tagged. Click any photo — the map shows exactly where it was taken."
- **Click:** any photo → it expands to show a mini-map with the GPS pin.
- **Click:** **⬇ Export CSV** → the full register downloads. The CSV is your audit log. *(This is the "transparency register" answer to the PS's expected outcome.)*

### Step 9 — CCTV + surprise VC (45s) ⭐
- **Click:** **CCTV Feeds** tab.
- **Say:** "Three self-hosted institute cameras — students in a classroom, hallway, corridor — with live timestamps and recording indicators. Camera four is a real DroidCam phone feed if you have one connected."
- **Click:** **LIVE SITE CAMERA (DroidCam)** → paste your phone's DroidCam URL if you brought one; otherwise just point at the three demo tiles and the surveillance overlay.
- **Switch back to the Map**, pick an institute, **📞 Start Surprise VC** → a Jitsi room opens in a new tab. Inspector gets the same URL.

### Step 10 — Security one-liner (if asked, 30s)
- **Say:** "Five layers. Field: signed-only app, GPS-stamped, AI face-check. Network: TLS 1.3, Jitsi E2E, JWT in headers. Server: bcrypt + RBAC + rate-limit + security headers. Storage: encrypted + backed up + append-only audit. Audit: every action recorded with user + time + location + fairness seed."
- **Show:** `docs/SECURITY.md` and `docs/SECURITY_QA.md`.

## 5. Likely judge questions + your answer

| Q | A (one-liner) |
|---|---|
| "How do you protect data?" | See §4 step 10. Full model in `docs/SECURITY.md`. |
| "What if a phone is stolen?" | 8h/24h JWT expiry + can be revoked server-side + photo hash means tampered photos are rejected. |
| "Can an inspector fake evidence?" | Server-side MIME sniff + 5 MB cap + AI face-count (0 faces = POSSIBLE_PROXY alert). |
| "How do you prevent collusion?" | Seeded RNG, seed stored on the row, anyone can re-run it. |
| "Show me the security headers" | Open `docs/SECURITY_QA.md` §1, run the curl, show the output. |
| "Is this HIPAA-grade?" | "For PII, we use Supabase at-rest encryption + HTTPS in transit + bcrypt at rest. We document HIPAA-relevant gaps in `docs/SECURITY.md` §9." |
| "What if the AI is wrong?" | AI flags anomalies; only humans resolve them. Every resolution is logged. |
| "Can you run offline?" | The dashboard needs the backend; the field app gracefully degrades to a "Server unreachable" message. Queue-and-forward is a v0.3.0 item. |
| "What's your business model?" | "Open-source prototype. If we win, we want to deploy it via the DoSJE on their own infra — no vendor lock-in." |
| "Why three apps?" | "Each is fit-for-purpose. Admins need a big screen with maps and charts; PMU inspectors need a one-handed phone app. Sharing one app would compromise both." |

## 6. If something breaks mid-demo

| Symptom | Fix |
|---|---|
| "All institutes grey on map" | Click a pin; if score is 10 (no issues), that's correct. If everything is grey, run AI Anomaly Scan to populate. |
| "AI Anomaly Scan says no anomalies" | That's actually the correct answer if everything is healthy — `seed.py` re-generates a fresh anomaly for one institute. |
| "Inspector task not appearing" | Field app polls every 20s. Click refresh, or go to a new tab and back. |
| "Backend slow on first call" | Free-tier cold start (~50s). Hit it again. |
| "Photo upload fails" | The web build needs a real image (not a fake byte stream). Use the file picker, or pick a random photo off the web. |
| "I'm logged in as admin but can't assign" | Try refreshing the page — sometimes the JWT in localStorage expires. |
| "PowerShell / terminal weirdness" | Restart the backend with `Start-Process` from a clean PowerShell. Don't try to kill it from the same window. |

## 7. After the demo

- [ ] Run `docs/SECURITY_QA.md` once to confirm the deployment is still secure
- [ ] `git status` → `nothing to commit, working tree clean`
- [ ] Pin the working commit SHA in `docs/planv5.md` so the next iteration starts from a known point
- [ ] If a judge asked something you couldn't answer, add it to §5 of this file for next time