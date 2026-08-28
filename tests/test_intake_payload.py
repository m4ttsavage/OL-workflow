import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import intake_payload  # noqa: E402

SEED = json.loads((ROOT / "config" / "seed-requests.json").read_text())


class IntakePayloadTests(unittest.TestCase):
    def test_seed_payloads_validate(self):
        for item in SEED:
            errors = intake_payload.validate(item["payload"], item["source"])
            self.assertEqual(errors, [], msg=item["payload"]["summary"])

    def test_customer_requires_phi_ack(self):
        payload = dict(SEED[0]["payload"])
        payload["no_phi_ack"] = False
        errors = intake_payload.validate(payload, "vdsd")
        self.assertTrue(any("no_phi_ack" in e for e in errors))

    def test_access_skips_program(self):
        payload = {
            "requester_name": "Pat",
            "requester_email": "pat@example.com",
            "organization": "Harbor Peak Health",
            "request_type": "Access",
            "impact_bucket": "Operations",
            "priority": "P3",
            "summary": "Add a brand admin",
            "description": "Portal access for a work email. No patient records.",
            "no_phi_ack": True,
        }
        self.assertEqual(intake_payload.validate(payload, "vdsd"), [])

    def test_revenue_requires_value(self):
        payload = dict(SEED[0]["payload"])
        payload.pop("business_value_usd")
        payload.pop("value_type")
        errors = intake_payload.validate(payload, "vdsd")
        self.assertTrue(any("business_value_usd" in e for e in errors))
        self.assertTrue(any("value_type" in e for e in errors))

    def test_phi_pattern_rejected(self):
        payload = dict(SEED[0]["payload"])
        payload["description"] = "Patient MRN 123 and date of birth attached."
        errors = intake_payload.validate(payload, "vdsd")
        self.assertTrue(any("PHI" in e for e in errors))

    def test_labels_and_adf(self):
        payload = SEED[0]["payload"]
        labs = intake_payload.labels(payload, "vdsd")
        self.assertIn("source:vdsd", labs)
        self.assertIn("type:Feature", labs)
        fields = intake_payload.jira_fields(payload, "vdsd")
        self.assertEqual(fields["project"]["key"], "VDSD")
        self.assertEqual(fields["description"]["type"], "doc")
        self.assertEqual(fields["priority"]["name"], "High")
        self.assertEqual(fields["customfield_10078"], "Ava Chen")
        self.assertEqual(fields["customfield_10079"], "ava.chen@northstar.example")
        self.assertEqual(fields["customfield_10080"], {"id": "10049"})
        self.assertEqual(fields["customfield_10082"], {"id": "10062"})
        self.assertEqual(fields["customfield_10088"], {"id": "10141"})
        self.assertEqual(fields["customfield_10090"], {"id": "10143"})
        self.assertEqual(fields["customfield_10086"], 240000.0)

    def test_resolve_source(self):
        import submit_intake

        self.assertEqual(submit_intake.resolve_source({"source": "vdsd"}, None), "vdsd")
        self.assertEqual(submit_intake.resolve_source({}, "vdv"), "vdv")
        self.assertIsNone(submit_intake.resolve_source({}, None))


if __name__ == "__main__":
    unittest.main()
