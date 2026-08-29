#!/usr/bin/env python3
"""Associate global intake custom fields with team-managed RND.

Classic JSM screens do not exist on next-gen projects (`GET /screens/{id}/tabs`
returns "Screen does not exist"). PUT /rest/api/3/field/association with
PROJECT_ID is the working admin API. It lets REST set the fields on Feature and
Task even when createmeta / the Fields UI layout still hides them.

Requires Administer Jira (classic `jira_admin_token`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIELDS = json.loads((ROOT / "config" / "field-ids.json").read_text())
TAX = json.loads((ROOT / "config" / "taxonomy.json").read_text())
PROJECT_ID = str(TAX["projects"]["internal"]["id"])


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
    if not field_ids:
        print("no fields in config/field-ids.json")
        return 2
    body = {
        "associationContexts": [{"identifier": int(PROJECT_ID), "type": "PROJECT_ID"}],
        "fields": [{"identifier": fid, "type": "FIELD_ID"} for fid in field_ids],
    }
    jira.put("/rest/api/3/field/association", body)
    print("associated", len(field_ids), "fields with project", TAX["projects"]["internal"]["key"], PROJECT_ID)
    for fid in field_ids:
        print(" ", fid)
    print("Pin the same fields on RND → Project settings → Fields if the work-item UI still hides them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
