# Integrations

```
Customer form → VDSD → (promote) → VDV → GitHub DummyCompany
                 \                      /
                  → Slack #dev-updates (+ watcher DMs)
```

## JSM ↔ VDV

- Stay in VDSD until triage. Only engineering-bound work is promoted.
- Link type: **Polaris work item link** (`implements` / `is implemented by`).
- Counterpart Key + labels `source:*`.
- Script: `scripts/promote_request.py`.
- Automation import: `automation/promote-to-vdv.json`.

## GitHub

Target repo: `m4ttsavage/DummyCompany` — **does not exist**, and GitHub MCP (`m4ttsavage`) returns **403** on `user/repos` create (`Resource not accessible by personal access token`). Engineering templates and demo PRs live in this control-plane repo (`m4ttsavage/OL-workflow`) until DummyCompany is created under that account.

- Branch: `VDV-123-short-slug`
- PR template requires `Jira: VDV-123` and optional `JSM: VDSD-45`
- Workflow `.github/workflows/jira-key-required.yml` fails PRs without `VDV-\d+`
- Workflow `.github/workflows/jira-comment.yml` comments on the VDV issue on PR open/merge and on release
- GitHub-for-Jira is already installed; map the engineering repo to **VDV**

## Slack

- Channel `#dev-updates` (`C0BT787UKGS`)
- Slack-for-Jira already installed (unfurls)
- Parent message per issue key; later events reply in-thread
- Watcher DMs by matching Jira watcher/reporter email to Slack users
- Templates: `docs/api-payloads/slack-parent.json`, `scripts/notify_slack.py`
- Slack MCP was unavailable at implement time; retry `slack_send_message` when the server is healthy

## Lovable intake

Public pages (workspace The Shadow Realm, project **Veridian Intake Hub**):

- Editor: https://lovable.dev/projects/f4958c29-f0e1-4e95-a908-1bb0c7975610
- Preview: https://id-preview--f4958c29-f0e1-4e95-a908-1bb0c7975610.lovable.app
- Published: https://veridian-intake.lovable.app
- `/customer` → VDSD
- `/internal` → VDV

Add Lovable secrets `ATLASSIAN_EMAIL` and `ATLASSIAN_API_TOKEN`. Local fallback forms: `apps/intake/`.

## MCP and skills

| System | MCP | Role |
| --- | --- | --- |
| Atlassian | ready | Issue create/edit/link/transition |
| GitHub | ready as m4ttsavage | Files, PRs; cannot create DummyCompany (403) |
| Slack | error at implement | DMs / channel posts |
| Lovable | ready | Public intake UX |

Admin field/SLA/workflow create needs a working classic API token (`jira_admin_veridian` currently 401).
