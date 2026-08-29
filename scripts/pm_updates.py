#!/usr/bin/env python3
"""Apply named Jira transitions and Ted comments from config/pm-updates.json.

Slack MCP posts live thread replies; this script prints copy for each slack_parent_key.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comment_jira  # noqa: E402
import jira_client as jira  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "config" / "pm-updates.json"
SLACK_POSTED_PATH = ROOT / "config" / "slack-posted.json"

# Later ranks skip earlier named moves so we do not walk RND/VDSD backwards.
STATUS_ORDER: dict[str, dict[str, int]] = {
    "RND": {"Idea": 0, "To Do": 1, "In Progress": 2, "Testing": 3, "Done": 4},
    "VDSD": {
        "To Do": 0,
        "In Progress": 1,
        "Pending": 2,
        "Promote to Engineering": 2,
        "Done": 3,
    },
}


def load_playbook(path: Path = PLAYBOOK_PATH) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_slack_posted(path: Path = SLACK_POSTED_PATH) -> dict[str, Any]:
    return json.loads(path.read_text())


def issue_status(key: str) -> str:
    issue = jira.get(f"/rest/api/3/issue/{key}?fields=status")
    return issue["fields"]["status"]["name"]


def available_transitions(key: str) -> list[dict[str, Any]]:
    data = jira.get(f"/rest/api/3/issue/{key}/transitions")
    return list(data.get("transitions") or [])


def find_transition(transitions: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    needle = name.strip().lower()
    for trans in transitions:
        if str(trans.get("name") or "").strip().lower() == needle:
            return trans
    for trans in transitions:
        to_name = str((trans.get("to") or {}).get("name") or "").strip().lower()
        if to_name == needle:
            return trans
    return None


def target_name(trans: dict[str, Any]) -> str:
    return str((trans.get("to") or {}).get("name") or "")


def should_skip(key: str, current: str, target: str) -> bool:
    if current.strip().lower() == target.strip().lower():
        return True
    project = key.split("-", 1)[0]
    order = STATUS_ORDER.get(project) or {}
    cur_rank = order.get(current)
    tgt_rank = order.get(target)
    if cur_rank is None or tgt_rank is None:
        return False
    return cur_rank >= tgt_rank


def apply_transition(key: str, name: str, dry_run: bool) -> dict[str, Any]:
    current = issue_status(key)
    transitions = available_transitions(key)
    match = find_transition(transitions, name)
    if match is None:
        if current.strip().lower() == name.strip().lower():
            return {"key": key, "action": "skip", "reason": f"already {current}", "asked": name}
        available = [(t.get("name"), target_name(t)) for t in transitions]
        raise RuntimeError(f"{key}: no transition {name!r} from {current!r}; available {available}")
    dest = target_name(match)
    if should_skip(key, current, dest):
        return {"key": key, "action": "skip", "reason": f"already {current}", "asked": name, "to": dest}
    if dry_run:
        return {
            "key": key,
            "action": "dry-run",
            "from": current,
            "transition": match["name"],
            "id": match["id"],
            "to": dest,
        }
    jira.post(f"/rest/api/3/issue/{key}/transitions", {"transition": {"id": match["id"]}})
    after = issue_status(key)
    return {
        "key": key,
        "action": "transitioned",
        "from": current,
        "transition": match["name"],
        "id": match["id"],
        "to": after,
    }


def slack_payload(step: dict[str, Any], posted: dict[str, Any]) -> dict[str, Any] | None:
    parent_key = step.get("slack_parent_key")
    if not parent_key:
        return None
    parents = posted.get("parents") or {}
    parent = parents.get(parent_key)
    if not parent:
        raise RuntimeError(f"slack_parent_key {parent_key} missing from slack-posted.json parents")
    text = step.get("slack_text") or step.get("comment") or ""
    return {
        "channel_id": posted.get("channel_id"),
        "parent_key": parent_key,
        "thread_ts": parent.get("ts"),
        "url": parent.get("url"),
        "mention": step.get("slack_mention"),
        "message": text,
    }


def adf_text(body: Any) -> str:
    if isinstance(body, str):
        return body
    if not isinstance(body, dict):
        return str(body)
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "text":
                parts.append(str(node.get("text") or ""))
            for child in node.get("content") or []:
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(body)
    return "".join(parts)


def dump_issues(keys: list[str]) -> list[dict[str, Any]]:
    rows = []
    for key in keys:
        issue = jira.get(f"/rest/api/3/issue/{key}?fields=status,summary,comment")
        comments = issue["fields"].get("comment", {}).get("comments") or []
        last = comments[-1] if comments else None
        rows.append(
            {
                "key": key,
                "summary": issue["fields"].get("summary"),
                "status": issue["fields"]["status"]["name"],
                "last_comment_author": (last or {}).get("author", {}).get("displayName") if last else None,
                "last_comment": adf_text((last or {}).get("body")) if last else None,
            }
        )
    return rows


def run_playbook(playbook: dict[str, Any], posted: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    slack_out: list[dict[str, Any]] = []
    for step in playbook.get("steps") or []:
        key = step["key"]
        name = step.get("transition")
        if name:
            results.append(apply_transition(key, name, dry_run=dry_run))
        comment = step.get("comment")
        if comment:
            if dry_run:
                results.append({"key": key, "action": "dry-run-comment", "comment": comment})
            else:
                comment_jira.comment(key, comment)
                results.append({"key": key, "action": "commented", "comment": comment})
        payload = slack_payload(step, posted)
        if payload:
            slack_out.append(payload)
    return {"results": results, "slack": slack_out}


def playbook_keys(playbook: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    vdsd: set[str] = set()
    rnd: set[str] = set()
    slack_parents: set[str] = set()
    for step in playbook.get("steps") or []:
        key = step["key"]
        if key.startswith("VDSD-"):
            vdsd.add(key)
        elif key.startswith("RND-"):
            rnd.add(key)
        parent = step.get("slack_parent_key")
        if parent:
            slack_parents.add(parent)
    return vdsd, rnd, slack_parents


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-only", action="store_true")
    args = parser.parse_args()
    playbook = load_playbook()
    posted = load_slack_posted()
    vdsd, rnd, _ = playbook_keys(playbook)
    keys = sorted(vdsd | rnd, key=lambda k: (k.split("-")[0], int(k.split("-")[1])))
    if args.status_only:
        print(json.dumps(dump_issues(keys), indent=2))
        return 0
    out = run_playbook(playbook, posted, dry_run=args.dry_run)
    print(json.dumps(out, indent=2))
    if not args.dry_run:
        print("\n=== status after ===")
        print(json.dumps(dump_issues(keys), indent=2))
    print("\n=== slack copy (post via Slack MCP as Ted) ===")
    for payload in out["slack"]:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
