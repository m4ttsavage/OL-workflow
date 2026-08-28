# DummyCompany (engineering)

This folder is the portable copy of `m4ttsavage/DummyCompany`.

GitHub MCP authenticated as `m4ttsavage` cannot create that repository (HTTP 403, `Resource not accessible by personal access token`). Until the repo exists, this control-plane repository (`m4ttsavage/OL-workflow`) hosts:

- `.github/pull_request_template.md` (requires `Jira: VDV-123`)
- `.github/workflows/jira-key-required.yml`
- `.github/workflows/jira-comment.yml`
- Demo feature notes under `features/`
- `CHANGELOG.md` for the v0.1.0 demo release

## Conventions

- Branch: `VDV-{n}-{short-slug}` (cloud agents also suffix `-ed09` when required)
- PR title: `[VDV-{n}] …`
- PR body includes `Jira: VDV-{n}` and `JSM: VDSD-{n}` when promoted from customer intake
- GitHub-for-Jira should map this repo (and DummyCompany later) to project **VDV**
