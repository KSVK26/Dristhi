"""
DRISHTI - End-to-end API smoke test
-----------------------------------
Run with the server NOT running (uses FastAPI's in-process TestClient):
    .venv\\Scripts\\python.exe test_api.py

Walks the full MONITOR -> DETECT -> VERIFY -> REPORT -> ACT demo flow:
  1. login as admin + inspector          (JWT auth)
  2. list institutes                     (map data)
  3. run AI anomaly detection            (IsolationForest)
  4. assign a random surprise inspection (seeded RNG)
  5. inspector sees the task             (field app)
  6. submit geo-tagged photo evidence    (AI face/proxy check)
  7. start surprise VC room              (Jitsi)
  8. resolve an alert                    (ACT step)
"""

import io
import sys

# Windows consoles default to cp1252 and crash on emoji output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient
from PIL import Image

from main import app

client = TestClient(app)


def make_photo(with_face_like_content=True):
    """Generate a small JPEG in memory (no camera needed for the test)."""
    img = Image.new("RGB", (320, 240), (60, 60, 60) if with_face_like_content else (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def main():
    print("== 1. LOGIN ==")
    r = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, r.text
    admin_tok = r.json()["token"]
    print("   admin OK, role =", r.json()["role"])

    r = client.post("/login", json={"username": "ravi", "password": "inspector123"})
    insp_tok = r.json()["token"]
    print("   inspector OK, role =", r.json()["role"])

    # RBAC check: inspector must NOT be able to run anomaly detection
    r = client.post("/analytics/run-anomaly",
                    headers={"Authorization": f"Bearer {insp_tok}"})
    assert r.status_code == 403
    print("   RBAC enforced: inspector blocked from admin endpoint (403)")

    ah = {"Authorization": f"Bearer {admin_tok}"}
    ih = {"Authorization": f"Bearer {insp_tok}"}

    print("== 2. INSTITUTES ==")
    r = client.get("/institutes", headers=ah)
    institutes = r.json()
    assert len(institutes) == 6
    print(f"   {len(institutes)} institutes loaded")

    print("== 3. AI ANOMALY DETECTION ==")
    r = client.post("/analytics/run-anomaly", headers=ah)
    flagged = r.json()["flagged"]
    print(f"   flagged {r.json()['flagged_count']} institute(s): "
          + ", ".join(f['institute'] for f in flagged))

    print("== 3b. RISK BREAKDOWN (why is the score raised?) ==")
    probe = institutes[0]
    # The breakdown recomputes the score, so fetch the institute fresh AFTER
    r = client.get(f"/institutes/{probe['id']}/risk-breakdown", headers=ah)
    assert r.status_code == 200, r.text
    bd = r.json()
    fresh = next(i for i in client.get("/institutes", headers=ah).json() if i["id"] == probe["id"])
    assert isinstance(bd["factors"], list)
    print(f"   {bd['name']}: score {bd['score']} from {len(bd['factors'])} factor(s)")
    for f in bd["factors"]:
        print(f"   • {f['icon']} {f['reason']} (+{f['points']}) — {f['detail']}")
    # factors must always explain the score exactly (breakdown also
    # recomputes+persists, so the DB and the response are now in sync)
    assert bd["score"] == fresh["risk_score"], \
        f"breakdown score {bd['score']} != institute risk_score {fresh['risk_score']}"

    print("== 4. RANDOM INSPECTION ASSIGNMENT ==")
    target = next((i for i in institutes if i["risk_score"] >= 50), institutes[0])
    r = client.post("/inspections/assign-random",
                    headers=ah, json={"institute_id": target["id"]})
    data = r.json()
    print(f"   assigned to {data['assigned_to']} "
          f"({data['distance_km']} km away), seed={data['assignment_seed']}")

    print("== 5. ASSIGNED INSPECTOR SEES TASK ==")
    task = None
    for uname in ("ravi", "priya", "arjun"):   # AI may pick any PMU inspector
        tok = client.post("/login",
                          json={"username": uname,
                                "password": "inspector123"}).json()["token"]
        cand = client.get("/inspections/my",
                          headers={"Authorization": f"Bearer {tok}"}).json()
        if cand:
            task = cand[0]
            ih = {"Authorization": f"Bearer {tok}"}
            print(f"   {uname} holds task #{task['inspection_id']} "
                  f"at {task['institute_name']}")
            break
    assert task, "no inspector received the assignment"

    print("== 6. SUBMIT GEO-TAGGED EVIDENCE ==")
    r = client.post(
        "/reports",
        headers=ih,
        data={
            "inspection_id": str(task["inspection_id"]),
            "geo_lat": str(task["lat"] + 0.001),
            "geo_lng": str(task["lng"] + 0.001),
            "checklist": '{"Staff physically present?":"yes",'
                         '"Beneficiaries visible on site?":"yes"}',
        },
        files={"photo": ("evidence.jpg", make_photo(), "image/jpeg")},
    )
    result = r.json()
    print(f"   report #{result['report_id']} saved; faces detected = "
          f"{result['faces_detected']}; ai_flags = {result['ai_flags']}")

    print("== 7. SURPRISE VC ==")
    r = client.post("/vc/start", headers=ah,
                    json={"institute_id": target["id"]})
    print("   Jitsi room:", r.json()["url"])

    print("== 8. ALERTS + RESOLVE ==")
    r = client.get("/alerts", headers=ah)
    alerts = r.json()
    print(f"   {len(alerts)} alert(s), latest: [{alerts[0]['severity']}] "
          f"{alerts[0]['message'][:70]}...")
    r = client.post(f"/alerts/{alerts[0]['id']}/resolve", headers=ah)
    assert r.json()["ok"]

    # QA fix #004 regression check:
    # resolving an alert MUST lower (or keep equal) the institute risk score,
    # because unresolved alerts feed the score.
    inst_id = alerts[0]["institute_id"]
    live = {i["id"]: i["risk_score"] for i in client.get("/institutes", headers=ah).json()}
    score_before = live[inst_id]

    # resolve every OPEN alert of this institute so nothing else moves the score
    open_alerts = [a for a in client.get("/alerts", headers=ah).json()
                   if a["institute_id"] == inst_id and not a["resolved"]]
    assert open_alerts, "expected at least one open alert to resolve"
    for a in open_alerts:
        assert client.post(f"/alerts/{a['id']}/resolve",
                           headers=ah).json()["ok"]

    score_after = next(i["risk_score"] for i in
                       client.get("/institutes", headers=ah).json()
                       if i["id"] == inst_id)
    print(f"   risk score of institute #{inst_id}: {score_before} -> "
          f"{score_after} (after resolving {len(open_alerts)} open alert(s))")
    assert score_after < score_before, \
        "risk score did not drop after resolving alerts!"

    print("== 9. SECURITY HEADERS ==")
    r = client.get("/", headers=ah)
    for h in ("X-Frame-Options", "X-Content-Type-Options",
              "Referrer-Policy", "Strict-Transport-Security",
              "Content-Security-Policy"):
        assert h in r.headers, f"Missing security header: {h}"
    print(f"   all 5 security headers present (HSTS, CSP, XFO, XCTO, RP)")

    print("== 10. LOGIN RATE LIMIT (5/min, then 60s lockout) ==")
    for i in range(6):
        r = client.post("/login", json={"username": "admin", "password": "WRONG"})
        if r.status_code == 429:
            print(f"   locked at attempt #{i+1}: {r.json()['detail'][:60]}")
            break
    else:
        raise AssertionError("Rate limit did not trigger after 6 failed attempts")
    # clear the lock so the rest of the test suite keeps working
    import auth as _auth
    with _auth._lock_mu:
        _auth._locks.clear()
        for q in _auth._attempts.values():
            q.clear()

    print("== 11. PHOTO INTEGRITY (tampered upload rejected) ==")
    my = client.get("/inspections/my", headers=ih).json()
    if my:
        t = my[0]
        # Use a real JPEG so the MIME sniffer passes
        from hashlib import sha256
        photo = make_photo(with_face_like_content=True)
        real = sha256(photo).hexdigest()
        bogus = "0" * 64
        r = client.post("/reports",
            headers=ih,
            data={"inspection_id": str(t["inspection_id"]),
                  "geo_lat": "28.61", "geo_lng": "77.20",
                  "checklist": "{}",
                  "photo_sha256": bogus},   # wrong hash on purpose
            files={"photo": ("e.jpg", photo, "image/jpeg")},
        )
        assert r.status_code == 400, r.text
        assert "integrity" in r.json()["detail"].lower(), r.json()
        print(f"   tampered photo rejected: {r.json()['detail'][:60]}")
        if t["status"] != "completed":
            r2 = client.post("/reports",
                headers=ih,
                data={"inspection_id": str(t["inspection_id"]),
                      "geo_lat": "28.61", "geo_lng": "77.20",
                      "checklist": "{}",
                      "photo_sha256": real,
                      "captured_at": "2026-08-29T14:00:00Z",
                      "device_id": "test-device-001"},
                files={"photo": ("e.jpg", photo, "image/jpeg")},
            )
            assert r2.status_code == 200, r2.text
            data = r2.json()
            assert data.get("ai_flags") is not None
            print(f"   correct hash accepted; ai_flags={data['ai_flags']}; "
                  f"photo_sha256 stored in DB")
        else:
            print("   task already done, integrity re-test skipped")
    else:
        print("   no inspector task to test against, skipped")

    print("== 12. JWT EXPIRY ==")
    short = client.post("/login",
                        json={"username": "admin", "password": "admin123"},
                        headers={})
    import jwt as _jwt, time as _time
    payload = _jwt.decode(short.json()["token"], _auth.SECRET_KEY, algorithms=["HS256"])
    assert "exp" in payload, "token has no exp claim"
    assert payload["exp"] > _time.time(), "exp is already in the past"
    # Manually craft an expired token to prove the 401
    expired = {**payload, "exp": _time.time() - 1}
    bad = _jwt.encode(expired, _auth.SECRET_KEY, algorithm="HS256")
    r = client.get("/institutes", headers={"Authorization": f"Bearer {bad}"})
    assert r.status_code == 401, r.text
    print(f"   exp claim enforced; expired token -> {r.json()['detail']}")

    print("ALL TESTS PASSED ✔")


if __name__ == "__main__":
    main()