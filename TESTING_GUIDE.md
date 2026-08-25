# 🧪 DRISHTI — Teammate Testing Guide

**Welcome!** This guide is written for someone who has **never done coding or testing
before**. Follow it top-to-bottom and tick the checkboxes. If something doesn't match
what this guide says, that's exactly what we want to know — Section D and E show you
how to report it.

---

## 📑 Table of Contents

| Section | What's inside | Time needed |
|---|---|---|
| **A1** | What is DRISHTI? | 2 min |
| **A2** | Install everything (one time) | 20–40 min |
| **A3** | Start the 3 apps | 5 min |
| **B1–B12** | Feature-by-feature testing checklist | 30–45 min |
| **C** | Full end-to-end workflow (the story) | 10 min |
| **D** | Error encyclopedia (if anything breaks) | as needed |
| **E** | Report issues & suggest features | 10 min |

---

# A1 — What is DRISHTI? 👁️

DRISHTI is a monitoring platform for the **Ministry of Social Justice and
Empowerment (MoSJE)**. It has **three apps** that talk to each other:

| # | App | Where it runs | Who uses it | What it's for |
|---|---|---|---|---|
| 1 | **Backend** (invisible) | your PC, port 8000 | nobody directly | the "brain" — stores data, runs the AI |
| 2 | **Dashboard** | your browser, port 5173 | DoSJE officials (`admin`) | monitor institutes, assign inspections, see alerts |
| 3 | **Field App** | your browser, port 5174 (or a phone) | PMU inspectors (`ravi`) | see assigned tasks, capture photo evidence |

**Two test logins you'll use constantly:**

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | DoSJE official — full control |
| `ravi` | `inspector123` | PMU field inspector |

> 💡 **What is "localhost"?** Your PC has addresses like a house has a door number.
> `localhost:5173` means "this app, on my own computer, door number 5173". When you
> open it in your browser, you're visiting the app running on *your* machine.

---

# A2 — Install everything (ONE TIME only)

Open **PowerShell**: press the **Windows key ⊞**, type `powershell`, press **Enter**.
A blue/black window with `PS C:\Users\YourName>` is your terminal — you'll type
commands here and press **Enter** after each one.

## ✅ A2.1 — Check what you already have

Type each command below. Compare with the "should say" column.

| Type this | Should say something like | If it says "not recognized" |
|---|---|---|
| `python --version` | `Python 3.14.6` (any 3.10+) | do A2.2 |
| `node --version` | `v24.19.0` (any 18+) | do A2.3 |
| `git --version` | `git version 2.x` | do A2.4 |
| `flutter --version` | `Flutter 3.47.1` | do A2.5 |

## ✅ A2.2 — Install Python (skip if A2.1 worked)

1. Go to **https://www.python.org/downloads/** and click the big yellow **Download Python** button.
2. Run the downloaded file. **IMPORTANT:** on the first screen, tick the checkbox
   ☑ **"Add python.exe to PATH"** at the bottom — forgetting this is the #1 setup error.
3. Click **Install Now**, wait, then **close and reopen PowerShell**.
4. Verify: `python --version`

## ✅ A2.3 — Install Node.js (skip if A2.1 worked)

1. Go to **https://nodejs.org/** → download the **LTS** version.
2. Install with all defaults → **close and reopen PowerShell**.
3. Verify: `node --version`

## ✅ A2.4 — Install Git (skip if A2.1 worked)

1. Go to **https://git-scm.com/downloads** → Windows → install with all defaults.
2. **Close and reopen PowerShell**. Verify: `git --version`

## ✅ A2.5 — Install Flutter (only needed for the Field App)

> ⚠ This is the heaviest install (~700 MB download, 10–20 min). If you only want to
> test the **dashboard**, you can skip A2.5 and A3.3 entirely and ask the team lead
> for a shared link to the already-running field app.

1. Go to **https://docs.flutter.dev/get-started/install/windows** and follow the
   "Simple install" (it downloads a zip).
2. Extract the zip to `C:\Users\YourName\flutter`
3. Add it to PATH (copy-paste this whole line, press Enter):
   ```powershell
   [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User').TrimEnd(';') + ';C:\Users\YourName\flutter\bin', 'User')
   ```
4. **Close and reopen PowerShell**. Verify: `flutter --version`
   (first run takes a few minutes — it's setting itself up)

## ✅ A2.6 — Get the DRISHTI code

In PowerShell:

```powershell
cd D:\
git clone https://github.com/KSVK26/Dristhi.git SIH26095
cd D:\SIH26095
```

**Should say:** `Cloning into 'SIH26095'... done.`
Then `dir` should show folders: `backend`, `dashboard`, `mobile`, `docs`.

> ✔ **A2 checklist:** Python works ☐ Node works ☐ Git works ☐ Flutter works ☐ Code downloaded ☐

---

# A3 — Start the 3 apps

> You will need **3 separate PowerShell windows** open at the same time
> (right-click the PowerShell icon → **New window**). Keep them all open while testing.

## ✅ A3.1 — Terminal 1: Start the Backend

```powershell
cd D:\SIH26095\backend
.\run.ps1
```

> If `run.ps1` gives an error, use the manual way:
> ```powershell
> python -m venv .venv
> .\.venv\Scripts\activate
> python -m pip install -r requirements.txt
> python seed.py
> python -m uvicorn main:app --reload --port 8000
> ```

**✅ Success looks like:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```
**Verify:** open your browser → **http://localhost:8000/docs** → you should see a page
titled "DRISHTI API" with a green list of endpoints. Leave this window running!

> ⚠ **Never close this window** while testing. It IS the brain of the system.

## ✅ A3.2 — Terminal 2: Start the Dashboard

Open a **new** PowerShell window:

```powershell
cd D:\SIH26095\dashboard
npm install
npm run dev
```

**✅ Success looks like:**
```
VITE v8.2.2  ready in ~3000 ms
➜  Local:   http://localhost:5173/
```
**Verify:** open your browser → **http://localhost:5173** → you should see a dark-blue
login page with the **drishti lotus logo**, two input boxes, and a blue **Sign In** button.

> The first `npm install` downloads packages — takes 1–2 minutes. Only needed once.

## ✅ A3.3 — Terminal 3: Start the Field App

Open a **third** PowerShell window:

```powershell
cd D:\SIH26095\mobile\drishti_app
flutter pub get
flutter build web --release
python -m http.server 5174 --directory build/web
```

**✅ Success looks like:** `Serving HTTP on 0.0.0.0 port 5174 ...`
**Verify:** open your browser → **http://localhost:5174** → same dark-blue login page,
but titled **"PMU Field Inspection App"**.

> ⚠ `flutter build web` takes 1–2 minutes and only needs re-running if the code changed.
> On later days you can skip straight to the `python -m http.server` line.

## ✅ A3.4 — "Is everything working?" final check

| Check | How | Expected |
|---|---|---|
| Backend | browser → localhost:8000/docs | "DRISHTI API" page |
| Dashboard | browser → localhost:5173 | login page with lotus logo |
| Field app | browser → localhost:5174 | "PMU Field Inspection App" login |

> ✔ **A3 checklist:** backend running ☐ dashboard opens ☐ field app opens ☐

---

# B — Feature testing checklist

> **How to test:** log in as instructed, follow the steps EXACTLY, compare what you
> see with "✅ You should see", then tick ☐ Pass or note ✗ Fail (→ Section E).
> **Hard-refresh tip:** press **Ctrl + Shift + R** in the browser if a page looks old/stale.

---

## ✅ B1 — Login as Admin (Dashboard)

**🎯 Intended functionality:** only registered people can enter; each role sees
different things. Admins get full control.

1. Open **http://localhost:5173**
2. The username box should already say `admin`, password `admin123` (pre-filled
   defaults). If not, type them in.
3. Click the blue **Sign In** button.

**✅ You should see:** a white sidebar on the left with the drishti logo, a blue
"👑 DoSJE Official" pill, menu items (Dashboard, Live Map, CCTV Feeds, Alerts,
Reports, Notifications, Profile), and a main area saying **"Welcome back, Admin"**
with 4 white stat cards.

**❌ If login fails:** "Wrong username or password" in red → recheck spelling →
if it persists, the backend may be down (Section D, error #2).

> ☐ B1 Pass ☐ B1 Fail

---

## ✅ B2 — Dashboard stat cards (Admin)

**🎯 Intended functionality:** officials see the health of ALL institutes at a glance
without opening anything.

1. Stay on the **Dashboard** tab (first sidebar item).
2. Look at the 4 cards under the welcome text.

**✅ You should see:** 🏛️ **Institutes monitored: 6** · 🚨 **High-risk institutes** (a
number, 0–6) · 🔔 **Open alerts** (a number) · 📋 **Evidence reports** (a number).
Numbers may differ if others tested before you — that's fine.

3. Below the cards, find the **Quick Actions** row (white card with buttons) and
   the **📞 Surprise VC Rooms** + **Recent Alerts** panels further down.

> ☐ B2 Pass ☐ B2 Fail

---

## ✅ B3 — AI Anomaly Scan

**🎯 Intended functionality:** the AI (IsolationForest) studies 30 days of attendance
at every institute and flags any whose pattern is abnormal (possible fake attendance).

1. On the Dashboard, in the Quick Actions card, click **🤖 Run AI Anomaly Scan**.
2. **Wait ~5 seconds** — a message appears inside the same card.

**✅ You should see:** either
`🤖 AI flagged: Divyangjan Rehabilitation Home – Dwarka` (the seeded anomaly), or
`🤖 Scan complete — no anomalies found.` if someone already resolved it.
Also: the map pin colours may change and a new alert appears under Recent Alerts.

> ☐ B3 Pass ☐ B3 Fail

---

## ✅ B4 — Random Inspection Assignment (with audit seed)

**🎯 Intended functionality:** instead of officials hand-picking inspectors (which can
be biased/colluded), the AI randomly picks a PMU inspector weighted by distance and
workload. The random "seed" is stored so anyone can later prove the draw was fair.

1. In Quick Actions, click the dropdown **— pick institute —** and select any
   institute (e.g., the one the AI flagged).
2. Click **🎯 Assign Inspection**.

**✅ You should see:**
`🎯 Assigned to {name} ({x} km away) · audit seed {a big number}`
The inspector's name will be one of: Ravi Kumar, Priya Sharma, Arjun Verma.

3. Assign a **second** one to another institute — note it may pick a different
   inspector. That's the randomness working.

> ☐ B4 Pass ☐ B4 Fail

---

## ✅ B5 — Surprise Video Conference (VC)

**🎯 Intended functionality:** officials can suddenly video-call any institute's
in-charge/staff/beneficiaries to verify they're really functioning — no advance warning.

1. With an institute still selected in the dropdown, click **📞 Start Surprise VC**.
2. **Wait 1–2 seconds.**

**✅ You should see:** `📞 VC room ready: https://meet.jit.si/drishti-inst...` in the
message area, AND a new entry in the **Surprise VC Rooms** panel with a red
blinking dot and a blue **Join** button.

3. Click **Join** → a new browser tab opens asking to join a Jitsi meeting.
   (Allow camera/mic if asked, or just confirm the page loads — you can close it.)

> ☐ B5 Pass ☐ B5 Fail

---

## ✅ B6 — Live Map, filters & attendance chart

**🎯 Intended functionality:** every institute under DoSJE schemes appears on a map,
colour-coded by risk (green = fine, orange = watch, red = danger), with real
attendance history.

1. Click **◉ Live Map** in the left sidebar.
2. **✅ You should see:** a map of Delhi with 6 coloured circle pins and two
   dropdown filters at the top.
3. Click any **red or orange pin** → the right panel shows the institute's name,
   contact person, a coloured **Risk Score** badge, and a **30-day attendance line
   chart** (grey = expected, blue = present).
4. Use the **district dropdown** → select one district → only that district's pins
   remain. Reset to **All districts**.
5. Use the **scheme dropdown** the same way.

> ☐ B6 Pass ☐ B6 Fail

---

## ✅ B7 — Live CCTV Feed Grid

**🎯 Intended functionality:** officials can watch live camera feeds from institutes
without visiting them. Real institutes would plug in their CCTV; the prototype uses
free public test streams, plus YOUR OWN PHONE as a real camera via the DroidCam app.

1. Click **📹 CCTV Feeds** in the sidebar.
2. **✅ You should see:** 4 black tiles in a grid. Tiles 1–3 should be **playing
   video** (free demo films) with a red blinking ● and a label like
   "Institute 1 – Main Hall". Tile 4 says "LIVE SITE CAMERA (DroidCam phone)".
3. **Optional (real camera test):** install the free **DroidCam** app on your phone,
   connect phone + PC to the same WiFi, open DroidCam, note the URL it shows
   (like `http://192.168.1.5:4747/video`), paste it into the input inside tile 4
   and press Enter → your phone's live camera appears in the grid!

> ⚠ If tiles 1–3 are black: the public stream server may be temporarily down
> (internet issue, not our bug). Note it and move on.

> ☐ B7 Pass ☐ B7 Fail (tiles 1-3) ☐ DroidCam tested

---

## ✅ B8 — Alerts: Resolve (Admin) & Acknowledge (Inspector)

**🎯 Intended functionality:** the AI raises alerts (proxy suspicion, anomalies, high
risk). Officials **resolve** them (investigated & handled). Inspectors can
**acknowledge** (I've seen this) but cannot resolve — separation of duties.

**As admin:**
1. Click **🚨 Alerts** in the sidebar.
2. **✅ You should see:** alert cards with coloured left borders (red/orange),
   severity tags (HIGH/MEDIUM), and a **✔ Mark Resolved** button on each.
3. Click **✔ Mark Resolved** on any one card → it fades and shows "✔ Resolved".
   (This also lowers that institute's risk score — check the map!)

**As inspector (later, in B11):** you'll see **👁 Acknowledge** instead — clicking it
shows "✔ You acknowledged this — resolution by DoSJE officials", and the admin's
view will show "acknowledged by {your name}".

> ☐ B8 Pass (admin resolve) ☐ Acknowledge tested in B11

---

## ✅ B9 — Reports gallery & CSV Export

**🎯 Intended functionality:** every photo evidence submitted from the field is
stored with its GPS location, checklist answers, and the AI's verdict — creating a
tamper-proof register that can be exported.

1. Click **📋 Reports** in the sidebar.
2. **✅ You should see:** cards with an evidence **photo**, institute name, a green
   **✔ AI verified** or red **⚠ possible proxy** tag, and ✅/❌ checklist answers —
   each answer with photo proof shows a **📷 proof** link.
3. **Click the photo** on any card → a small map appears below showing exactly
   **where the photo was taken** (GPS pin). Click the photo again to hide it.
4. Click **📄 Official Report** on any card → the **auto-generated official
   inspection document** opens: DoSJE letterhead, institute & inspector details,
   GPS + Google-Maps link, main photo, checklist table with per-answer photos,
   AI verdict, risk score, and the fairness audit seed for random assignments.
5. Click **⬇ Save as PDF / Print** → your browser's print dialog shows ONLY the
   document → save it as a PDF. Close the modal afterwards.
6. Click **⬇ Export CSV** (top right) → a `.csv` file downloads → open it in Excel.

**✅ You should see:** one row per report with ID, institute, date, GPS coordinates,
AI flags, and checklist answers.

> ☐ B9 Pass ☐ B9 Fail ☐ Official Report PDF saved

---

## ✅ B10 — Notifications (bell + page, both roles)

**🎯 Intended functionality:** nobody has to keep refreshing to know what happened —
new inspections, VC calls, proxy suspicions and high-risk events arrive as
notifications within ~15 seconds.

**As admin:**
1. Look at the **top-right** of the dashboard: a 🔔 circle button. If there are
   unread notifications, it has a **red number badge** (and pulses red for
   high-severity ones).
2. Click the 🔔 → a dropdown opens listing notifications with timestamps.
3. Click **Mark all read** → the badge disappears.
4. Click **🔔 Notifications** in the sidebar → full-page list view.

> ☐ B10 Pass ☐ B10 Fail

---

## ✅ B11 — Login as Inspector (Field Ops view) + Profile

**🎯 Intended functionality:** inspectors see THEIR tasks and THEIR submissions —
with read-only access to oversight data (no assign/resolve powers).

1. Click **⏻ Logout** (bottom-left of the sidebar).
2. Log in as `ravi` / `inspector123`.
3. **✅ You should see:** the pill now says **🧭 PMU Field Team**, the first sidebar
   item is **My Dashboard**, and there's a **🗂️ My Tasks** item admins don't have.
4. The Dashboard shows: ⏳ Pending · ✅ Completed · 📅 Completed this week ·
   ⚠ Proxy flags — plus a **🧭 NEXT UP hero card** (nearest pending task with km
   distance) and a Recent Activity feed.
5. Click **👤 Profile** in the sidebar → **✅ You should see:** your avatar, name
   (Ravi Kumar (PMU)), @ravi, Account ID, organization, a 📊 **Field performance**
   card, and a permissions list (✅ what you can do, 🔒 what you can't).

> ☐ B11 Pass ☐ B11 Fail

---

## ✅ B12 — Inspector: My Tasks page + Map context + Reports filter

1. Click **🗂️ My Tasks** → **✅ You should see:** filter chips (all / pending /
   in progress / completed / surprise), an offline hint banner, and task cards
   each showing **📍 X.X km away**, a 🧭 Navigate button, a ▶ Start button (or
   status chip), and a mini map.
2. Click **▶ Start** on a pending task → its chip flips to **🔄 In progress**.
3. Click **🧭 Navigate** on any task → Google Maps opens with that location.
4. Click **◉ Live Map** → click any institute pin → the panel now shows
   **🧭 Navigate** (instead of admin buttons) and, if you have a task there,
   **"🗂️ You have a task assigned here"** or **"✔ You inspected this on {date}"**.
5. Click **📋 Reports** → click the **my submissions only** chip → only YOUR
   reports remain. **⬇ Export CSV** exports just those.

> ☐ B12 Pass ☐ B12 Fail

---

## ✅ B13 — Field App: Dashboard tab

**🎯 Intended functionality:** the inspector's phone app mirrors the web dashboard —
stats and "what to do next" before leaving for site.

1. Open **http://localhost:5174** (hard refresh with **Ctrl+Shift+R** if it looks old).
2. Log in as `ravi` / `inspector123`.
3. **✅ You should see:** a **Home tab** at the bottom with:
   - **"Namaste, Ravi Kumar (PMU)"** and today's date
   - 4 stat tiles: ⏳ Pending · 🔄 In progress · ✅ Completed · ⚠ Proxy flags
   - a **🧭 NEXT UP — NEAREST PENDING TASK** white card with a **Capture Evidence**
     button and a 🧭 button
   - a **RECENT ACTIVITY** list (✔ AI verified / ⚠ Proxy flag raised)
4. **Pull down** anywhere on the screen to refresh.

> ☐ B13 Pass ☐ B13 Fail

---

## ✅ B14 — Field App: My Tasks tab (distance + start flow)

**🎯 Intended functionality:** tasks sorted by distance so the inspector knows what's
closest; tasks move through statuses (assigned → in progress → completed).

1. Tap **🗂️ My Tasks** in the bottom bar.
2. **✅ You should see:** a 📶 offline hint banner, then task cards each with a mini
   map, **📍 X.X km away**, a status chip (⏳ Assigned / 🔄 In progress / ✔
   Completed), **Navigate** and **Join VC** buttons.
3. Tap **Navigate** on any card → Google Maps opens with the location.
4. On a pending (⏳) task, tap **Start & Capture** → the status chip flips to
   **🔄 In progress** and the Capture screen opens.

> ☐ B14 Pass ☐ B14 Fail

---

## ✅ B15 — Field App: Capture Evidence + AI proxy flag ⭐ (star feature)

**🎯 Intended functionality:** proof of visit. The app stamps WHO (login), WHERE
(GPS), WHAT (checklist) and WHEN onto a photo. The backend AI then counts human
faces in the photo — **zero faces = suspected fake/proxy reporting**.

1. On the Capture screen (from B14 step 4):
   - Tap the big grey box → **allow camera access** → take a photo of anything.
   - Check the line under the photo says **📍 with GPS coordinates** (allow
     location access if asked).
   - Flip the 5 checklist switches (they start ON = yes).
   - NEW — under each switch there's a **📷 Add photo proof** button: tap it on
     1–2 answers (e.g. "Records / registers available?") and take an extra
     photo. A thumbnail appears next to the answer; ✕ removes it.
2. Tap **Submit Geo-Tagged Report** → wait ~3 seconds.

**✅ You should see — TWO outcomes:**
   - **Photo of a wall/empty room (no faces):** dialog **"⚠ AI Flag Raised — No human
     faces detected... flagged as POSSIBLE PROXY"** → the dashboard gets a red HIGH alert!
   - **Photo containing a face (your own, or print one):** dialog
     **"✅ Report Submitted — saved with N face(s) verified"**

3. **Verify on the dashboard:** log into :5173 as admin → 🚨 Alerts → the proxy
   alert is there → 📋 Reports → your photo with its GPS pin.

> ☐ B15 Pass (proxy flag) ☐ B15 Pass (face verified) ☐ B15 Fail

---

## ✅ B16 — Field App: Alerts tab

**🎯 Intended functionality:** the inspector is instantly informed of new assignments
and VC calls — same feed as the dashboard bell.

1. Tap **🔔 Alerts** in the bottom bar.
2. **✅ You should see:** "Alerts (N unread)", cards with coloured severity dots —
   🎯 NEW ASSIGNMENT and 📞 SURPRISE VC messages.
3. Tap **Mark read** on one → it disappears. Tap **Mark all read** → the tab shows
   "🎉 All caught up".
4. The badge on the bottom **Alerts tab icon** disappears too.

> ☐ B16 Pass ☐ B16 Fail

---

# C — Full end-to-end workflow (the whole story)

> Do this in order with **two browser windows side by side** (:5173 as admin,
> :5174 as ravi). This is exactly how we'll demo on stage.

| # | Actor | Action | What it proves (PS requirement) |
|---|---|---|---|
| 1 | Admin (:5173) | Live Map → click red pin → see attendance chart | Real-time monitoring |
| 2 | Admin | 🤖 Run AI Anomaly Scan → institute flagged | AI-based anomaly analytics |
| 3 | Admin | 🎯 Assign Random Inspection → inspector + seed shown | Random AI assignment, auditable |
| 4 | Ravi (:5174) | 🔔 Alerts tab → assignment notification arrived | Real-time notification |
| 5 | Ravi | My Tasks → ▶ Start → status = In progress | Mobile inspection module |
| 6 | Ravi | Navigate to site → Capture Evidence → photo of empty wall + 📷 proof on one checkbox → Submit | Geo-tagged live evidence |
| 7 | AI (automatic) | 0 faces → **POSSIBLE PROXY** flag | AI proxy detection, anti fake-reporting |
| 8 | Ravi | sees ⚠ warning dialog instantly | Transparency to field staff |
| 9 | Admin (:5173) | 🔔 bell → red HIGH alert arrived | Real-time oversight |
| 10 | Admin | Alerts → Mark Resolved → risk score drops | Better inspection governance |
| 11 | Admin | 📞 Start Surprise VC → Join → video call works | Random VC connectivity |
| 12 | Admin | 📋 Reports → Export CSV | Transparency & compliance records |

> ✔ **C checklist:** all 12 steps done ☐ — note any step that failed: ________

---

# D — Error encyclopedia (what breaks & how to fix it)

> Find the EXACT error text you see in the left column. If your error isn't here,
> screenshot it and report it (Section E).

## D1 — Backend (Terminal 1) errors

| You see | Why | Fix |
|---|---|---|
| `Fatal error in launcher: Unable to create process using '"D:\...old path...\pip.exe"'` | The project folder was moved after `.venv` was created; pip remembers the old path | Run: `.\.venv\Scripts\python.exe -m pip install --upgrade --force-reinstall pip` — or rebuild: delete the `.venv` folder, then redo A3.1 manual steps |
| `[WinError 10013]` when starting uvicorn | Port 8000 is already used by an old server | Find the culprit: `Get-NetTCPConnection -LocalPort 8000` → note its OwningProcess → `Stop-Process -Id <that number> -Force` → start again |
| `ModuleNotFoundError: No module named 'fastapi'` | You're not inside the venv, or packages aren't installed | In the backend folder run `.\.venv\Scripts\activate` then `python -m pip install -r requirements.txt` |
| `sqlalchemy.exc.OperationalError: no such column: alerts.acknowledged` | Old database file from a previous version | Stop the backend, delete `backend\drishti.db`, run `python seed.py`, start again |
| `seed.py` says "Database already seeded — skipping" | Normal! Data already exists | Nothing to do (delete `drishti.db` only if you want a fresh start) |

## D2 — Dashboard (Terminal 2 / browser) errors

| You see | Why | Fix |
|---|---|---|
| `npm : The term 'npm' is not recognized` | Node.js not installed or PATH not refreshed | Install Node (A2.3), reopen PowerShell |
| Browser shows **blank white page** at :5173 | Old cached code | Press **Ctrl + Shift + R** (hard refresh) |
| `Login failed` / red error at login | Backend (Terminal 1) is not running | Check Terminal 1; restart A3.1 |
| Buttons look plain/unstyled, no sidebar | Browser cached an old build | Ctrl + Shift + R; if persists, `npm run build` in the dashboard folder and reopen |
| `Failed to fetch` everywhere | Backend down or restarted | Wait 5 s for Terminal 1 to finish restarting, then refresh the page |

## D3 — Field App (Terminal 3 / browser) errors

| You see | Why | Fix |
|---|---|---|
| `flutter : The term 'flutter' is not recognized` | Flutter not in PATH | Redo A2.5 step 3, reopen PowerShell |
| `flutter build web` fails with `Target of URI doesn't exist` | You're in the wrong folder | `cd D:\SIH26095\mobile\drishti_app` first |
| Camera doesn't open on Capture screen | Browser blocked camera | Click the 🔒/📷 icon in the address bar → allow camera → reload |
| GPS shows "Acquiring GPS…" forever | Browser blocked location | Address-bar icon → allow location. Note: browsers give a fake nearby location for `localhost` — that's normal |
| Photo submitted but no AI flag raised | Your photo actually contained faces (AI working correctly!) | Retake with a photo of an empty wall to trigger the proxy flag |
| Page at :5174 looks like the OLD app | Browser cache | Ctrl + Shift + R |
| `Serving HTTP` line not visible | Server didn't start / port busy | Check the exact port (5174); try `python -m http.server 5175 --directory build/web` and open :5175 |

## D4 — Harmless warnings (IGNORE these)

| You see | Why it's fine |
|---|---|
| `InsecureKeyLengthWarning: The HMAC key is 29 bytes...` in the backend | Demo-only secret; production would use a long env-variable key |
| Weird symbols like `ΓÇô` or `≡ƒô₧` in the PowerShell window | Windows terminal can't draw emoji — the apps show them fine |
| `StarletteDeprecationWarning` during backend tests | Internal library notice, zero impact |
| `npm fund` / `npm audit` messages | Donation/security-bulletin info, not errors |

---

# E — Report issues & suggest features

## 🐞 E1 — Bug report template (copy this, fill it, send it)

```
BUG #___
Tester name:
Date/time:
Feature (B-number or name):      e.g. B4 — Random assignment
What I did (exact steps):
  1.
  2.
  3.
What I EXPECTED to happen:
What ACTUALLY happened:
Exact error text (if any):
Screenshot attached?            Yes / No
How bad is it?                  🔴 Blocked / 🟠 Wrong behaviour / 🟡 Cosmetic
```

## 💡 E2 — Feature suggestion template

```
IDEA #___
Tester name:
Feature I wish existed:
Which app + role:               Dashboard(admin) / Dashboard(inspector) / Field app
Why it would help (the problem it solves):
How urgent:                     Must-have / Nice-to-have / Someday
```

## 📋 E3 — Final summary sheet (fill & return this)

| Feature | Pass | Fail | Notes |
|---|---|---|---|
| B1 Admin login | ☐ | ☐ | |
| B2 Stat cards | ☐ | ☐ | |
| B3 AI anomaly scan | ☐ | ☐ | |
| B4 Random assignment | ☐ | ☐ | |
| B5 Surprise VC | ☐ | ☐ | |
| B6 Live map + filters | ☐ | ☐ | |
| B7 CCTV grid | ☐ | ☐ | |
| B8 Alerts resolve/ack | ☐ | ☐ | |
| B9 Reports + CSV | ☐ | ☐ | |
| B10 Notifications | ☐ | ☐ | |
| B11 Inspector view + profile | ☐ | ☐ | |
| B12 My Tasks / map / reports | ☐ | ☐ | |
| B13 App dashboard tab | ☐ | ☐ | |
| B14 App tasks + distance | ☐ | ☐ | |
| B15 Capture + proxy flag | ☐ | ☐ | |
| B16 App alerts tab | ☐ | ☐ | |
| C End-to-end (12 steps) | ☐ | ☐ | |

**Bugs found (count):** ____ **Feature ideas (count):** ____

---

*Thank you for testing DRISHTI! Every bug you catch makes the demo stronger. 🙌*

*— Team DRISHTI · SIH 2026 · PS 26095*
