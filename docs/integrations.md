# Integrations

```
Customer form → VDSD → (promote) → RND → GitHub DummyCompany
                 \                      /
                  → Slack #dev-updates (+ watcher DMs)

Internal form → RND
```

**VDV** (Veridian Dynamics v2) is a leftover JSM project. Do not promote customer work there.

## JSM ↔ RND

- Stay in VDSD until triage. Only engineering-bound work is promoted.
- Link type: **Polaris work item link** (`implements` / `is implemented by`).
- Counterpart Key + labels `source:*`.
- Script: `scripts/promote_request.py` (Feature or New program launch → RND **Feature**; everything else → **Task**).
- Automation import: `automation/promote-to-rnd.json` (always Task if imported as-is; prefer the script for work-type mapping and custom fields).

## GitHub

Target repo: `m4ttsavage/DummyCompany` — **does not exist**, and GitHub MCP (`m4ttsavage`) returns **403** on `user/repos` create (`Resource not accessible by personal access token`). Engineering templates and demo PRs live in this control-plane repo (`m4ttsavage/OL-workflow`) until DummyCompany is created under that account.

- Branch: `RND-123-short-slug`
- PR template requires `Jira: RND-123` and optional `JSM: VDSD-45`
- Workflow `.github/workflows/jira-key-required.yml` fails PRs without `RND-\d+` (legacy `VDV-\d+` still passes)
- Workflow `.github/workflows/jira-comment.yml` comments on the RND (or legacy VDV) issue on PR open/merge and on release
- GitHub-for-Jira is already installed; map the engineering repo to **RND**

## Slack

- Channel `#dev-updates` (`C0BT787UKGS`)
- Slack-for-Jira already installed (unfurls)
- Posted 2026-08-28: parents for VDSD-1, VDSD-2, VDSD-7, VDV-2, VDV-4; promotion/GitHub replies in-thread. Record: [`config/slack-posted.json`](../config/slack-posted.json)
- Watcher DM: Ted Crisp (`U0BTAN0LM3N` / `matthewmsavage@gmail.com`) — the only Slack user who also exists in Jira
- Four more Slack users are in `#dev-updates` (Lem, Veronica, Phil, Linda) but have **no Jira accounts yet**, so they cannot be added as issue watchers. Invite them to the Atlassian site to enable email-match DMs.

## Lovable intake

Public pages (workspace The Shadow Realm, project **Veridian Intake Hub**):

- Editor: https://lovable.dev/projects/f4958c29-f0e1-4e95-a908-1bb0c7975610
- Preview: https://id-preview--f4958c29-f0e1-4e95-a908-1bb0c7975610.lovable.app
- Published: https://veridian-intake.lovable.app
- `/customer` → VDSD
- `/internal` → RND (update the published form if it still labels VDV)

The published form validates and returns copyable JSON. Create the Jira issue with **Actions → Submit intake** (`workflow_dispatch`) and repo secrets `JIRA_EMAIL` + `JIRA_API_TOKEN` — do not put the token in Lovable. Local fallback forms: `apps/intake/`.

## MCP and skills

| System | MCP | Role |
| --- | --- | --- |
| Atlassian | ready | Issue create/edit/link/transition |
| GitHub | ready as m4ttsavage | Files, PRs; cannot create DummyCompany (403) |
| Slack | error at implement | DMs / channel posts |
| Lovable | ready | Public intake UX |

Admin field/SLA/workflow create needs a working classic API token (`jira_admin_token` via `api.atlassian.com/ex/jira/{cloudId}`). Fields, screens, and workflows are configured. Portal request types, SLAs, and Automation import remain UI (REST 401).
