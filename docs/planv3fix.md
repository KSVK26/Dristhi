# 📋 Plan v3-fix — Flutter Field App: inspector feature sync

> Companion to `planv3.md` (dashboard-side). The backend endpoints already exist —
> this is purely Flutter work, no new packages, no backend changes.

## Goal
Inspectors primarily use the Flutter app in the field, so the v3 features
(distance, start-flow, notifications) must exist there too — not just on the
dashboard.

## Status legend
- [x] done · [ ] todo

## 1. My Tasks screen upgrade (`lib/tasks_screen.dart`)
- [x] 📍 Distance on every task card — one GPS fix via geolocator (already
      integrated), haversine in Dart, tasks sorted nearest-first
- [x] ▶ **Start** button on pending tasks → `POST /inspections/{id}/start`
      → card flips to 🔄 **In progress** chip
- [x] Status chips on all cards: ⏳ Assigned / 🔄 In progress / ✔ Completed
- [x] 📶 Offline hint banner (evidence syncs when back online)
- [x] 🔔 AppBar bell icon with red unread-count badge → Notifications screen

## 2. New Notifications screen (`lib/notifications_screen.dart`)
- [x] List unread notifications from `GET /notifications`
      (🎯 assignments, 📞 VC alerts — same data as the dashboard bell)
- [x] Severity color dots, timestamps, Mark-read per item + Mark-all-read
- [x] Auto-refresh every 15 s

## 3. QA & ship
- [x] `flutter analyze` + `flutter test` clean
- [x] `flutter build web --release` → redeploy :5174
- [x] Live verify: login ravi → distances shown, start a task → In progress,
      bell badge → notifications list → mark read
- [x] Commit + push

## Out of scope (by design)
- Acknowledge alerts (dashboard-only: officials resolve, inspectors get
  notifications) · compliance card (profile-level, dashboard)
