"""
auth.py
-------
Authentication module for CampusAware AI.
Handles student registration, login and session management.

Uses SQLite (same campus.db) with bcrypt password hashing.
No cloud dependency — fully on-premises.

Author: Akhila
"""

import sqlite3
import hashlib
import os
import re
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("SQLITE_DB_PATH", "data/campus.db")


def get_conn():
    """Get SQLite connection."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_auth_table():
    """
    Create students table if it doesn't exist.
    Called once at app startup.
    """
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            full_name    TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login   DATETIME
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 with a salt.
    Simple but secure enough for academic use.
    """
    salt = "campusaware_latrobe_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def validate_student_id(student_id: str) -> bool:
    """
    Validate La Trobe student ID format.
    Must be 8 digits starting with 2.
    e.g. 20012345
    """
    return bool(re.match(r'^2\d{7}$', student_id.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength requirements.
    Must be at least 8 characters, with 1 uppercase, 1 lowercase, 1 digit, and 1 special character.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    
    return True, ""


def register_student(student_id: str, password: str, full_name: str = "") -> tuple[bool, str]:
    """
    Register a new student.

    Args:
        student_id: 8-digit La Trobe student ID
        password: Plain text password (will be hashed)
        full_name: Optional full name

    Returns:
        (success, message)
    """
    if not validate_student_id(student_id):
        return False, "Invalid student ID format. Must be 8 digits starting with 2."

    is_valid_pw, pw_msg = validate_password(password)
    if not is_valid_pw:
        return False, pw_msg

    conn = get_conn()
    try:
        # Check if already registered
        existing = conn.execute(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        if existing:
            return False, "Student ID already registered. Please log in."

        # Register new student
        conn.execute(
            "INSERT INTO students (student_id, password_hash, full_name) VALUES (?, ?, ?)",
            (student_id, hash_password(password), full_name)
        )
        conn.commit()
        return True, "Registration successful! You can now log in."

    except Exception as e:
        return False, f"Registration error: {str(e)}"
    finally:
        conn.close()


def login_student(student_id: str, password: str) -> tuple[bool, str]:
    """
    Authenticate a student.

    Args:
        student_id: 8-digit La Trobe student ID
        password: Plain text password

    Returns:
        (success, message or full_name)
    """
    if not validate_student_id(student_id):
        return False, "Invalid student ID format."

    conn = get_conn()
    try:
        student = conn.execute(
            "SELECT student_id, password_hash, full_name FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        if not student:
            return False, "Student ID not found. Please register first."

        if student[1] != hash_password(password):
            return False, "Incorrect password. Please try again."

        # Update last login
        conn.execute(
            "UPDATE students SET last_login = CURRENT_TIMESTAMP WHERE student_id = ?",
            (student_id,)
        )
        conn.commit()

        full_name = student[2] or student_id
        return True, full_name

    except Exception as e:
        return False, f"Login error: {str(e)}"
    finally:
        conn.close()


def create_session_token(student_id: str) -> str:
    """
    Create a session token for a student and store in DB.
    Token expires after 5 minutes.
    """
    import secrets
    import time
    token = secrets.token_urlsafe(32)
    expires_at = time.time() + (5 * 60)  # 5 minutes

    conn = get_conn()
    try:
        # Create sessions table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token       TEXT PRIMARY KEY,
                student_id  TEXT NOT NULL,
                expires_at  REAL NOT NULL,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Clean old expired sessions
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
        # Insert new session
        conn.execute(
            "INSERT INTO sessions (token, student_id, expires_at) VALUES (?, ?, ?)",
            (token, student_id, expires_at)
        )
        conn.commit()
        return token
    finally:
        conn.close()


def validate_session_token(token: str):
    """
    Validate a session token.
    Returns (student_id, full_name) if valid, else (None, None).
    Refreshes expiry by 5 more minutes on each validation.
    """
    import time
    if not token:
        return None, None

    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT s.student_id, st.full_name FROM sessions s JOIN students st ON s.student_id = st.student_id WHERE s.token = ? AND s.expires_at > ?",
            (token, time.time())
        ).fetchone()

        if not row:
            return None, None

        # Refresh expiry — 5 more minutes from now
        new_expiry = time.time() + (5 * 60)
        conn.execute("UPDATE sessions SET expires_at = ? WHERE token = ?", (new_expiry, token))
        conn.commit()
        return row[0], row[1] or row[0]
    finally:
        conn.close()


def delete_session_token(token: str):
    """Delete a session token (logout)."""
    conn = get_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()

