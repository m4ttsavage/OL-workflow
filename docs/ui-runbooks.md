# Jira / JSM UI runbook (admin)

Use this when REST admin calls fail (scoped API token 401). Site: https://veridian-dynamics.atlassian.net

## Shared custom fields (Settings → Issues → Custom fields)

Create each field in [fields.md](fields.md), Context = Apply to all issues, then **Associate to screens** for both **VDSD** and **VDV** (Default/Create/Edit/View).

Select options must match IDs in `config/taxonomy.json`.

## VDSD request types (Project settings → Request types)

Keep native portal types as fallback. Add portal request types that match taxonomy **labels** (not IDs):

Feature, Bug, Incident, Operational change, Access, Question, Compliance, New program launch, Pharmacy / fulfillment, Clinical operations, Internal IT.

Portal URL: **VDSD → Channels → Portal**. Internal users use Lovable `/internal` (and can also use the VDV portal).

Issue types on both classic projects today: Submit a request or incident, Ask a question, Emailed request, Task, Sub-task. Feature/Bug are **intake request types** (labels + description table), not extra Jira issue types, until you add them in the UI.

## VDSD workflow

Project settings → Workflows → edit. Add status **Promote to Engineering**. Add transition from In progress / Triage to that status, then to Resolved.

## VDV workflow

Add **In Review** between In Progress and Done.

## SLAs (VDSD → Project settings → SLAs)

Create calendar **Veridian Business Hours** (America/Chicago 09:00–17:00 Mon–Fri) and **24x7**.

| Goal | Calendar | P1 | P2 | P3 | P4 |
| --- | --- | --- | --- | --- | --- |
| Time to first response | 24x7 for P1, business otherwise | 15m | 1h | 4h | 1d |
| Time to resolution | same | 4h | 8h | 3d | 10d |

## Automation

Project settings → Automation → Import:

1. `automation/promote-to-vdv.json`
2. `automation/status-sync.json`
3. `automation/slack-notify.json` (channel `#dev-updates`)

## GitHub for Jira

Already installed. Connect repository `m4ttsavage/DummyCompany` (or this repo until that exists) to project **VDV**.

## Slack for Jira

Already installed. Confirm `#dev-updates` can receive issue unfurls.
