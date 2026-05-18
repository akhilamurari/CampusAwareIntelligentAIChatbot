"""
create_student.py
-----------------
Admin script to register students in CampusAware AI.

Usage:
    python3 create_student.py

Run this on the server to add students to the database.
Students can also self-register via the app.

Author: Akhila
"""

from auth import init_auth_table, register_student

def main():
    # Initialise the table
    init_auth_table()
    print("CampusAware AI — Student Registration")
    print("=" * 40)

    while True:
        print("\n1. Register a student")
        print("2. Exit")
        choice = input("\nChoice: ").strip()

        if choice == "2":
            break

        if choice == "1":
            student_id = input("Student ID (8 digits starting with 2): ").strip()
            full_name  = input("Full name (optional, press Enter to skip): ").strip()
            password   = input("Password (min 6 chars): ").strip()
            confirm    = input("Confirm password: ").strip()

            if password != confirm:
                print("❌ Passwords do not match.")
                continue

            success, msg = register_student(student_id, password, full_name)
            if success:
                print(f"✅ {msg}")
            else:
                print(f"❌ {msg}")

if __name__ == "__main__":
    main()