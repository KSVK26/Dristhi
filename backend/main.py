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
import shutil

from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import ai_engine
from auth import create_access_token, get_current_user, require_role, verify_password
from database import engine, get_db
from models import Alert, AttendanceLog, Inspection, Institute, Report, User

app = FastAPI(
    title="DRISHTI API",
    description="Smart Real-Time Monitoring & Inspection platform for DoSJE (SIH 26095)",
    version="0.1.0",
)

# Allow the React dashboard + Flutter app (running on other ports) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # demo only — restrict in production!
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded evidence photos at http://localhost:8000/uploads/<file>
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def _ensure_schema_columns():
    """
    Tiny self-healing migration for columns added after the first deployment.
    Runs on every boot; each ALTER is a no-op once applied. Works identically
    on SQLite (local dev) and PostgreSQL (Supabase/Render) — no manual DB work.
    """
    from sqlalchemy import text
    statements = [
        "ALTER TABLE reports ADD COLUMN question_photos_json TEXT DEFAULT '{}'",
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
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {
        "token": create_access_token(user),
        "role": user.role,
        "name": user.name,
        "username": user.username,
    }


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
    # Free public HLS test streams simulate real RTSP/IP-camera feeds.
    {"id": 1, "label": "Institute 1 – Main Hall",
     "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"},
    {"id": 2, "label": "Institute 2 – Classroom A",
     "url": "https://test-streams.mux.dev/pts_shift/master.m3u8"},
    {"id": 3, "label": "Institute 3 – Entrance Gate",
     "url": "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8"},
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
    db: Session = Depends(get_db),
    user: User = Depends(require_role("inspector")),
):
    """
    Field-app submission: GPS + photo + checklist.
    AI runs face detection on the photo; zero faces => possible_proxy flag.
    """
    inspection = db.get(Inspection, inspection_id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")
    if inspection.inspector_id != user.id:
        raise HTTPException(403, "This inspection belongs to another inspector")

    # Read the uploaded photo ONCE — reused for both saving and AI analysis
    image_bytes = await photo.read()

    ext = os.path.splitext(photo.filename or "photo.jpg")[1] or ".jpg"
    path = os.path.join("uploads", f"report_{inspection_id}_{user.id}{ext}")
    with open(path, "wb") as f:
        f.write(image_bytes)

    # ---- optional per-checklist-item photos (photo proof per answer) ----
    question_files = [q0_photo, q1_photo, q2_photo, q3_photo, q4_photo]
    question_photos = {}
    for idx, qfile in enumerate(question_files):
        if qfile is None or not qfile.filename:
            continue
        qext = os.path.splitext(qfile.filename or "q.jpg")[1] or ".jpg"
        qpath = os.path.join(
            "uploads", f"report_{inspection_id}_{user.id}_q{idx}{qext}")
        with open(qpath, "wb") as f:
            f.write(await qfile.read())
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


@app.get("/")
def root():
    return {"app": "DRISHTI API", "docs": "/docs"}