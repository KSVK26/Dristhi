"""
DRISHTI - Database Models (tables)
----------------------------------
Six tables power the whole prototype:

  User          -> admins, inspectors (PMU), institute staff  (RBAC roles)
  Institute     -> NGO / project / institute being monitored
  Inspection    -> an inspection task (random or scheduled)
  Report        -> geo-tagged evidence submitted from the field app
  AttendanceLog -> daily beneficiary attendance (feeds the anomaly AI)
  Alert         -> anomalies / events raised by the AI engine
"""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """Any person who logs in. role enforces RBAC: admin | inspector | institute."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' | 'inspector' | 'institute'
    password_hash = Column(String(200), nullable=False)

    # last known GPS position of field inspectors (used for nearest-officer assignment)
    lat = Column(Float, default=28.6139)   # default: New Delhi
    lng = Column(Float, default=77.2090)


class Institute(Base):
    """A project / NGO / institute running under a DoSJE scheme."""

    __tablename__ = "institutes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    district = Column(String(80), nullable=False)
    scheme = Column(String(120), nullable=False)      # e.g. 'PM-DAKSH', 'Vayoshreshtha Samman'
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    risk_score = Column(Integer, default=10)           # 0-100, drives map colour
    contact_person = Column(String(100))
    phone = Column(String(20))

    inspections = relationship("Inspection", back_populates="institute")
    attendance_logs = relationship("AttendanceLog", back_populates="institute")


class Inspection(Base):
    """An inspection task assigned to a field inspector."""

    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey("institutes.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="assigned")    # assigned | in_progress | completed
    is_random = Column(Boolean, default=False)         # True => AI surprise assignment
    assignment_seed = Column(String(32))               # stored RNG seed = tamper-proof fairness proof
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    institute = relationship("Institute", back_populates="inspections")
    inspector = relationship("User")
    reports = relationship("Report", back_populates="inspection")


class Report(Base):
    """Geo-tagged evidence submitted by an inspector from the mobile app."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    geo_lat = Column(Float, nullable=False)
    geo_lng = Column(Float, nullable=False)
    photo_path = Column(String(300), nullable=False)   # file saved under backend/uploads/
    checklist_json = Column(Text, nullable=False)      # answers to the yes/no checklist
    ai_flags = Column(String(300), default="")         # e.g. 'possible_proxy', 'geo_mismatch'
    # optional per-checklist-item evidence: {"0": "/uploads/..._q0.jpg", ...}
    question_photos_json = Column(Text, default="{}")
    # SECURITY: in-transit integrity — hash of the photo bytes computed
    # on the client, re-verified server-side; SHA-256 hex (64 chars).
    photo_sha256 = Column(String(64), nullable=True)
    # ISO-8601 timestamp the inspector captured the photo on-device.
    captured_at = Column(String(40), nullable=True)
    # Stable per-install device id; helps correlate submissions to a phone
    # and detect anomalies (a stolen token + new device would show up here).
    device_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="reports")


class AttendanceLog(Base):
    """Daily beneficiary attendance per institute — input for IsolationForest AI."""

    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey("institutes.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    expected = Column(Integer, nullable=False)
    present = Column(Integer, nullable=False)
    face_verified = Column(Boolean, default=False)     # did CCTV/photo face-check pass?

    institute = relationship("Institute", back_populates="attendance_logs")


class Alert(Base):
    """Anything the system wants officials to notice immediately."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)          # anomaly | proxy_suspect | vc_started | ...
    severity = Column(String(10), default="low")       # low | medium | high
    message = Column(Text, nullable=False)
    institute_id = Column(Integer, ForeignKey("institutes.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ---- notification routing (v1) ----
    # audience: 'admin' | 'inspector' | NULL (NULL = system/event log, not a notification)
    audience = Column(String(20), nullable=True)
    # target_user_id: direct notification to one user (e.g. assigned inspector)
    target_user_id = Column(Integer, nullable=True)
    # is_read: notification consumed? (alerts list keeps using `resolved`)
    is_read = Column(Boolean, default=False)
    # acknowledged: an inspector has seen/acted on this alert (resolution
    # itself stays with admins)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, nullable=True)