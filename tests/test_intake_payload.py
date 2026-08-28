import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import intake_payload  # noqa: E402
import jsm_customers  # noqa: E402

SEED = json.loads((ROOT / "config" / "seed-requests.json").read_text())
BATCH2 = json.loads((ROOT / "config" / "seed-requests-batch-2.json").read_text())
JSM = json.loads((ROOT / "config" / "jsm-customers.json").read_text())
TAX = json.loads((ROOT / "config" / "taxonomy.json").read_text())


class IntakePayloadTests(unittest.TestCase):
    def test_seed_payloads_validate(self):
        for item in SEED + BATCH2:
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
            "requester_email": "matthewmsavage+harbor-peak-health-ops@gmail.com",
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
        self.assertEqual(fields["customfield_10079"], "matthewmsavage+northstar-wellness@gmail.com")
        self.assertEqual(fields["customfield_10080"], {"id": "10049"})
        self.assertEqual(fields["customfield_10082"], {"id": "10062"})
        self.assertEqual(fields["customfield_10088"], {"id": "10141"})
        self.assertEqual(fields["customfield_10090"], {"id": "10143"})
        self.assertEqual(fields["customfield_10086"], 240000.0)
        self.assertEqual(fields["customfield_10002"], [{"id": "1"}])

    def test_resolve_source(self):
        import submit_intake

        self.assertEqual(submit_intake.resolve_source({"source": "vdsd"}, None), "vdsd")
        self.assertEqual(submit_intake.resolve_source({}, "rnd"), "rnd")
        self.assertEqual(submit_intake.resolve_source({}, "vdv"), "vdv")
        self.assertIsNone(submit_intake.resolve_source({}, None))

    def test_engineering_issue_types(self):
        self.assertEqual(intake_payload.engineering_issue_type("Feature"), "Feature")
        self.assertEqual(intake_payload.engineering_issue_type("New_Program_Launch"), "Feature")
        self.assertEqual(intake_payload.engineering_issue_type("Compliance"), "Task")
        self.assertEqual(intake_payload.engineering_issue_type("Bug"), "Task")
        self.assertEqual(intake_payload.project_key("vdsd"), "VDSD")
        self.assertEqual(intake_payload.project_key("rnd"), "RND")
        self.assertEqual(intake_payload.project_key("vdv"), "VDV")

    def test_internal_maps_to_rnd_without_jsm_org(self):
        payload = SEED[0]["payload"]
        fields = intake_payload.jira_fields(payload, "rnd")
        self.assertEqual(fields["project"]["key"], "RND")
        self.assertEqual(fields["issuetype"]["name"], "Feature")
        self.assertEqual(fields["customfield_10078"], "Ava Chen")
        self.assertNotIn("customfield_10002", fields)
        self.assertEqual(fields["customfield_10088"], {"id": "10147"})
        self.assertIn("source:rnd", intake_payload.labels(payload, "rnd"))

    def test_compliance_internal_is_task(self):
        payload = dict(SEED[7]["payload"])
        fields = intake_payload.jira_fields(payload, "rnd")
        self.assertEqual(fields["issuetype"]["name"], "Task")
        self.assertEqual(fields["project"]["key"], "RND")


class JsmCustomerTests(unittest.TestCase):
    def test_plus_email(self):
        self.assertEqual(
            jsm_customers.plus_email("northstar-wellness"),
            "matthewmsavage+northstar-wellness@gmail.com",
        )
        self.assertEqual(
            jsm_customers.plus_email("+Cedar-Ridge-Telehealth-ops"),
            "matthewmsavage+cedar-ridge-telehealth-ops@gmail.com",
        )

    def test_plus_email_rejects_bad_tag(self):
        with self.assertRaises(ValueError):
            jsm_customers.plus_email("not an email")

    def test_config_validates(self):
        self.assertEqual(jsm_customers.validate_config(JSM), [])

    def test_org_slugs_match_taxonomy(self):
        tax_customer = [name for name in TAX["organizations"]["customer"] if name != "Other"]
        config_names = [org["name"] for org in JSM["organizations"]]
        self.assertEqual(sorted(tax_customer), sorted(config_names))
        for org in JSM["organizations"]:
            self.assertEqual(org["slug"], jsm_customers.org_slug(org["name"]))

    def test_seed_emails_are_plus_aliases(self):
        by_name = {
            (org["name"], customer["display_name"]): jsm_customers.customer_email(customer, org)
            for org in JSM["organizations"]
            for customer in org["customers"]
        }
        for item in SEED + BATCH2:
            payload = item["payload"]
            if item["source"] != "vdsd":
                continue
            email = by_name[(payload["organization"], payload["requester_name"])]
            self.assertEqual(payload["requester_email"], email)
            self.assertTrue(payload["requester_email"].startswith("matthewmsavage+"))
            self.assertTrue(payload["requester_email"].endswith("@gmail.com"))
            self.assertIn(jsm_customers.org_slug(payload["organization"]), payload["requester_email"])


if __name__ == "__main__":
    unittest.main()
