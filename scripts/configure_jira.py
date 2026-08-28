#!/usr/bin/env python3
"""Create global custom fields and select options from config/taxonomy.json.

Requires a working classic Atlassian API token (jira_admin_veridian currently 401).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TAX = json.loads((ROOT / "config" / "taxonomy.json").read_text())

TEXT = "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
TEXT_SEARCH = "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
SELECT = "com.atlassian.jira.plugin.system.customfieldtypes:select"
SELECT_SEARCH = "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher"
NUMBER = "com.atlassian.jira.plugin.system.customfieldtypes:float"
NUMBER_SEARCH = "com.atlassian.jira.plugin.system.customfieldtypes:exactnumber"
CHECKBOX = "com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons"
CHECKBOX_SEARCH = "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher"


def existing_by_name() -> dict[str, dict]:
    fields = jira.get("/rest/api/3/field")
    out: dict[str, dict] = {}
    for field in fields:
        out.setdefault(field["name"], field)
    return out


def create_field(name: str, field_type: str, searcher: str) -> dict:
    return jira.post(
        "/rest/api/3/field",
        {"name": name, "type": field_type, "searcherKey": searcher, "description": "Veridian Dynamics intake"},
    )


def ensure_field(name: str, field_type: str, searcher: str, cache: dict) -> dict:
    if name in cache and cache[name].get("id", "").startswith("customfield_"):
        print("exists", name, cache[name]["id"])
        return cache[name]
    created = create_field(name, field_type, searcher)
    cache[name] = created
    print("created", name, created.get("id"))
    return created


def context_id(field_id: str) -> str:
    data = jira.get(f"/rest/api/3/field/{field_id}/context")
    values = data.get("values") or []
    if not values:
        raise RuntimeError(f"no context for {field_id}")
    return values[0]["id"]


def add_options(field_id: str, ctx: str, options: list[str]) -> None:
    existing = jira.get(f"/rest/api/3/field/{field_id}/context/{ctx}/option")
    have = {opt["value"] for opt in existing.get("values") or []}
    missing = [{"value": opt} for opt in options if opt not in have]
    if not missing:
        return
    jira.post(f"/rest/api/3/field/{field_id}/context/{ctx}/option", {"options": missing})
    print("  options +", [m["value"] for m in missing])


def main() -> int:
    try:
        me = jira.probe()
        print("hello", me.get("displayName"))
    except Exception as exc:
        print("Cannot authenticate to Jira REST:", exc)
        print("Create a classic API token and store it as jira_admin_veridian. See docs/credentials.md")
        return 2

    cache = existing_by_name()
    fields = []

    name_cf = ensure_field("Requester Name", TEXT, TEXT_SEARCH, cache)
    email_cf = ensure_field("Requester Email", TEXT, TEXT_SEARCH, cache)
    org_cf = ensure_field("Organization", SELECT, SELECT_SEARCH, cache)
    org_other = ensure_field("Organization Other", TEXT, TEXT_SEARCH, cache)
    rtype = ensure_field("Intake Request Type", SELECT, SELECT_SEARCH, cache)
    program = ensure_field("Clinical Program", SELECT, SELECT_SEARCH, cache)
    sub = ensure_field("Subprogram", SELECT, SELECT_SEARCH, cache)
    impact = ensure_field("Impact Bucket", SELECT, SELECT_SEARCH, cache)
    value = ensure_field("Business Value USD", NUMBER, NUMBER_SEARCH, cache)
    vtype = ensure_field("Value Type", SELECT, SELECT_SEARCH, cache)
    source = ensure_field("Source", SELECT, SELECT_SEARCH, cache)
    counterpart = ensure_field("Counterpart Key", TEXT, TEXT_SEARCH, cache)
    phi = ensure_field("No PHI Acknowledgement", CHECKBOX, CHECKBOX_SEARCH, cache)

    add_options(org_cf["id"], context_id(org_cf["id"]), TAX["organizations"]["customer"] + TAX["organizations"]["internal"])
    add_options(rtype["id"], context_id(rtype["id"]), [t["id"] for t in TAX["request_types"]])
    add_options(program["id"], context_id(program["id"]), [p["id"] for p in TAX["clinical_programs"]])
    subs: list[str] = []
    for prog in TAX["clinical_programs"]:
        for item in prog.get("subprograms") or []:
            if item["id"] not in subs:
                subs.append(item["id"])
    add_options(sub["id"], context_id(sub["id"]), subs)
    add_options(impact["id"], context_id(impact["id"]), [i["id"] for i in TAX["impact_buckets"]])
    add_options(vtype["id"], context_id(vtype["id"]), [v["id"] for v in TAX["value_types"]])
    add_options(source["id"], context_id(source["id"]), ["vdsd", "vdv"])
    add_options(phi["id"], context_id(phi["id"]), ["Yes", "No"])

    mapping = {
        "Requester Name": name_cf["id"],
        "Requester Email": email_cf["id"],
        "Organization": org_cf["id"],
        "Organization Other": org_other["id"],
        "Intake Request Type": rtype["id"],
        "Clinical Program": program["id"],
        "Subprogram": sub["id"],
        "Impact Bucket": impact["id"],
        "Business Value USD": value["id"],
        "Value Type": vtype["id"],
        "Source": source["id"],
        "Counterpart Key": counterpart["id"],
        "No PHI Acknowledgement": phi["id"],
    }
    out = ROOT / "config" / "field-ids.json"
    out.write_text(json.dumps(mapping, indent=2) + "\n")
    print("wrote", out)
    print("Associate these fields to VDSD and VDV screens (docs/ui-runbooks.md).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
