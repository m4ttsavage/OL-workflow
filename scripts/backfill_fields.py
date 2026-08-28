#!/usr/bin/env python3
"""Write custom fields on seeded VDSD/VDV issues from seed-requests.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import field_ids  # noqa: E402
import jira_client as jira  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEED = json.loads((ROOT / "config" / "seed-requests.json").read_text())
CREATED = json.loads((ROOT / "config" / "seed-created.json").read_text())


def counterparts() -> dict[str, str]:
    out = {}
    for row in CREATED.get("promoted") or []:
        out[row["vdsd"]] = row["vdv"]
        out[row["vdv"]] = row["vdsd"]
    return out


def update_issue(key: str, payload: dict, source: str, counterpart: str | None) -> None:
    body = dict(payload)
    if counterpart:
        body["counterpart_key"] = counterpart
    fields = field_ids.custom_fields_from_payload(body, source)
    labels = jira.get(f"/rest/api/3/issue/{key}?fields=labels")["fields"].get("labels") or []
    if counterpart:
        tag = f"counterpart:{counterpart}"
        if tag not in labels:
            labels.append(tag)
        fields["labels"] = labels
    jira.put(f"/rest/api/3/issue/{key}", {"fields": fields})
    print("updated", key, list(fields)[:6])


def main() -> int:
    cmap = counterparts()
    vdsd_keys = CREATED["vdsd"]
    vdsd_payloads = [item for item in SEED if item["source"] == "vdsd"]
    if len(vdsd_keys) != len(vdsd_payloads):
        print("seed/vdsd length mismatch", len(vdsd_keys), len(vdsd_payloads))
    for key, item in zip(vdsd_keys, vdsd_payloads):
        update_issue(key, item["payload"], "vdsd", cmap.get(key))

    internal = [item for item in SEED if item["source"] == "vdv"]
    for key, item in zip(CREATED.get("internal_direct") or [], internal):
        update_issue(key, item["payload"], "vdv", None)

    promoted_payloads = [item for item in SEED if item["source"] == "vdsd" and item.get("promote")]
    for pair, item in zip(CREATED.get("promoted") or [], promoted_payloads):
        payload = dict(item["payload"])
        payload["counterpart_key"] = pair["vdsd"]
        update_issue(pair["vdv"], payload, "vdsd", pair["vdsd"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
