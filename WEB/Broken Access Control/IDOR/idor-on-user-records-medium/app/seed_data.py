"""Demonstration data for the Willow Creek Family Clinic patient portal.

The portal is rebuilt from this module each time the service starts, so the
practice always opens with the same people, appointments, prescriptions and
chart notes. Everything here is invented; no real patient data is used.
"""

from __future__ import annotations

import logging
import os
import random
import secrets
import time
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
from typing import Any

import auth
import db

log = logging.getLogger("wcc.seed")

DATA_DIR = Path(os.environ.get("PORTAL_DATA_DIR", "/data"))
RNG_SEED = 20261108
MIGRATION_TICKET = "WCC-2231"

DEMO_ACCOUNT_EMAIL = "maya.ellison@example.com"

STAFF_IDS = (1001, 1002, 1003, 1004)

PEOPLE: list[dict[str, Any]] = [
    {
        "id": 1001, "given": "Alan", "family": "Reyes", "dob": "1975-03-14", "sex": "Male",
        "role": "staff", "title": "MD", "specialty": "Family Medicine",
        "email": "alan.reyes@willowcreekclinic.example", "phone": "(503) 555-0142",
        "street": "18 Northvale Terrace", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Willow Creek Staff Plan", "member": "WCC-ST-000142", "group": "WCC900",
        "registered": "2016-05-02",
    },
    {
        "id": 1002, "given": "Naomi", "family": "Fischer", "dob": "1981-11-03", "sex": "Female",
        "role": "staff", "title": "MD", "specialty": "Internal Medicine",
        "email": "naomi.fischer@willowcreekclinic.example", "phone": "(503) 555-0177",
        "street": "402 Riverbend Way, Apt 3C", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Willow Creek Staff Plan", "member": "WCC-ST-000177", "group": "WCC900",
        "registered": "2016-05-02",
    },
    {
        "id": 1003, "given": "Grace", "family": "Adeyemi", "dob": "1990-06-21", "sex": "Female",
        "role": "staff", "title": "RN", "specialty": "Care Coordination",
        "email": "grace.adeyemi@willowcreekclinic.example", "phone": "(503) 555-0119",
        "street": "77 Larkspur Lane", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Willow Creek Staff Plan", "member": "WCC-ST-000119", "group": "WCC900",
        "registered": "2018-02-12",
    },
    {
        "id": 1004, "given": "Peter", "family": "Lund", "dob": "1968-01-27", "sex": "Male",
        "role": "staff", "title": "Records Office Lead", "specialty": "Health Information",
        "email": "peter.lund@willowcreekclinic.example", "phone": "(503) 555-0103",
        "street": "9 Quarry Hill Road", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Willow Creek Staff Plan", "member": "WCC-ST-000103", "group": "WCC900",
        "registered": "2016-05-02",
    },
    {
        "id": 1012, "given": "Maya", "family": "Ellison", "dob": "1988-06-02", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": DEMO_ACCOUNT_EMAIL, "phone": "(503) 555-0164",
        "street": "231 Alder Court", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Cascade PPO", "member": "CAS-4471902", "group": "CSC220",
        "registered": "2019-04-08",
    },
    {
        "id": 1013, "given": "Owen", "family": "Ellison", "dob": "1986-11-19", "sex": "Male",
        "role": "patient", "title": None, "specialty": None,
        "email": "owen.ellison@example.com", "phone": "(503) 555-0165",
        "street": "231 Alder Court", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Cascade PPO", "member": "CAS-4471903", "group": "CSC220",
        "registered": "2019-04-08",
    },
    {
        "id": 1014, "given": "Juniper", "family": "Ellison", "dob": "2017-04-23", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": None, "phone": "(503) 555-0164",
        "street": "231 Alder Court", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Cascade PPO", "member": "CAS-4471904", "group": "CSC220",
        "registered": "2019-04-08",
    },
    {
        "id": 1015, "given": "Priya", "family": "Raman", "dob": "1979-09-08", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": "priya.raman@example.com", "phone": "(503) 555-0188",
        "street": "1450 Fremont Street, Unit 12", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Willamette HMO", "member": "WIL-8820413", "group": "WLM118",
        "registered": "2017-09-19",
    },
    {
        "id": 1016, "given": "Arun", "family": "Raman", "dob": "1977-01-30", "sex": "Male",
        "role": "patient", "title": None, "specialty": None,
        "email": "arun.raman@example.com", "phone": "(503) 555-0189",
        "street": "1450 Fremont Street, Unit 12", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Willamette HMO", "member": "WIL-8820414", "group": "WLM118",
        "registered": "2017-09-19",
    },
    {
        "id": 1017, "given": "Daniel", "family": "Okafor", "dob": "1992-02-14", "sex": "Male",
        "role": "patient", "title": None, "specialty": None,
        "email": "daniel.okafor@example.com", "phone": "(503) 555-0121",
        "street": "60 Harvest Park Drive", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Bridgeport Family Plan", "member": "BRP-3390117", "group": "BRG410",
        "registered": "2021-01-11",
    },
    {
        "id": 1018, "given": "Rosa", "family": "Delgado", "dob": "1965-07-27", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": "rosa.delgado@example.com", "phone": "(503) 555-0150",
        "street": "8 Cypress Row", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Northvale Community Plan", "member": "NVC-1120984", "group": "NVC050",
        "registered": "2016-11-30",
    },
    {
        "id": 1019, "given": "Camila", "family": "Delgado", "dob": "1996-12-05", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": "camila.delgado@example.com", "phone": "(503) 555-0151",
        "street": "8 Cypress Row", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Northvale Community Plan", "member": "NVC-1120985", "group": "NVC050",
        "registered": "2018-06-14",
    },
    {
        "id": 1020, "given": "Tomas", "family": "Novak", "dob": "1958-03-11", "sex": "Male",
        "role": "patient", "title": None, "specialty": None,
        "email": "tomas.novak@example.com", "phone": "(503) 555-0136",
        "street": "501 Beacon Hill Road", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Cascade PPO", "member": "CAS-2201884", "group": "CSC220",
        "registered": "2016-08-22",
    },
    {
        "id": 1021, "given": "Hannah", "family": "Brooks", "dob": "1999-10-02", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": "hannah.brooks@example.com", "phone": "(503) 555-0198",
        "street": "22 Millrace Avenue, Apt 5", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Bridgeport Family Plan", "member": "BRP-3390502", "group": "BRG410",
        "registered": "2022-03-07",
    },
    {
        "id": 1022, "given": "Samuel", "family": "Okonkwo", "dob": "1984-05-21", "sex": "Male",
        "role": "patient", "title": None, "specialty": None,
        "email": "samuel.okonkwo@example.com", "phone": "(503) 555-0110",
        "street": "310 Sycamore Bottom Road", "city": "Northvale", "region": "OR", "postal": "97214",
        "plan": "Willamette HMO", "member": "WIL-8820777", "group": "WLM118",
        "registered": "2020-10-05",
    },
    {
        "id": 1023, "given": "Elena", "family": "Petrova", "dob": "1971-08-16", "sex": "Female",
        "role": "patient", "title": None, "specialty": None,
        "email": "elena.petrova@example.com", "phone": "(503) 555-0127",
        "street": "4 Windermere Close", "city": "Riverbend", "region": "OR", "postal": "97005",
        "plan": "Self-pay (no coverage on file)", "member": None, "group": None,
        "registered": "2023-01-23",
    },
]

# Portal access has been activated for these accounts. The sign-in secret for
# every account except the demonstration one is generated when the data is
# loaded and is never written down anywhere.
ACTIVATED_PATIENT_IDS = (1012, 1015, 1018, 1021)

LINKS: list[tuple[int, int, str, str]] = [
    (1012, 1013, "household", "Spouse"),
    (1012, 1014, "household", "Child"),
    (1013, 1012, "household", "Spouse"),
    (1013, 1014, "household", "Child"),
    (1014, 1012, "household", "Parent"),
    (1014, 1013, "household", "Parent"),
    (1015, 1016, "household", "Spouse"),
    (1016, 1015, "household", "Spouse"),
    (1018, 1019, "household", "Child"),
    (1019, 1018, "household", "Parent"),
]

APPOINTMENT_KINDS = (
    "Annual physical",
    "Follow-up visit",
    "Lab review",
    "Vaccination",
    "Care plan review",
    "Nurse check-in",
)

APPOINTMENT_SLOTS = ("08:30", "09:00", "09:45", "10:30", "11:15", "13:00", "13:45", "14:30", "15:15", "16:00")

LOCATIONS = (
    "Northvale Campus, Suite 210",
    "Northvale Campus, Suite 118",
    "Riverbend Campus, Room 4",
    "Telehealth (video visit)",
)

MEDICATIONS = (
    ("Lisinopril", "10 mg", "One tablet by mouth each morning", 3),
    ("Metformin", "500 mg", "One tablet twice daily with food", 2),
    ("Sertraline", "50 mg", "One capsule daily", 5),
    ("Albuterol inhaler", "90 mcg", "Two puffs as needed for wheeze", 1),
    ("Atorvastatin", "20 mg", "One tablet each evening", 4),
    ("Levothyroxine", "50 mcg", "One tablet each morning before food", 2),
    ("Cetirizine", "10 mg", "One tablet daily through the spring", 0),
    ("Amoxicillin", "500 mg", "One capsule three times daily for seven days", 0),
    ("Omeprazole", "20 mg", "One capsule daily before breakfast", 3),
    ("Cholecalciferol", "2000 IU", "One capsule daily", 6),
)

NOTE_BODIES = {
    "visit": (
        "Annual physical completed. Vitals stable, blood pressure 118/76. Current plan continues; return in twelve months.",
        "Follow-up for seasonal symptoms. Improvement since starting the nasal spray. No further action unless symptoms return.",
        "Seen for a persistent cough of two weeks. Chest examination clear. Advice given on fluids and rest; review if worse.",
        "Well-child visit. Growth tracking along the expected curve. School sports form signed and returned to the family.",
    ),
    "lab": (
        "Lipid panel reviewed. Total cholesterol 182 mg/dL, LDL 96 mg/dL. Dietary advice given, repeat in one year.",
        "HbA1c 5.6 percent, within range. Fasting glucose 94 mg/dL. Continue current management.",
        "Full blood count normal. Ferritin slightly low; increase iron-rich foods and recheck in three months.",
        "Thyroid function rechecked after the dose change. TSH 2.1 mIU/L, no adjustment required.",
    ),
    "referral": (
        "Referred to physiotherapy for a lower back strain. Six sessions approved; the front desk will confirm the dates.",
        "Referral sent to dermatology for review of a changing mole. Routine priority, appointment expected within six weeks.",
        "Referred to the dietitian for support with meal planning. The family will be contacted directly.",
    ),
    "care-plan": (
        "Care plan updated after the review call. An evening walk was added; next review in three months.",
        "Care coordination call completed. Transport to the Riverbend campus arranged for the next two appointments.",
        "Medication review completed with the patient. One duplicate item stopped and the pharmacy notified.",
    ),
    "administrative": (
        "Coverage details confirmed with the member services line. No change to the plan on file.",
        "Records request from the patient's employer clinic completed and released with written consent.",
        "Interpreter preference recorded; Portuguese required for future visits at the Riverbend campus.",
    ),
}


def runtime_reference() -> str:
    """Return the operations reference issued for this running instance."""
    from_env = os.environ.get("RECORDS_MIGRATION_REF")
    if from_env:
        return from_env.strip()

    stored = DATA_DIR / "runtime" / "flag"
    try:
        value = stored.read_text(encoding="utf-8").strip()
    except OSError:
        value = ""
    if value:
        return value

    log.warning("no operations reference supplied; using a temporary local value")
    return "WCC-LOCAL-" + secrets.token_hex(8)


def migration_note(reference: str) -> str:
    return (
        f"Records migration {MIGRATION_TICKET} has been applied to the clinical staff charts. "
        f"Operations reference {reference} was recorded by the migration team and stays with this "
        "chart until the next audit cycle, when it will be retired."
    )


def _slots(rng: random.Random, day: date) -> tuple[str, str]:
    start_text = rng.choice(APPOINTMENT_SLOTS)
    hour, minute = (int(part) for part in start_text.split(":"))
    starts = datetime.combine(day, dtime(hour, minute))
    ends = starts + timedelta(minutes=rng.choice((20, 30, 45)))
    return starts.isoformat(timespec="minutes") + ":00", ends.isoformat(timespec="minutes") + ":00"


def _appointments(rng: random.Random, person_id: int, today: date) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for _ in range(rng.randint(1, 3)):
        day = today - timedelta(days=rng.randint(9, 170))
        starts, ends = _slots(rng, day)
        rows.append((
            person_id, rng.choice(STAFF_IDS), starts, ends,
            rng.choice(APPOINTMENT_KINDS), rng.choice(LOCATIONS), "completed",
        ))
    for _ in range(rng.choice((0, 1, 1, 2))):
        day = today + timedelta(days=rng.randint(2, 62))
        starts, ends = _slots(rng, day)
        rows.append((
            person_id, rng.choice(STAFF_IDS), starts, ends,
            rng.choice(APPOINTMENT_KINDS), rng.choice(LOCATIONS), "scheduled",
        ))
    return rows


def _prescriptions(rng: random.Random, person_id: int, today: date) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    count = rng.choice((0, 1, 1, 2, 3))
    for name, strength, instructions, refills in rng.sample(MEDICATIONS, count):
        started = today - timedelta(days=rng.randint(20, 700))
        rows.append((
            person_id, rng.choice(STAFF_IDS), name, strength, instructions,
            started.isoformat(), max(0, refills + rng.choice((-1, 0, 0, 1))),
        ))
    return rows


def _notes(rng: random.Random, person_id: int, today: date) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    categories = rng.sample(tuple(NOTE_BODIES), rng.randint(2, 4))
    for index, category in enumerate(categories):
        body = rng.choice(NOTE_BODIES[category])
        created = today - timedelta(days=rng.randint(4 + index * 12, 40 + index * 45))
        rows.append((person_id, rng.choice(STAFF_IDS), category, created.isoformat(), body))
    rows.sort(key=lambda row: row[3])
    return rows


def _display(person: dict[str, Any]) -> str:
    if person.get("title"):
        return f"{person['given']} {person['family']}, {person['title']}"
    return f"{person['given']} {person['family']}"


def load_portal_data() -> dict[str, int]:
    """Rebuild the portal database and return a summary of what was loaded."""
    rng = random.Random(RNG_SEED)
    today = date.today()
    now = int(time.time())
    reference = runtime_reference()

    db.rebuild_schema()

    patients = [
        (
            person["id"], person["given"], person["family"], _display(person), person["dob"],
            person["sex"], person["phone"], person["email"], person["street"], person["city"],
            person["region"], person["postal"], person.get("title"), person.get("specialty"),
            person["plan"], person.get("member"), person.get("group"), person["registered"],
        )
        for person in PEOPLE
    ]
    db.insert_many(
        """
        INSERT INTO patients (
            id, given_name, family_name, display_name, dob, sex, phone, email,
            address_line, city, region, postal_code, title, specialty,
            coverage_plan, coverage_member_id, coverage_group, registered_on
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        patients,
    )

    accounts: list[tuple[Any, ...]] = []
    account_id = 0
    for person in PEOPLE:
        activated = person["role"] == "staff" or person["id"] in ACTIVATED_PATIENT_IDS
        if not activated:
            continue
        account_id += 1
        secret = secrets.token_urlsafe(18)
        salt = auth.new_salt()
        accounts.append((
            account_id, person["email"], _display(person), person["role"], person["id"],
            auth.derive(secret, salt), salt, now,
        ))
    db.insert_many(
        """
        INSERT INTO accounts (id, email, display_name, role, patient_id, credential_hash, salt, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        accounts,
    )

    db.insert_many(
        """
        INSERT INTO links (id, patient_id, other_patient_id, kind, relationship, shares_records)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [(index + 1, patient_id, other_id, kind, relationship, 1)
         for index, (patient_id, other_id, kind, relationship) in enumerate(LINKS)],
    )

    appointments: list[tuple[Any, ...]] = []
    prescriptions: list[tuple[Any, ...]] = []
    notes: list[tuple[Any, ...]] = []
    for person in PEOPLE:
        appointments.extend(_appointments(rng, person["id"], today))
        prescriptions.extend(_prescriptions(rng, person["id"], today))
        notes.extend(_notes(rng, person["id"], today))

    notes.append((
        1001, 1004, "systems", (today - timedelta(days=6)).isoformat(), migration_note(reference),
    ))

    db.insert_many(
        """
        INSERT INTO appointments (
            patient_id, clinician_patient_id, starts_at, ends_at, kind, location, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        appointments,
    )
    db.insert_many(
        """
        INSERT INTO prescriptions (
            patient_id, prescriber_patient_id, name, strength, instructions, started_on, refills_left
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        prescriptions,
    )
    db.insert_many(
        """
        INSERT INTO notes (patient_id, author_patient_id, category, created_on, body)
        VALUES (?, ?, ?, ?, ?)
        """,
        notes,
    )

    recorded = db.query_one(
        """
        SELECT body
        FROM notes
        WHERE patient_id = 1001 AND category = 'systems'
        ORDER BY id DESC
        LIMIT 1
        """
    )
    if recorded is None or reference not in recorded["body"]:
        raise RuntimeError("portal data did not record the current operations reference")

    summary = {
        "patients": len(patients),
        "accounts": len(accounts),
        "links": len(LINKS),
        "appointments": len(appointments),
        "prescriptions": len(prescriptions),
        "notes": len(notes),
    }
    log.info("portal data loaded: %s", summary)
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    counts = load_portal_data()
    print("Portal data loaded into", db.DB_PATH)
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
