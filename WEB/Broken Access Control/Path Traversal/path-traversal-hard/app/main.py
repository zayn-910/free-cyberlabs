import os
import json
import hashlib
import base64
import urllib.parse
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Cobalt Archive")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = str(BASE_DIR / "data")
ARCHIVE_ROOT = os.path.join(DATA_DIR, "archive")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _load_users() -> list[dict]:
    with open(USERS_FILE, "r") as fh:
        return json.load(fh)


def _hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return dk.hex()


def _encode_session(data: dict) -> str:
    raw = json.dumps(data, separators=(',', ':'))
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_session(token: str) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        return json.loads(raw)
    except Exception:
        return None


def _current_user(request: Request) -> dict | None:
    token = request.cookies.get("auth")
    if not token:
        return None
    return _decode_session(token)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = _current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if _current_user(request):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request, "error": None,
    })


@app.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    users = _load_users()
    for user in users:
        if user["username"] == username:
            if _hash_password(password, user["salt"]) == user["password_hash"]:
                session_data = {
                    "u": user["id"],
                    "r": user["role"],
                    "n": user["display_name"],
                }
                token = _encode_session(session_data)
                resp = RedirectResponse("/dashboard", status_code=303)
                resp.set_cookie("auth", token, httponly=False, samesite="lax", max_age=7200)
                return resp
            break

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid credentials.",
    })


@app.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("auth")
    return resp


# ---------------------------------------------------------------------------
# User dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = _current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    user_dir = os.path.join(ARCHIVE_ROOT, user["u"])
    documents = []
    if os.path.isdir(user_dir):
        for name in sorted(os.listdir(user_dir)):
            full = os.path.join(user_dir, name)
            if os.path.isfile(full):
                documents.append({"name": name, "size": os.path.getsize(full)})

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "documents": documents,
    })


@app.get("/documents/view")
def view_document(filename: str, request: Request):
    user = _current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    filepath = os.path.join(ARCHIVE_ROOT, user["u"], filename)
    filepath = os.path.realpath(filepath)
    user_real = os.path.realpath(os.path.join(ARCHIVE_ROOT, user["u"]))

    if not filepath.startswith(user_real + os.sep):
        return HTMLResponse("<h2>Access denied</h2><p><a href='/dashboard'>Back</a></p>", status_code=403)

    if not os.path.isfile(filepath):
        return HTMLResponse("<h2>File not found</h2><p><a href='/dashboard'>Back</a></p>", status_code=404)

    with open(filepath, "r") as fh:
        content = fh.read()

    return templates.TemplateResponse("viewer.html", {
        "request": request, "user": user,
        "filename": filename, "content": content,
    })


# ---------------------------------------------------------------------------
# Admin panel
# ---------------------------------------------------------------------------

@app.get("/admin/", response_class=HTMLResponse)
def admin_home(request: Request):
    user = _current_user(request)
    if not user or user.get("r") != "admin":
        return HTMLResponse(
            "<h2>403 — Admin access required</h2><p><a href='/dashboard'>Back</a></p>",
            status_code=403,
        )

    return templates.TemplateResponse("admin_home.html", {
        "request": request, "user": user,
    })


@app.get("/admin/reader", response_class=HTMLResponse)
def admin_reader_page(request: Request):
    user = _current_user(request)
    if not user or user.get("r") != "admin":
        return HTMLResponse(
            "<h2>403 — Admin access required</h2><p><a href='/dashboard'>Back</a></p>",
            status_code=403,
        )

    return templates.TemplateResponse("admin_reader.html", {
        "request": request, "user": user,
    })


@app.post("/admin/api/read")
async def admin_api_read(request: Request):
    user = _current_user(request)
    if not user or user.get("r") != "admin":
        return JSONResponse({"error": "Admin access required"}, status_code=403)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    path = body.get("path", "")
    if not path:
        return JSONResponse({"error": "Missing 'path' field"}, status_code=400)

    if '..' in path:
        return JSONResponse({"error": "Invalid characters in path"}, status_code=400)

    decoded_path = urllib.parse.unquote(path)
    filepath = os.path.join(ARCHIVE_ROOT, decoded_path)

    try:
        with open(filepath, "r") as fh:
            content = fh.read()
        return JSONResponse({"content": content, "path": filepath})
    except FileNotFoundError:
        return JSONResponse({"error": "File not found", "path": filepath}, status_code=404)
    except IsADirectoryError:
        return JSONResponse({"error": "Path is a directory", "path": filepath}, status_code=400)
    except PermissionError:
        return JSONResponse({"error": "Permission denied", "path": filepath}, status_code=403)
    except Exception as e:
        return JSONResponse({"error": str(e), "path": filepath}, status_code=500)
