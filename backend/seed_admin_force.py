from db.database import SessionLocal, engine
from db.models import User
from auth import get_password_hash
from loguru import logger
import sys

def force_seed_admin():
    print(f"Using Database URL: {engine.url}")
    db = SessionLocal()
    try:
        print("Checking for admin user...")
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("Creating admin user...")
            admin_user = User(
                username="admin",
                email="admin@clinic.com",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                otid="00000"
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully.")
        else:
            print(f"Admin user already exists. ID: {user.id}")
    except Exception as e:
        print(f"Error seeding admin: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    force_seed_admin()
