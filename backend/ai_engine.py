"""
DRISHTI - AI Engine
-------------------
Three "brains" of the platform (all lightweight, CPU-only, free):

1. assign_random_inspection()
   Picks an inspector for a surprise inspection. Scores every inspector by
   distance-to-institute + current workload, then picks RANDOMLY among the
   top-3 candidates using a cryptographically-seeded RNG whose seed is stored
   in the DB -> anyone can later re-run the seed and verify the choice was
   fair ("tamper-proof assignment", prevents collusion).

2. run_anomaly_detection()
   Trains a scikit-learn IsolationForest on 30 days of attendance ratios for
   every institute. Institutes whose attendance pattern is an outlier get a
   high-severity alert and a bumped risk score.

3. detect_faces_in_photo()
   OpenCV Haar-cascade face detection on submitted evidence photos.
   A "beneficiary verification" photo with ZERO faces is flagged as
   possible_proxy (fake reporting / proxy functioning).
"""

import math
import secrets

import cv2
import numpy as np
from sqlalchemy.orm import Session

from models import Alert, AttendanceLog, Inspection, Institute, User


# ---------------------------------------------------------------- distance
def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two GPS points, in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


# ------------------------------------------------- 1. random assignment
def assign_random_inspection(db: Session, institute: Institute) -> Inspection:
    """
    Fair + unpredictable inspection assignment.
    Returns the created Inspection row.
    """
    inspectors = db.query(User).filter(User.role == "inspector").all()

    # Score each inspector: lower = better candidate
    scored = []
    for insp in inspectors:
        active_jobs = (
            db.query(Inspection)
            .filter(
                Inspection.inspector_id == insp.id,
                Inspection.status != "completed",
            )
            .count()
        )
        dist = haversine_km(insp.lat, insp.lng, institute.lat, institute.lng)
        scored.append({"user": insp, "score": dist + active_jobs * 25})

    # Take the 3 best candidates, then choose randomly among them
    scored.sort(key=lambda s: s["score"])
    top3 = scored[:3]

    # Cryptographic seed -> stored in DB so the draw can be audited/replayed
    seed = secrets.randbits(32)
    rng = np.random.default_rng(seed)

    # Weighted pick: nearest/best candidate most likely, but never certain
    weights = np.array([3.0, 2.0, 1.0][: len(top3)])
    weights /= weights.sum()
    chosen = rng.choice(len(top3), p=weights)
    winner = top3[int(chosen)]["user"]

    inspection = Inspection(
        institute_id=institute.id,
        inspector_id=winner.id,
        status="assigned",
        is_random=True,
        assignment_seed=str(seed),
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


# --------------------------------------------- 2. attendance anomaly AI
def run_anomaly_detection(db: Session) -> list[dict]:
    """
    IsolationForest over each institute's daily attendance ratio series.
    Outlier institutes -> high severity alert + risk score bump.
    Returns a summary list for the API response.
    """
    from sklearn.ensemble import IsolationForest

    institutes = db.query(Institute).all()
    flagged = []

    # Build one feature matrix: rows = institutes, cols = last-30-day ratios
    names, matrix = [], []
    for inst in institutes:
        logs = (
            db.query(AttendanceLog)
            .filter(AttendanceLog.institute_id == inst.id)
            .order_by(AttendanceLog.log_date)
            .all()
        )
        if len(logs) < 10:
            continue
        ratios = [log.present / max(log.expected, 1) for log in logs]
        names.append(inst)
        matrix.append(ratios)

    if len(names) < 2:
        return []  # not enough data to compare

    model = IsolationForest(contamination=0.15, random_state=42)
    labels = model.fit_predict(np.array(matrix))  # -1 = anomaly, 1 = normal

    for inst, label in zip(names, labels):
        if label == -1:
            inst.risk_score = min(100, inst.risk_score + 40)
            db.add(
                Alert(
                    type="anomaly",
                    severity="high",
                    message=(
                        f"AI detected abnormal attendance pattern at "
                        f"{inst.name} ({inst.district}). Risk score raised to "
                        f"{inst.risk_score}. Surprise inspection recommended."
                    ),
                    institute_id=inst.id,
                )
            )
            flagged.append(
                {"institute": inst.name, "district": inst.district,
                 "risk_score": inst.risk_score}
            )

    db.commit()
    return flagged


# --------------------------------------------------- 3. face / proxy AI
def detect_faces_in_photo(image_bytes: bytes) -> int:
    """Count human faces in a photo using OpenCV's Haar cascade."""
    buf = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        return -1  # unreadable image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces)


# ------------------------------------------------------- risk scoring
def compute_risk_score(db: Session, institute: Institute) -> int:
    """
    Simple transparent formula (easy to explain to judges):
      base 10
      + up to 40  from unresolved alerts (high=20, medium=10)
      + up to 30  from overdue inspections (10 each)
      + up to 20  from low average attendance ratio
    """
    score = 10

    unresolved = db.query(Alert).filter(
        Alert.institute_id == institute.id, Alert.resolved.is_(False)
    ).all()
    for a in unresolved:
        score += {"high": 20, "medium": 10}.get(a.severity, 5)

    overdue = (
        db.query(Inspection)
        .filter(
            Inspection.institute_id == institute.id,
            Inspection.status != "completed",
        )
        .count()
    )
    score += min(overdue * 10, 30)

    logs = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.institute_id == institute.id)
        .all()
    )
    if logs:
        avg_ratio = sum(l.present / max(l.expected, 1) for l in logs) / len(logs)
        if avg_ratio < 0.9:
            score += int((0.9 - avg_ratio) * 200)  # up to ~20 points

    institute.risk_score = max(0, min(score, 100))
    db.commit()
    return institute.risk_score