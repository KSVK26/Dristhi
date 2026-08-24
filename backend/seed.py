"""
DRISHTI - Demo Data Seeder
--------------------------
Run once before the demo:
    python seed.py

Creates:
  * 1 admin, 3 field inspectors (PMU), 1 institute staff user
  * 6 institutes across Delhi-NCR districts under real DoSJE schemes
  * 30 days of daily attendance per institute — with 2 institutes
    deliberately given abnormal patterns so the AI has something to find
"""

import random
from datetime import date, timedelta

from auth import hash_password
from database import Base, SessionLocal, engine
from models import AttendanceLog, Institute, User

random.seed(42)  # reproducible demo data


def main():
    # Create all tables from the models
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    if db.query(User).count() > 0:
        print("Database already seeded — skipping. Delete drishti.db to re-seed.")
        return

    # ---------------- users ----------------
    users = [
        User(username="admin", name="DoSJE Oversight Officer",
             role="admin", password_hash=hash_password("admin123")),
        User(username="ravi", name="Ravi Kumar (PMU)",
             role="inspector", lat=28.7041, lng=77.1025,
             password_hash=hash_password("inspector123")),   # Rohini side
        User(username="priya", name="Priya Sharma (PMU)",
             role="inspector", lat=28.4595, lng=77.0266,
             password_hash=hash_password("inspector123")),   # Gurugram side
        User(username="arjun", name="Arjun Verma (PMU)",
             role="inspector", lat=28.6139, lng=77.2090,
             password_hash=hash_password("inspector123")),   # Central Delhi
        User(username="ngostaff", name="Shalini (Institute Staff)",
             role="institute", password_hash=hash_password("institute123")),
    ]
    db.add_all(users)

    # ------------- institutes -------------
    institutes = [
        Institute(name="Samarth Skill Centre – Rohini", district="North West Delhi",
                  scheme="PM-DAKSH", lat=28.7495, lng=77.0565,
                  contact_person="Mr. Anil Gupta", phone="+91-9810011111"),
        Institute(name="Divyangjan Rehabilitation Home – Dwarka", district="South West Delhi",
                  scheme="ADIP Scheme", lat=28.5921, lng=77.0460,
                  contact_person="Mrs. Kavita Rao", phone="+91-9810022222"),
        Institute(name="Vriddha Ashray Seva Sadan – Narela", district="North Delhi",
                  scheme="National Action Plan for Senior Citizens", lat=28.8527, lng=77.0929,
                  contact_person="Mr. Suresh Yadav", phone="+91-9810033333"),
        Institute(name="Garima Aashiyam – Badarpur", district="South East Delhi",
                  scheme="SMILE Scheme", lat=28.4986, lng=77.3025,
                  contact_person="Ms. Farah Khan", phone="+91-9810044444"),
        Institute(name="Pradhan Mantri Daksh Kendra – Najafgarh", district="West Delhi",
                  scheme="PM-DAKSH", lat=28.5706, lng=76.9342,
                  contact_person="Mr. Rakesh Mehta", phone="+91-9810055555"),
        Institute(name="Nasha Mukt Bharat Centre – Shahdara", district="East Delhi",
                  scheme="NMBA", lat=28.6733, lng=77.2970,
                  contact_person="Dr. Neha Singh", phone="+91-9810066666"),
    ]
    db.add_all(institutes)
    db.commit()

    # ------------- attendance logs (30 days) -------------
    today = date.today()
    for idx, inst in enumerate(institutes):
        expected = random.choice([40, 50, 60, 80])
        for d in range(30):
            day = today - timedelta(days=d)
            if day.weekday() == 6:      # Sunday holiday
                continue
            ratio = random.uniform(0.88, 0.99)   # healthy attendance
            present = int(expected * ratio)

            # Inject anomalies: institutes 2 and 4 have collapsing attendance
            if inst.id in (2, 4) and d < 10:
                present = int(expected * random.uniform(0.25, 0.45))

            db.add(AttendanceLog(
                institute_id=inst.id, log_date=day,
                expected=expected, present=present,
                face_verified=random.random() > 0.15,
            ))

    db.commit()
    print("Seeded successfully!")
    print("  admin / admin123")
    print("  ravi | priya | arjun  -> inspector123")
    print("  ngostaff / institute123")


if __name__ == "__main__":
    main()