# Dummy JSM organizations and customers

Source: [`config/jsm-customers.json`](../config/jsm-customers.json). Seed (idempotent):

```bash
python scripts/seed_jsm_customers.py
```

Creates six brand **Organizations** on VDSD (service desk id 1) and two **customers** per org. Each customer email is a Gmail plus-alias of `matthewmsavage@gmail.com`, so Jira treats them as unique portal registrations and mail still arrives in one inbox.

Live IDs after a successful seed: [`config/jsm-customers-created.json`](../config/jsm-customers-created.json). Intake payloads set native Organizations (`customfield_10002`) from that file.

A second batch of **unsubmitted** VDSD payloads is in [`config/seed-requests-batch-2.json`](../config/seed-requests-batch-2.json). Submit later with `python scripts/seed_demo.py` after pointing it at that file, or `python scripts/submit_intake.py` per payload.

Creating a customer sends a JSM portal invite to the plus-address.
