#!/usr/bin/env python3
"""Create demo users and sample documents for the consulting portal."""

import os
import json
import hashlib

DATA_DIR = "/app/data"
DOCS_DIR = os.path.join(DATA_DIR, "documents")


def hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return dk.hex()


# --- Users -------------------------------------------------------------------

_raw_users = [
    {
        "id": "jchen",
        "username": "jchen",
        "display_name": "Jamie Chen",
        "role": "consultant",
        "salt": "mR4kT9wP",
        "plaintext": "bridge42",
    },
    {
        "id": "mkowalski",
        "username": "mkowalski",
        "display_name": "Marta Kowalski",
        "role": "project_manager",
        "salt": "xL7nQ2vJ",
        "plaintext": "harbor88",
    },
    {
        "id": "svc_backup",
        "username": "svc_backup",
        "display_name": "Backup Service",
        "role": "service",
        "salt": "bK3pW8yN",
        "plaintext": "z9Tm4Rq2Xv",
    },
]

users = []
for u in _raw_users:
    users.append({
        "id": u["id"],
        "username": u["username"],
        "display_name": u["display_name"],
        "role": u["role"],
        "salt": u["salt"],
        "password_hash": hash_password(u["plaintext"], u["salt"]),
    })

os.makedirs(DATA_DIR, exist_ok=True)
with open(os.path.join(DATA_DIR, "users.json"), "w") as fh:
    json.dump(users, fh, indent=2)


# --- Documents ---------------------------------------------------------------

_documents = {
    "jchen": [
        (
            "project_charter.txt",
            (
                "MERIDIAN CONSULTING — PROJECT CHARTER\n"
                "\n"
                "Project : Apex Digital Transformation\n"
                "Client  : Apex Retail Group\n"
                "Lead    : Jamie Chen\n"
                "Start   : 1 September 2024\n"
                "End     : 28 February 2025\n"
                "\n"
                "Objectives:\n"
                "  1. Migrate legacy inventory system to cloud platform.\n"
                "  2. Integrate POS data with analytics dashboard.\n"
                "  3. Train 40+ staff on new workflows.\n"
                "\n"
                "Budget  : $420,000\n"
                "Status  : On track (Phase 2 of 4)\n"
            ),
        ),
        (
            "meeting_notes_q3.txt",
            (
                "MEETING NOTES — Q3 Steering Committee\n"
                "Date: 18 October 2024\n"
                "\n"
                "Attendees: J. Chen, M. Kowalski, R. Patel (client), S. Okafor (client)\n"
                "\n"
                "Agenda:\n"
                "  • Phase 1 retrospective — completed on schedule.\n"
                "  • Phase 2 kickoff — data migration begins November 4.\n"
                "  • Risk: client IT team availability in December (holiday freeze).\n"
                "\n"
                "Action items:\n"
                "  1. Jamie to finalize migration runbook by Oct 25.\n"
                "  2. Marta to confirm vendor contracts for cloud hosting.\n"
                "  3. Rajesh to provide test data set by Nov 1.\n"
            ),
        ),
        (
            "template_proposal.txt",
            (
                "MERIDIAN CONSULTING — PROPOSAL TEMPLATE\n"
                "\n"
                "[Client Name]\n"
                "[Project Title]\n"
                "[Date]\n"
                "\n"
                "1. Executive Summary\n"
                "   [Brief description of the engagement and expected outcomes.]\n"
                "\n"
                "2. Scope of Work\n"
                "   [Detailed list of deliverables and milestones.]\n"
                "\n"
                "3. Timeline & Resources\n"
                "   [Team composition, estimated hours, key dates.]\n"
                "\n"
                "4. Investment\n"
                "   [Fee structure, payment schedule.]\n"
                "\n"
                "5. Terms & Conditions\n"
                "   [Standard Meridian engagement terms.]\n"
            ),
        ),
    ],
    "mkowalski": [
        (
            "resource_plan.txt",
            (
                "RESOURCE ALLOCATION — Q4 2024\n"
                "\n"
                "Project            | Consultant    | Allocation\n"
                "-------------------|---------------|-----------\n"
                "Apex Digital       | J. Chen       | 80%\n"
                "Apex Digital       | A. Nguyen     | 60%\n"
                "Harbor Logistics   | M. Kowalski   | 100%\n"
                "Summit Healthcare  | L. Garcia     | 75%\n"
                "Summit Healthcare  | D. Osei       | 50%\n"
            ),
        ),
        (
            "vendor_contacts.txt",
            (
                "PREFERRED VENDOR LIST\n"
                "\n"
                "Cloud hosting  : NimbusScale Inc.  — accounts@nimbusscale.io\n"
                "Data migration : ETL Partners      — projects@etlpartners.com\n"
                "Training       : SkillBridge Corp  — enterprise@skillbridge.co\n"
                "\n"
                "All vendor contracts must be reviewed by legal before signing.\n"
            ),
        ),
    ],
}

for user_id, files in _documents.items():
    user_dir = os.path.join(DOCS_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    for filename, content in files:
        with open(os.path.join(user_dir, filename), "w") as fh:
            fh.write(content)

print("Seed data created successfully.")
