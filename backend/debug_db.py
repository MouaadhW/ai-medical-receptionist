import sqlite3
import os

db_path = "./medicalreceptionist.db"

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
else:
    print(f"Database file found at {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", tables)
        
        # Check users table
        if ('users',) in tables:
            print("Users table exists.")
            cursor.execute("SELECT * FROM users;")
            users = cursor.fetchall()
            print("Users count:", len(users))
            for u in users:
                print(u)
        else:
            print("Users table DOES NOT exist.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
