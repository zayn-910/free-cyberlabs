import os
import sqlite3
import urllib.error
import urllib.request

from flask import Flask, render_template_string, request

app = Flask(__name__)
DATABASE = os.environ.get("CLINIC_DATABASE", "/run/lab/clinic.sqlite3")

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
    <p class="muted">Preview an operational document using its web address before adding it to the clinic workspace.</p>
    <form method="post" action="/preview">
      <label for="url">Document URL</label>
      <input id="url" name="url" type="url" placeholder="https://example.org/clinic-handbook" required>
      <button type="submit">Preview document</button>
    </form>
    {% if message %}<p class="notice">{{ message }}</p>{% endif %}
    {% if preview %}<h3>Preview response</h3><pre>{{ preview }}</pre>{% endif %}
  </section>
</body>
</html>"""


def get_appointments():
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute(
            "SELECT slot, clinician, service, room, status "
            "FROM appointments ORDER BY slot"
        ).fetchall()


@app.get("/")
def home():
    return render_template_string(PAGE, appointments=get_appointments(), message=None, preview=None)


@app.post("/preview")
def preview():
    target = request.form.get("url", "")
    try:
        with urllib.request.urlopen(target, timeout=5) as response:
            content = response.read(8192).decode("utf-8", errors="replace")
            message = f"Received HTTP {response.status}."
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        content = ""
        message = f"The document could not be loaded: {error}"
    return render_template_string(
        PAGE,
        appointments=get_appointments(),
        message=message,
        preview=content,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
