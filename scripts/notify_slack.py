#!/usr/bin/env python3
"""Post a #dev-updates parent (or thread reply) for a Jira issue.

Uses SLACK_BOT_TOKEN if set. Channel default C0BT787UKGS (#dev-updates).
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.request

CHANNEL = os.environ.get("SLACK_DEV_UPDATES_CHANNEL_ID", "C0BT787UKGS")
TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")


def slack(method: str, body: dict) -> dict:
    if not TOKEN:
        raise SystemExit("Set SLACK_BOT_TOKEN or use Slack MCP slack_send_message")
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    if not data.get("ok"):
        raise RuntimeError(data)
    return data


def message_text(key: str, summary: str, extra: str = "") -> str:
    url = f"https://veridian-dynamics.atlassian.net/browse/{key}"
    text = f"*{key}* — {summary}\n{url}"
    if extra:
        text += f"\n{extra}"
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    parser.add_argument("summary")
    parser.add_argument("--thread-ts")
    parser.add_argument("--extra", default="")
    parser.add_argument("--dm-user")
    args = parser.parse_args()
    text = message_text(args.key, args.summary, args.extra)
    body = {"channel": CHANNEL, "text": text}
    if args.thread_ts:
        body["thread_ts"] = args.thread_ts
    posted = slack("chat.postMessage", body)
    print("ts", posted.get("ts"), "channel", posted.get("channel"))
    if args.dm_user:
        slack("chat.postMessage", {"channel": args.dm_user, "text": text})
        print("dm", args.dm_user)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
