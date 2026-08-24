# 📋 Plan v3 — Inspector "Field Ops" Dashboard

> Progression: `planv1.md` (v2 redesign: branding, role dashboards, notifications)
> → **this plan** (v3: full inspector experience). Original build notes lived in
> `planv0.md` (removed after the v2 cleanup; see git history).

## Goal
Give the inspector a first-class, polished experience — not a read-only copy of
the admin view. Same drishti theme (navy #0E1A2F · blue #2563EB), different
layout and content, everything built around the inspector's actual job.

## Status legend
- [x] done · [ ] todo

## 1. Inspector Home redesign
- [x] 4 tailored stat cards: ⏳ Pending · ✅ Completed · 📅 Completed this week · ⚠ Proxy flags
- [x] **"Next up" hero card** — nearest pending task (haversine from inspector GPS),
      distance shown, checklist preview, big 🧭 Navigate button
- [x] Recent activity feed (✔ verified / ⚠ proxy-flagged submissions)

## 2. New "My Tasks" page (`pages/TasksPage.jsx`)
- [x] Filter chips: All / Pending / In progress / Completed / Surprise
- [x] Task cards sorted by distance, with 🧭 Navigate + **▶ Start** button
- [x] Offline hint banner (field app syncs evidence when back online)

## 3. Live Map — role-swapped side panel
- [x] 🧭 Navigate button for inspectors (instead of admin assign/VC)
- [x] "🗂️ You have a task here" badge when the institute matches an open assignment
- [x] "✔ You inspected this on {date}" history line

## 4. Alerts — Acknowledge (not Resolve)
- [x] Model: `Alert.acknowledged` + `Alert.acknowledged_by` columns (DB reseeded)
- [x] `POST /alerts/{id}/acknowledge` — inspector-only endpoint
- [x] Inspector UI: 👁 Acknowledge button → "✔ You acknowledged this"
- [x] Admin UI: shows "✔ acknowledged by {name}" on alert cards

## 5. Reports — mine + export
- [x] "my submissions only" toggle for inspectors (filters by their inspection IDs)
- [x] CSV export works on the filtered view

## 6. Profile — compliance card
- [x] 📊 Field performance: inspections completed · reports submitted ·
      evidence quality % (share of submissions without proxy flags)

## 7. Notifications polish
- [x] 🔔 Bell pulses red while a high-severity notification is unread (CSS animation)

## 8. Backend additions
- [x] `GET /me` now returns inspector GPS (lat/lng) for distance calc
- [x] `POST /inspections/{id}/start` — inspector marks task in_progress
      (guard: own task only, rejects completed)
- [x] `POST /alerts/{id}/acknowledge` — inspector-only
- [x] `GET /alerts` includes acknowledged + acknowledged_by (resolved to a name)

## 9. QA & ship
- [x] DB reseeded (schema change) · backend e2e test: ALL TESTS PASSED
- [x] Live-verified: start flow (`in_progress`), acknowledge (persisted + name),
      `/me` GPS, guard rejection of completed tasks
- [x] Dashboard production build clean (1.5 s)
- [x] Services :8000 / :5173 / :5174 all HTTP 200
- [x] Committed & pushed (`e793b56`)
