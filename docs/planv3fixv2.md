# 📋 Plan v3-fix-v2 — Flutter Dashboard Screen

> Follows `planv3fixv1.md`. The Flutter app jumped straight into the task list
> with no overview — this adds a proper in-app dashboard mirroring the web
> inspector home (`DashboardHome.jsx`), plus bottom navigation.

## Status legend
- [x] done · [ ] todo

## 1. New Dashboard screen (`lib/dashboard_screen.dart`)
- [x] Welcome header "Namaste, {name}" + today's date
- [x] 4 stat cards: ⏳ Pending · 🔄 In progress · ✅ Completed · ⚠ Proxy flags
- [x] "Next up" hero card — nearest pending task, km distance, SURPRISE badge,
      checklist preview, 🧭 Navigate + Capture Evidence (auto start-flow)
- [x] Recent activity feed (✔ verified / ⚠ proxy-flag indicators)
- [x] Pull-to-refresh

## 2. App shell (`lib/app_shell.dart`)
- [x] Bottom NavigationBar: 🏠 Home · 🗂️ My Tasks · 🔔 Alerts
- [x] Unread-count badge on the Alerts tab icon
- [x] Tab state preserved across switches (IndexedStack)

## 3. Refactors
- [x] `main.dart`: login → AppShell
- [x] `tasks_screen.dart`: AppBar bell removed (Alerts tab replaces it)
- [x] `notifications_screen.dart`: converted to tab content (no nested Scaffold)

## 4. QA & ship
- [x] `flutter analyze` + `flutter test` clean
- [x] `flutter build web --release` → live on :5174
- [x] Live verify: login ravi → dashboard stats → tabs → commit + push

No backend changes · no new packages · reuses /inspections/my, /reports,
/notifications, /me.
