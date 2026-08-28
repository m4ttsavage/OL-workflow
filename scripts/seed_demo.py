#!/usr/bin/env python3
"""Seed dummy VDSD then VDV requests from config/seed-requests.json via REST."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_payload  # noqa: E402
import jira_client as jira  # noqa: E402

DEFAULT_SEED = Path(__file__).resolve().parents[1] / "config" / "seed-requests.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(DEFAULT_SEED), help="Seed JSON array (default: config/seed-requests.json)")
    args = parser.parse_args()
    seed_path = Path(args.file)
    items = json.loads(seed_path.read_text())
    created = []
    for item in items:
        source = item["source"]
        payload = item["payload"]
        errors = intake_payload.validate(payload, source)
        if errors:
            print("skip invalid", payload.get("summary"), errors)
            continue
        fields = intake_payload.jira_fields(payload, source)
        issue = jira.post("/rest/api/3/issue", {"fields": fields})
        created.append({"source": source, "key": issue["key"], "promote": item.get("promote")})
        print(source, issue["key"])
    vdsd_for_promote = [c["key"] for c in created if c["source"] == "vdsd" and c.get("promote")]
    print("promote these with scripts/promote_request.py:", " ".join(vdsd_for_promote))
    (Path(__file__).resolve().parents[1] / "config" / "seed-created.json").write_text(json.dumps(created, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
