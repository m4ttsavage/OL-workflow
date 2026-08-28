# Workflows and SLAs

## VDSD (customer)

Target statuses:

`Submitted` → `Triage` → `Waiting for customer` | `In progress` | `Promote to Engineering` → `Resolved` → `Closed`

Live mapping on **SUP: Default ESM workflow for Jira Service Management** (used by issue type **Submit a request or incident**, id 10010):

| Desired | Live status | id | Transition |
| --- | --- | --- | --- |
| Submitted | **To Do** | 10011 | (initial Create) |
| Triage / In progress | **In Progress** | 3 | Start |
| Waiting for customer | **Pending** | 10013 | In review |
| Promote to Engineering | **Promote to Engineering** | 10020 | Promote to Engineering (from In Progress) |
| Resolved | **Done** | 10012 | Resolved |

`python scripts/update_workflows.py` added status **Promote to Engineering** and the transition from In Progress. Verified on **VDSD-7** (In Progress → transition 151).

Ask a question (10011) uses **SUP: Simple ESM**. Task (10013) uses **SUP: Jira Service Management default workflow**. Both now include **In Review** (id 10021). New customer intake via `submit_intake.py --source vdsd` creates **Submit a request or incident**, so Promote is on the path agents use.

### Promote to Engineering

When an agent transitions a VDSD issue to **Promote to Engineering** (or clicks the Automation trigger):

1. Create an **RND** issue: **Feature** when Intake Request Type is `Feature` or `New_Program_Launch`, otherwise **Task**.
2. Copy intake metadata (custom fields if present, else description table + labels). Do **not** copy native JSM Organizations (`customfield_10002`).
3. Set Source = `vdsd` on RND and Counterpart Key both ways.
4. Link with type **Polaris work item link**: RND `implements` VDSD / VDSD `is implemented by` RND.
   - `createIssueLink`: inwardIssue = VDSD key, outwardIssue = RND key, type = `Polaris work item link` (inward “is implemented by”, outward “implements”).
5. Copy reporter and watchers by email.

Automation rule JSON: [`automation/promote-to-rnd.json`](../automation/promote-to-rnd.json). Import under **Project settings → Automation** — REST create of Automation rules returns 401 (`scope does not match`). Runtime promote: `python scripts/promote_request.py VDSD-123` (copies custom fields, picks Feature vs Task, and writes Counterpart Key).

## RND (engineering)

Team-managed software project. Work types: Epic, Feature, Task, Subtask. Statuses are project-scoped (Idea / To Do / …). GitHub-for-Jira keys off `RND-n`, not status names.

GitHub PR open/merge comments on the RND issue; merge does not auto-transition.

Bidirectional: when RND moves to In Review or Done, comment on the linked VDSD issue. VDSD **Waiting for customer** does not move RND. Status-sync Automation is UI-import only (`automation/status-sync.json`).

## VDV (unused)

**Veridian Dynamics v2** remains as a leftover JSM project with earlier demo issues (VDV-1..5). Do not send new customer promotions there.

## SLAs (VDSD only)

Calendar: America/Chicago, Mon–Fri 09:00–17:00. **P1 uses 24×7**.

| Priority | Time to first response | Time to resolution |
| --- | --- | --- |
| P1 / Highest | 15 minutes | 4 hours |
| P2 / High | 1 hour | 8 hours |
| P3 / Medium | 4 hours | 3 business days |
| P4 / Low | 1 business day | 10 business days |

JSM SLA **create** APIs are not available with the classic API token via `api.atlassian.com` (legacy `/rest/servicedesk/1/.../sla` returns 401 `scope does not match`). `GET /rest/servicedeskapi/request/VDSD-1/sla` currently returns no goals.

Configure in **VDSD → Project settings → SLAs**. Attach both goals to all request types. Pause Time to resolution on Waiting for customer / Pending.

UI click-path: [`docs/ui-runbooks.md`](ui-runbooks.md).
