#!/usr/bin/env python3
"""Add intake custom fields to VDSD JSM screens.

Team-managed RND has no classic screens — use scripts/associate_rnd_fields.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIELDS = json.loads((ROOT / "config" / "field-ids.json").read_text())
SCREEN_IDS = ["10010", "10011", "10012"]  # SUP JSM default / request / question


def tabs(screen_id: str) -> list[dict]:
    return jira.get(f"/rest/api/3/screens/{screen_id}/tabs")


def existing_fields(screen_id: str, tab_id: str) -> set[str]:
    data = jira.get(f"/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields")
    return {item.get("id") for item in data or []}


def field_id_list() -> list[str]:
    out = []
    for rec in FIELDS.values():
        if isinstance(rec, dict):
            out.append(rec["id"])
        else:
            out.append(rec)
    return out


def main() -> int:
    field_ids = field_id_list()
    for screen_id in SCREEN_IDS:
        tab_list = tabs(screen_id)
        if not tab_list:
            print("no tabs", screen_id)
            continue
        tab_id = tab_list[0]["id"]
        have = existing_fields(screen_id, tab_id)
        print(f"screen {screen_id} tab {tab_id} already {len(have)}")
        for field_id in field_ids:
            if field_id in have:
                continue
            try:
                jira.post(f"/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields", {"fieldId": field_id})
                print("  +", field_id)
            except Exception as exc:
                print("  fail", field_id, exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
