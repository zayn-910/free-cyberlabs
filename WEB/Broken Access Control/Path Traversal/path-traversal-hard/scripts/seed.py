#!/usr/bin/env python3
"""Create users and archive documents for Cobalt Archive."""

import os
import json
import hashlib

DATA_DIR = "/app/data"
ARCHIVE_ROOT = os.path.join(DATA_DIR, "archive")


def hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return dk.hex()


# --- Users -------------------------------------------------------------------

_raw_users = [
    {
        "id": "arivera",
        "username": "arivera",
        "display_name": "Alex Rivera",
        "role": "viewer",
        "salt": "qM7kW3rT",
        "plaintext": "dolphin42",
    },
    {
        "id": "jthornton",
        "username": "jthornton",
        "display_name": "Jordan Thornton",
        "role": "admin",
        "salt": "pN4xY8vK",
        "plaintext": "cascade99",
    },
    {
        "id": "svc_sync",
        "username": "svc_sync",
        "display_name": "Sync Service",
        "role": "service",
        "salt": "bR6zL2mQ",
        "plaintext": "tP9wK4nX7yJ3",
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


# --- Archive documents -------------------------------------------------------

_documents = {
    "arivera": [
        (
            "q3_sales_report.txt",
            (
                "COBALT SYSTEMS — Q3 2024 Sales Summary\n"
                "\n"
                "Prepared by: Sales Analytics Team\n"
                "Date: 15 October 2024\n"
                "\n"
                "Revenue: $2.4M (up 12% from Q2)\n"
                "New clients: 14\n"
                "Renewals: 31 of 34 (91%)\n"
                "Pipeline value: $1.8M\n"
                "\n"
                "Top-performing segments:\n"
                "  1. Mid-market SaaS — $980K\n"
                "  2. Enterprise consulting — $720K\n"
                "  3. SMB support contracts — $410K\n"
                "\n"
                "Notes: Q4 target is $2.6M. Focus on renewing three at-risk accounts.\n"
            ),
        ),
        (
            "client_onboarding_checklist.txt",
            (
                "CLIENT ONBOARDING CHECKLIST\n"
                "\n"
                "Phase 1 — Pre-kickoff\n"
                "  [ ] Signed contract received\n"
                "  [ ] Kickoff meeting scheduled\n"
                "  [ ] Access credentials provisioned\n"
                "  [ ] Welcome email sent\n"
                "\n"
                "Phase 2 — Kickoff week\n"
                "  [ ] Requirements workshop completed\n"
                "  [ ] Technical environment assessed\n"
                "  [ ] Project plan shared with client\n"
                "  [ ] Slack channel created\n"
                "\n"
                "Phase 3 — First deliverable\n"
                "  [ ] Initial configuration deployed\n"
                "  [ ] Client training session 1 delivered\n"
                "  [ ] Feedback collected and reviewed\n"
            ),
        ),
        (
            "team_calendar_november.txt",
            (
                "TEAM CALENDAR — NOVEMBER 2024\n"
                "\n"
                "Nov 4  : Sprint 14 begins\n"
                "Nov 8  : Client demo — Apex Retail (2pm)\n"
                "Nov 11 : Veterans Day (office closed)\n"
                "Nov 15 : Sprint 14 review + retro\n"
                "Nov 18 : Sprint 15 begins\n"
                "Nov 22 : Q4 planning session (all hands)\n"
                "Nov 28 : Thanksgiving (office closed)\n"
                "Nov 29 : Flex day\n"
            ),
        ),
    ],
    "jthornton": [
        (
            "board_deck_draft.txt",
            (
                "BOARD PRESENTATION — Q3 2024\n"
                "DRAFT — DO NOT DISTRIBUTE\n"
                "\n"
                "Slide 1: Title — Cobalt Systems Q3 Board Update\n"
                "Slide 2: Executive summary\n"
                "Slide 3: Financial highlights\n"
                "Slide 4: Client acquisition & retention\n"
                "Slide 5: Product roadmap update\n"
                "Slide 6: Hiring plan — Q4\n"
                "Slide 7: Risks and mitigations\n"
                "Slide 8: Q4 outlook and targets\n"
                "\n"
                "Notes: Need updated revenue numbers from finance before Friday.\n"
            ),
        ),
    ],
}

# Also create some shared archive directories
_shared = {
    "shared/company_policies/remote_work_policy.txt": (
        "REMOTE WORK POLICY — COBALT SYSTEMS\n"
        "\n"
        "Effective: 1 January 2024\n"
        "\n"
        "All full-time employees may work remotely up to 3 days per week.\n"
        "Team leads may approve fully remote arrangements on a case-by-case basis.\n"
        "\n"
        "Requirements:\n"
        "  - Stable internet connection (minimum 25 Mbps)\n"
        "  - Availability during core hours (10am–3pm local time)\n"
        "  - Attendance at mandatory in-person meetings\n"
    ),
    "shared/templates/invoice_template.txt": (
        "COBALT SYSTEMS — INVOICE\n"
        "\n"
        "Invoice #: [INV-YYYY-NNN]\n"
        "Date: [DATE]\n"
        "Due: [DATE + 30 days]\n"
        "\n"
        "Bill to:\n"
        "  [Client Name]\n"
        "  [Address]\n"
        "\n"
        "Description                  Qty    Rate      Amount\n"
        "---------------------------------------------------\n"
        "[Service description]        [n]    [$r]      [$total]\n"
        "\n"
        "Subtotal:                              [$subtotal]\n"
        "Tax (0%):                                [$tax]\n"
        "Total:                                 [$total]\n"
    ),
}

# Write user archives
for user_id, files in _documents.items():
    user_dir = os.path.join(ARCHIVE_ROOT, user_id)
    os.makedirs(user_dir, exist_ok=True)
    for filename, content in files:
        with open(os.path.join(user_dir, filename), "w") as fh:
            fh.write(content)

# Write shared archives
for relpath, content in _shared.items():
    full = os.path.join(ARCHIVE_ROOT, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(content)

# Create config directory with a non-sensitive file (for realism)
config_dir = "/app/config"
os.makedirs(config_dir, exist_ok=True)
with open(os.path.join(config_dir, "app_settings.json"), "w") as fh:
    json.dump({
        "app_name": "Cobalt Archive",
        "version": "2.4.1",
        "archive_root": "/app/data/archive",
        "max_upload_size_mb": 50,
        "session_duration_hours": 2,
    }, fh, indent=2)

print("Seed data created successfully.")
