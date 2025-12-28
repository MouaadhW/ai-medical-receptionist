from db.database import SessionLocal
from db.models import User
from auth import verify_password

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()

if user:
    print(f"User found: {user.username}")
    print(f"Role: {user.role}")
    print(f"OTID: {user.otid}")
    is_valid = verify_password("admin123", user.hashed_password)
    print(f"Password 'admin123' valid: {is_valid}")
else:
    print("User 'admin' not found")

db.close()
