# Veridian Dynamics request intake

Control plane for customer (JSM **VDSD**) and engineering (**RND**) product/operational requests, GitHub engineering references (`RND-123`), and Slack `#dev-updates`. **VDV** is a leftover service desk and is not the engineering destination.

Always follow [`AGENTS.MD`](AGENTS.MD). Taxonomy lives in [`config/taxonomy.json`](config/taxonomy.json).

## Quick start

```bash
# 1. Classic API token as jira_admin_token (preferred) or jira_admin_veridian
python scripts/jira_client.py          # probe auth
python scripts/configure_jira.py       # create global custom fields
python scripts/associate_screens.py   # add fields to VDSD JSM screens
python scripts/associate_rnd_fields.py # associate the same fields with team-managed RND
python scripts/update_workflows.py    # Promote to Engineering + In Review
python scripts/seed_jsm_customers.py  # dummy orgs + plus-addressed customers on VDSD

# 2. Submit (local)
python scripts/submit_intake.py path/to/payload.json --source vdsd

# Or GitHub Actions → Submit intake (repo secrets JIRA_EMAIL + JIRA_API_TOKEN)
# gh workflow run submit-intake.yml -f source=vdsd -f payload="$(jq -c . payload.json)"

# 3. Promote to engineering (creates an RND Feature or Task)
python scripts/promote_request.py VDSD-123
```

Local form (dependent fields, PHI checkbox): open [`apps/intake/index.html`](apps/intake/index.html).

Public form (Lovable):

- Published: https://veridian-intake.lovable.app (`/customer`, `/internal`)
- Editor: https://lovable.dev/projects/f4958c29-f0e1-4e95-a908-1bb0c7975610
- The form validates and returns copyable JSON (no Jira token in the browser).
- Create the issue with **Actions → Submit intake** (`workflow_dispatch`) using repo secrets `JIRA_EMAIL` and `JIRA_API_TOKEN`. See [credentials](docs/credentials.md).

## Docs

- [taxonomy](docs/taxonomy.md)
- [JSM dummy orgs and customers](docs/jsm-customers.md)
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

PRs must include `RND-\d+` (legacy `VDV-\d+` still accepted). Templates: [`.github/pull_request_template.md`](.github/pull_request_template.md). Copy the same workflows into `m4ttsavage/DummyCompany` when that repository is writable (see [`github/DummyCompany/README.md`](github/DummyCompany/README.md)).
