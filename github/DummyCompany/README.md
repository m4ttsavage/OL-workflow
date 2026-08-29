# DummyCompany (engineering)

This folder is the portable copy of `m4ttsavage/DummyCompany`.

GitHub MCP authenticated as `m4ttsavage` cannot create that repository (HTTP 403, `Resource not accessible by personal access token`). Until the repo exists, this control-plane repository (`m4ttsavage/OL-workflow`) hosts:

- `.github/pull_request_template.md` (requires `Jira: RND-123`; legacy `VDV-123` still accepted)
- `.github/workflows/jira-key-required.yml`
- `.github/workflows/jira-comment.yml`
- Demo feature notes under `features/`
- `CHANGELOG.md` for the v0.1.0 demo release

## Conventions

- Branch: `RND-{n}-{short-slug}` (cloud agents also suffix `-05cc` when required)
- PR title: `[RND-{n}] …`
- PR body includes `Jira: RND-{n}` and `JSM: VDSD-{n}` when promoted from customer intake
- GitHub-for-Jira should map this repo (and DummyCompany later) to project **RND**
- Existing demo PRs keyed to **VDV** remain valid
