#!/usr/bin/env python3
"""Create dummy JSM organizations and plus-addressed customers on VDSD.

Idempotent. Source: config/jsm-customers.json. Writes config/jsm-customers-created.json.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402
import jsm_customers  # noqa: E402


def service_desk_id(project_key: str) -> str:
    data = jira.get("/rest/servicedeskapi/servicedesk")
    for desk in data.get("values") or []:
        if desk.get("projectKey") == project_key:
            return str(desk["id"])
    raise RuntimeError(f"service desk not found for {project_key}")


def list_organizations() -> dict[str, dict]:
    data = jira.get("/rest/servicedeskapi/organization?limit=50")
    return {org["name"]: org for org in data.get("values") or []}


def ensure_organization(name: str, existing: dict[str, dict]) -> dict:
    if name in existing:
        print("org exists", name, existing[name]["id"])
        return existing[name]
    created = jira.post("/rest/servicedeskapi/organization", {"name": name})
    existing[name] = created
    print("org created", name, created["id"])
    return created


def ensure_org_on_desk(desk_id: str, org_id: str, attached: set[str]) -> None:
    if org_id in attached:
        return
    jira.post(f"/rest/servicedeskapi/servicedesk/{desk_id}/organization", {"organizationId": int(org_id)})
    attached.add(org_id)
    print("  linked to VDSD")


def desk_organizations(desk_id: str) -> set[str]:
    data = jira.get(f"/rest/servicedeskapi/servicedesk/{desk_id}/organization?limit=50")
    return {str(org["id"]) for org in data.get("values") or []}


def find_customer(email: str) -> dict | None:
    q = urllib.parse.quote(email)
    users = jira.get(f"/rest/api/3/user/search?query={q}")
    for user in users or []:
        if (user.get("emailAddress") or "").lower() == email.lower():
            return user
    return None


def org_members(org_id: str) -> set[str]:
    data = jira.get(f"/rest/servicedeskapi/organization/{org_id}/user?limit=50")
    return {user.get("accountId") for user in data.get("values") or [] if user.get("accountId")}


def ensure_customer(display_name: str, email: str) -> dict:
    found = find_customer(email)
    if found:
        print("  customer exists", display_name, email)
        return found
    created = jira.post("/rest/servicedeskapi/customer", {"email": email, "displayName": display_name})
    print("  customer created", display_name, email)
    return created


def ensure_customer_in_org(org_id: str, account_id: str, members: set[str]) -> None:
    if account_id in members:
        return
    jira.post(f"/rest/servicedeskapi/organization/{org_id}/user", {"accountIds": [account_id]})
    members.add(account_id)
    print("  added to organization")


def ensure_customer_on_desk(desk_id: str, account_id: str) -> None:
    jira.post(f"/rest/servicedeskapi/servicedesk/{desk_id}/customer", {"accountIds": [account_id]})


def main() -> int:
    config = jsm_customers.load_config()
    errors = jsm_customers.validate_config(config)
    if errors:
        print("invalid config:", errors)
        return 2
    try:
        me = jira.probe()
        print("hello", me.get("displayName"))
    except Exception as exc:
        print("Cannot authenticate to Jira REST:", exc)
        return 2

    desk_id = service_desk_id(config["service_desk_project_key"])
    existing_orgs = list_organizations()
    attached = desk_organizations(desk_id)
    created: dict[str, Any] = {
        "service_desk_id": desk_id,
        "service_desk_project_key": config["service_desk_project_key"],
        "organizations": [],
    }

    for org in config["organizations"]:
        record = ensure_organization(org["name"], existing_orgs)
        org_id = str(record["id"])
        ensure_org_on_desk(desk_id, org_id, attached)
        members = org_members(org_id)
        customers_out = []
        for customer in org["customers"]:
            email = jsm_customers.customer_email(customer, org)
            account = ensure_customer(customer["display_name"], email)
            account_id = account["accountId"]
            ensure_customer_in_org(org_id, account_id, members)
            ensure_customer_on_desk(desk_id, account_id)
            customers_out.append(
                {
                    "display_name": customer["display_name"],
                    "role": customer.get("role"),
                    "plus_tag": customer.get("plus_tag"),
                    "email": email,
                    "account_id": account_id,
                }
            )
        created["organizations"].append(
            {
                "name": org["name"],
                "slug": org.get("slug") or jsm_customers.org_slug(org["name"]),
                "id": org_id,
                "uuid": record.get("uuid"),
                "customers": customers_out,
            }
        )

    jsm_customers.CREATED_PATH.write_text(json.dumps(created, indent=2) + "\n")
    print("wrote", jsm_customers.CREATED_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
