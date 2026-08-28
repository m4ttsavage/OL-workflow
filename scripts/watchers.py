#!/usr/bin/env python3
"""Resolve Veridian internal users and add them as Jira watchers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "internal-users.json"


def load() -> list[dict[str, Any]]:
    if not PATH.exists():
        return []
    return json.loads(PATH.read_text()).get("users") or []


def resolve(token: str) -> dict[str, Any] | None:
    needle = (token or "").strip().lower()
    if not needle:
        return None
    for user in load():
        fields = [
            user.get("id"),
            user.get("name"),
            user.get("jira_display_name"),
            user.get("email"),
            user.get("account_id"),
            user.get("slack_user_id"),
        ]
        if any(str(v).lower() == needle for v in fields if v):
            return user
    return None


def resolve_many(tokens: list[str] | str | None) -> list[dict[str, Any]]:
    if tokens is None:
        return []
    if isinstance(tokens, str):
        parts = [p.strip() for p in tokens.split(",") if p.strip()]
    else:
        parts = [str(t).strip() for t in tokens if str(t).strip()]
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for token in parts:
        user = resolve(token)
        if not user:
            raise ValueError(f"unknown internal user: {token}")
        aid = user["account_id"]
        if aid not in seen:
            seen.add(aid)
            out.append(user)
    return out


def add_watcher(issue_key: str, account_id: str) -> None:
    jira.post(f"/rest/api/3/issue/{issue_key}/watchers", account_id)


def add_watchers(issue_key: str, tokens: list[str] | str | None) -> list[dict[str, Any]]:
    added = []
    for user in resolve_many(tokens):
        add_watcher(issue_key, user["account_id"])
        added.append(user)
    return added


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_key")
    parser.add_argument("watchers", help="Comma-separated ids, names, or emails from config/internal-users.json")
    args = parser.parse_args()
    try:
        added = add_watchers(args.issue_key, args.watchers)
    except ValueError as exc:
        print(exc)
        return 2
    for user in added:
        print(args.issue_key, user["name"], user["account_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
