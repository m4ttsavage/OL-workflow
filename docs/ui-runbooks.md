# Jira / JSM UI runbook (admin)

Site: https://veridian-dynamics.atlassian.net

## Done via REST (`jira_admin_token`)

- Global custom fields + options: `python scripts/configure_jira.py`
- Screens (SUP 10010/10011/10012, shared by VDSD and VDV): `python scripts/associate_screens.py`
- Workflows: `python scripts/update_workflows.py`
  - **Promote to Engineering** on SUP Default ESM (Submit a request)
  - **In Review** on SUP JSM default (Task) and Simple ESM (Ask a question)

## Still UI-only (REST 401 / no write API)

### VDSD request types (Project settings → Request types)

`GET /rest/servicedeskapi/servicedesk/1/requesttype` works (Ask a question, Submit a request or incident, Emailed request). `POST` to create types returns **401 scope does not match**.

Keep native portal types as fallback. Add portal request types that match taxonomy **labels** (not IDs):

Feature, Bug, Incident, Operational change, Access, Question, Compliance, New program launch, Pharmacy / fulfillment, Clinical operations, Internal IT.

Portal (customer submission UX): https://veridian-dynamics.atlassian.net/servicedesk/customer/portal/1 — **VDSD → Channels → Portal**. Internal employees file in project **VDV**. Intake Request Type on the issue is the taxonomy select (`customfield_10082`), independent of portal request type.

### SLAs (VDSD → Project settings → SLAs)

Create calendar **Veridian Business Hours** (America/Chicago 09:00–17:00 Mon–Fri) and **24x7**.

| Goal | Calendar | P1 | P2 | P3 | P4 |
| --- | --- | --- | --- | --- | --- |
| Time to first response | 24x7 for P1, business otherwise | 15m | 1h | 4h | 1d |
| Time to resolution | same | 4h | 8h | 3d | 10d |

### Automation

Project settings → Automation → Create / Import (JSON import may be rejected; recreate steps):

1. `automation/promote-to-vdv.json` — trigger: transitioned to **Promote to Engineering**
2. `automation/status-sync.json`
3. `automation/slack-notify.json` (channel `#dev-updates`)

Until Automation is imported, use `python scripts/promote_request.py VDSD-n`.

## GitHub for Jira

Already installed. Connect repository `m4ttsavage/DummyCompany` (or this repo until that exists) to project **VDV**.

## Slack for Jira

Already installed. Confirm `#dev-updates` can receive issue unfurls.
