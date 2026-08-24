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
import shutil

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import ai_engine
from auth import create_access_token, get_current_user, require_role, verify_password
from database import get_db
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


# ================================================================ schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class AssignRequest(BaseModel):
    institute_id: int


class VCRequest(BaseModel):
    institute_id: int


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
    return {"id": user.id, "name": user.name, "role": user.role}


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
    return [
        {"id": a.id, "type": a.type, "severity": a.severity,
         "message": a.message, "resolved": a.resolved,
         "created_at": str(a.created_at), "institute_id": a.institute_id}
        for a in alerts
    ]


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
    ))
    db.commit()
    return {"room": room, "url": url}


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
    photo: UploadFile = File(...),
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
        ))

    ai_engine.compute_risk_score(db, inst)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "ai_flags": flags,
        "faces_detected": face_count,
        "checklist_questions": CHECKLIST_QUESTIONS,
        "photo_url": f"/{report.photo_path}",
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
            "geo_lat": r.geo_lat, "geo_lng": r.geo_lng,
            "photo_url": f"/{r.photo_path}",
            "checklist": json.loads(r.checklist_json),
            "ai_flags": [f for f in r.ai_flags.split(",") if f],
            "created_at": str(r.created_at),
        })
    return out


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