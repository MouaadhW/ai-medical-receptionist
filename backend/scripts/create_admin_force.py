from db.database import SessionLocal
from db.models import User, Doctor, Patient, Appointment, Call, MedicalKnowledge
from auth import get_password_hash
import sys

def create_admin():
    db = SessionLocal()
    try:
        # Check existing
        existing = db.query(User).filter(User.username == "admin_test").first()
        if existing:
            print("Admin already exists")
            return

        u = User(
            username='admin_test', 
            email='admintest@med.com', 
            hashed_password=get_password_hash('password123'), 
            role='admin', 
            otid='99999'
        )
        db.add(u)
        db.commit()
        print("Admin Created Successfully")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
