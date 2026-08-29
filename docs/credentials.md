# Credentials (names only)

Never commit values. Never put tokens in browser JavaScript.

| Name | Where | Used for |
| --- | --- | --- |
| `jira_admin_token` | Cursor / cloud-agent secret | **Preferred** Jira REST admin token (classic `ATATT…`). Scripts read this first. |
| `jira_admin_veridian` | Cursor / cloud-agent secret | Fallback. The value injected in the first run was a scoped `ATCTT` token and returns HTTP 401. |
| `ATLASSIAN_EMAIL` | env | `matthewmsavage@gmail.com` |
| `ATLASSIAN_BASE_URL` | env | `https://veridian-dynamics.atlassian.net` |
| `ATLASSIAN_CLOUD_ID` | env | `2cddf272-587f-44fe-92ed-d157674c74f1` |
| `JSM_PROJECT_KEY` | env | `VDSD` |
| `JIRA_PROJECT_KEY` | env | `RND` |
| GitHub Actions `JIRA_EMAIL` + `JIRA_API_TOKEN` | This repo Actions secrets | **Submit intake** workflow plus PR/release comments on RND issues |
| `SLACK_BOT_TOKEN` | env (optional) | Watcher DMs if Slack MCP is down |
| Slack channel | n/a | `#dev-updates` / `C0BT787UKGS` |

## Submit intake (operator path)

Customers use the [JSM portal](https://veridian-dynamics.atlassian.net/servicedesk/customer/portal/1). For operator seeding after copying JSON from `apps/intake/`:

1. Repo **Settings → Secrets and variables → Actions**: `JIRA_EMAIL` (`matthewmsavage@gmail.com`) and `JIRA_API_TOKEN` (classic `ATATT…` token).
2. **Actions → Submit intake → Run workflow**. Choose `vdsd` or `rnd` and paste the JSON (one line / minified is fine).
3. Or from a machine with `gh`:

```bash
gh workflow run submit-intake.yml -f source=vdsd -f payload="$(jq -c . payload.json)"
```

The workflow checks out this repo and runs `python scripts/submit_intake.py`. Only people who can run workflows on this repo can create issues this way.

## MCP

- Atlassian MCP: issue CRUD, links, transitions (`read:jira-work`, `write:jira-work`). Cannot create fields, SLAs, or workflows.
- GitHub MCP: authenticated as `m4ttsavage`. Cannot create new repos with this token (403). `m4ttsavage/DummyCompany` was not found; engineering templates and demo PRs live in this control-plane repo (`m4ttsavage/OL-workflow`).
- Slack MCP: ready. Posted parents/threads in `#dev-updates` and DMs to Ted Crisp. See [`docs/slack-backfill.md`](slack-backfill.md) and `config/slack-posted.json`.
