import os
import sqlite3

DATABASE = os.environ.get("CLINIC_DATABASE", "/run/lab/clinic.sqlite3")

APPOINTMENTS = [
    ("08:30", "Dr. Meera Sethi", "Family medicine", "Room 04", "Confirmed"),
    ("09:15", "Dr. Arjun Rao", "Cardiology", "Room 12", "Checked in"),
    ("10:00", "Dr. Kavita Nair", "Dermatology", "Room 07", "Confirmed"),
    ("11:30", "Dr. Omar Khan", "Physiotherapy", "Room 16", "In progress"),
]


def seed():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS staff "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, display_name TEXT NOT NULL, "
            "unit TEXT NOT NULL, role TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS sessions "
            "(token_digest TEXT PRIMARY KEY, staff_id INTEGER NOT NULL, "
            "FOREIGN KEY(staff_id) REFERENCES staff(id))"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS appointments "
            "(slot TEXT, clinician TEXT, service TEXT, room TEXT, status TEXT)"
        )
        connection.execute("DELETE FROM appointments")
        connection.executemany(
            "INSERT INTO appointments VALUES (?, ?, ?, ?, ?)", APPOINTMENTS
        )
        connection.commit()


if __name__ == "__main__":
    seed()
