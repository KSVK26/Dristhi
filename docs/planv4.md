# PLAN v4 — Free Hosting + Evidence Hardening (session log)

> Continues planv3fixv2. Everything below is **implemented and validated**.
> Follow-up deployment steps live in `DEPLOYMENT_PLAN.md`.

## Goal

1. Host all three DRISHTI apps online for ₹0 (demo-ready, no localhost).
2. Let admins onboard institutes from the dashboard (no seed.py edits).
3. Photo proof for each checklist answer (stronger evidence).
4. Auto-generate the official inspection report — nobody writes it by hand.

## 1. Hosting architecture (₹0)

| Piece | Host | Notes |
|---|---|---|
| FastAPI backend | Render free web service | CPU-only AI fits 512 MB; sleeps after ~15 min idle |
| Database | Supabase free Postgres | switched on via `DATABASE_URL` env var — the promised "one-line SQLite→PostgreSQL migration", now real |
| Dashboard | Render static site | built from repo (`npm run build`); API URL via `VITE_API_URL` env var |
| Field app (web) | Render static site | committed `flutter build web --dart-define=DRISHTI_API=…` output under `mobile/web_app/` |
| Jitsi VC + HLS CCTV | unchanged | public services already used |

Two platforms total: supabase.com (data) + render.com (API + both frontends,
all visible and auto-deployed from one dashboard).

Code enablers: `database.py` reads `DATABASE_URL` (SQLite fallback keeps local
dev identical); `psycopg2-binary` added; `api.js` uses
`import.meta.env.VITE_API_URL`; Flutter `kApiBase` honours the `DRISHTI_API`
dart-define.

## 2. Feature: ➕ Add Institute (admin panel)

- `POST /institutes` (admin-only JWT): name, district, scheme, lat/lng,
  contact person, phone; starts at risk_score 10 like seed data.
- Optional `generate_attendance`: creates ~26 days of healthy attendance
  (Sunday holidays skipped, same pattern as seed.py) so map colour, attendance
  chart and IsolationForest scan work immediately on the new pin.
- Logs an `institute_added` event.
- Dashboard: "➕ Add Institute" button in Quick Actions expands a validated
  form; save → list reloads → pin appears instantly.

## 3. Feature: 📷 Photo proof per checklist item

- Field app: each yes/no switch gets an "Add photo proof" camera button +
  thumbnail (retake/remove supported). Still ONE submission upload.
- `POST /reports` accepts optional `q0_photo` … `q4_photo`; files saved as
  `uploads/report_{id}_{user}_q{i}.jpg`; index→path map stored in the new
  `reports.question_photos_json` column.
- Self-healing migration `_ensure_schema_columns()` runs on boot
  (`ALTER TABLE ADD COLUMN`, silently skipped when present) — works on SQLite
  AND Supabase; zero manual DB work.
- `GET /reports` returns the `question_photos` map; dashboard shows a
  "📷 proof" link beside answered items.

## 4. Feature: 📄 Auto-generated Official Inspection Report

- On submission the backend marks the inspection completed AND raises an
  automatic `inspection_completed` alert ("official report generated").
- `GET /reports/{id}/document` compiles the report LIVE from data (never
  stale, nothing stored): DoSJE letterhead, institute/inspector details,
  timestamp, GPS + Google-Maps link, main photo, checklist table with
  ✅/❌ + inline per-question photos, AI verification verdict, current risk
  score, and the random-assignment audit seed when applicable, signature
  blocks, document ID.
- Dashboard Reports page: "📄 Official Report" button opens a print-styled
  modal; "⬇ Save as PDF / Print" uses browser print-to-PDF (`@media print`
  CSS isolates the document). Zero new dependencies.

## 5. Files touched

| File | Change |
|---|---|
| `backend/database.py` | `DATABASE_URL` env var + pool_pre_ping |
| `backend/requirements.txt` | + psycopg2-binary |
| `backend/main.py` | POST /institutes, q-photo fields, completion alert, `/reports/{id}/document`, schema self-migration |
| `backend/models.py` | `Report.question_photos_json` column |
| `dashboard/src/api.js` | VITE_API_URL support |
| `dashboard/src/pages/DashboardHome.jsx` | ➕ Add Institute form |
| `dashboard/src/pages/Reports.jsx` | 📷 proof links, Official Report modal |
| `dashboard/src/index.css` | form + modal/print styles |
| `mobile/drishti_app/lib/capture_screen.dart` | per-question camera buttons + upload |
| `mobile/drishti_app/lib/main.dart` | DRISHTI_API dart-define |
| `docs/DEPLOYMENT_PLAN.md` | full hosting guide (Parts 0–6) |

## 6. Validation performed

- 7/7 backend smoke tests passed (isolated DB): random assignment → multi-
  photo submit → q-photo map persisted → document compiled with audit seed →
  completion alert → migration idempotent.
- Earlier session: 6/6 smoke tests for Add Institute incl. role guard
  (inspector gets 403).
- `flutter analyze`: No issues found. `npm run build`: clean.

## 7. Remaining manual steps (human-only)

1. Supabase project → connection string → `$env:DATABASE_URL=…; python seed.py`.
2. Push repo → Render API service (`DATABASE_URL` env var) → Render static
   sites for dashboard + field app (`VITE_API_URL`; field app = rebuild +
   copy to `mobile/web_app/` + push).
3. Demo-day warm-up sequence in DEPLOYMENT_PLAN.md Part 5.
