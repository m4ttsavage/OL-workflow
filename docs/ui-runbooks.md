# Jira / JSM UI runbook (admin)

Site: https://veridian-dynamics.atlassian.net

## Done via REST (`jira_admin_token`)

- Global custom fields + options: `python scripts/configure_jira.py`
- VDSD screens (SUP 10010/10011/10012): `python scripts/associate_screens.py`
- RND field association (team-managed, no classic screens): `python scripts/associate_rnd_fields.py`
- Workflows: `python scripts/update_workflows.py`
  - **Promote to Engineering** on SUP Default ESM (Submit a request)
  - **In Review** on SUP JSM default (Task) and Simple ESM (Ask a question)

## RND Fields page

https://veridian-dynamics.atlassian.net/jira/software/projects/RND/settings/fields

`associate_rnd_fields.py` lets REST **set** the 13 intake fields on Feature and Task. The Fields / work-type layout table can still look empty until an admin pins those fields on the Feature and Task layouts in the UI. Values already stored on an issue remain after that pin.

Do **not** add native JSM fields (Organizations `customfield_10002`, Request Type `customfield_10010`, request participants) to RND.

## Still UI-only (REST 401 / no write API)

### VDSD request types (Project settings → Request types)

`GET /rest/servicedeskapi/servicedesk/1/requesttype` works (Ask a question, Submit a request or incident, Emailed request). `POST` to create types returns **401 scope does not match**.

Keep native portal types as fallback. Add portal request types that match taxonomy **labels** (not IDs):

Feature, Bug, Incident, Operational change, Access, Question, Compliance, New program launch, Pharmacy / fulfillment, Clinical operations, Internal IT.

Portal (customer submission UX): https://veridian-dynamics.atlassian.net/servicedesk/customer/portal/1 — **VDSD → Channels → Portal**. Internal employees file in project **RND**. Intake Request Type on the issue is the taxonomy select (`customfield_10082`), independent of portal request type.

### SLAs (VDSD → Project settings → SLAs)

Create calendar **Veridian Business Hours** (America/Chicago 09:00–17:00 Mon–Fri) and **24x7**.

| Goal | Calendar | P1 | P2 | P3 | P4 |
| --- | --- | --- | --- | --- | --- |
| Time to first response | 24x7 for P1, business otherwise | 15m | 1h | 4h | 1d |
| Time to resolution | same | 4h | 8h | 3d | 10d |

### Automation

Project settings → Automation → Create / Import (JSON import may be rejected; recreate steps):

1. `automation/promote-to-rnd.json` — trigger: transitioned to **Promote to Engineering**
2. `automation/status-sync.json`
3. `automation/slack-notify.json` (channel `#dev-updates`)

Until Automation is imported, use `python scripts/promote_request.py VDSD-n`.

## Dummy JSM organizations and customers

`python scripts/seed_jsm_customers.py` creates (or reuses) the six brand Organizations on **VDSD** and two portal customers per org. Emails are Gmail plus-aliases of `matthewmsavage@gmail.com` so each registration is unique and still delivers to the same inbox.

| Organization | Primary | Ops / second contact |
| --- | --- | --- |
| Northstar Wellness | `matthewmsavage+northstar-wellness@gmail.com` | `…+northstar-wellness-ops@gmail.com` |
| Harbor Peak Health | `matthewmsavage+harbor-peak-health@gmail.com` | `…+harbor-peak-health-ops@gmail.com` |
| Lumen Clinic | `matthewmsavage+lumen-clinic@gmail.com` | `…+lumen-clinic-ops@gmail.com` |
| Atlas Fitness Care | `matthewmsavage+atlas-fitness-care@gmail.com` | `…+atlas-fitness-care-compliance@gmail.com` |
| Cedar Ridge Telehealth | `matthewmsavage+cedar-ridge-telehealth@gmail.com` | `…+cedar-ridge-telehealth-ops@gmail.com` |
| Summit Peak Wellness | `matthewmsavage+summit-peak-wellness@gmail.com` | `…+summit-peak-wellness-ops@gmail.com` |

Ready-to-submit payloads for the next batch: [`config/seed-requests-batch-2.json`](../config/seed-requests-batch-2.json). Do **not** seed those until you want live VDSD issues. Creating customers sends portal invites to the plus-addresses.

## GitHub for Jira

Already installed. Connect repository `m4ttsavage/DummyCompany` (or this repo until that exists) to project **RND**.

## Slack for Jira

Already installed. Confirm `#dev-updates` can receive issue unfurls.
