# DRISHTI — Free Online Hosting Guide (Demo-Ready in ~90 minutes)

## Part 0 — What's new since this guide was first written ✨

These features were added after the first deployment. **If you already
deployed, redeploy to pick them up** (see "Redeploying" below).

| Feature | Where | Demo moment |
|---|---|---|
| **➕ Add Institute (admin panel)** | Dashboard → Quick Actions | Onboard an institute LIVE on stage — pin appears on the map instantly |
| **📷 Photo proof per checklist item** | Field app capture screen | Every yes/no answer can carry its own geo-tagged photo ("records available? here's the register") |
| **📄 Auto-generated Official Inspection Report** | Dashboard → Reports → "📄 Official Report" button | The system compiles a print/PDF-ready report automatically — photos, GPS, AI verdict, fairness audit seed, signature blocks. Nobody writes reports by hand anymore |

**Technical notes:**
- The per-question photos + official report needed one extra DB column
  (`reports.question_photos_json`). The backend **migrates itself on boot**
  (`ALTER TABLE ... ADD COLUMN`, silently skipped if it already exists) — so
  your Supabase database upgrades itself on the next Render deploy. Zero
  manual DB work.
- New endpoint: `GET /reports/{id}/document` — returns the compiled report
  document (rendered by the dashboard as a printable page).
- Old single-photo reports still work everywhere — fully backward compatible.

**Redeploying after these changes:**
1. **Backend:** push to GitHub → Render auto-deploys (or Manual Deploy →
   Deploy latest commit). Watch logs for `Uvicorn running`.
2. **Dashboard:** the SAME push triggers its Render Static Site rebuild too
   (`npm install && npm run build` reruns automatically).
3. **Field app:** rebuild + copy + push:
   ```powershell
   cd mobile\drishti_app
   flutter build web --dart-define=DRISHTI_API=https://drishti-api.onrender.com
   Remove-Item -Recurse -Force ..\web_app -ErrorAction SilentlyContinue
   Copy-Item -Recurse build\web ..\web_app
   git add ..\web_app ; git commit -m "rebuild field app" ; git push
   ```

---

> Goal: all three DRISHTI apps running on public HTTPS URLs for **₹0**, ready
> for the internal hackathon demo. Follow the parts in order.
>
> **Final result — only TWO platforms (supabase.com + render.com):**
> | Piece | Hosted at | Cost |
> |---|---|---|
> | Database | Supabase free Postgres (persists forever) | ₹0 |
> | FastAPI API | `https://drishti-api.onrender.com` | ₹0 |
> | Admin dashboard (static) | `https://drishti-dashboard.onrender.com` | ₹0 |
> | Field app (static) | `https://drishti-field-app.onrender.com` | ₹0 |
>
> All three Render services live in ONE dashboard and auto-deploy from ONE
> `git push`.

---

## Part 1 — Supabase database (~15 min)

The backend now reads `DATABASE_URL`. When it's absent you get local SQLite as
before; when it points at Postgres, **everything just works** (SQLAlchemy).

1. Go to <https://supabase.com> → **Sign up** (GitHub login works).
2. Click **New project** → name `drishti`, pick a region near you (Mumbai),
   set a **database password** (SAVE IT — shown once).
3. Wait ~2 min for provisioning.
4. Get the connection string: sidebar → ⚙️ **Project Settings** → **Database**
   → *Connection string* → **URI** tab → copy. It looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxx.supabase.co:5432/postgres
   ```
   Replace `[YOUR-PASSWORD]` with your real password (URL-encode special
   chars: `@`→`%40`, `#`→`%23`, `:`→`%3A`).
5. **Seed it once from your machine** (PowerShell, repo root):
   ```powershell
   cd backend
   .\.venv\Scripts\activate
   python -m pip install psycopg2-binary
   $env:DATABASE_URL = "postgresql://postgres:YOURPASS@db.xxxx.supabase.co:5432/postgres"
   python seed.py
   ```
   You should see `Seeded successfully!` — tables + demo data now live in
   Supabase (check Table Editor in the browser to confirm).
6. Keep this URL handy — Render will need it as an env var.

> 💡 If the direct URI gives IPv6 errors, use the **Session pooler** string
> instead (port 5432, host like `aws-0-ap-south-1.pooler.supabase.com`).

## Part 2 — Backend on Render (~15 min)

1. Push this repo to GitHub if not already:
   ```powershell
   git add . ; git commit -m "DRISHTI" ; git push
   ```
   ⚠️ Check `.gitignore` covers `backend/.venv`, `backend/drishti.db`,
   `node_modules` before pushing (never commit DBs or secrets).
2. Go to <https://render.com> → sign in with GitHub → **New +** →
   **Web Service** → pick your repo → connect.
3. Fill the form exactly:
   - **Name:** `drishti-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
4. **Environment** tab → **Add Environment Variable**:
   Key `DATABASE_URL` → Value = your Supabase URI from Part 1.
5. Click **Create Web Service**. First deploy takes ~5 min (installs
   scikit-learn/OpenCV). Watch logs until:
   `Uvicorn running on https://drishti-api.onrender.com ...`
6. Verify: open `https://drishti-api.onrender.com/docs` → "DRISHTI API" page ✅
7. Try `POST /login` from the docs UI with `admin/admin123`.

> ⚠️ **Free tier sleep:** after ~15 min idle, Render spins down and the next
> request takes ~50 s to wake it. **Before your demo**: open `/docs` once.
> Optional: free keep-warm pinger at <https://cron-job.org> hitting `GET /`
> every 10 minutes during demo hours.

## Part 3 — Dashboard as a Render Static Site (~10 min)

Same render.com account as the backend — one dashboard lists all services.

1. Render dashboard → **New +** → **Static Site** → pick the same repo.
2. Fill the form:
   - **Name:** `drishti-dashboard`
   - **Root Directory:** `dashboard`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
3. Under **Advanced** → **Add Environment Variable**:
   Key `VITE_API_URL` → Value `https://drishti-api.onrender.com`
   *(no trailing slash)*
4. Create Static Site → build takes ~2 min → open the given URL.
5. Verify: login page loads → `admin / admin123` → map pins + stat cards show.
6. Blank map / login failing? DevTools Console → CORS error usually means
   `VITE_API_URL` has a trailing slash or typo → fix → redeploy.
7. If refreshing a deep link ever shows 404, add a Rewrite Rule:
   Source `/*` → Destination `/index.html` (SPA fallback).

## Part 4 — Field app as a Render Static Site (~20 min)

Flutter can't be compiled inside Render's static environment, so we build
locally once and commit the output (`mobile/web_app/`). Updates afterwards are
one command + push.

1. Build with your backend URL baked in:
   ```powershell
   cd mobile\drishti_app
   flutter build web --dart-define=DRISHTI_API=https://drishti-api.onrender.com
   ```
   (Skip the flag to keep pointing at `localhost:8000` for local testing.)
2. Copy the output into the tracked folder:
   ```powershell
   Remove-Item -Recurse -Force ..\web_app -ErrorAction SilentlyContinue
   Copy-Item -Recurse build\web ..\web_app
   ```
3. Commit + push (`.gitignore` intentionally allows `mobile/web_app/`):
   ```powershell
   git add ..\web_app ; git commit -m "field app web build" ; git push
   ```
4. Render dashboard → **New +** → **Static Site** → same repo:
   - **Name:** `drishti-field-app`
   - **Root Directory:** *(leave blank)*
   - **Build Command:** *(leave empty — files are pre-built)*
   - **Publish Directory:** `mobile/web_app`
5. Open the URL → login `ravi / inspector123` → tasks/alerts load from the
   Render API ✅

> Updating the field app later = repeat steps 1–3; its Render service
> redeploys automatically on push.
> The login screen still shows a "Server address" box — testers on phones can
> override it anytime. Android emulator default remains `10.0.2.2:8000`.

## Part 5 — Demo-day checklist ✅

**30 minutes before:**
1. Ping `https://drishti-api.onrender.com/docs` (wake it up)
2. Open dashboard URL → login admin → check map pins render
3. Run 🤖 AI Anomaly Scan once (warms everything + produces a flag to show)
4. Open field app URL → login ravi

**Judge flow (extends TESTING_GUIDE section C):**
| # | Action | Where |
|---|---|---|
| 0 | ➕ Add Institute live on stage — fill name/district/scheme/lat-lng, pin appears on the map instantly! | Dashboard Quick Actions |
| 1 | Live Map → click red pin → attendance chart works on your new institute too | Dashboard |
| 2 | 🤖 Run AI Anomaly Scan → seeded anomaly flagged | Dashboard |
| 3 | 🎯 Assign Random Inspection → nearest officer + audit seed shown | Dashboard |
| 4 | 🔔 notification arrives → ▶ Start task → photo + GPS submit (**add photo proof to 1–2 checkboxes!**) | Field app |
| 5 | 🚨 proxy alert appears → resolve → risk drops | Dashboard |
| 6 | 📄 **Official Report** → auto-generated document with photos, GPS, AI verdict & audit seed → ⬇ Save as PDF live on stage | Dashboard |
| 7 | 📞 Surprise VC room opens (Jitsi — works from any device) | Both |

**Killer new line for judges:** *"This isn't localhost — it's deployed.
Public HTTPS URLs, managed PostgreSQL switched on with one environment
variable: the exact one-line SQLite→Postgres migration we promised."*

## Part 6 — Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| First request takes ~50 s | Render free-tier cold start | Ping first / cron-job.org keep-warm |
| `OperationalError` / auth failed on Render logs | Wrong DATABASE_URL or unencoded password chars | Re-copy URI; encode `@ # :` etc. |
| Supabase "Tenant or user not found" | Old direct URI after project pause | Use Session pooler URI (Part 1 tip) |
| Dashboard blank map / login fails | CORS or bad VITE_API_URL | No trailing slash; exact URL; redeploy |
| Photos 404 after a Render redeploy | Free tier disk is ephemeral | Report *rows* persist in Supabase; photo files need Cloudinary (future work) |
| `flutter build web` fails | Web platform not enabled | `flutter create . --platforms=web` then rebuild |
| New institute missing from pickers | Stale page state | Refresh — save also calls load() automatically |

---

*Code changes that enabled this: `DATABASE_URL` env var (`backend/database.py`),
`psycopg2-binary` (`requirements.txt`), admin `POST /institutes` endpoint +
"➕ Add Institute" dashboard form (institute onboarding), `VITE_API_URL`
(`dashboard/src/api.js`), `--dart-define=DRISHTI_API`
(`mobile/drishti_app/lib/main.dart`).*

