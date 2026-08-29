#!/usr/bin/env python3
"""Submit an intake JSON file to VDSD (customer) or RND (engineering) via Jira REST.

`--source vdv` remains for the leftover VDV service desk only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_payload  # noqa: E402
import jira_client as jira  # noqa: E402
import watchers  # noqa: E402


def load_payload(path: str) -> dict:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("payload must be a JSON object")
    return data


VALID_SOURCES = ("vdsd", "rnd", "vdv")


def resolve_source(payload: dict, explicit: str | None) -> str | None:
    source = explicit or payload.get("source")
    if source in VALID_SOURCES:
        return source
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", nargs="?", default="-", help="JSON file, or - for stdin")
    parser.add_argument("--source", choices=VALID_SOURCES, help="Defaults to payload.source")
    args = parser.parse_args()
    try:
        payload = load_payload(args.json_path)
    except (json.JSONDecodeError, ValueError) as exc:
        print("invalid JSON:", exc)
        return 2
    source = resolve_source(payload, args.source)
    if not source:
        print("missing --source (or payload.source of vdsd|rnd|vdv)")
        return 2
    errors = intake_payload.validate(payload, source)
    if errors:
        print("invalid:", *errors, sep="\n- ")
        return 2
    fields = intake_payload.jira_fields(payload, source)
    created = jira.post("/rest/api/3/issue", {"fields": fields})
    key = created["key"]
    watcher_tokens = payload.get("watchers")
    if watcher_tokens:
        added = watchers.add_watchers(key, watcher_tokens)
        print("watchers", ",".join(u["id"] for u in added))
    print(key)
    print(f"{jira.SITE}/browse/{key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
