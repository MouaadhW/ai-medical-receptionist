
import sqlite3
import os

db_path = "backend/medicalreceptionist.db"

if not os.path.exists(db_path):
    print("❌ DB file not found!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {tables}")
        
        # Check call columns if table exists
        if ('calls',) in tables:
             cursor.execute("PRAGMA table_info(calls)")
             cols = cursor.fetchall()
             print("Calls columns:", [c[1] for c in cols])
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
