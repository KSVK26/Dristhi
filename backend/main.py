"""
DRISHTI - FastAPI Application (API Gateway)
-------------------------------------------
Run the server:
    .venv\\Scripts\\python -m uvicorn main:app --reload --port 8000

Interactive API docs open automatically at:
    http://localhost:8000/docs

Endpoint map (grouped by the MONITOR -> DETECT -> VERIFY -> REPORT -> ACT flow):
    MONITOR : GET /institutes, GET /cctv/streams, GET /attendance/analytics/{id}
    DETECT  : POST /analytics/run-anomaly, GET /alerts
    VERIFY  : POST /inspections/assign-random, POST /vc/start
    REPORT  : POST /reports (geo-tagged photo + checklist from field app)
    ACT     : POST /alerts/{id}/resolve, risk scores auto-update everywhere
"""

import json
import os
import random
import re
import secrets
import shutil
import time
import hashlib
import io
import struct

from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import ai_engine
from auth import (
    create_access_token,
    decode_token,
    get_current_user,
    login_rate_limit_check,
    login_rate_limit_record,
    require_role,
    verify_password,
)
from database import engine, get_db
from models import Alert, AttendanceLog, Inspection, Institute, Report, User

app = FastAPI(
    title="DRISHTI API",
    description="Smart Real-Time Monitoring & Inspection platform for DoSJE (SIH 26095)",
    version="0.2.0",
    # SECURITY/HARDENING: Swagger UI is served from a self-hosted bundle
    # under /static/swagger/ (NOT from cdn.jsdelivr.net) so the docs UI
    # works even when Render's outbound network can't reach third-party CDNs.
    docs_url="/docs-old",       # legacy path kept disabled to avoid clash
    redoc_url="/redoc-old",     # (ReDoc also defaults to cdn.jsdelivr.net)
)

# Shared HTTPBearer for the few endpoints (refresh, etc.) that read the
# token manually rather than via get_current_user.
bearer_scheme = HTTPBearer(auto_error=False)

# ---- upload validation helpers ----------------------------------------
MAX_PHOTO_BYTES = 5 * 1024 * 1024   # 5 MB per photo

def _is_jpeg(data: bytes) -> bool:
    return data[:3] == b"\xff\xd8\xff"

def _is_png(data: bytes) -> bool:
    return data[:8] == b"\x89PNG\r\n\x1a\n"

def _is_webp(data: bytes) -> bool:
    return data[:4] == b"RIFF" and data[8:12] == b"WEBP"

def sniff_image(data: bytes) -> str:
    """Return the sniffed image MIME, or '' if the bytes are not a real image."""
    if _is_jpeg(data): return "image/jpeg"
    if _is_png(data):  return "image/png"
    if _is_webp(data): return "image/webp"
    return ""

def _validate_photo_field(field_bytes: bytes, declared_filename: str) -> str:
    """Reject empty, oversized, or non-image uploads. Return sniffed mime."""
    if not field_bytes:
        raise HTTPException(400, "Photo is empty")
    if len(field_bytes) > MAX_PHOTO_BYTES:
        raise HTTPException(413, f"Photo exceeds {MAX_PHOTO_BYTES//1024//1024} MB limit")
    sniffed = sniff_image(field_bytes)
    if not sniffed:
        raise HTTPException(400, "Uploaded file is not a valid image "
                                 "(only JPEG / PNG / WebP accepted)")
    return sniffed

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---- self-hosted Swagger UI (no CDN) ---------------------------------
import os
from fastapi.responses import HTMLResponse, FileResponse

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
SWAGGER_DIR = os.path.join(STATIC_DIR, "swagger")
SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title} - API docs</title>
  <link rel="stylesheet" href="/static/swagger/swagger-ui.css" />
  <link rel="icon" href="data:," />
  <noscript>
    <style>
      body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
      h1 {{ color: #0d2137; }}
      a {{ color: #1565c0; }}
      table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
      th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 14px; }}
      th {{ background: #f4f6fa; }}
      code {{ background: #f4f6fa; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
    </style>
  </noscript>
</head>
<body>
  <noscript>
    <h1>{title}</h1>
    <p>Swagger UI needs JavaScript. Here is a quick reference:</p>
    <ul>
      <li><a href="/openapi.json">/openapi.json</a> &mdash; the full OpenAPI spec (JSON)</li>
      <li><a href="/docs">/docs</a> &mdash; this page (try enabling JavaScript)</li>
      <li><a href="/">/</a> &mdash; the API root</li>
    </ul>
    <h2>Demo accounts</h2>
    <table>
      <tr><th>Username</th><th>Password</th><th>Role</th></tr>
      <tr><td>admin</td><td>admin123</td><td>Department official</td></tr>
      <tr><td>ravi / priya / arjun</td><td>inspector123</td><td>PMU field inspectors</td></tr>
      <tr><td>ngostaff</td><td>institute123</td><td>NGO staff</td></tr>
    </table>
    <p>Get a token with <code>POST /login</code> then click &ldquo;Authorize&rdquo; in Swagger UI to test protected endpoints.</p>
  </noscript>
  <div id="swagger-ui"></div>
  <script src="/static/swagger/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {{
      window.ui = SwaggerUIBundle({{
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        plugins: [SwaggerUIBundle.plugins.DownloadUrl],
        layout: "StandaloneLayout",
        docExpansion: "none",
        persistAuthorization: true
      }});
    }};
  </script>
</body>
</html>
"""

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """Self-hosted Swagger UI - JS/CSS served from backend/static/swagger/.
    The default FastAPI docs page uses cdn.jsdelivr.net which Render's
    outbound network often can't reach, leaving the user with a blank
    page. This route ships the same UI from inside the repo."""
    if not os.path.isdir(SWAGGER_DIR):
        # Fallback: pure-HTML no-JS page so the docs are at least readable
        openapi = app.openapi()
        rows = []
        for path, ops in openapi.get("paths", {}).items():
            for method, op in ops.items():
                rows.append((method.upper(), path,
                             op.get("summary") or op.get("description") or ""))
        body = ['<table><tr><th>Method</th><th>Path</th><th>Summary</th></tr>']
        for m, p, s in rows:
            body.append(f'<tr><td><code>{m}</code></td>'
                        f'<td><code>{p}</code></td>'
                        f'<td>{s}</td></tr>')
        body.append('</table>')
        return HTMLResponse(
            "<h1>DRISHTI API</h1>"
            "<p>(Swagger UI assets not vendored yet. Showing plain list. "
            "Run <code>fetch_swagger.bat</code> on the server to enable the "
            "interactive UI.)</p>"
            '<p>Get a token: <code>POST /login</code> with '
            '<code>{"username":"admin","password":"admin123"}</code></p>'
            + "".join(body)
        )
    return HTMLResponse(SWAGGER_HTML.format(title=app.title))


# ---- security middleware -----------------------------------------------
async def add_security_headers(request, call_next):
    """Add baseline security headers to every response."""
    resp = await call_next(request)
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    # HSTS: only meaningful over HTTPS; browsers will simply ignore on http://
    resp.headers.setdefault(
        "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
    )
    # Content-Security-Policy: API responses don't render HTML, so the
    # restrictive default-src is fine.
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'none'; frame-ancestors 'none'",
    )
    return resp


app.middleware("http")(add_security_headers)


# CORS: env-driven allowlist. Default = "*" for local dev; set CORS_ORIGINS
# in production to your real origins (e.g. "https://drishti-dashboard.onrender.com").
_cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:8000,http://10.0.2.2:8000",
).split(",")
if "*" in _cors_origins or not any(o.strip() for o in _cors_origins):
    _cors_origins = ["*"]  # dev mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=600,
)

# Serve uploaded evidence photos at http://localhost:8000/uploads/<file>
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve self-hosted Swagger UI assets (vendor under backend/static/swagger/)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _ensure_schema_columns():
    """
    Tiny self-healing migration for columns added after the first deployment.
    Runs on every boot; each ALTER is a no-op once applied. Works identically
    on SQLite (local dev) and PostgreSQL (Supabase/Render) — no manual DB work.
    """
    from sqlalchemy import text
    statements = [
        "ALTER TABLE reports ADD COLUMN question_photos_json TEXT DEFAULT '{}'",
        # SECURITY hardening (added in v0.2.0): in-transit photo integrity
        "ALTER TABLE reports ADD COLUMN photo_sha256 VARCHAR(64)",
        "ALTER TABLE reports ADD COLUMN captured_at VARCHAR(40)",
        "ALTER TABLE reports ADD COLUMN device_id VARCHAR(64)",
    ]
    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass  # column already exists


_ensure_schema_columns()


# ================================================================ schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class AssignRequest(BaseModel):
    institute_id: int


class VCRequest(BaseModel):
    institute_id: int


class InstituteCreate(BaseModel):
    """Admin onboarding of a new institute (POST /institutes)."""
    name: str
    district: str
    scheme: str
    lat: float
    lng: float
    contact_person: str = ""
    phone: str = ""
    generate_attendance: bool = True   # 30 days of healthy logs => AI scan + chart work instantly


# ================================================================== AUTH
@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """All three apps (dashboard, Flutter app) log in here and get a JWT."""
    # SECURITY: rate-limit per username (5 / minute, 60s lockout beyond that)
    login_rate_limit_check(body.username)
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        login_rate_limit_record(body.username)
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {
        "token": create_access_token(user),
        "role": user.role,
        "name": user.name,
        "username": user.username,
    }


@app.post("/auth/refresh")
def refresh_token(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                  db: Session = Depends(get_db)):
    """
    Exchange an old (possibly just-expired) JWT for a fresh one.
    Accepts tokens that expired up to JWT_REFRESH_GRACE_SECONDS ago.
    """
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(creds.credentials, allow_grace=True)
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return {"token": create_access_token(user), "role": user.role}


@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "role": user.role,
            "username": user.username,
            "lat": user.lat, "lng": user.lng}


# =============================================================== MONITOR
@app.get("/institutes")
def list_institutes(db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    """Map pins for the dashboard. Colour comes from risk_score."""
    institutes = db.query(Institute).all()
    return [
        {
            "id": i.id, "name": i.name, "district": i.district,
            "scheme": i.scheme, "lat": i.lat, "lng": i.lng,
            "risk_score": i.risk_score,
            "contact_person": i.contact_person, "phone": i.phone,
        }
        for i in institutes
    ]


@app.get("/institutes/{institute_id}")
def institute_detail(institute_id: int, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    inst = db.get(Institute, institute_id)
    if not inst:
        raise HTTPException(404, "Institute not found")
    inspections = (
        db.query(Inspection)
        .filter(Inspection.institute_id == institute_id)
        .order_by(Inspection.scheduled_at.desc())
        .all()
    )
    return {
        **{"id": inst.id, "name": inst.name, "district": inst.district,
           "scheme": inst.scheme, "lat": inst.lat, "lng": inst.lng,
           "risk_score": inst.risk_score},
        "inspections": [
            {"id": x.id, "status": x.status, "is_random": x.is_random,
             "seed": x.assignment_seed, "scheduled_at": str(x.scheduled_at)}
            for x in inspections
        ],
    }


@app.get("/institutes/{institute_id}/risk-breakdown")
def institute_risk_breakdown(institute_id: int, db: Session = Depends(get_db),
                             user: User = Depends(get_current_user)):
    """
    Explain WHY an institute's risk score is what it is:
    returns the score plus each contributing factor (alerts,
    incomplete inspections, weak attendance). Also recomputes and
    persists the score so the returned number always matches the
    stored institute.risk_score.
    """
    inst = db.get(Institute, institute_id)
    if not inst:
        raise HTTPException(404, "Institute not found")
    # Recompute + persist so the returned score matches DB
    ai_engine.compute_risk_score(db, inst)
    db.commit()
    score, factors = ai_engine.risk_factors(db, inst)
    return {
        "institute_id": institute_id,
        "name": inst.name,
        "score": score,
        "factors": factors,
        "hint": ("Resolve the open alerts and complete pending inspections "
                 "to lower this score." if factors else None),
    }


@app.get("/attendance/analytics/{institute_id}")
def attendance_analytics(institute_id: int, db: Session = Depends(get_db),
                         user: User = Depends(get_current_user)):
    """Daily expected-vs-present series for the dashboard chart."""
    logs = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.institute_id == institute_id)
        .order_by(AttendanceLog.log_date)
        .all()
    )
    return [
        {"date": str(l.log_date), "expected": l.expected,
         "present": l.present, "face_verified": l.face_verified}
        for l in logs
    ]


CCTV_STREAMS = [
    # Demo: 3 self-hosted loops under dashboard/public/cctv (committed
    # to the repo) so they can never die mid-demo. Frontend detects a
    # relative URL and plays with plain <video loop muted>, no HLS.
    {"id": 1, "label": "Institute 1 – Main Hall (students)",
     "url": "/cctv/cam1-classroom.mp4"},
    {"id": 2, "label": "Institute 2 – Hallway",
     "url": "/cctv/cam2-hallway.mp4"},
    {"id": 3, "label": "Institute 3 – Corridor",
     "url": "/cctv/cam3-corridor.mp4"},
    {"id": 4, "label": "LIVE SITE CAMERA (DroidCam phone)",
     "url": "droidcam"},   # dashboard shows instructions for this tile
]


@app.get("/cctv/streams")
def cctv_streams(user: User = Depends(get_current_user)):
    return CCTV_STREAMS


# ====================================================== MANAGE (admin CRUD)
@app.post("/institutes", status_code=201)
def create_institute(body: InstituteCreate,
                     db: Session = Depends(get_db),
                     user: User = Depends(require_role("admin"))):
    """
    Admin panel: onboard a new institute without touching seed.py.
    Optionally generates 30 days of healthy attendance (same pattern as
    seed.py) so map colours, the attendance chart and AI anomaly scans all
    work immediately on the new pin.
    """
    inst = Institute(
        name=body.name.strip(), district=body.district.strip(),
        scheme=body.scheme.strip(), lat=body.lat, lng=body.lng,
        contact_person=body.contact_person.strip() or None,
        phone=body.phone.strip() or None,
        risk_score=10,                       # neutral starting score, like seed.py
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)

    generated_days = 0
    if body.generate_attendance:
        rng = random.Random(inst.id)         # deterministic per institute
        expected = rng.choice([40, 50, 60, 80])
        today = date.today()
        for d in range(30):
            day = today - timedelta(days=d)
            if day.weekday() == 6:           # Sunday holiday, matches seed.py
                continue
            db.add(AttendanceLog(
                institute_id=inst.id, log_date=day,
                expected=expected,
                present=int(expected * rng.uniform(0.88, 0.99)),
                face_verified=rng.random() > 0.15,
            ))
            generated_days += 1
        db.commit()

    db.add(Alert(
        type="institute_added",
        severity="low",
        message=f"{inst.name} ({inst.district}) onboarded by {user.name}.",
    ))
    db.commit()

    return {
        "id": inst.id, "name": inst.name, "district": inst.district,
        "scheme": inst.scheme, "lat": inst.lat, "lng": inst.lng,
        "risk_score": inst.risk_score,
        "contact_person": inst.contact_person, "phone": inst.phone,
        "attendance_generated": generated_days,
    }


# ================================================================ DETECT
@app.post("/analytics/run-anomaly")
def run_anomaly(db: Session = Depends(get_db),
                user: User = Depends(require_role("admin"))):
    """Train IsolationForest on attendance data and flag outlier institutes."""
    flagged = ai_engine.run_anomaly_detection(db)
    return {"flagged_count": len(flagged), "flagged": flagged}


@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
    ack_names = {}
    for a in alerts:
        if a.acknowledged_by:
            ack_names[a.id] = db.get(User, a.acknowledged_by).name
    return [
        {"id": a.id, "type": a.type, "severity": a.severity,
         "message": a.message, "resolved": a.resolved,
         "acknowledged": a.acknowledged,
         "acknowledged_by": ack_names.get(a.id),
         "created_at": str(a.created_at), "institute_id": a.institute_id}
        for a in alerts
    ]


@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db),
                      user: User = Depends(require_role("inspector"))):
    """Inspector marks an alert as seen/acted-upon (resolution stays with admins)."""
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = True
    alert.acknowledged_by = user.id
    db.commit()
    return {"ok": True, "alert_id": alert_id, "acknowledged_by": user.name}


# ================================================================ VERIFY
@app.post("/inspections/assign-random")
def assign_random(body: AssignRequest, db: Session = Depends(get_db),
                  user: User = Depends(require_role("admin"))):
    """
    AI picks the inspector for a surprise inspection.
    The RNG seed is stored on the inspection row -> auditable fairness.
    """
    inst = db.get(Institute, body.institute_id)
    if not inst:
        raise HTTPException(404, "Institute not found")

    inspection = ai_engine.assign_random_inspection(db, inst)
    inspector = db.get(User, inspection.inspector_id)

    db.add(Alert(
        type="inspection_assigned",
        severity="medium",
        message=(f"Surprise inspection assigned for {inst.name} to "
                 f"{inspector.name}. Seed={inspection.assignment_seed}"),
        institute_id=inst.id,
        audience="admin",
    ))
    # direct notification to the assigned inspector
    db.add(Alert(
        type="inspection_assigned",
        severity="medium",
        message=(f"🎯 NEW ASSIGNMENT: Surprise inspection at {inst.name} "
                 f"({inst.district}). Check My Tasks in the field app."),
        institute_id=inst.id,
        target_user_id=inspector.id,
    ))
    db.commit()

    return {
        "inspection_id": inspection.id,
        "assigned_to": inspector.name,
        "distance_km": round(ai_engine.haversine_km(
            inspector.lat, inspector.lng, inst.lat, inst.lng), 2),
        "assignment_seed": inspection.assignment_seed,
        "note": "Seed stored — re-running it reproduces the exact same draw.",
    }


@app.post("/inspections/{inspection_id}/start")
def start_inspection(inspection_id: int, db: Session = Depends(get_db),
                     user: User = Depends(require_role("inspector"))):
    """Inspector marks an assigned task as in_progress (assigned -> in_progress)."""
    insp = db.get(Inspection, inspection_id)
    if not insp:
        raise HTTPException(404, "Inspection not found")
    if insp.inspector_id != user.id:
        raise HTTPException(403, "This inspection belongs to another inspector")
    if insp.status == "completed":
        raise HTTPException(400, "Already completed")
    insp.status = "in_progress"
    db.commit()
    return {"ok": True, "inspection_id": inspection_id, "status": "in_progress"}


@app.get("/inspections/my")
def my_inspections(db: Session = Depends(get_db),
                   user: User = Depends(require_role("inspector"))):
    """Tasks shown in the Flutter field app."""
    rows = (
        db.query(Inspection)
        .filter(Inspection.inspector_id == user.id)
        .order_by(Inspection.scheduled_at.desc())
        .all()
    )
    out = []
    for r in rows:
        inst = db.get(Institute, r.institute_id)
        out.append({
            "inspection_id": r.id, "status": r.status,
            "is_random": r.is_random, "scheduled_at": str(r.scheduled_at),
            "institute_id": inst.id, "institute_name": inst.name,
            "district": inst.district, "scheme": inst.scheme,
            "lat": inst.lat, "lng": inst.lng,
        })
    return out


@app.post("/vc/start")
def start_vc(body: VCRequest, db: Session = Depends(get_db),
             user: User = Depends(require_role("admin"))):
    """Create a surprise Jitsi video-conference room with an institute."""
    inst = db.get(Institute, body.institute_id)
    if not inst:
        raise HTTPException(404, "Institute not found")

    room = f"drishti-inst{inst.id}-{int(__import__('time').time())}"
    url = f"https://meet.jit.si/{room}"

    db.add(Alert(
        type="vc_started",
        severity="medium",
        message=f"Surprise VC initiated with {inst.name}: {url}",
        institute_id=inst.id,
        audience="admin",
    ))
    # notify every field inspector so anyone nearby can join/support
    db.add(Alert(
        type="vc_started",
        severity="medium",
        message=(f"📞 SURPRISE VC at {inst.name} ({inst.district}) is LIVE. "
                 f"Join: {url}"),
        institute_id=inst.id,
        audience="inspector",
    ))
    db.commit()
    return {"room": room, "url": url}


# ========================================================== NOTIFICATIONS
@app.get("/notifications")
def my_notifications(db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    """
    Unread notifications for the logged-in user:
      - direct:   target_user_id == me
      - by role:  target_user_id IS NULL and audience == my role
    """
    rows = (
        db.query(Alert)
        .filter(
            Alert.is_read.is_(False),
            ((Alert.target_user_id == user.id) |
             ((Alert.target_user_id.is_(None)) & (Alert.audience == user.role))),
        )
        .order_by(Alert.created_at.desc())
        .limit(30)
        .all()
    )
    return [
        {"id": n.id, "type": n.type, "severity": n.severity,
         "message": n.message, "created_at": str(n.created_at),
         "institute_id": n.institute_id}
        for n in rows
    ]


@app.post("/notifications/{alert_id}/read")
def mark_notification_read(alert_id: int, db: Session = Depends(get_db),
                           user: User = Depends(get_current_user)):
    n = db.get(Alert, alert_id)
    if not n:
        raise HTTPException(404, "Notification not found")
    # only the recipient (or that role) may dismiss it
    if n.target_user_id not in (None, user.id) and n.audience != user.role:
        raise HTTPException(403, "Not your notification")
    n.is_read = True
    db.commit()
    return {"ok": True}


@app.post("/notifications/read-all")
def mark_all_notifications_read(db: Session = Depends(get_db),
                                user: User = Depends(get_current_user)):
    rows = (
        db.query(Alert)
        .filter(
            Alert.is_read.is_(False),
            ((Alert.target_user_id == user.id) |
             ((Alert.target_user_id.is_(None)) & (Alert.audience == user.role))),
        )
        .all()
    )
    for n in rows:
        n.is_read = True
    db.commit()
    return {"ok": True, "marked": len(rows)}


# ================================================================ REPORT
CHECKLIST_QUESTIONS = [
    "Staff physically present?",
    "Beneficiaries visible on site?",
    "Records / registers available?",
    "Scheme activities running today?",
    "Facilities clean & usable?",
]


@app.post("/reports")
async def submit_report(
    inspection_id: int = Form(...),
    geo_lat: float = Form(...),
    geo_lng: float = Form(...),
    checklist: str = Form(...),           # JSON string of yes/no answers
    photo: UploadFile = File(...),        # main overview evidence (required)
    q0_photo: UploadFile = File(None),    # optional per-checklist-item photos
    q1_photo: UploadFile = File(None),
    q2_photo: UploadFile = File(None),
    q3_photo: UploadFile = File(None),
    q4_photo: UploadFile = File(None),
    # SECURITY: in-transit integrity manifest
    photo_sha256: str = Form(None),       # client-computed SHA-256 hex
    captured_at:  str = Form(None),       # ISO 8601 device capture time
    device_id:    str = Form(None),       # stable per-install UUID
    db: Session = Depends(get_db),
    user: User = Depends(require_role("inspector")),
):
    """
    Field-app submission: GPS + photo + checklist.
    AI runs face detection on the photo; zero faces => possible_proxy flag.

    SECURITY: the client computes SHA-256 of the photo bytes and sends it
    along with a captured_at timestamp and a per-install device_id. The
    server re-hashes the photo and refuses to accept the report if the
    hashes don't match (catches in-flight tampering).
    """
    inspection = db.get(Inspection, inspection_id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")
    if inspection.inspector_id != user.id:
        raise HTTPException(403, "This inspection belongs to another inspector")

    # Read the uploaded photo ONCE — reused for saving, hash, and AI analysis
    image_bytes = await photo.read()
    _validate_photo_field(image_bytes, photo.filename or "photo.jpg")

    # SECURITY: reject in-flight tampered photos
    if photo_sha256:
        if not re.fullmatch(r"[0-9a-f]{64}", photo_sha256 or ""):
            raise HTTPException(400, "photo_sha256 must be a 64-char hex string")
        if _sha256_hex(image_bytes) != photo_sha256:
            raise HTTPException(
                400, "Photo integrity check failed (hash mismatch — "
                     "the photo was modified between the device and the server)")

    # Build a safe extension from the sniffed MIME (NOT from the filename —
    # never trust client-provided extensions).
    sniffed = sniff_image(image_bytes)
    ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    ext = ext_map.get(sniffed, ".jpg")
    path = os.path.join("uploads", f"report_{inspection_id}_{user.id}{ext}")
    with open(path, "wb") as f:
        f.write(image_bytes)

    # ---- optional per-checklist-item photos (photo proof per answer) ----
    question_files = [q0_photo, q1_photo, q2_photo, q3_photo, q4_photo]
    question_photos = {}
    for idx, qfile in enumerate(question_files):
        if qfile is None or not qfile.filename:
            continue
        qb = await qfile.read()
        if not qb:
            continue
        _validate_photo_field(qb, qfile.filename)
        qext = ext_map.get(sniff_image(qb), ".jpg")
        qpath = os.path.join(
            "uploads", f"report_{inspection_id}_{user.id}_q{idx}{qext}")
        with open(qpath, "wb") as f:
            f.write(qb)
        question_photos[str(idx)] = "/" + qpath.replace("\\", "/")

    # ---- AI proxy check ----
    face_count = ai_engine.detect_faces_in_photo(image_bytes)
    flags = []
    if face_count == 0:
        flags.append("possible_proxy")   # no humans visible in evidence photo
    elif face_count == -1:
        flags.append("unreadable_image")

    report = Report(
        inspection_id=inspection_id,
        geo_lat=geo_lat, geo_lng=geo_lng,
        photo_path=path.replace("\\", "/"),
        checklist_json=checklist,
        ai_flags=",".join(flags),
        question_photos_json=json.dumps(question_photos),
        photo_sha256=_sha256_hex(image_bytes),
        captured_at=(captured_at or "")[:40] or None,
        device_id=(device_id or "")[:64] or None,
    )
    db.add(report)

    inspection.status = "completed"
    inspection.completed_at = __import__("datetime").datetime.utcnow()

    inst = db.get(Institute, inspection.institute_id)
    if "possible_proxy" in flags:
        db.add(Alert(
            type="proxy_suspect",
            severity="high",
            message=(f"Evidence photo from {inst.name} contains NO human faces "
                     f"— possible fake/proxy reporting by field staff."),
            institute_id=inst.id,
            audience="admin",
        ))

    # ---- auto-generate the official report event (nobody writes it by hand)
    db.add(Alert(
        type="inspection_completed",
        severity="low",
        message=(f"📋 Inspection #{inspection.id} completed at {inst.name} "
                 f"by {user.name}. Official report generated automatically."),
        institute_id=inst.id,
        audience="admin",
    ))

    ai_engine.compute_risk_score(db, inst)
    ai_engine.notify_high_risk(db, inst)   # admin notification if score >= 70
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "ai_flags": flags,
        "faces_detected": face_count,
        "checklist_questions": CHECKLIST_QUESTIONS,
        "photo_url": f"/{report.photo_path}",
        "question_photos": question_photos,
        "document_url": f"/reports/{report.id}/document",
    }


@app.get("/reports")
def list_reports(db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    rows = db.query(Report).order_by(Report.created_at.desc()).all()
    out = []
    for r in rows:
        insp = db.get(Inspection, r.inspection_id)
        inst = db.get(Institute, insp.institute_id)
        out.append({
            "id": r.id, "institute_name": inst.name,
            "inspection_id": r.inspection_id,
            "inspector_id": insp.inspector_id,
            "geo_lat": r.geo_lat, "geo_lng": r.geo_lng,
            "photo_url": f"/{r.photo_path}",
            "checklist": json.loads(r.checklist_json),
            "ai_flags": [f for f in r.ai_flags.split(",") if f],
            "question_photos": json.loads(r.question_photos_json or "{}"),
            "created_at": str(r.created_at),
        })
    return out


# ==================================================== AUTO REPORT DOCUMENT
@app.get("/reports/{report_id}/document")
def report_document(report_id: int, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    """
    Auto-generated OFFICIAL INSPECTION REPORT — compiled live from the data
    the moment an inspector submits. Nobody writes it by hand; nothing is
    stored stale. The dashboard renders this as a print/PDF-ready document.
    """
    r = db.get(Report, report_id)
    if not r:
        raise HTTPException(404, "Report not found")
    insp = db.get(Inspection, r.inspection_id)
    inst = db.get(Institute, insp.institute_id)
    inspector = db.get(User, insp.inspector_id)

    answers = json.loads(r.checklist_json)
    qphotos = json.loads(r.question_photos_json or "{}")
    checklist_rows = [
        {
            "question": q,
            "answer": "Yes" if a in (True, "yes", "true", True) else "No",
            "photo_url": qphotos.get(str(i)),
        }
        for i, (q, a) in enumerate(answers.items())
    ]

    return {
        "title": "OFFICIAL INSPECTION REPORT",
        "authority": "Dept. of Social Justice & Empowerment · DRISHTI Platform",
        "report_id": r.id,
        "inspection_id": r.inspection_id,
        "generated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "institute": {
            "name": inst.name, "district": inst.district,
            "scheme": inst.scheme,
            "contact_person": inst.contact_person, "phone": inst.phone,
        },
        "inspector": {"name": inspector.name if inspector else "Unknown",
                      "username": inspector.username if inspector else "-"},
        "captured_at": str(r.created_at),
        "gps": {"lat": r.geo_lat, "lng": r.geo_lng},
        "map_link": f"https://www.google.com/maps?q={r.geo_lat},{r.geo_lng}",
        "checklist": checklist_rows,
        "main_photo_url": f"/{r.photo_path}",
        "ai_verification": {
            "flags": [f for f in r.ai_flags.split(",") if f],
            "summary": ("⚠ AI raised flags on this evidence — review required."
                        if r.ai_flags else
                        "✔ Evidence passed automated verification."),
        },
        "risk_score_now": inst.risk_score,
        "random_assignment": (
            {"audit_seed": insp.assignment_seed} if insp.is_random else None),
    }


# =================================================================== ACT
@app.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db),
                  user: User = Depends(require_role("admin"))):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.resolved = True
    if alert.institute_id:
        inst = db.get(Institute, alert.institute_id)
        ai_engine.compute_risk_score(db, inst)
    db.commit()
    return {"ok": True, "alert_id": alert_id}


# ------------------------------------------------- Google Maps link helper
@app.post("/utils/expand-maps-link")
def expand_maps_link(body: dict,
                     user: User = Depends(require_role("admin"))):
    """
    Resolve a short https://maps.app.goo.gl/xxx link to its final long URL
    so the dashboard can extract lat/lng. Long links are returned as-is.
    """
    url = (body or {}).get("url", "").strip()
    if not url:
        raise HTTPException(400, "Missing 'url' in body")

    if not ("goo.gl" in url or "maps.app." in url):
        return {"url": url}          # already a long link

    import urllib.request
    req = urllib.request.Request(url, method="HEAD")
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
    try:
        with opener.open(req, timeout=8) as resp:
            return {"url": resp.url}
    except Exception as e:
        raise HTTPException(400, f"Could not resolve short link: {e}")


@app.get("/")
def root():
    return {"app": "DRISHTI API", "docs": "/docs"}