import sqlite3
import os
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "recharge_checker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print(f"Initializing database at: {DB_FILE}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Schema Migration Check: If old table with 'username' exists, drop it to migrate to V3 mobile/pin structure
    try:
        cursor.execute("SELECT username FROM users LIMIT 1")
        print("Migration: Dropping legacy 'users' table to upgrade to V3 mobile/pin layout.")
        cursor.execute("DROP TABLE users")
        conn.commit()
    except sqlite3.OperationalError:
        # Table does not exist or already updated to mobile/pin, ignore
        pass
    
    # Create V3 users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create OTP mock table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            otp TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Database Access Operations
def create_user(mobile, pin_hash, email=None, full_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (mobile, pin_hash, email, full_name) VALUES (?, ?, ?, ?)",
            (mobile, pin_hash, email, full_name)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        raise e
    finally:
        conn.close()

def get_user_by_mobile(mobile):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def store_otp(email, otp, expires_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO otps (email, otp, expires_at) VALUES (?, ?, ?)", (email, otp, expires_at))
    conn.commit()
    conn.close()

def get_otp(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM otps WHERE email = ?", (email,))
    row = json_row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def delete_otp(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
    conn.commit()
    conn.close()
