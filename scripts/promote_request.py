#!/usr/bin/env python3
"""Promote a VDSD issue to RND (engineering) and link implements / is implemented by."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import field_ids  # noqa: E402
import intake_payload  # noqa: E402
import jira_client as jira  # noqa: E402

IDS = field_ids.load()
CUSTOM_KEYS = ",".join(rec["id"] for rec in IDS.values())
ENGINEERING_KEY = intake_payload.TAX["projects"]["internal"]["key"]


def issue(key: str) -> dict:
    extra = f",{CUSTOM_KEYS}" if CUSTOM_KEYS else ""
    return jira.get(f"/rest/api/3/issue/{key}?fields=summary,description,priority,labels,issuetype{extra}")


def request_type_id(src_fields: dict) -> str | None:
    fid = field_ids.field_id(IDS, "Intake Request Type")
    val = src_fields.get(fid) if fid else None
    if isinstance(val, dict):
        return val.get("value")
    return None


def copy_custom_fields(src_fields: dict) -> dict:
    out = {}
    for rec in IDS.values():
        fid = rec["id"]
        val = src_fields.get(fid)
        if val not in (None, "", []):
            out[fid] = field_ids.sanitize_for_put(val)
    source_id = field_ids.field_id(IDS, "Source")
    source_sel = field_ids.select(IDS, "Source", "vdsd")
    if source_id and source_sel:
        out[source_id] = source_sel
    return out


def set_counterpart(key: str, counterpart: str) -> None:
    fid = field_ids.field_id(IDS, "Counterpart Key")
    if not fid:
        return
    jira.put(f"/rest/api/3/issue/{key}", {"fields": {fid: counterpart}})


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
    if not summary.startswith("["):
        summary = f"[{args.vdsd_key}] {summary}"
    issue_type = intake_payload.engineering_issue_type(request_type_id(fields))
    body_fields = {
        "project": {"key": ENGINEERING_KEY},
        "issuetype": {"name": issue_type},
        "summary": summary[:255],
        "priority": fields.get("priority") or {"name": "Medium"},
        "labels": labels,
        "description": fields.get("description"),
    }
    body_fields.update(copy_custom_fields(fields))
    created = jira.post("/rest/api/3/issue", {"fields": body_fields})
    eng_key = created["key"]
    labels.append(f"counterpart:{eng_key}")
    jira.put(f"/rest/api/3/issue/{eng_key}", {"fields": {"labels": labels}})
    src_labels = list(fields.get("labels") or [])
    tag = f"counterpart:{eng_key}"
    if tag not in src_labels:
        src_labels.append(tag)
        jira.put(f"/rest/api/3/issue/{args.vdsd_key}", {"fields": {"labels": src_labels}})
    set_counterpart(args.vdsd_key, eng_key)
    set_counterpart(eng_key, args.vdsd_key)
    jira.post(
        "/rest/api/3/issueLink",
        {
            "type": {"name": "Polaris work item link"},
            "inwardIssue": {"key": args.vdsd_key},
            "outwardIssue": {"key": eng_key},
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
                            "text": f"Promoted to engineering {eng_key} (implements this request).",
                        }
                    ],
                }
            ],
        }
    }
    jira.post(f"/rest/api/3/issue/{args.vdsd_key}/comment", comment)
    print(eng_key)
    print(f"{jira.SITE}/browse/{eng_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
