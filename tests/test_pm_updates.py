import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pm_updates  # noqa: E402

PLAYBOOK = json.loads((ROOT / "config" / "pm-updates.json").read_text())
SLACK = json.loads((ROOT / "config" / "slack-posted.json").read_text())
USERS = json.loads((ROOT / "config" / "internal-users.json").read_text())


class PmUpdatesPlaybookTests(unittest.TestCase):
    def test_playbook_keys_and_slack_parents(self):
        vdsd, rnd, slack_parents = pm_updates.playbook_keys(PLAYBOOK)
        self.assertEqual(len(vdsd), 6, msg=sorted(vdsd))
        self.assertEqual(len(rnd), 3, msg=sorted(rnd))
        self.assertEqual(vdsd, {f"VDSD-{n}" for n in range(11, 17)})
        self.assertEqual(rnd, {"RND-7", "RND-8", "RND-9"})
        parents = SLACK.get("parents") or {}
        for key in slack_parents:
            self.assertIn(key, parents, msg=f"slack_parent_key {key} missing from slack-posted.json")
        self.assertEqual(slack_parents, vdsd)

    def test_ted_identity_is_comment_author(self):
        ted = next(u for u in USERS["users"] if u["id"] == "ted")
        self.assertEqual(ted["name"], "Ted Crisp")
        self.assertEqual(ted["jira_display_name"], "Ted Crisp")
        self.assertEqual(ted["slack_user_id"], "U0BTAN0LM3N")

    def test_find_transition_matches_name_or_target(self):
        transitions = [
            {"id": "81", "name": "Start", "to": {"name": "In Progress"}},
            {"id": "91", "name": "In review", "to": {"name": "Pending"}},
            {"id": "101", "name": "Resolved", "to": {"name": "Done"}},
        ]
        start = pm_updates.find_transition(transitions, "Start")
        self.assertEqual(start["id"], "81")
        pending = pm_updates.find_transition(transitions, "Pending")
        self.assertEqual(pending["id"], "91")
        done = pm_updates.find_transition(transitions, "Done")
        self.assertEqual(done["id"], "101")
        self.assertIsNone(pm_updates.find_transition(transitions, "Promote to Engineering"))

    def test_skip_does_not_walk_backwards(self):
        self.assertTrue(pm_updates.should_skip("RND-7", "Done", "To Do"))
        self.assertTrue(pm_updates.should_skip("RND-7", "Done", "Done"))
        self.assertFalse(pm_updates.should_skip("RND-8", "To Do", "In Progress"))
        self.assertTrue(pm_updates.should_skip("VDSD-11", "In Progress", "In Progress"))
        self.assertFalse(pm_updates.should_skip("VDSD-11", "To Do", "In Progress"))

    def test_recorded_run_and_slack_replies(self):
        ran = json.loads((ROOT / "config" / "pm-updates-ran.json").read_text())
        self.assertEqual(ran["author"], "Ted Crisp")
        keys = {row["key"] for row in ran["issues"]}
        self.assertEqual(keys, {f"VDSD-{n}" for n in range(11, 17)} | {"RND-7", "RND-8", "RND-9"})
        for row in ran["issues"]:
            self.assertEqual(row["last_comment_author"], "Ted Crisp")
        threads = SLACK.get("threads") or {}
        for n in range(11, 17):
            rec = threads[f"pm-VDSD-{n}"]
            self.assertEqual(rec["thread_of"], f"VDSD-{n}")
            self.assertTrue(rec.get("ts"))


if __name__ == "__main__":
    unittest.main()
