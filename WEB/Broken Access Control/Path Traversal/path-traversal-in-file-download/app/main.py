import os
import json
import hashlib
import secrets
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Greenfield Medical Clinic - Patient Portal")

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = str(BASE_DIR / "data" / "documents")
USERS_FILE = str(BASE_DIR / "data" / "users.json")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# In-memory session store (single-process app)
_sessions: dict[str, dict] = {}


def _load_users() -> list[dict]:
    with open(USERS_FILE, "r") as fh:
        return json.load(fh)


def _hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return dk.hex()


def _current_user(request: Request) -> dict | None:
    token = request.cookies.get("session_token")
    if token and token in _sessions:
        return _sessions[token]
    return None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if _current_user(request):
        return RedirectResponse("/dashboard", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if _current_user(request):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None,
    })


@app.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    users = _load_users()
    for user in users:
        if user["username"] == username:
            if _hash_password(password, user["salt"]) == user["password_hash"]:
                token = secrets.token_hex(32)
                _sessions[token] = user
                resp = RedirectResponse("/dashboard", status_code=303)
                resp.set_cookie(
                    "session_token",
                    token,
                    httponly=True,
                    samesite="lax",
                    max_age=3600,
                )
                return resp
            break

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid username or password. Please try again.",
    })


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = _current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    user_dir = os.path.join(DOCS_DIR, user["id"])
    documents = []
    if os.path.isdir(user_dir):
        for name in sorted(os.listdir(user_dir)):
            full = os.path.join(user_dir, name)
            if os.path.isfile(full):
                documents.append({
                    "name": name,
                    "size": os.path.getsize(full),
                })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "documents": documents,
    })


@app.get("/documents/download")
def download_document(filename: str, request: Request):
    user = _current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    filepath = os.path.join(DOCS_DIR, user["id"], filename)

    if not os.path.isfile(filepath):
        return HTMLResponse(
            "<h2>Document not found</h2><p><a href='/dashboard'>Back to dashboard</a></p>",
            status_code=404,
        )

    return FileResponse(
        path=filepath,
        media_type="text/plain",
    )


@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session_token")
    if token and token in _sessions:
        del _sessions[token]
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp
