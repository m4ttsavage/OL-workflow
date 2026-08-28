#!/usr/bin/env python3
"""Submit an intake JSON file to VDSD or VDV via Jira REST."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_payload  # noqa: E402
import jira_client as jira  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path")
    parser.add_argument("--source", choices=("vdsd", "vdv"), required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.json_path).read_text())
    errors = intake_payload.validate(payload, args.source)
    if errors:
        print("invalid:", *errors, sep="\n- ")
        return 2
    fields = intake_payload.jira_fields(payload, args.source)
    created = jira.post("/rest/api/3/issue", {"fields": fields})
    key = created["key"]
    print(key)
    print(f"{jira.BASE}/browse/{key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
