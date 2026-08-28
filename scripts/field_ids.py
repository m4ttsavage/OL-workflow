"""Load config/field-ids.json (nested or flat) for REST payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "field-ids.json"
JSM_CREATED = ROOT / "config" / "jsm-customers-created.json"


def jsm_organization_id(name: str | None) -> str | None:
    """Native JSM Organizations field id from the last seed_jsm_customers run."""
    if not name or not JSM_CREATED.exists():
        return None
    data = json.loads(JSM_CREATED.read_text())
    for org in data.get("organizations") or []:
        if org.get("name") == name and org.get("id") is not None:
            return str(org["id"])
    return None


def load() -> dict[str, Any]:
    if not PATH.exists():
        return {}
    raw = json.loads(PATH.read_text())
    out: dict[str, Any] = {}
    for name, rec in raw.items():
        if isinstance(rec, str):
            out[name] = {"id": rec, "contextId": None, "options": {}}
        else:
            out[name] = {
                "id": rec["id"],
                "contextId": rec.get("contextId"),
                "options": rec.get("options") or {},
            }
    return out


def field_id(fields: dict[str, Any], name: str) -> str | None:
    rec = fields.get(name)
    return rec["id"] if rec else None


def option_id(fields: dict[str, Any], name: str, value: str | None) -> str | None:
    if not value:
        return None
    rec = fields.get(name) or {}
    return (rec.get("options") or {}).get(value)


def select(fields: dict[str, Any], name: str, value: str | None) -> dict | None:
    if not value:
        return None
    oid = option_id(fields, name, value)
    if oid:
        return {"id": oid}
    return {"value": value}


def sanitize_for_put(value: Any) -> Any:
    if isinstance(value, dict) and "id" in value and not value["id"].startswith("customfield_"):
        if "value" in value or "self" in value:
            return {"id": value["id"]}
    return value


def custom_fields_from_payload(payload: dict, source: str) -> dict[str, Any]:
    """Map intake JSON onto Jira customfield_* keys. Empty if field-ids.json is missing."""
    fields = load()
    if not fields:
        return {}
    out: dict[str, Any] = {}

    def put_text(name: str, value: Any) -> None:
        fid = field_id(fields, name)
        if fid and value not in (None, ""):
            out[fid] = str(value)

    def put_select(name: str, value: str | None) -> None:
        fid = field_id(fields, name)
        sel = select(fields, name, value)
        if fid and sel:
            out[fid] = sel

    put_text("Requester Name", payload.get("requester_name"))
    put_text("Requester Email", payload.get("requester_email"))
    put_select("Organization", payload.get("organization"))
    if payload.get("organization") == "Other":
        put_text("Organization Other", payload.get("organization_other"))
    put_select("Intake Request Type", payload.get("request_type"))
    put_select("Clinical Program", payload.get("clinical_program"))
    put_select("Subprogram", payload.get("subprogram"))
    put_select("Impact Bucket", payload.get("impact_bucket"))
    usd = payload.get("business_value_usd")
    fid_usd = field_id(fields, "Business Value USD")
    if fid_usd and usd not in (None, ""):
        out[fid_usd] = float(usd)
    put_select("Value Type", payload.get("value_type"))
    put_select("Source", source)
    put_text("Counterpart Key", payload.get("counterpart_key"))
    ack = payload.get("no_phi_ack")
    if source == "vdsd" and ack in (True, "Yes", "yes"):
        put_select("No PHI Acknowledgement", "Yes")
    elif ack in (False, "No", "no"):
        put_select("No PHI Acknowledgement", "No")
    org_id = jsm_organization_id(payload.get("organization"))
    if org_id:
        out["customfield_10002"] = [{"id": org_id}]
    return out
