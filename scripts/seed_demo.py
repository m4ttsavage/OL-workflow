#!/usr/bin/env python3
"""Seed dummy requests from a JSON array via REST.

By default records into config/seed-created.json. Pass --merge-created (the
default when --file is not the original seed-requests.json) so a later batch
does not wipe earlier keys.
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

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "config" / "seed-requests.json"
CREATED_PATH = ROOT / "config" / "seed-created.json"


def merge_created(created: dict, batch: dict) -> dict:
    out = dict(created)
    vdsd = list(out.get("vdsd") or [])
    for key in batch.get("vdsd") or []:
        if key not in vdsd:
            vdsd.append(key)
    out["vdsd"] = vdsd
    promoted = list(out.get("promoted") or [])
    for row in batch.get("promoted") or []:
        if row not in promoted:
            promoted.append(row)
    out["promoted"] = promoted
    internal = list(out.get("internal_direct") or [])
    for key in batch.get("internal_direct") or []:
        if key not in internal:
            internal.append(key)
    out["internal_direct"] = internal
    if batch.get("batch_2"):
        out["batch_2"] = batch["batch_2"]
    if batch.get("notes"):
        out["notes"] = batch["notes"]
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(DEFAULT_SEED), help="Seed JSON array")
    parser.add_argument(
        "--merge-created",
        action="store_true",
        default=None,
        help="Merge new keys into config/seed-created.json instead of replacing it",
    )
    parser.add_argument("--replace-created", action="store_true")
    args = parser.parse_args()
    seed_path = Path(args.file)
    items = json.loads(seed_path.read_text())
    created_rows = []
    for item in items:
        source = item["source"]
        payload = item["payload"]
        errors = intake_payload.validate(payload, source)
        if errors:
            print("skip invalid", payload.get("summary"), errors)
            continue
        fields = intake_payload.jira_fields(payload, source)
        issue = jira.post("/rest/api/3/issue", {"fields": fields})
        key = issue["key"]
        watcher_tokens = item.get("watchers") or payload.get("watchers")
        added = []
        if watcher_tokens:
            added = watchers.add_watchers(key, watcher_tokens)
        created_rows.append(
            {
                "source": source,
                "key": key,
                "promote": bool(item.get("promote")),
                "watchers": [u["id"] for u in added],
                "summary": payload.get("summary"),
            }
        )
        print(source, key, "watchers", ",".join(u["id"] for u in added) or "-")
    vdsd_for_promote = [c["key"] for c in created_rows if c["source"] == "vdsd" and c.get("promote")]
    print("promote these with scripts/promote_request.py:", " ".join(vdsd_for_promote))

    batch = {
        "vdsd": [c["key"] for c in created_rows if c["source"] == "vdsd"],
        "internal_direct": [c["key"] for c in created_rows if c["source"] in ("rnd", "vdv")],
        "batch_2": created_rows,
        "notes": "Batch submitted via seed_demo.py. Promote flagged keys with scripts/promote_request.py.",
    }
    merge = args.merge_created
    if args.replace_created:
        merge = False
    elif merge is None:
        merge = seed_path.resolve() != DEFAULT_SEED.resolve()
    if merge and CREATED_PATH.exists():
        existing = json.loads(CREATED_PATH.read_text())
        out = merge_created(existing, batch)
    else:
        out = batch
    CREATED_PATH.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", CREATED_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
