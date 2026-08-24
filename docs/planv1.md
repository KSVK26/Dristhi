# 📋 Plan v1 — Role-Based Dashboards + Notifications (drishti redesign)

> Supersedes the UI portions of `planv0.md` (original build plan).
> Brand palette from the drishti lotus-eye logo: navy `#0E1A2F`, blue `#2563EB`,
> background `#F4F6FA`, white cards, muted `#64748B`.

## Status legend
- [x] done · [ ] todo

## 1. Branding & shell
- [x] `components/Logo.jsx` — SVG lotus-eye logo (any size, optional wordmark)
- [x] `components/Layout.jsx` — sidebar (logo, role pill, nav, user card) + topbar (breadcrumbs, date, avatar, 🔔 bell)
- [ ] `index.css` full rewrite to the modern light theme

## 2. Admin — "DoSJE Command Center" (`DashboardHome.jsx`, role-aware)
- [ ] Welcome header + date eyebrow
- [ ] 4 stat cards: Institutes · High-risk · Open alerts · Evidence reports
- [ ] Quick Actions: 🤖 AI scan · 🎯 Assign inspection (picker) · 📞 Surprise VC (picker)
- [ ] Surprise VC panel (initiated rooms + join links)
- [ ] Recent alerts feed
- [ ] Live Map: District + Scheme filters
- [ ] Reports: Export CSV

## 3. Inspector — "PMU Field Ops" home (same component, role switch)
- [ ] Stats: Assigned · Completed · Pending
- [ ] Task cards: status chips + "Open in Google Maps" + checklist preview
- [ ] My Submissions history (✔ verified / ⚠ proxy flags)
- [ ] Read-only elsewhere (🔒 hints) — Alerts resolve & Map actions already admin-gated

## 4. Profile page (`Profile.jsx`)
- [ ] Avatar initials, name, @username, role badge, account ID
- [ ] Backend: `GET /me` returns username too
- [ ] Per-role permissions checklist

## 5. Notifications (polling, no websockets)
Backend:
- [ ] `Alert` gains: `audience` ('admin'/'inspector'/null), `target_user_id`, `is_read`
- [ ] `GET /notifications`, `POST /notifications/{id}/read`, `POST /notifications/read-all`
- [ ] Triggers: assignment → target inspector; VC started → inspectors + admin;
      proxy evidence → admin; risk ≥ 70 → admin (deduped); AI anomaly → admin
Frontend:
- [ ] 🔔 bell in topbar with unread badge + dropdown (15 s polling)
- [ ] "Notifications" page in sidebar nav (full list, mark-all-read)

## 6. QA & ship
- [ ] Recreate DB (schema change) + reseed
- [ ] Backend e2e test green · flutter analyze/test green
- [ ] `npm run build`, serve 5173, click-through as admin then ravi
- [ ] Live-verify notification triggers end-to-end
- [ ] git commit
