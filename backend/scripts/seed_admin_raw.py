import sqlite3
import datetime
import os
import sys
# We need passlib for hashing, reusing the one installed
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

def seed():
    log_file = "/app/seed_raw_debug.log"
    with open(log_file, "w") as f:
        try:
            db_path = "./medicalreceptionist.db"
            abs_path = os.path.abspath(db_path)
            f.write(f"Absolute DB Path: {abs_path}\n")
            
            if os.path.exists(abs_path):
                f.write(f"File exists. Size: {os.path.getsize(abs_path)} bytes\n")
                if os.access(abs_path, os.W_OK):
                     f.write("File is writable.\n")
                else:
                     f.write("File is NOT writable.\n")
            else:
                f.write("File does not exist.\n")

            f.write("Connecting to database...\n")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            existing = cursor.fetchone()
            
            if existing:
                f.write("Admin user already exists (raw check).\n")
            else:
                f.write("Creating admin user (raw insert)...\n")
                hashed = get_password_hash("admin123")
                now = datetime.datetime.utcnow()
                cursor.execute(
                    "INSERT INTO users (username, email, hashed_password, role, otid, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("admin", "admin@clinic.com", hashed, "admin", "00000", now, now)
                )
                f.write(f"Inserted {cursor.rowcount} rows.\n")
                conn.commit()
                f.write("Committed changes.\n")
                
            conn.close()
        except Exception as e:
            f.write(f"Error: {e}\n")
            import traceback
            traceback.print_exc(file=f)

if __name__ == "__main__":
    seed()
