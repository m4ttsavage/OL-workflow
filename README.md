# Veridian Dynamics request intake

Control plane for customer (JSM **VDSD**) and internal (**VDV**) product/operational requests, GitHub engineering references (`VDV-123`), and Slack `#dev-updates`.

Always follow [`AGENTS.MD`](AGENTS.MD). Taxonomy lives in [`config/taxonomy.json`](config/taxonomy.json).

## Quick start

```bash
# 1. Classic API token as jira_admin_token (preferred) or jira_admin_veridian
python scripts/jira_client.py          # probe auth
python scripts/configure_jira.py       # create global custom fields
python scripts/associate_screens.py    # add fields to VDSD/VDV screens
python scripts/update_workflows.py    # Promote to Engineering + In Review

# 2. Submit
python scripts/submit_intake.py path/to/payload.json --source vdsd

# 3. Promote to engineering
python scripts/promote_request.py VDSD-123
```

Local form (dependent fields, PHI checkbox): open [`apps/intake/index.html`](apps/intake/index.html).

Public form (Lovable):

- Published: https://veridian-intake.lovable.app (`/customer`, `/internal`)
- Editor: https://lovable.dev/projects/f4958c29-f0e1-4e95-a908-1bb0c7975610
- Add secrets `ATLASSIAN_EMAIL` and `ATLASSIAN_API_TOKEN` (classic API token) so submit creates Jira issues. Until then, the form validates and returns a copyable JSON payload.

## Docs

- [taxonomy](docs/taxonomy.md)
- [fields](docs/fields.md)
- [workflows and SLAs](docs/workflows-and-slas.md)
- [integrations](docs/integrations.md)
- [credentials (names only)](docs/credentials.md)
- [UI runbook](docs/ui-runbooks.md)
- [Slack backfill copy](docs/slack-backfill.md)
- [API payloads](docs/api-payloads/)

## PHI

Jira, GitHub, Slack, and Lovable must not hold Protected Health Information. Customer intake requires an explicit acknowledgement.

## Engineering repo

PRs must include `VDV-\d+`. Templates: [`.github/pull_request_template.md`](.github/pull_request_template.md). Copy the same workflows into `m4ttsavage/DummyCompany` when that repository is writable (see [`github/DummyCompany/README.md`](github/DummyCompany/README.md)).
