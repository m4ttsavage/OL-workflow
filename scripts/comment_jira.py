#!/usr/bin/env python3
"""Post an ADF comment on a Jira issue (GitHub workflow stand-in)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_client as jira  # noqa: E402


def comment(key: str, text: str) -> None:
    jira.post(
        f"/rest/api/3/issue/{key}/comment",
        {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
            }
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    parser.add_argument("text")
    args = parser.parse_args()
    comment(args.key, args.text)
    print(args.key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
