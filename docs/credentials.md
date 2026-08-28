# Credentials (names only)

Never commit values. Never put tokens in browser JavaScript or Lovable client code.

| Name | Where | Used for |
| --- | --- | --- |
| `jira_admin_veridian` | Cursor / cloud-agent secret | Jira REST admin (fields, SLAs, automation). Current token returns HTTP 401 against site REST; recreate a **classic** API token at https://id.atlassian.com/manage-profile/security/api-tokens and store it under the same name. |
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
- Slack MCP: connection error at implement time; Slack-for-Jira is already installed. Paste-ready backfill is in `docs/slack-backfill.md`. Retry MCP for DMs to Ted Crisp (`U0BTAN0LM3N`).
- Lovable MCP: workspace “The Shadow Realm” (`748VhuycC5GCD4Pkhhb2`).
