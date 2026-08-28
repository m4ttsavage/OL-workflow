#!/usr/bin/env python3
"""Build ADF-ready description + labels from an intake payload."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import field_ids  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TAX = json.loads((ROOT / "config" / "taxonomy.json").read_text())

PHI_PATTERNS = [
    re.compile(r"\b(ssn|social security|mrn|medical record|date of birth|dob|phi)\b", re.I),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
]


def org_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def validate(payload: dict, source: str) -> list[str]:
    errors: list[str] = []
    required = ["requester_name", "requester_email", "organization", "request_type", "impact_bucket", "priority", "summary", "description"]
    for key in required:
        if not payload.get(key):
            errors.append(f"missing {key}")
    rtype = payload.get("request_type")
    program_required = True
    for item in TAX["request_types"]:
        if item["id"] == rtype:
            program_required = item.get("program_required", True)
    if program_required and not payload.get("clinical_program"):
        errors.append("clinical_program required for this request type")
    program = payload.get("clinical_program")
    sub_required = True
    for prog in TAX["clinical_programs"]:
        if prog["id"] == program:
            sub_required = prog.get("subprogram_required", True)
    if program_required and sub_required and not payload.get("subprogram"):
        errors.append("subprogram required for this clinical program")
    impact = payload.get("impact_bucket")
    for bucket in TAX["impact_buckets"]:
        if bucket["id"] == impact and bucket.get("value_required"):
            if payload.get("business_value_usd") in (None, ""):
                errors.append("business_value_usd required")
            if not payload.get("value_type"):
                errors.append("value_type required")
    if source == "vdsd" and payload.get("no_phi_ack") not in (True, "Yes", "yes"):
        errors.append("no_phi_ack required on customer intake")
    blob = " ".join(str(payload.get(k, "")) for k in ("summary", "description", "requester_name"))
    for pat in PHI_PATTERNS:
        if pat.search(blob):
            errors.append("possible PHI detected; remove clinical/patient identifiers")
            break
    return errors


def labels(payload: dict, source: str) -> list[str]:
    out = [f"source:{source}", f"type:{payload['request_type']}", f"impact:{payload['impact_bucket']}", f"org:{org_slug(payload['organization'])}"]
    if payload.get("clinical_program"):
        out.append(f"program:{payload['clinical_program']}")
    if payload.get("subprogram"):
        out.append(f"sub:{payload['subprogram']}")
    return out


def description_markdown(payload: dict, source: str) -> str:
    rows = [
        ("Requester Name", payload.get("requester_name")),
        ("Requester Email", payload.get("requester_email")),
        ("Organization", payload.get("organization")),
        ("Request Type", payload.get("request_type")),
        ("Clinical Program", payload.get("clinical_program") or "NA"),
        ("Subprogram", payload.get("subprogram") or "NA"),
        ("Impact Bucket", payload.get("impact_bucket")),
        ("Business Value USD", payload.get("business_value_usd")),
        ("Value Type", payload.get("value_type")),
        ("Priority", payload.get("priority")),
        ("Source", source),
        ("No PHI Acknowledgement", payload.get("no_phi_ack")),
    ]
    lines = [payload.get("description", "").strip(), "", "## Intake metadata", "", "| Field | Value |", "| --- | --- |"]
    for key, val in rows:
        if val in (None, ""):
            continue
        lines.append(f"| {key} | {val} |")
    lines.append("")
    lines.append("_Do not add patient or clinical data to this issue._")
    return "\n".join(lines)


def markdown_to_adf(text: str) -> dict:
    """Minimal ADF so Jira REST v3 accepts the description without a wiki renderer."""
    content: list[dict] = []
    for block in (text or "").split("\n\n"):
        lines = block.split("\n")
        paragraph: list[dict] = []
        for i, line in enumerate(lines):
            if line:
                paragraph.append({"type": "text", "text": line})
            if i < len(lines) - 1:
                paragraph.append({"type": "hardBreak"})
        content.append({"type": "paragraph", "content": paragraph or []})
    if not content:
        content = [{"type": "paragraph", "content": []}]
    return {"type": "doc", "version": 1, "content": content}


def jira_fields(payload: dict, source: str) -> dict:
    project = "VDSD" if source == "vdsd" else "VDV"
    issue_type = "Submit a request or incident" if source == "vdsd" else "Task"
    for item in TAX["request_types"]:
        if item["id"] == payload.get("request_type") and source == "vdv":
            issue_type = item.get("vdv_issue_type") or "Task"
    priority = TAX["priority_map"].get(payload.get("priority"), payload.get("priority") or "Medium")
    fields = {
        "project": {"key": project},
        "issuetype": {"name": issue_type},
        "summary": payload["summary"],
        "priority": {"name": priority},
        "labels": labels(payload, source),
        "description": markdown_to_adf(description_markdown(payload, source)),
    }
    fields.update(field_ids.custom_fields_from_payload(payload, source))
    return fields
