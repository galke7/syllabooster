# -*- coding: utf-8 -*-
import os
import json
import sqlite3
import time
from typing import Dict, Any, List
from flask import Flask, render_template, request, Response, abort

# Use the DB path baked into the container image (overrideable via env)
DB_PATH = os.getenv("DB_PATH", "/app/app.db")
# Open read-only & immutable so SQLite never tries to write WAL/journal files
CONNECT_URI = f"file:{DB_PATH}?mode=ro&immutable=1"

CACHE_TTL_SECONDS = 60

app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")
app.config["JSON_AS_ASCII"] = False  # Keep Hebrew UTF-8 in JSON

# Very small in-memory cache: { key: (timestamp, data) }
_cache: Dict[str, Any] = {}

TABLE_MAP = {
    "home": "home_items",
    "docs": "docs",
    "tasks": "tasks",
    "notes": "notes",
    "alerts": "alerts",
    "links": "links",
    "hs": "highschool",  # NEW: תיכון
}
ALLOWED_TABS = set(TABLE_MAP.keys())


def _connect():
    # Read-only, immutable connection; safe on Cloud Run's read-only image FS
    conn = sqlite3.connect(CONNECT_URI, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _cache_get(key: str):
    now = time.time()
    entry = _cache.get(key)
    if not entry:
        return None
    ts, data = entry
    if (now - ts) > CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return data


def _cache_set(key: str, data):
    _cache[key] = (time.time(), data)


def fetch_settings() -> Dict[str, Any]:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, tab_home, tab_docs, tab_tasks, tab_notes, tab_alerts, tab_links, tab_highschool,
                   home_title, home_description
            FROM main_settings
            ORDER BY id LIMIT 1
            """
        ).fetchone()
    if not row:
        # Provide sane fallback if DB hasn't been seeded yet
        return {
            "tab_home": "בית",
            "tab_docs": "מסמכים",
            "tab_tasks": "משימות",
            "tab_notes": "פתקים",
            "tab_alerts": "התראות",
            "tab_links": "קישורים",
            "tab_highschool": "תיכון",
            "home_title": "ברוכים הבאים",
            "home_description": "אנא הריצו את קבצי schema.sql ו-seed.sql כדי לטעון נתונים לדוגמה.",
        }
    return dict(row)


def get_tabs_config(settings: Dict[str, Any]) -> List[Dict[str, str]]:
    # Icons: Bootstrap Icons
    return [
        {"id": "home", "label": settings["tab_home"], "icon": "bi bi-house"},
        {"id": "docs", "label": settings["tab_docs"], "icon": "bi bi-file-text"},
        {"id": "tasks", "label": settings["tab_tasks"], "icon": "bi bi-check2-square"},
        {"id": "notes", "label": settings["tab_notes"], "icon": "bi bi-journal-text"},
        {"id": "alerts", "label": settings["tab_alerts"], "icon": "bi bi-bell"},
        {"id": "links", "label": settings["tab_links"], "icon": "bi bi-link-45deg"},
        {"id": "hs",   "label": settings["tab_highschool"], "icon": "bi bi-mortarboard"},  # תיכון
    ]


def fetch_rows_for_tab(tab: str) -> List[Dict[str, Any]]:
    """Return rows for a given logical tab, converting allow_valenteres to boolean."""
    if tab not in ALLOWED_TABS:
        abort(404)
    cache_key = f"tab:{tab}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    table = TABLE_MAP[tab]
    with _connect() as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()

    data: List[Dict[str, Any]] = []
    for r in rows:
        d = dict(r)
        # Convert 0/1 to True/False in JSON
        d["allow_valenteres"] = bool(d.get("allow_valenteres", 0))
        data.append(d)

    _cache_set(cache_key, data)
    return data


@app.after_request
def force_utf8_headers(resp: Response):
    # Ensure UTF-8 for HTML
    if resp.mimetype == "text/html" and "charset" not in (resp.content_type or ""):
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.route("/")
def index():
    tab = (request.args.get("tab") or "").strip().lower()
    if tab not in ALLOWED_TABS:
        tab = "home"

    settings = fetch_settings()
    tabs_config = get_tabs_config(settings)
    return render_template(
        "index.html",
        tabs_config=tabs_config,
        active_tab=tab,
        settings=settings,
    )


@app.route("/api/<tab>")
def api_tab(tab: str):
    tab = (tab or "").strip().lower()
    if tab not in ALLOWED_TABS:
        abort(404)
    payload = fetch_rows_for_tab(tab)
    # Explicit UTF-8 JSON response
    return Response(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
    )


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    # Allows local run: respects $PORT (Cloud Run) but defaults to 5000
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)