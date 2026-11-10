"""SQLite storage helpers for the Meridian Family Health patient portal."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Optional, Sequence

DATA_DIR = Path(os.environ.get("PORTAL_DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "portal.db"

DROP_STATEMENTS = """
DROP TABLE IF EXISTS record_views;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS links;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS patients;
"""

CREATE_STATEMENTS = """
CREATE TABLE IF NOT EXISTS patients (
    id                   INTEGER PRIMARY KEY,
    given_name           TEXT    NOT NULL,
    family_name          TEXT    NOT NULL,
    display_name         TEXT    NOT NULL,
    dob                  TEXT    NOT NULL,
    sex                  TEXT    NOT NULL,
    phone                TEXT    NOT NULL,
    email                TEXT,
    address_line         TEXT    NOT NULL,
    city                 TEXT    NOT NULL,
    region               TEXT    NOT NULL,
    postal_code          TEXT    NOT NULL,
    title                TEXT,
    specialty            TEXT,
    coverage_plan        TEXT,
    coverage_member_id   TEXT,
    coverage_group       TEXT,
    registered_on        TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id            INTEGER PRIMARY KEY,
    email         TEXT    NOT NULL UNIQUE,
    display_name  TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('patient', 'staff')),
    patient_id    INTEGER REFERENCES patients (id) ON DELETE CASCADE,
    credential_hash TEXT  NOT NULL,
    salt          TEXT    NOT NULL,
    created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT    PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts (id) ON DELETE CASCADE,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS links (
    id               INTEGER PRIMARY KEY,
    patient_id       INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    other_patient_id INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    kind             TEXT    NOT NULL,
    relationship     TEXT    NOT NULL,
    shares_records   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS appointments (
    id                     INTEGER PRIMARY KEY,
    patient_id             INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    clinician_patient_id   INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    starts_at              TEXT    NOT NULL,
    ends_at                TEXT    NOT NULL,
    kind                   TEXT    NOT NULL,
    location               TEXT    NOT NULL,
    status                 TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id                      INTEGER PRIMARY KEY,
    patient_id              INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    prescriber_patient_id   INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    name                    TEXT    NOT NULL,
    strength                TEXT    NOT NULL,
    instructions            TEXT    NOT NULL,
    started_on              TEXT    NOT NULL,
    refills_left            INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id                INTEGER PRIMARY KEY,
    patient_id        INTEGER NOT NULL REFERENCES patients (id) ON DELETE CASCADE,
    author_patient_id INTEGER REFERENCES patients (id) ON DELETE SET NULL,
    category          TEXT    NOT NULL,
    created_on        TEXT    NOT NULL,
    body              TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS record_views (
    id                INTEGER PRIMARY KEY,
    viewer_account_id INTEGER NOT NULL REFERENCES accounts (id) ON DELETE CASCADE,
    patient_id        INTEGER NOT NULL,
    viewed_at         INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_accounts_patient    ON accounts (patient_id);
CREATE INDEX IF NOT EXISTS ix_appointments_start  ON appointments (patient_id, starts_at);
CREATE INDEX IF NOT EXISTS ix_links_patient       ON links (patient_id);
CREATE INDEX IF NOT EXISTS ix_notes_patient       ON notes (patient_id);
CREATE INDEX IF NOT EXISTS ix_views_viewer        ON record_views (viewer_account_id, viewed_at);
"""


def connect() -> sqlite3.Connection:
    """Open a connection to the portal database, creating the data directory first."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema() -> None:
    """Create any tables that are not present yet."""
    conn = connect()
    try:
        with conn:
            conn.executescript(CREATE_STATEMENTS)
    finally:
        conn.close()


def rebuild_schema() -> None:
    """Drop every table and recreate it, ready for a fresh set of portal data."""
    conn = connect()
    try:
        with conn:
            conn.executescript(DROP_STATEMENTS + CREATE_STATEMENTS)
    finally:
        conn.close()


def query_all(sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    conn = connect()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def query_one(sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
    conn = connect()
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()


def execute(sql: str, params: Sequence[Any] = ()) -> None:
    conn = connect()
    try:
        with conn:
            conn.execute(sql, params)
    finally:
        conn.close()


def insert_many(sql: str, rows: Sequence[Sequence[Any]]) -> None:
    conn = connect()
    try:
        with conn:
            conn.executemany(sql, rows)
    finally:
        conn.close()
