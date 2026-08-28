# Credentials (names only)

Never commit values. Never put tokens in browser JavaScript or Lovable client code.

| Name | Where | Used for |
| --- | --- | --- |
| `jira_admin_token` | Cursor / cloud-agent secret | **Preferred** Jira REST admin token (classic `ATATT…`). Scripts read this first. |
| `jira_admin_veridian` | Cursor / cloud-agent secret | Fallback. The value injected in the first run was a scoped `ATCTT` token and returns HTTP 401. |
| `ATLASSIAN_EMAIL` | env | `matthewmsavage@gmail.com` |
| `ATLASSIAN_BASE_URL` | env | `https://veridian-dynamics.atlassian.net` |
| `ATLASSIAN_CLOUD_ID` | env | `2cddf272-587f-44fe-92ed-d157674c74f1` |
| `JSM_PROJECT_KEY` | env | `VDSD` |
| `JIRA_PROJECT_KEY` | env | `VDV` |
| Lovable secrets `ATLASSIAN_EMAIL` + `ATLASSIAN_API_TOKEN` | Lovable project settings | Server-side intake POST |
| GitHub Actions `JIRA_EMAIL` + `JIRA_API_TOKEN` | DummyCompany / this repo secrets | PR/release comments on VDV issues |
| `SLACK_BOT_TOKEN` | env (optional) | Watcher DMs if Slack MCP is down |
| Slack channel | n/a | `#dev-updates` / `C0BT787UKGS` |

## MCP

- Atlassian MCP: issue CRUD, links, transitions (`read:jira-work`, `write:jira-work`). Cannot create fields, SLAs, or workflows.
- GitHub MCP: authenticated as `m4ttsavage`. Cannot create new repos with this token (403). `m4ttsavage/DummyCompany` was not found; engineering templates and demo PRs live in this control-plane repo (`m4ttsavage/OL-workflow`).
- Slack MCP: ready. Posted parents/threads in `#dev-updates` and DMs to Ted Crisp. See [`docs/slack-backfill.md`](slack-backfill.md) and `config/slack-posted.json`.
- Lovable MCP: workspace “The Shadow Realm” (`748VhuycC5GCD4Pkhhb2`).
