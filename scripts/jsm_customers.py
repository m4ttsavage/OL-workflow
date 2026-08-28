"""Helpers for dummy JSM organizations and plus-addressed customer accounts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "jsm-customers.json"
CREATED_PATH = ROOT / "config" / "jsm-customers-created.json"

PLUS_LOCAL = "matthewmsavage"
EMAIL_DOMAIN = "gmail.com"
PLUS_TAG_RE = re.compile(r"[a-z0-9][a-z0-9._+-]*$")


def org_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def plus_email(plus_tag: str) -> str:
    """Gmail plus-address used as a unique JSM customer registration.

    All mail still lands in matthewmsavage@gmail.com.
    """
    tag = (plus_tag or "").strip().lower().lstrip("+")
    if not PLUS_TAG_RE.fullmatch(tag):
        raise ValueError(f"invalid plus tag: {plus_tag!r}")
    return f"{PLUS_LOCAL}+{tag}@{EMAIL_DOMAIN}"


def customer_email(customer: dict[str, Any], org: dict[str, Any] | None = None) -> str:
    if customer.get("email"):
        return str(customer["email"]).strip().lower()
    tag = customer.get("plus_tag") or (org_slug(org["name"]) if org else None)
    if not tag:
        raise ValueError("customer needs email or plus_tag")
    return plus_email(str(tag))


def load_config(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or CONFIG_PATH).read_text())


def load_created(path: Path | None = None) -> dict[str, Any]:
    target = path or CREATED_PATH
    if not target.exists():
        return {}
    return json.loads(target.read_text())


def organization_id(name: str, created: dict[str, Any] | None = None) -> str | None:
    data = created if created is not None else load_created()
    for org in data.get("organizations") or []:
        if org.get("name") == name:
            return str(org["id"]) if org.get("id") is not None else None
    return None


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    orgs = config.get("organizations") or []
    if not orgs:
        errors.append("no organizations")
    names: set[str] = set()
    emails: set[str] = set()
    tags: set[str] = set()
    for org in orgs:
        name = org.get("name")
        if not name:
            errors.append("organization missing name")
            continue
        slug = org.get("slug") or org_slug(name)
        if slug != org_slug(name):
            errors.append(f"{name}: slug {org.get('slug')!r} does not match {org_slug(name)!r}")
        if name in names:
            errors.append(f"duplicate organization {name}")
        names.add(name)
        customers = org.get("customers") or []
        if not customers:
            errors.append(f"{name}: no customers")
        for customer in customers:
            display = customer.get("display_name")
            if not display:
                errors.append(f"{name}: customer missing display_name")
            try:
                email = customer_email(customer, org)
            except ValueError as exc:
                errors.append(f"{name}: {exc}")
                continue
            if not email.endswith(f"@{EMAIL_DOMAIN}") or f"{PLUS_LOCAL}+" not in email:
                errors.append(f"{name}/{display}: email {email} is not a {PLUS_LOCAL}+ permutation")
            if email in emails:
                errors.append(f"duplicate email {email}")
            emails.add(email)
            tag = customer.get("plus_tag") or slug
            if tag in tags:
                errors.append(f"duplicate plus_tag {tag}")
            tags.add(tag)
            if org_slug(name) not in str(tag):
                errors.append(f"{name}/{display}: plus_tag {tag!r} does not include org slug")
    return errors
