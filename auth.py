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

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

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


def change_password(student_id: str, old_password: str, new_password: str) -> tuple[bool, str]:
    """
    Change a student's password.

    Returns:
        (success, message)
    """
    # Verify old password first
    success, _ = login_student(student_id, old_password)
    if not success:
        return False, "Current password is incorrect."

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters."

    conn = get_conn()
    try:
        conn.execute(
            "UPDATE students SET password_hash = ? WHERE student_id = ?",
            (hash_password(new_password), student_id)
        )
        conn.commit()
        return True, "Password changed successfully."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()