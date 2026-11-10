"""Northgate Care Network patient portal web application."""

from __future__ import annotations

import base64
import hashlib
import html
import sqlite3
import time
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response

import auth
import db
import seed_data

SESSION_COOKIE = "ncn_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
DUMMY_SALT = "00" * 16
DUMMY_HASH = "0" * 64

app = FastAPI(
    title="Northgate Care Network Patient Portal",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


CSS = """
:root {
  color-scheme: light;
  --ink: #173042;
  --muted: #5d7284;
  --teal: #087f8c;
  --teal-dark: #066675;
  --line: #d8e3e8;
  --soft: #eef6f7;
  --paper: #ffffff;
  --page: #f3f7f8;
  --warn: #8a5a00;
  --warn-bg: #fff4d6;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--page);
  color: var(--ink);
}
a { color: var(--teal-dark); }
.topbar {
  background: var(--paper);
  border-bottom: 1px solid var(--line);
}
.topbar-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.mark {
  width: 40px; height: 40px; border-radius: 12px;
  display: grid; place-items: center;
  background: var(--teal); color: white; font-weight: 800; font-size: 20px;
}
.brand strong { display: block; font-size: 18px; letter-spacing: .01em; }
.brand span { display: block; color: var(--muted); font-size: 13px; margin-top: 2px; }
nav { display: flex; align-items: center; gap: 16px; font-size: 14px; }
nav form { margin: 0; }
button, .button {
  border: 0; border-radius: 999px; background: var(--teal); color: white;
  padding: 10px 16px; font: inherit; font-weight: 700; cursor: pointer;
  text-decoration: none; display: inline-block;
}
button:hover, .button:hover { background: var(--teal-dark); }
button.secondary, .button.secondary {
  background: var(--soft); color: var(--teal-dark); border: 1px solid var(--line);
}
main { max-width: 1120px; margin: 0 auto; padding: 32px 24px 48px; }
.hero {
  background: linear-gradient(135deg, #dff2f3, #ffffff 62%);
  border: 1px solid var(--line); border-radius: 24px; padding: 28px;
  display: grid; grid-template-columns: 1.4fr .8fr; gap: 24px; margin-bottom: 24px;
}
.hero h1 { margin: 0 0 10px; font-size: clamp(28px, 4vw, 42px); line-height: 1.05; }
.hero p { color: var(--muted); line-height: 1.6; margin: 0; }
.panel, .card {
  background: var(--paper); border: 1px solid var(--line); border-radius: 20px;
  padding: 22px; box-shadow: 0 10px 28px rgba(23, 48, 66, .05);
}
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.card h2, .panel h2 { margin-top: 0; }
.card p, .panel p { color: var(--muted); line-height: 1.55; }
.meta { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 20px; margin: 18px 0; }
.meta dt { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
.meta dd { margin: 4px 0 0; font-weight: 650; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; }
th, td { text-align: left; padding: 11px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .07em; }
.badge {
  display: inline-flex; border-radius: 999px; padding: 3px 9px; background: var(--soft);
  color: var(--teal-dark); font-size: 12px; font-weight: 700;
}
.notice { background: var(--warn-bg); color: var(--warn); border-radius: 14px; padding: 12px 14px; }
.error { background: #fdecec; color: #7a1f1f; border-radius: 14px; padding: 12px 14px; margin-bottom: 16px; }
.login-wrap { max-width: 460px; margin: 48px auto; }
label { display: block; font-weight: 700; margin: 16px 0 7px; }
input {
  width: 100%; border: 1px solid var(--line); border-radius: 12px; padding: 12px 13px;
  font: inherit; background: white;
}
.stack { display: grid; gap: 14px; }
.muted { color: var(--muted); }
.small { font-size: 13px; }
.section { margin-top: 24px; }
footer { max-width: 1120px; margin: 0 auto; padding: 0 24px 32px; color: var(--muted); font-size: 13px; }
@media (max-width: 820px) {
  .topbar-inner, nav { align-items: flex-start; flex-direction: column; }
  .hero, .grid, .grid.two { grid-template-columns: 1fr; }
  .meta { grid-template-columns: 1fr; }
}
"""


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def format_date(value: Optional[str]) -> str:
    if not value:
        return "Not recorded"
    for pattern in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, pattern).strftime("%B %d, %Y")
        except ValueError:
            continue
    return value


def format_moment(value: Optional[str]) -> str:
    if not value:
        return "Not recorded"
    try:
        return datetime.fromisoformat(value).strftime("%b %d, %Y · %I:%M %p")
    except ValueError:
        return format_date(value)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def record_ref(patient_id: int) -> str:
    raw = f"NC-{int(patient_id)}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def parse_record_ref(ref: str) -> Optional[int]:
    try:
        padded = ref + ("=" * (-len(ref) % 4))
        raw = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        prefix, _, value = raw.partition("-")
        if prefix != "NC":
            return None
        patient_id = int(value)
    except (ValueError, UnicodeDecodeError):
        return None
    return patient_id if patient_id > 0 else None


def current_account(request: Request) -> Optional[sqlite3.Row]:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    return db.query_one(
        """
        SELECT a.*
        FROM sessions AS s
        JOIN accounts AS a ON a.id = s.account_id
        WHERE s.token = ? AND s.expires_at > ?
        """,
        (token_digest(token), int(time.time())),
    )


def start_session(account_id: int, request: Request) -> RedirectResponse:
    old_token = request.cookies.get(SESSION_COOKIE)
    if old_token:
        db.execute("DELETE FROM sessions WHERE token = ?", (token_digest(old_token),))

    token = auth.new_token()
    now = int(time.time())
    db.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
    db.execute(
        "INSERT INTO sessions (token, account_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token_digest(token), account_id, now, now + SESSION_TTL_SECONDS),
    )
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


def layout(title: str, body: str, account: Optional[sqlite3.Row] = None, status_code: int = 200) -> HTMLResponse:
    if account is None:
        nav = '<a href="/login">Sign in</a>'
    else:
        nav = (
            '<a href="/dashboard">Dashboard</a>'
            f'<a href="/records/{record_ref(int(account["patient_id"]))}">My record</a>'
            '<a href="/team">Care team</a>'
            '<a href="/settings/sharing">Sharing</a>'
            '<form method="post" action="/logout">'
            '<button class="secondary" type="submit">Sign out</button></form>'
        )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · Northgate Care Network</title>
  <link rel="stylesheet" href="/assets/site.css">
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <div class="mark" aria-hidden="true">+</div>
        <div><strong>Northgate Care Network</strong><span>Patient portal</span></div>
      </div>
      <nav>{nav}</nav>
    </div>
  </header>
  <main>{body}</main>
  <footer>Northgate Care Network · Northvale and Riverbend campuses · Portal help: (503) 555-0100</footer>
</body>
</html>"""
    return HTMLResponse(document, status_code=status_code)


def message_page(title: str, heading: str, text: str, account: Optional[sqlite3.Row], status_code: int) -> HTMLResponse:
    body = f"""
    <section class="panel">
      <h1>{esc(heading)}</h1>
      <p>{esc(text)}</p>
      <p><a class="button" href="/dashboard">Return to dashboard</a></p>
    </section>"""
    return layout(title, body, account, status_code)


def accessible_patient_ids(account: sqlite3.Row) -> list[int]:
    own_id = int(account["patient_id"])
    rows = db.query_all(
        """
        SELECT other_patient_id
        FROM links
        WHERE patient_id = ? AND shares_records = 1
        ORDER BY other_patient_id
        """,
        (own_id,),
    )
    ids = [own_id]
    for row in rows:
        patient_id = int(row["other_patient_id"])
        if patient_id not in ids:
            ids.append(patient_id)
    return ids


def patient_card(patient: sqlite3.Row, relationship: str) -> str:
    return f"""
    <article class="card">
      <span class="badge">{esc(relationship)}</span>
      <h2>{esc(patient["display_name"])}</h2>
      <p>Date of birth: {esc(format_date(patient["dob"]))}<br>
      Coverage: {esc(patient["coverage_plan"] or "No plan recorded")}</p>
      <p><a class="button" href="/records/{record_ref(int(patient["id"]))}">Open record</a></p>
    </article>"""


@app.middleware("http")
async def response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    db.query_one("SELECT 1 AS ok")
    return {"status": "ok", "service": "patient-portal"}


@app.get("/assets/site.css")
def site_css() -> PlainTextResponse:
    return PlainTextResponse(CSS, media_type="text/css")


@app.get("/")
def index(request: Request) -> Response:
    if current_account(request) is not None:
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login")
def login_page(request: Request) -> Response:
    if current_account(request) is not None:
        return RedirectResponse(url="/dashboard", status_code=303)
    body = """
    <section class="panel login-wrap">
      <h1>Welcome back</h1>
      <p>Sign in to review appointments, prescriptions, coverage details and chart notes for your household.</p>
      <form method="post" action="/login">
        <label for="email">Email address</label>
        <input id="email" name="email" type="email" autocomplete="username" required>
        <label for="credential">Portal credential</label>
        <input id="credential" name="credential" type="password" autocomplete="current-password" required>
        <p><button type="submit">Sign in</button></p>
      </form>
      <hr>
      <p>Visiting the demonstration portal for a training session?</p>
      <form method="post" action="/demo-sign-in">
        <button class="secondary" type="submit">Continue with the demonstration account</button>
      </form>
      <p class="small muted">For your security, sign out when you finish using a shared computer.</p>
    </section>"""
    return layout("Sign in", body)


@app.post("/login")
def login(request: Request, email: str = Form(...), credential: str = Form(...)) -> Response:
    normalized_email = email.strip().lower()
    account = db.query_one("SELECT * FROM accounts WHERE lower(email) = ?", (normalized_email,))
    if account is None:
        auth.matches(credential, DUMMY_SALT, DUMMY_HASH)
        authenticated = False
    else:
        authenticated = auth.matches(credential, account["salt"], account["credential_hash"])

    if not authenticated or account is None:
        body = f"""
        <section class="panel login-wrap">
          <h1>Welcome back</h1>
          <div class="error">The email address or credential did not match our records.</div>
          <form method="post" action="/login">
            <label for="email">Email address</label>
            <input id="email" name="email" type="email" autocomplete="username" value="{esc(normalized_email)}" required>
            <label for="credential">Portal credential</label>
            <input id="credential" name="credential" type="password" autocomplete="current-password" required>
            <p><button type="submit">Try again</button></p>
          </form>
          <p class="small"><a href="/login">Return to sign in</a></p>
        </section>"""
        return layout("Sign in", body, status_code=401)

    return start_session(int(account["id"]), request)


@app.post("/demo-sign-in")
def demo_sign_in(request: Request) -> Response:
    account = db.query_one(
        "SELECT * FROM accounts WHERE lower(email) = ?",
        (seed_data.DEMO_ACCOUNT_EMAIL.lower(),),
    )
    if account is None:
        return message_page("Unavailable", "Demonstration account unavailable", "Please contact the portal help desk.", None, 503)
    return start_session(int(account["id"]), request)


@app.post("/logout")
def logout(request: Request) -> RedirectResponse:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        db.execute("DELETE FROM sessions WHERE token = ?", (token_digest(token),))
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@app.get("/dashboard")
def dashboard(request: Request) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    patient_ids = accessible_patient_ids(account)
    placeholders = ", ".join("?" for _ in patient_ids)
    patients = db.query_all(
        f"SELECT * FROM patients WHERE id IN ({placeholders}) ORDER BY CASE WHEN id = ? THEN 0 ELSE 1 END, display_name",
        (*patient_ids, int(account["patient_id"])),
    )
    relationships = {
        int(row["other_patient_id"]): row["relationship"]
        for row in db.query_all(
            "SELECT other_patient_id, relationship FROM links WHERE patient_id = ? AND shares_records = 1",
            (int(account["patient_id"]),),
        )
    }
    cards = []
    for patient in patients:
        label = "Your record" if int(patient["id"]) == int(account["patient_id"]) else relationships.get(int(patient["id"]), "Household record")
        cards.append(patient_card(patient, label))

    body = f"""
    <section class="hero">
      <div>
        <h1>Good day, {esc(account["display_name"])}</h1>
        <p>Review your care team visits, active prescriptions and coverage information. Household records shared with you appear below.</p>
      </div>
      <div class="panel">
        <h2>Care reminders</h2>
        <p>Annual physicals can be scheduled from the front desk at (503) 555-0100.</p>
        <p class="small muted">Messages sent through the portal are reviewed during clinic hours.</p>
      </div>
    </section>
    <section>
      <h2>Records available to you</h2>
      <div class="grid">{''.join(cards)}</div>
    </section>"""
    return layout("Dashboard", body, account)


def account_for_patient(patient_id: int) -> Optional[sqlite3.Row]:
    return db.query_one("SELECT * FROM accounts WHERE patient_id = ?", (patient_id,))


def sharing_page(
    account: sqlite3.Row,
    error: Optional[str] = None,
    status_code: int = 200,
) -> HTMLResponse:
    rows = db.query_all(
        """
        SELECT p.*, l.relationship, l.shares_records
        FROM links AS l
        JOIN patients AS p ON p.id = l.other_patient_id
        WHERE l.patient_id = ?
        ORDER BY l.shares_records DESC, p.display_name
        """,
        (int(account["patient_id"]),),
    )
    items = "".join(
        f"""
        <article class="card">
          <span class="badge">{'Active share' if int(row['shares_records']) == 1 else 'Pending acceptance'}</span>
          <h3>{esc(row["display_name"])}</h3>
          <p>{esc(row["relationship"])} · Chart {int(row["id"])}</p>
          <form method="post" action="/settings/sharing/remove">
            <input type="hidden" name="chart_no" value="{int(row["id"])}">
            <button class="secondary" type="submit">Remove</button>
          </form>
        </article>"""
        for row in rows
    ) or '<div class="panel"><p>No household charts are shared with you yet.</p></div>'
    error_html = f'<div class="error">{esc(error)}</div>' if error else ""
    body = f"""
    <section class="panel">
      <h1>Household sharing</h1>
      <p>Share your chart with a household member, or accept access to a family member's chart. New portal requests stay pending until the other person accepts from their own account. Requests confirmed by the front desk are marked active right away.</p>
      {error_html}
      <form method="post" action="/settings/sharing">
        <label for="email">Household member email</label>
        <input id="email" name="email" type="email" autocomplete="email" placeholder="name@example.com">
        <input type="hidden" name="verified" value="0">
        <p><button type="submit">Send sharing request</button></p>
      </form>
    </section>
    <section class="section">
      <h2>Charts shared with you</h2>
      <div class="grid">{items}</div>
    </section>"""
    return layout("Household sharing", body, account, status_code)


@app.get("/team")
def care_team(request: Request) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    clinicians = db.query_all(
        """
        SELECT p.*
        FROM patients AS p
        JOIN accounts AS a ON a.patient_id = p.id
        WHERE a.role = 'staff'
        ORDER BY p.display_name
        """
    )
    cards = "".join(
        f"""
        <article class="card">
          <span class="badge">{esc(row["specialty"] or "Clinic team")}</span>
          <h2>{esc(row["display_name"])}</h2>
          <p>{esc(row["title"] or "Care team")} · Northgate Care Network</p>
          <p><a class="button secondary" href="/team/{record_ref(int(row["id"]))}">View profile</a></p>
        </article>"""
        for row in clinicians
    )
    body = f"""
    <section class="panel">
      <h1>Care team</h1>
      <p>Meet the clinicians and coordinators who provide care at our Northvale and Riverbend campuses.</p>
    </section>
    <section class="section"><div class="grid">{cards}</div></section>"""
    return layout("Care team", body, account)


@app.get("/team/{ref}")
def clinician_profile(request: Request, ref: str) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    patient_id = parse_record_ref(ref)
    if patient_id is None:
        return message_page("Profile not found", "Profile not found", "That care team profile is not available.", account, 404)

    patient = db.query_one("SELECT * FROM patients WHERE id = ?", (patient_id,))
    clinician_account = account_for_patient(patient_id) if patient is not None else None
    if patient is None or clinician_account is None or clinician_account["role"] != "staff":
        return message_page("Profile not found", "Profile not found", "That care team profile is not available.", account, 404)

    body = f"""
    <section class="panel">
      <span class="badge">{esc(patient["specialty"] or "Clinic team")}</span>
      <h1>{esc(patient["display_name"])}</h1>
      <p>{esc(patient["title"] or "Care team")} with Northgate Care Network. To book or change an appointment with this clinician, call the front desk at (503) 555-0100.</p>
      <dl class="meta">
        <div><dt>Work email</dt><dd>{esc(patient["email"] or "Not listed")}</dd></div>
        <div><dt>Clinic phone</dt><dd>{esc(patient["phone"])}</dd></div>
        <div><dt>Campus</dt><dd>Northvale Campus</dd></div>
        <div><dt>With Northgate since</dt><dd>{esc(format_date(patient["registered_on"]))}</dd></div>
      </dl>
      <p><a class="button secondary" href="/team">Back to care team</a></p>
    </section>"""
    return layout(patient["display_name"], body, account)


@app.get("/settings/sharing")
def sharing_settings(request: Request) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)
    return sharing_page(account)


@app.post("/settings/sharing")
def create_sharing_request(
    request: Request,
    email: str = Form(""),
    chart_no: str = Form(""),
    verified: str = Form("0"),
) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    own_id = int(account["patient_id"])
    normalized_email = email.strip().lower()
    target: Optional[sqlite3.Row] = None

    if normalized_email:
        target = db.query_one("SELECT * FROM patients WHERE lower(email) = ?", (normalized_email,))
        if target is not None:
            target_account = account_for_patient(int(target["id"]))
            if (
                (target_account is not None and target_account["role"] == "staff")
                or normalized_email.endswith("@northgatecare.example")
            ):
                return sharing_page(account, "Clinic team accounts cannot be added to household sharing.", 400)
    elif chart_no.strip():
        try:
            target_id = int(chart_no.strip())
        except ValueError:
            return sharing_page(account, "That chart reference was not recognized.", 400)
        target = db.query_one("SELECT * FROM patients WHERE id = ?", (target_id,))
    else:
        return sharing_page(account, "Enter a household member email to send a sharing request.", 400)

    if target is None:
        return sharing_page(account, "No portal chart matched that request.", 404)
    if int(target["id"]) == own_id:
        return sharing_page(account, "Your own chart is already on your dashboard.", 400)

    active = 1 if verified == "1" else 0
    db.execute(
        "DELETE FROM links WHERE patient_id = ? AND other_patient_id = ?",
        (own_id, int(target["id"])),
    )
    db.execute(
        """
        INSERT INTO links (patient_id, other_patient_id, kind, relationship, shares_records)
        VALUES (?, ?, 'household', 'Shared chart', ?)
        """,
        (own_id, int(target["id"]), active),
    )
    return RedirectResponse(url="/settings/sharing", status_code=303)


@app.post("/settings/sharing/remove")
def remove_sharing(request: Request, chart_no: str = Form(...)) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        target_id = int(chart_no)
    except ValueError:
        return RedirectResponse(url="/settings/sharing", status_code=303)

    db.execute(
        "DELETE FROM links WHERE patient_id = ? AND other_patient_id = ?",
        (int(account["patient_id"]), target_id),
    )
    return RedirectResponse(url="/settings/sharing", status_code=303)


@app.get("/records/{ref}")
def patient_record(request: Request, ref: str) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    patient_id = parse_record_ref(ref)
    if patient_id is None:
        return message_page("Record not found", "Record not found", "That chart is not available in the portal.", account, 404)

    if patient_id not in accessible_patient_ids(account):
        return message_page("Record unavailable", "Record unavailable", "That chart is not shared with your portal account.", account, 403)

    patient = db.query_one("SELECT * FROM patients WHERE id = ?", (patient_id,))
    if patient is None:
        return message_page("Record not found", "Record not found", "That chart is not available in the portal.", account, 404)

    db.execute(
        "INSERT INTO record_views (viewer_account_id, patient_id, channel, viewed_at) VALUES (?, ?, ?, ?)",
        (int(account["id"]), patient_id, "chart", int(time.time())),
    )

    appointments = db.query_all(
        """
        SELECT a.*, clinician.display_name AS clinician_name
        FROM appointments AS a
        JOIN patients AS clinician ON clinician.id = a.clinician_patient_id
        WHERE a.patient_id = ?
        ORDER BY a.starts_at
        """,
        (patient_id,),
    )
    prescriptions = db.query_all(
        """
        SELECT rx.*, prescriber.display_name AS prescriber_name
        FROM prescriptions AS rx
        JOIN patients AS prescriber ON prescriber.id = rx.prescriber_patient_id
        WHERE rx.patient_id = ?
        ORDER BY rx.started_on DESC
        """,
        (patient_id,),
    )
    notes = db.query_all(
        """
        SELECT n.*, author.display_name AS author_name
        FROM notes AS n
        LEFT JOIN patients AS author ON author.id = n.author_patient_id
        WHERE n.patient_id = ?
        ORDER BY n.created_on DESC
        """,
        (patient_id,),
    )
    household = db.query_all(
        """
        SELECT p.*, l.relationship
        FROM links AS l
        JOIN patients AS p ON p.id = l.other_patient_id
        WHERE l.patient_id = ? AND l.shares_records = 1
        ORDER BY p.display_name
        """,
        (patient_id,),
    )

    appointment_rows = "".join(
        "<tr>"
        f"<td>{esc(format_moment(row['starts_at']))}</td>"
        f"<td>{esc(row['kind'])}</td>"
        f"<td>{esc(row['clinician_name'])}</td>"
        f"<td>{esc(row['location'])}</td>"
        f"<td><span class='badge'>{esc(row['status'])}</span></td>"
        "</tr>"
        for row in appointments
    ) or '<tr><td colspan="5">No appointments are recorded.</td></tr>'

    prescription_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(row['name'])}</strong> {esc(row['strength'])}</td>"
        f"<td>{esc(row['instructions'])}</td>"
        f"<td>{esc(row['prescriber_name'])}</td>"
        f"<td>{esc(format_date(row['started_on']))}</td>"
        f"<td>{int(row['refills_left'])}</td>"
        "</tr>"
        for row in prescriptions
    ) or '<tr><td colspan="5">No prescriptions are recorded.</td></tr>'

    note_cards = "".join(
        f"""
        <article class="card">
          <span class="badge">{esc(row["category"])}</span>
          <h3>{esc(format_date(row["created_on"]))}</h3>
          <p>{esc(row["body"])}</p>
          <p class="small muted">Recorded by {esc(row["author_name"] or "Clinic team")}</p>
        </article>"""
        for row in notes
    ) or '<div class="panel"><p>No chart notes are recorded.</p></div>'

    household_items = "".join(
        f'<li><a href="/records/{record_ref(int(row["id"]))}">{esc(row["display_name"])}</a> · {esc(row["relationship"])}</li>'
        for row in household
    ) or "<li>No household connections are recorded.</li>"

    body = f"""
    <section class="panel">
      <span class="badge">Patient record</span>
      <h1>{esc(patient["display_name"])}</h1>
      <p class="muted">Chart opened by {esc(account["display_name"])} · Registered {esc(format_date(patient["registered_on"]))}</p>
      <p><a class="button secondary" href="/records/{record_ref(patient_id)}/summary">Printable summary</a></p>
      <dl class="meta">
        <div><dt>Date of birth</dt><dd>{esc(format_date(patient["dob"]))}</dd></div>
        <div><dt>Sex</dt><dd>{esc(patient["sex"])}</dd></div>
        <div><dt>Phone</dt><dd>{esc(patient["phone"])}</dd></div>
        <div><dt>Email</dt><dd>{esc(patient["email"] or "Not recorded")}</dd></div>
        <div><dt>Address</dt><dd>{esc(patient["address_line"])}, {esc(patient["city"])}, {esc(patient["region"])} {esc(patient["postal_code"])}</dd></div>
        <div><dt>Coverage</dt><dd>{esc(patient["coverage_plan"] or "Not recorded")}</dd></div>
        <div><dt>Member ID</dt><dd>{esc(patient["coverage_member_id"] or "Not recorded")}</dd></div>
        <div><dt>Group</dt><dd>{esc(patient["coverage_group"] or "Not recorded")}</dd></div>
      </dl>
      <h2>Household connections</h2>
      <ul>{household_items}</ul>
    </section>

    <section class="panel section">
      <h2>Appointments</h2>
      <table><thead><tr><th>When</th><th>Visit</th><th>Clinician</th><th>Location</th><th>Status</th></tr></thead>
      <tbody>{appointment_rows}</tbody></table>
    </section>

    <section class="panel section">
      <h2>Prescriptions</h2>
      <table><thead><tr><th>Medication</th><th>Instructions</th><th>Prescriber</th><th>Started</th><th>Refills</th></tr></thead>
      <tbody>{prescription_rows}</tbody></table>
    </section>

    <section class="section">
      <h2>Chart notes</h2>
      <div class="grid two">{note_cards}</div>
    </section>"""
    return layout(patient["display_name"], body, account)


@app.get("/records/{ref}/summary")
def record_summary(request: Request, ref: str) -> Response:
    account = current_account(request)
    if account is None:
        return RedirectResponse(url="/login", status_code=303)

    patient_id = parse_record_ref(ref)
    if patient_id is None:
        return message_page("Record not found", "Record not found", "That chart is not available in the portal.", account, 404)

    if patient_id not in accessible_patient_ids(account):
        return message_page("Record unavailable", "Record unavailable", "That chart is not shared with your portal account.", account, 403)

    patient = db.query_one("SELECT * FROM patients WHERE id = ?", (patient_id,))
    if patient is None:
        return message_page("Record not found", "Record not found", "That chart is not available in the portal.", account, 404)

    db.execute(
        "INSERT INTO record_views (viewer_account_id, patient_id, channel, viewed_at) VALUES (?, ?, ?, ?)",
        (int(account["id"]), patient_id, "summary", int(time.time())),
    )

    appointments = db.query_all(
        """
        SELECT a.*, clinician.display_name AS clinician_name
        FROM appointments AS a
        JOIN patients AS clinician ON clinician.id = a.clinician_patient_id
        WHERE a.patient_id = ?
        ORDER BY a.starts_at
        """,
        (patient_id,),
    )
    prescriptions = db.query_all(
        """
        SELECT rx.*, prescriber.display_name AS prescriber_name
        FROM prescriptions AS rx
        JOIN patients AS prescriber ON prescriber.id = rx.prescriber_patient_id
        WHERE rx.patient_id = ?
        ORDER BY rx.started_on DESC
        """,
        (patient_id,),
    )
    notes = db.query_all(
        """
        SELECT n.*, author.display_name AS author_name
        FROM notes AS n
        LEFT JOIN patients AS author ON author.id = n.author_patient_id
        WHERE n.patient_id = ?
        ORDER BY n.created_on DESC
        """,
        (patient_id,),
    )

    appointment_items = "".join(
        f"<li>{esc(format_moment(row['starts_at']))} — {esc(row['kind'])} with "
        f"{esc(row['clinician_name'])} · {esc(row['location'])} ({esc(row['status'])})</li>"
        for row in appointments
    ) or "<li>No appointments are recorded.</li>"
    prescription_items = "".join(
        f"<li><strong>{esc(row['name'])}</strong> {esc(row['strength'])} — {esc(row['instructions'])}</li>"
        for row in prescriptions
    ) or "<li>No prescriptions are recorded.</li>"
    note_items = "".join(
        f"""
        <article class="card">
          <span class="badge">{esc(row["category"])}</span>
          <h3>{esc(format_date(row["created_on"]))}</h3>
          <p>{esc(row["body"])}</p>
          <p class="small muted">Recorded by {esc(row["author_name"] or "Clinic team")}</p>
        </article>"""
        for row in notes
    ) or '<div class="panel"><p>No chart notes are recorded.</p></div>'

    body = f"""
    <section class="panel">
      <span class="badge">Printable summary</span>
      <h1>{esc(patient["display_name"])}</h1>
      <p class="muted">Summary prepared for {esc(account["display_name"])} · Registered {esc(format_date(patient["registered_on"]))}</p>
      <dl class="meta">
        <div><dt>Date of birth</dt><dd>{esc(format_date(patient["dob"]))}</dd></div>
        <div><dt>Phone</dt><dd>{esc(patient["phone"])}</dd></div>
        <div><dt>Email</dt><dd>{esc(patient["email"] or "Not recorded")}</dd></div>
        <div><dt>Address</dt><dd>{esc(patient["address_line"])}, {esc(patient["city"])}, {esc(patient["region"])} {esc(patient["postal_code"])}</dd></div>
        <div><dt>Coverage</dt><dd>{esc(patient["coverage_plan"] or "Not recorded")}</dd></div>
        <div><dt>Member ID</dt><dd>{esc(patient["coverage_member_id"] or "Not recorded")}</dd></div>
      </dl>
    </section>

    <section class="panel section">
      <h2>Appointments</h2>
      <ul>{appointment_items}</ul>
    </section>

    <section class="panel section">
      <h2>Prescriptions</h2>
      <ul>{prescription_items}</ul>
    </section>

    <section class="section">
      <h2>Chart notes</h2>
      <div class="grid two">{note_items}</div>
    </section>"""
    return layout(f"Summary · {patient['display_name']}", body, account)
