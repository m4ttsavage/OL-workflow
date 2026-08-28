#!/usr/bin/env python3
"""Add Promote to Engineering (VDSD ESM) and In Review (VDV Simple ESM)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402

PROMOTE = "10020"
IN_REVIEW = "10021"


def fetch() -> dict:
    return jira.post(
        "/rest/api/3/workflows",
        {
            "projectAndIssueTypes": [
                {"projectId": "10002", "issueTypeId": "10010"},
                {"projectId": "10002", "issueTypeId": "10011"},
                {"projectId": "10005", "issueTypeId": "10013"},
            ]
        },
    )


def extra_statuses() -> list[dict]:
    return [
        {
            "id": PROMOTE,
            "statusReference": PROMOTE,
            "name": "Promote to Engineering",
            "statusCategory": "IN_PROGRESS",
            "scope": {"type": "GLOBAL"},
            "description": "Customer request promoted to VDV engineering work",
        },
        {
            "id": IN_REVIEW,
            "statusReference": IN_REVIEW,
            "name": "In Review",
            "statusCategory": "IN_PROGRESS",
            "scope": {"type": "GLOBAL"},
            "description": "Engineering work in review",
        },
    ]


def has_status(wf: dict, ref: str) -> bool:
    return any(s.get("statusReference") == ref for s in wf.get("statuses") or [])


def has_transition(wf: dict, name: str, to_ref: str) -> bool:
    for t in wf.get("transitions") or []:
        if t.get("name") == name and t.get("toStatusReference") == to_ref:
            return True
    return False


def patch_default_esm(wf: dict) -> None:
    if has_status(wf, PROMOTE):
        return
    if not has_status(wf, PROMOTE):
        wf["statuses"].append(
            {
                "statusReference": PROMOTE,
                "layout": {"x": 546.0, "y": 230.0},
                "properties": {},
                "deprecated": False,
            }
        )
    if not has_transition(wf, "Promote to Engineering", PROMOTE):
        wf["transitions"].append(
            {
                "id": "151",
                "type": "DIRECTED",
                "name": "Promote to Engineering",
                "description": "Create linked VDV engineering work",
                "toStatusReference": PROMOTE,
                "links": [{"fromStatusReference": "3", "fromPort": 7, "toPort": 1}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )
    if not has_transition(wf, "Resolved from Engineering", "10012"):
        wf["transitions"].append(
            {
                "id": "161",
                "type": "DIRECTED",
                "name": "Resolved",
                "description": "",
                "toStatusReference": "10012",
                "links": [{"fromStatusReference": PROMOTE, "fromPort": 3, "toPort": 7}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )


def patch_simple_esm(wf: dict) -> None:
    if has_status(wf, IN_REVIEW):
        return
    if not has_status(wf, IN_REVIEW):
        wf["statuses"].append(
            {
                "statusReference": IN_REVIEW,
                "layout": {"x": 545.0, "y": 107.8},
                "properties": {},
                "deprecated": False,
            }
        )
    if not has_transition(wf, "In Review", IN_REVIEW):
        wf["transitions"].append(
            {
                "id": "141",
                "type": "DIRECTED",
                "name": "In Review",
                "description": "",
                "toStatusReference": IN_REVIEW,
                "links": [{"fromStatusReference": "3", "fromPort": 5, "toPort": 7}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )
    if not has_transition(wf, "Resolved from Review", "10012"):
        wf["transitions"].append(
            {
                "id": "151",
                "type": "DIRECTED",
                "name": "Resolved",
                "description": "",
                "toStatusReference": "10012",
                "links": [{"fromStatusReference": IN_REVIEW, "fromPort": 3, "toPort": 7}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )
    if not has_transition(wf, "Back to progress", "3"):
        wf["transitions"].append(
            {
                "id": "161",
                "type": "DIRECTED",
                "name": "Back to progress",
                "description": "",
                "toStatusReference": "3",
                "links": [{"fromStatusReference": IN_REVIEW, "fromPort": 7, "toPort": 3}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )


def patch_jsm_default(wf: dict) -> None:
    if has_status(wf, IN_REVIEW):
        return
    if not has_status(wf, IN_REVIEW):
        wf["statuses"].append(
            {
                "statusReference": IN_REVIEW,
                "layout": {"x": 750.0, "y": 166.1},
                "properties": {},
                "deprecated": False,
            }
        )
    if not has_transition(wf, "In Review", IN_REVIEW):
        wf["transitions"].append(
            {
                "id": "81",
                "type": "DIRECTED",
                "name": "In Review",
                "description": "",
                "toStatusReference": IN_REVIEW,
                "links": [
                    {"fromStatusReference": "10010", "fromPort": 3, "toPort": 7},
                    {"fromStatusReference": "1", "fromPort": 3, "toPort": 7},
                ],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )
    if not has_transition(wf, "Mark as done from Review", "10012"):
        wf["transitions"].append(
            {
                "id": "91",
                "type": "DIRECTED",
                "name": "Mark as done",
                "description": "",
                "toStatusReference": "10012",
                "links": [{"fromStatusReference": IN_REVIEW, "fromPort": 3, "toPort": 7}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )
    if not has_transition(wf, "Back to progress", "10010"):
        wf["transitions"].append(
            {
                "id": "101",
                "type": "DIRECTED",
                "name": "Start progress",
                "description": "",
                "toStatusReference": "10010",
                "links": [{"fromStatusReference": IN_REVIEW, "fromPort": 7, "toPort": 3}],
                "actions": [],
                "validators": [],
                "triggers": [],
                "properties": {},
            }
        )


def main() -> int:
    data = fetch()
    statuses = list(data["statuses"])
    for extra in extra_statuses():
        if not any(s["id"] == extra["id"] for s in statuses):
            statuses.append(extra)

    workflows = []
    for wf in data["workflows"]:
        before = json.dumps(wf["statuses"]) + json.dumps([(t["id"], t["name"]) for t in wf["transitions"]])
        if wf["id"] == "d3dce03c-c3c9-4b01-a003-f1bafef1b8a9":
            patch_default_esm(wf)
        elif wf["id"] == "22674daf-a1ce-4971-ac0d-a26adae322cb":
            patch_simple_esm(wf)
        elif wf["id"] == "4e6734dd-1438-4698-80f2-748be7b71d89":
            patch_jsm_default(wf)
        after = json.dumps(wf["statuses"]) + json.dumps([(t["id"], t["name"]) for t in wf["transitions"]])
        if before == after:
            print("unchanged", wf["name"])
            continue
        body = {
            "id": wf["id"],
            "version": wf["version"],
            "name": wf["name"],
            "description": wf.get("description", ""),
            "startPointLayout": wf.get("startPointLayout"),
            "statuses": wf["statuses"],
            "transitions": wf["transitions"],
        }
        workflows.append(body)

    if not workflows:
        print("no workflow changes")
        return 0

    payload = {"statuses": statuses, "workflows": workflows}
    try:
        validation = jira.post("/rest/api/3/workflows/update/validation", {"payload": payload})
        print("validation", json.dumps(validation)[:800])
    except Exception as exc:
        print("validation endpoint:", exc)

    try:
        result = jira.post("/rest/api/3/workflows/update", payload)
        print("updated", json.dumps(result)[:1200])
    except Exception as exc:
        print("update failed:", exc)
        return 1

    after = fetch()
    for wf in after["workflows"]:
        print(wf["name"], [s.get("statusReference") for s in wf["statuses"]], [t.get("name") for t in wf["transitions"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
