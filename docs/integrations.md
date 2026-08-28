# Integrations

```
JSM portal → VDSD → (promote) → VDV → GitHub DummyCompany
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
- Posted 2026-08-28: parents for VDSD-1, VDSD-2, VDSD-7, VDV-2, VDV-4; promotion/GitHub replies in-thread. Record: [`config/slack-posted.json`](../config/slack-posted.json)
- Watcher DM: Ted Crisp (`U0BTAN0LM3N` / `matthewmsavage@gmail.com`) — the only Slack user who also exists in Jira
- Four more Slack users are in `#dev-updates` (Lem, Veronica, Phil, Linda) but have **no Jira accounts yet**, so they cannot be added as issue watchers. Invite them to the Atlassian site to enable email-match DMs.

## JSM portal intake

Customers submit in the VDSD Help Center (service desk id `1`):

- Portal: https://veridian-dynamics.atlassian.net/servicedesk/customer/portal/1
- Request types live under **VDSD → Channels → Portal** (see [`docs/ui-runbooks.md`](ui-runbooks.md))
- Internal employees file in project **VDV**

Operator fallback (not public): local form [`apps/intake/`](../apps/intake/) plus **Actions → Submit intake** (`workflow_dispatch`) with repo secrets `JIRA_EMAIL` + `JIRA_API_TOKEN`.

## MCP and skills

| System | MCP | Role |
| --- | --- | --- |
| Atlassian | ready | Issue create/edit/link/transition |
| GitHub | ready as m4ttsavage | Files, PRs; cannot create DummyCompany (403) |
| Slack | error at implement | DMs / channel posts |

Admin field/SLA/workflow create needs a working classic API token (`jira_admin_token` via `api.atlassian.com/ex/jira/{cloudId}`). Fields, screens, and workflows are configured. Portal request types, SLAs, and Automation import remain UI (REST 401).
