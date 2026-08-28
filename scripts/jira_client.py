"""Jira Cloud REST helper. Auth: ATLASSIAN_EMAIL + jira_admin_veridian (or ATLASSIAN_API_TOKEN)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

BASE = os.environ.get("ATLASSIAN_BASE_URL", "https://veridian-dynamics.atlassian.net").rstrip("/")
EMAIL = os.environ.get("ATLASSIAN_EMAIL", "matthewmsavage@gmail.com")
TOKEN = os.environ.get("ATLASSIAN_API_TOKEN") or os.environ.get("jira_admin_veridian", "")


def _auth_header() -> str:
    import base64

    if not TOKEN:
        raise SystemExit("Set jira_admin_veridian or ATLASSIAN_API_TOKEN")
    raw = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
    return f"Basic {raw}"


def request(method: str, path: str, body: Any | None = None, extra_headers: dict | None = None) -> Any:
    url = path if path.startswith("http") else f"{BASE}{path}"
    headers = {
        "Authorization": _auth_header(),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"{method} {url} -> {exc.code}: {err[:800]}") from exc


def get(path: str) -> Any:
    return request("GET", path)


def post(path: str, body: Any) -> Any:
    return request("POST", path, body)


def put(path: str, body: Any) -> Any:
    return request("PUT", path, body)


def probe() -> dict:
    return get("/rest/api/3/myself")


if __name__ == "__main__":
    try:
        me = probe()
        print("authenticated as", me.get("displayName"), me.get("emailAddress"))
    except Exception as exc:
        print("auth failed:", exc, file=sys.stderr)
        sys.exit(1)
