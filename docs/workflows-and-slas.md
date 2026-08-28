# Workflows and SLAs

## VDSD (customer)

Target statuses:

`Submitted` → `Triage` → `Waiting for customer` | `In progress` | `Promote to Engineering` → `Resolved` → `Closed`

Observed on the live classic JSM workflow (August 2026):

| Desired | Live status today | Transition name |
| --- | --- | --- |
| Submitted | **To Do** (id 10011) or **Open** (id 1) depending on request type | (initial) |
| Triage / In progress | **In Progress** (id 3) | Start |
| Waiting for customer / In Review | **Pending** (id 10013) | In review |
| Promote to Engineering | **not present** — add this status (category In Progress) | add transition from In Progress |
| Resolved / Closed | add or map to JSM Resolved / Closed | |

Until **Promote to Engineering** exists, use `python scripts/promote_request.py VDSD-n` (or Atlassian MCP create + Polarise link). Live promotions already created VDV-1/3/4/5.

### Promote to Engineering

When an agent transitions a VDSD issue to **Promote to Engineering** (or clicks the Automation trigger):

1. Create a **VDV** issue (Task, unless Request Type is Incident or Question).
2. Copy intake metadata (custom fields if present, else description table + labels).
3. Set Source = `vdsd` on VDV and Counterpart Key both ways.
4. Link with type **Polaris work item link**: VDV `implements` VDSD / VDSD `is implemented by` VDV.
   - `createIssueLink`: inwardIssue = VDSD key, outwardIssue = VDV key, type = `Polaris work item link` (inward “is implemented by”, outward “implements”).
5. Copy reporter and watchers by email.

Automation rule JSON: [`automation/promote-to-vdv.json`](../automation/promote-to-vdv.json). Import under **Project settings → Automation** if REST create is unavailable. Runtime promote: `python scripts/promote_request.py VDSD-123`.

## VDV (internal engineering)

Target: `To Do` → `In Progress` → `In Review` → `Done`

Live mapping on the classic JSM workflow:

| Desired | Live status | Transition name |
| --- | --- | --- |
| To Do | **Open** (id 1) | (initial) |
| In Progress | **Work in progress** (id 10010) | Start progress |
| In Review | **Pending** (id 10013) | Pending |
| Done | **Done** (id 10012) | Mark as done |

Do not rename statuses in the first pass; GitHub-for-Jira keys off `VDV-n`, not status names. Optional: add a status named **In Review** if you want the name to match the software workflow. GitHub PR open/merge comments on the VDV issue; merge does not auto-transition.

Bidirectional: when VDV moves to In Review or Done, comment on the linked VDSD issue. VDSD **Waiting for customer** does not move VDV.

## SLAs (VDSD only)

Calendar: America/Chicago, Mon–Fri 09:00–17:00. **P1 uses 24×7**.

| Priority | Time to first response | Time to resolution |
| --- | --- | --- |
| P1 / Highest | 15 minutes | 4 hours |
| P2 / High | 1 hour | 8 hours |
| P3 / Medium | 4 hours | 3 business days |
| P4 / Low | 1 business day | 10 business days |

Configure in **VDSD → Project settings → SLAs**. Attach both goals to all request types. Pause Time to resolution on Waiting for customer.

UI click-path: [`docs/ui-runbooks.md`](ui-runbooks.md).
