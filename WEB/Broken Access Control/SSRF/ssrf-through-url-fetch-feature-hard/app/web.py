import hashlib
import os
import secrets
import sqlite3

import requests
from flask import Flask, make_response, redirect, render_template_string, request, url_for
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
DATABASE = os.environ.get("CLINIC_DATABASE", "/run/lab/clinic.sqlite3")
HANDBOOK_PREFIX = "http://handbook.cedarridge.test:8082"

SIGN_IN_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cedar Ridge Clinic | Staff Portal</title>
<style>
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #172b3a; background: #f2f6f5; }
body { max-width: 880px; margin: 38px auto; padding: 0 18px; }
header, main { background: white; border: 1px solid #dce7e3; border-radius: 12px; padding: 22px; margin-bottom: 18px; }
header { border-top: 5px solid #16836e; } h1 { margin: 0 0 6px; } .muted { color: #536b73; }
label { display: block; font-weight: 650; margin: 14px 0 6px; }
input, select { box-sizing: border-box; width: 100%; padding: 11px; border: 1px solid #afc3bc; border-radius: 7px; }
button { margin-top: 14px; background: #126b5a; color: white; border: 0; border-radius: 7px; padding: 10px 16px; font-weight: 650; cursor: pointer; }
footer { color: #536b73; font-size: .9rem; padding: 4px 2px 18px; }
.notice { padding: 12px; background: #fff6dc; border-radius: 7px; }
</style></head><body>
<header><h1>Cedar Ridge Clinic</h1><div class="muted">Staff portal · Jaipur</div></header>
<main><h2>Begin a front-desk shift</h2><p class="muted">Use this shared workstation to check the day's schedule and clinic resources.</p>
{% if message %}<p class="notice">{{ message }}</p>{% endif %}
<form method="post" action="/start">
<label for="display_name">Staff display name</label><input id="display_name" name="display_name" maxlength="80" required>
<label for="unit">Clinic unit</label><select id="unit" name="unit"><option>Front desk</option><option>Cardiology</option><option>Family medicine</option><option>Pharmacy</option></select>
<button type="submit">Begin shift</button></form></main>
<footer>Lab by zayn-910</footer></body></html>"""

STAFF_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cedar Ridge Clinic | Staff Portal</title>
<style>
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #172b3a; background: #f2f6f5; }
body { max-width: 960px; margin: 36px auto; padding: 0 18px; }
header, section { background: white; border: 1px solid #dce7e3; border-radius: 12px; padding: 22px; margin-bottom: 18px; }
header { border-top: 5px solid #16836e; } h1 { margin: 0 0 6px; font-size: 1.7rem; }
h2 { margin-top: 0; font-size: 1.15rem; } .muted { color: #536b73; }
table { width: 100%; border-collapse: collapse; } th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #e6eeeb; }
th { color: #536b73; font-size: .88rem; } label { display: block; font-weight: 650; margin: 12px 0 6px; }
input, select { box-sizing: border-box; width: 100%; padding: 10px; border: 1px solid #afc3bc; border-radius: 7px; }
button, .button { display: inline-block; margin-top: 10px; background: #126b5a; color: white; border: 0; border-radius: 7px; padding: 10px 16px; font-weight: 650; cursor: pointer; text-decoration: none; }
footer { color: #536b73; font-size: .9rem; padding: 4px 2px 18px; } .notice { padding: 12px; background: #fff6dc; border-radius: 7px; }
</style></head><body>
<header><h1>Cedar Ridge Clinic</h1><div class="muted">Staff portal · Jaipur · Tuesday, 17 June</div></header>
<section><h2>Today's appointments</h2>
<table><thead><tr><th>Time</th><th>Clinician</th><th>Service</th><th>Room</th><th>Status</th></tr></thead><tbody>
{% for row in appointments %}<tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>{% endfor %}
</tbody></table></section>
<section><h2>Staff profile</h2><p class="muted">Signed in as {{ staff.display_name }} · {{ staff.unit }} · {{ staff.role }}</p>
{% if message %}<p class="notice">{{ message }}</p>{% endif %}
<form method="post" action="/profile"><label for="display_name">Display name</label><input id="display_name" name="display_name" value="{{ staff.display_name }}" maxlength="80" required>
<label for="unit">Clinic unit</label><select id="unit" name="unit">
<option{% if staff.unit == 'Front desk' %} selected{% endif %}>Front desk</option><option{% if staff.unit == 'Cardiology' %} selected{% endif %}>Cardiology</option><option{% if staff.unit == 'Family medicine' %} selected{% endif %}>Family medicine</option><option{% if staff.unit == 'Pharmacy' %} selected{% endif %}>Pharmacy</option>
</select><button type="submit">Save profile</button></form>
<p><a class="button" href="/control">Operations console</a></p></section>
<footer>Lab by zayn-910</footer></body></html>"""

CONTROL_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cedar Ridge Clinic | Operations</title>
<style>
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #172b3a; background: #f2f6f5; }
body { max-width: 880px; margin: 38px auto; padding: 0 18px; }
header, main { background: white; border: 1px solid #dce7e3; border-radius: 12px; padding: 22px; margin-bottom: 18px; }
header { border-top: 5px solid #16836e; } h1 { margin: 0 0 6px; } .muted { color: #536b73; }
label { display: block; font-weight: 650; margin: 14px 0 6px; }
input { box-sizing: border-box; width: 100%; padding: 11px; border: 1px solid #afc3bc; border-radius: 7px; }
button, a { display: inline-block; margin-top: 12px; background: #126b5a; color: white; border: 0; border-radius: 7px; padding: 10px 16px; font-weight: 650; cursor: pointer; text-decoration: none; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f3f7f6; border-radius: 7px; padding: 14px; }
.notice { padding: 12px; background: #fff6dc; border-radius: 7px; } footer { color: #536b73; font-size: .9rem; padding: 4px 2px 18px; }
</style></head><body>
<header><h1>Cedar Ridge Clinic</h1><div class="muted">Operations console · Internal resources</div></header>
<main><h2>Document retrieval</h2><p class="muted">Preview approved handbook resources for operational review. Handbook service: <code>http://handbook.cedarridge.test:8082/</code></p>
{% if message %}<p class="notice">{{ message }}</p>{% endif %}
<form method="post" action="/preview"><label for="url">Resource address</label><input id="url" name="url" type="url" placeholder="http://handbook.cedarridge.test:8082/" required><button type="submit">Retrieve resource</button></form>
{% if preview %}<h3>Retrieved response</h3><pre>{{ preview }}</pre>{% endif %}<p><a href="/">Return to staff portal</a></p></main>
<footer>Lab by zayn-910</footer></body></html>"""

ERROR_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Cedar Ridge Clinic</title></head>
<body><h1>{{ title }}</h1><p>{{ detail }}</p><footer>Lab by zayn-910</footer></body></html>"""


def connect():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def current_staff():
    token = request.cookies.get("cr_session")
    if not token:
        return None
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect() as connection:
        row = connection.execute(
            "SELECT staff.id, staff.display_name, staff.unit, staff.role "
            "FROM staff JOIN sessions ON sessions.staff_id = staff.id "
            "WHERE sessions.token_digest = ?",
            (digest,),
        ).fetchone()
    return dict(row) if row else None


def get_appointments():
    with connect() as connection:
        return connection.execute(
            "SELECT slot, clinician, service, room, status "
            "FROM appointments ORDER BY slot"
        ).fetchall()


def render_staff(staff, message=None):
    return render_template_string(
        STAFF_PAGE,
        appointments=get_appointments(),
        staff=staff,
        message=message,
    )


def error_page(title, detail, status):
    return render_template_string(ERROR_PAGE, title=title, detail=detail), status


@app.after_request
def add_author_header(response):
    response.headers["X-Lab-Author"] = "zayn-910"
    return response


@app.get("/")
def home():
    staff = current_staff()
    if staff is None:
        return render_template_string(SIGN_IN_PAGE, message=None)
    return render_staff(staff)


@app.post("/start")
def start_shift():
    display_name = request.form.get("display_name", "").strip()
    unit = request.form.get("unit", "Front desk")
    if not display_name or len(display_name) > 80:
        return render_template_string(
            SIGN_IN_PAGE, message="Enter a display name of 1 to 80 characters."
        ), 400
    if unit not in {"Front desk", "Cardiology", "Family medicine", "Pharmacy"}:
        unit = "Front desk"
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO staff (display_name, unit, role) VALUES (?, ?, ?)",
            (display_name, unit, "frontdesk"),
        )
        connection.execute(
            "INSERT INTO sessions (token_digest, staff_id) VALUES (?, ?)",
            (digest, cursor.lastrowid),
        )
        connection.commit()
    response = make_response(redirect(url_for("home")))
    response.set_cookie(
        "cr_session", token, httponly=True, samesite="Lax", max_age=28800
    )
    return response


@app.post("/profile")
def update_profile():
    staff = current_staff()
    if staff is None:
        return redirect(url_for("home"))
    display_name = request.form.get("display_name", "").strip()
    unit = request.form.get("unit", staff["unit"])
    role = request.form.get("role", staff["role"])
    if not display_name or len(display_name) > 80:
        return render_staff(staff, "Enter a display name of 1 to 80 characters."), 400
    if unit not in {"Front desk", "Cardiology", "Family medicine", "Pharmacy"}:
        return render_staff(staff, "Choose a listed clinic unit."), 400
    if role not in {"frontdesk", "operations"}:
        return render_staff(staff, "Choose a valid staff role."), 400
    with connect() as connection:
        connection.execute(
            "UPDATE staff SET display_name = ?, unit = ?, role = ? WHERE id = ?",
            (display_name, unit, role, staff["id"]),
        )
        connection.commit()
    updated = current_staff()
    return render_staff(updated, "Profile saved.")


@app.get("/control")
def control():
    staff = current_staff()
    if staff is None:
        return redirect(url_for("home"))
    if staff["role"] != "operations":
        return error_page(
            "Operations role required",
            "Your current staff role cannot open this console.",
            403,
        )
    return render_template_string(CONTROL_PAGE, message=None, preview=None)


@app.post("/preview")
def preview():
    staff = current_staff()
    if staff is None:
        return redirect(url_for("home"))
    if staff["role"] != "operations":
        return error_page(
            "Operations role required",
            "Your current staff role cannot retrieve these resources.",
            403,
        )
    target = request.form.get("url", "")
    if not target.startswith(HANDBOOK_PREFIX):
        return render_template_string(
            CONTROL_PAGE,
            message="Only Cedar Ridge handbook addresses are approved.",
            preview=None,
        ), 400
    response = None
    try:
        response = requests.get(
            target,
            headers={"X-Clinic-Role": staff["role"]},
            timeout=(2, 5),
            allow_redirects=False,
            stream=True,
        )
        content = bytearray()
        for chunk in response.iter_content(chunk_size=1024):
            if not chunk:
                continue
            remaining = 8192 - len(content)
            content.extend(chunk[:remaining])
            if len(content) >= 8192:
                break
        preview_text = content.decode("utf-8", errors="replace")
        message = f"Received HTTP {response.status_code}."
    except (requests.RequestException, ValueError) as error:
        preview_text = ""
        message = f"The resource could not be loaded: {error}"
    finally:
        if response is not None:
            response.close()
    return render_template_string(
        CONTROL_PAGE, message=message, preview=preview_text
    )


@app.get("/health")
def health():
    return {"status": "ok", "author": "zayn-910"}


@app.errorhandler(HTTPException)
def http_error(error):
    return error_page("Request not available", "That request could not be completed.", error.code)


@app.errorhandler(500)
def server_error(error):
    return error_page("Service unavailable", "Please try again later.", 500)


print("Cedar Ridge portal ready | Lab by zayn-910", flush=True)
