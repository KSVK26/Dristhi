# 📱 DRISHTI — Mobile (Android) Testing Guide

This guide gets the **DRISHTI field app running on a real Android phone** — with
real GPS, a real camera, and real notifications. Written for complete beginners.

> **Who does what:**
> - **Team lead** (the person with the project code): does **M1 once** to build an
>     APK file, then shares it.
> - **Testers** (everyone else): do **M2, M3, M4** — install, connect, test.

---

## 📑 Contents

| Section | What | Time |
|---|---|---|
| M0 | What you need | 2 min |
| M1 | Lead: build the APK (once) | 20 min |
| M2 | Tester: install the APK on your phone | 5 min |
| M3 | Tester: connect the phone to the lead's PC | 10 min |
| M4 | Mobile feature tests (real GPS, camera, proxy flag!) | 20 min |
| M5 | Mobile troubleshooting | as needed |
| M6 | Report bugs / ideas | 10 min |

---

## M0 — What you need

| Who | Needs |
|---|---|
| **Team lead's PC** | The project code, backend + dashboard already running (see TESTING_GUIDE.md A3), **Android Studio** installed (M1) |
| **Every tester's phone** | Android 8.0 or newer, ~50 MB free space, connected to the **same WiFi** as the lead's PC |
| **Both** | The lead's PC must stay powered on with Terminal 1 (backend) running for the whole test session |

> 💡 **Why same WiFi?** The phone app talks to the backend running on the lead's PC.
> WiFi is the road between them. Mobile data (4G) will NOT work for this test.

---

## M1 — TEAM LEAD: build the APK (one time)

### M1.1 — Install Android tooling

1. Download **Android Studio**: https://developer.android.com/studio
   (file is ~1 GB — grab a coffee ☕)
2. Install with **all default options** (keep "Android Virtual Device" ticked or
   unticked — doesn't matter for us).
3. Open Android Studio once, click through the setup wizard so it downloads the
   **Android SDK** (another ~10 min).
4. Open **PowerShell** and accept the licenses (type `y` and Enter for each):
   ```powershell
   flutter doctor --android-licenses
   ```
5. Verify everything:
   ```powershell
   flutter doctor
   ```
   **✅ You should see:** a green ✓ in front of **[√] Flutter** AND
   **[√] Android toolchain**. Other ✗ rows (Chrome, Visual Studio) don't matter.

> ❌ If Android toolchain shows ✗: read its message. Usually it says to run
> `flutter config --android-sdk <path>` — copy the path it suggests from
> Android Studio → Settings → Languages & Frameworks → Android SDK →
> "Android SDK Location".

### M1.2 — Point the app at YOUR PC

There are now **two build modes** and the right one depends on where the
app will run.

| Where the app runs | Command |
|---|---|
| Local browser (`http://localhost:5174`)  → backend on your PC | `flutter build web --release` (no flag — defaults to `http://localhost:8000`) |
| Physical Android phone on same WiFi      | `flutter build web --dart-define=DRISHTI_API=http://YOUR_PC_IP:8000` |
| Hosted static site (Render, Netlify)     | `flutter build web --release --dart-define=DRISHTI_API=https://YOUR_BACKEND` |

The "Server address" box on the login screen is still available for one-off
overrides on **physical phones only** — on web builds it is reset to the
baked-in URL on every reload so a stale `localhost` can never stick. Use
the "↻ Reset to default" link if you ever need to clear the cached value.

### M1.3 — Build the APK

```powershell
cd D:\SIH26095\mobile\drishti_app
flutter build apk --release
```

**✅ Success looks like:**
```
√ Built build\app\outputs\flutter-apk\app-release.apk (XX.XMB)
```
**The APK file is at:**
`D:\SIH26095\mobile\drishti_app\build\app\outputs\flutter-apk\app-release.apk`

### M1.4 — Open the firewall door (so phones can reach the backend)

Run in PowerShell **as Administrator** (right-click PowerShell → Run as administrator):

```powershell
netsh advfirewall firewall add rule name="DRISHTI Backend 8000" dir=in action=allow protocol=TCP localport=8000
```

**✅ Success looks like:** `Ok.`

### M1.5 — Share the APK

Send `app-release.apk` to testers via WhatsApp / Google Drive / USB — any way
you like. Also tell them **your PC's IPv4 address** (from `ipconfig`) — they'll
type it in the app.

> ✔ **M1 checklist:** Android toolchain ✓ ☐ IP set in main.dart ☐ APK built ☐
> Firewall rule added ☐ APK shared + IP shared ☐

---

## M2 — TESTER: install the APK on your phone

1. Receive `app-release.apk` (WhatsApp/Drive/USB).
2. Tap the file. Android will warn: **"For your security, your phone is not
   allowed to install unknown apps from this source"** — this is normal.
3. Tap **Settings** on that popup → toggle ON **"Allow from this source"** →
   press back → tap **Install**.
4. When it finishes, tap **Open** (or find the **DRISHTI** icon in your app drawer).

**✅ You should see:** the dark-blue login screen with the lotus logo, three
boxes (Username, Password, **Server address**) and a blue **Sign In** button.

> ☐ M2 checklist: APK installed ☐ app opens ☐

---

## M3 — TESTER: connect the phone to the lead's PC

1. **Connect your phone to the SAME WiFi** as the lead's PC.
   (Settings → WiFi → tap the network → check it's the same name.)
2. Ask the lead for their **IPv4 address** (looks like `192.168.1.10`).
3. In the app's **Server address** box, type exactly:
   ```
   http://192.168.1.10:8000
   ```
   (replace `192.168.1.10` with the lead's actual IP — keep the `http://`
   and the `:8000`!)
4. Username: `ravi` · Password: `inspector123` → tap **Sign In**.

**✅ You should see:** the app's **Home tab** — "Namaste, Ravi Kumar (PMU)",
4 stat tiles, the NEXT UP card, and a bottom bar with 🏠 Home / 🗂️ My Tasks /
🔔 Alerts.

**❌ If it fails with a connection error:** see M5 (troubleshooting) — it's
almost always WiFi or firewall.

> ☐ M3 checklist: same WiFi ☐ server address typed ☐ logged in ☐

---

## M4 — MOBILE FEATURE TESTS

> These are the tests that are only possible on a real phone. Do them in order.

### ✅ M4.1 — Real GPS distance

**🎯 Intended:** task distances are computed from YOUR real position — walk and
watch them change.

1. On the **Home** tab, note the **NEXT UP** card's distance (e.g. "6.7 km").
2. Allow location permission if the app asks (**While using the app**).
3. Walk 50–100 metres away (or step outside), pull down to refresh.
4. **✅ You should see:** the distance number changed, and if you walked closer to
   one institute than another, **NEXT UP may switch to a different task**.

> ☐ M4.1 Pass ☐ Fail — distance before: ____ after: ____

### ✅ M4.2 — Real camera evidence + AI proxy flag ⭐

**🎯 Intended:** genuine on-site proof. The AI checks the photo for human faces —
no faces = suspected proxy reporting.

1. Home tab → **Capture Evidence** on the NEXT UP card.
2. Tap the grey photo box → **Allow camera** → photograph an **empty wall or
   corridor** (no people!).
3. Confirm **📍 GPS coordinates** appear under the photo.
4. NEW — tap **📷 Add photo proof** on 1–2 checklist answers and take extra
   close-up photos; thumbnails appear beside those answers.
5. Tap **Submit Geo-Tagged Report** → wait ~5 s (photos upload to the PC).

**✅ You should see:** **"⚠ AI Flag Raised — POSSIBLE PROXY"** dialog
(because the wall has no faces).

6. Repeat with a photo **of a person's face** (a colleague).
   **✅ You should see:** **"✅ Report Submitted — N face(s) verified"**.

7. **Cross-check on the dashboard** (lead's PC, :5173 as admin):
   🚨 Alerts shows the red **proxy** alert; 📋 Reports shows both photos with
   their GPS pins on the mini-map and **📷 proof** links beside answered items.

> ☐ M4.2 Pass (proxy flag) ☐ Pass (face verified) ☐ Fail

### ✅ M4.3 — Real-time notifications

**🎯 Intended:** the inspector's phone learns about new work instantly.

1. Keep the app open on the **Alerts** tab.
2. Ask the lead to assign a new inspection from the dashboard
   (Dashboard → pick institute → 🎯 Assign Inspection).
3. **Within ~15 seconds**, pull-to-refresh the Alerts tab.
   **✅ You should see:** a **🎯 NEW ASSIGNMENT** card.
4. Ask the lead to start a Surprise VC.
   **✅ You should see:** a **📞 SURPRISE VC** card with the join link.

> ☐ M4.3 Pass ☐ Fail

### ✅ M4.4 — Start inspection & status flow on the go

1. My Tasks tab → find a ⏳ Assigned task → tap **Start & Capture**
   (then back out of the capture screen).
2. **✅ You should see:** the chip now reads **🔄 In progress**.
3. Ask the lead to check the **dashboard** → their view shows the same
   In-progress status. Everyone is in sync.

> ☐ M4.4 Pass ☐ Fail

### ✅ M4.5 — Join VC from the phone

1. My Tasks tab → tap **Join VC** on any card.
2. **✅ You should see:** the phone browser opens the Jitsi meeting page.
   Allow mic/camera if asked. (The meeting is only "live" if the lead also
   joined from the dashboard — otherwise you'll be alone in the room, which
   still proves the link works.)

> ☐ M4.5 Pass ☐ Fail

---

# M5 — Mobile troubleshooting

| You see | Why | Fix |
|---|---|---|
| **"Failed host lookup" / connection error at login** | Phone can't reach the PC at all | 1) Same WiFi? 2) PC firewall rule added (M1.4)? 3) IP typed exactly? 4) Backend running? |
| Login works on the PC but not from the phone | Windows Firewall is blocking port 8000 | Redo **M1.4** exactly, run PowerShell as Administrator |
| `Server address must start with http://` | Missing `http://` in the box | Type the full address: `http://192.168.1.10:8000` |
| **"Install blocked"** when installing the APK | Android security | Settings → Apps → (menu) Special access → Install unknown apps → allow your browser/file manager |
| App opens but is stuck on the login spinner | Backend unreachable mid-request | Check Terminal 1 on the PC is still running; pull-to-refresh and retry |
| **"GPS permission denied"** / distance never appears | Location permission refused | Phone Settings → Apps → DRISHTI → Permissions → Location → **Allow while using** |
| **Camera doesn't open** | Camera permission refused | Phone Settings → Apps → DRISHTI → Permissions → Camera → Allow |
| Photo submitted but dashboard shows old data | Browser/dashboard cache | Hard-refresh the dashboard (Ctrl+Shift+R) |
| Distance numbers are huge (e.g. 8000 km) | Phone GPS hadn't locked on yet | Step outside or near a window, wait 30 s, refresh |
| App crashes when opening | Old Android version or corrupt install | Uninstall → re-install the APK; check Android 8.0+ |
| Everything worked yesterday, nothing today | The lead's PC IP changed (routers reassign IPs) | Lead: re-run `ipconfig`, tell testers the new IP; testers retype it on the login screen |

---

# M6 — Report bugs & share feedback

Use the same templates as `TESTING_GUIDE.md` Section E, **plus** these phone details:

```
MOBILE BUG #___
Tester name:
Phone model + Android version:      e.g. Redmi Note 10, Android 12
WiFi or mobile data:                WiFi
Server address used:                http://___:8000
Feature (M-number):                 e.g. M4.2 — camera proxy flag
What I did:
What I expected:
What actually happened:
Screenshot attached?                Yes / No
Severity:                           🔴 Blocked / 🟠 Wrong / 🟡 Cosmetic
```

## 📋 Mobile test summary sheet (fill & return)

| Test | Pass | Fail | Notes |
|---|---|---|---|
| M2 APK installed | ☐ | ☐ | |
| M3 Connected to backend | ☐ | ☐ | |
| M4.1 Real GPS distance | ☐ | ☐ | before: ___ after: ___ |
| M4.2 Camera + proxy flag | ☐ | ☐ | |
| M4.2b Face verified | ☐ | ☐ | |
| M4.3 Notifications | ☐ | ☐ | |
| M4.4 Start → In progress | ☐ | ☐ | |
| M4.5 Join VC | ☐ | ☐ | |

**Bugs found (count):** ____ **Ideas (count):** ____

---

*Real phones, real GPS, real cameras — this is where DRISHTI comes alive. Thank you
for testing! 📱👁️*

*— Team DRISHTI · SIH 2026 · PS 26095*
