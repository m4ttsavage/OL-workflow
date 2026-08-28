#!/usr/bin/env python3
"""Promote a VDSD issue to VDV and link implements / is implemented by."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402

TAX = json.loads((Path(__file__).resolve().parents[1] / "config" / "taxonomy.json").read_text())


def issue(key: str) -> dict:
    return jira.get(f"/rest/api/3/issue/{key}?fields=summary,description,priority,labels,issuetype")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vdsd_key")
    args = parser.parse_args()
    src = issue(args.vdsd_key)
    fields = src["fields"]
    labels = list(fields.get("labels") or [])
    if "source:vdsd" not in labels:
        labels.append("source:vdsd")
    summary = fields["summary"]
    if not summary.startswith("[") :
        summary = f"[{args.vdsd_key}] {summary}"
    body = {
        "fields": {
            "project": {"key": "VDV"},
            "issuetype": {"name": "Task"},
            "summary": summary[:255],
            "priority": fields.get("priority") or {"name": "Medium"},
            "labels": labels,
            "description": fields.get("description"),
        }
    }
    created = jira.post("/rest/api/3/issue", body)
    vdv_key = created["key"]
    jira.post(
        "/rest/api/3/issueLink",
        {
            "type": {"name": "Polaris work item link"},
            "inwardIssue": {"key": args.vdsd_key},
            "outwardIssue": {"key": vdv_key},
        },
    )
    comment = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Promoted to engineering {vdv_key} (implements this request).",
                        }
                    ],
                }
            ],
        }
    }
    jira.post(f"/rest/api/3/issue/{args.vdsd_key}/comment", comment)
    print(vdv_key)
    print(f"{jira.BASE}/browse/{vdv_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
