import os
import sqlite3

import requests
from flask import Flask, render_template_string, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
DATABASE = os.environ.get("CLINIC_DATABASE", "/run/lab/clinic.sqlite3")
HANDBOOK_PREFIX = "http://handbook.cedarridge.test:8082"

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cedar Ridge Clinic | Staff Portal</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; color: #172b3a; background: #f2f6f5; }
    body { max-width: 960px; margin: 36px auto; padding: 0 18px; }
    header, section { background: white; border: 1px solid #dce7e3; border-radius: 12px; padding: 22px; margin-bottom: 18px; }
    header { border-top: 5px solid #16836e; }
    h1 { margin: 0 0 6px; font-size: 1.7rem; }
    h2 { margin-top: 0; font-size: 1.15rem; }
    .muted { color: #536b73; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #e6eeeb; }
    th { color: #536b73; font-size: .88rem; }
    label { display: block; font-weight: 650; margin-bottom: 8px; }
    input { box-sizing: border-box; width: 100%; padding: 11px; border: 1px solid #afc3bc; border-radius: 7px; }
    button { margin-top: 10px; background: #126b5a; color: white; border: 0; border-radius: 7px; padding: 10px 16px; font-weight: 650; cursor: pointer; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f3f7f6; border-radius: 7px; padding: 14px; }
    .notice { padding: 12px; background: #fff6dc; border-radius: 7px; }
    footer { color: #536b73; font-size: .9rem; padding: 4px 2px 18px; }
  </style>
</head>
<body>
  <header>
    <h1>Cedar Ridge Clinic</h1>
    <div class="muted">Staff portal · Jaipur · Tuesday, 17 June</div>
  </header>
  <section>
    <h2>Today's appointments</h2>
    <table>
      <thead><tr><th>Time</th><th>Clinician</th><th>Service</th><th>Room</th><th>Status</th></tr></thead>
      <tbody>
      {% for row in appointments %}
        <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
      {% endfor %}
      </tbody>
    </table>
  </section>
  <section>
    <h2>Document preview</h2>
    <p class="muted">Preview clinic handbook documents before adding them to the workspace. Approved handbook host: <code>http://handbook.cedarridge.test:8082/</code></p>
    <form method="post" action="/preview">
      <label for="url">Document URL</label>
      <input id="url" name="url" type="url" placeholder="http://handbook.cedarridge.test:8082/" required>
      <button type="submit">Preview document</button>
    </form>
    {% if message %}<p class="notice">{{ message }}</p>{% endif %}
    {% if preview %}<h3>Preview response</h3><pre>{{ preview }}</pre>{% endif %}
  </section>
  <footer>Lab by zayn-910</footer>
</body>
</html>"""

ERROR_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Cedar Ridge Clinic</title></head>
<body><h1>{{ title }}</h1><p>{{ detail }}</p><footer>Lab by zayn-910</footer></body></html>"""


@app.after_request
def add_author_header(response):
    response.headers["X-Lab-Author"] = "zayn-910"
    return response


def get_appointments():
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute(
            "SELECT slot, clinician, service, room, status "
            "FROM appointments ORDER BY slot"
        ).fetchall()


def render_portal(message=None, preview=None):
    return render_template_string(
        PAGE,
        appointments=get_appointments(),
        message=message,
        preview=preview,
    )


@app.get("/")
def home():
    return render_portal()


@app.post("/preview")
def preview():
    target = request.form.get("url", "")
    if not target.startswith(HANDBOOK_PREFIX):
        return render_portal(
            message="Only addresses from the Cedar Ridge handbook can be previewed."
        )
    response = None
    try:
        response = requests.get(
            target,
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
        message = f"The document could not be loaded: {error}"
    finally:
        if response is not None:
            response.close()
    return render_portal(message=message, preview=preview_text)


@app.get("/health")
def health():
    return {"status": "ok", "author": "zayn-910"}


@app.errorhandler(HTTPException)
def http_error(error):
    return render_template_string(
        ERROR_PAGE,
        title="Request not available",
        detail="That request could not be completed.",
    ), error.code


@app.errorhandler(500)
def server_error(error):
    return render_template_string(
        ERROR_PAGE, title="Service unavailable", detail="Please try again later."
    ), 500


print("Cedar Ridge portal ready | Lab by zayn-910", flush=True)
