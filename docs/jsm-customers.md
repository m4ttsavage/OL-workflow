# Dummy JSM organizations and customers

Source: [`config/jsm-customers.json`](../config/jsm-customers.json). Seed (idempotent):

```bash
python scripts/seed_jsm_customers.py
```

Creates six brand **Organizations** on VDSD (service desk id 1) and two **customers** per org. Each customer email is a Gmail plus-alias of `matthewmsavage@gmail.com`, so Jira treats them as unique portal registrations and mail still arrives in one inbox.

Live IDs after a successful seed: [`config/jsm-customers-created.json`](../config/jsm-customers-created.json). Intake payloads set native Organizations (`customfield_10002`) from that file.

A second batch of VDSD payloads is in [`config/seed-requests-batch-2.json`](../config/seed-requests-batch-2.json) (Cedar Ridge, Summit Peak, plus Lumen/Atlas follow-ups). Each item lists internal watchers from [`config/internal-users.json`](../config/internal-users.json). Half are flagged `promote: true` for RND.

```bash
python scripts/seed_demo.py --file config/seed-requests-batch-2.json
python scripts/promote_request.py VDSD-n   # for each promote: true key
python scripts/watchers.py VDSD-n ted,linda
```

Creating a customer sends a JSM portal invite to the plus-address.
