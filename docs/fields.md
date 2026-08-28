# Custom fields (VDSD and VDV)

Create **once as global fields**, then add them to screens on both classic projects. **No prefixes.** Jira will assign `customfield_xxxxx` IDs; record them in the table at the bottom after `scripts/configure_jira.py` succeeds.

Native JSM already has a field named **Request Type** (`customfield_10010`) for portal request types. Our taxonomy field is a separate select named **Intake Request Type** in Jira (display still “Request Type” on the public forms). Native **Organizations** (`customfield_10002`) is the JSM customer-org picker; our **Organization** field is a brand/department select.

## Field definitions

| Display name | Type | Required | Notes |
| --- | --- | --- | --- |
| Requester Name | Text | always | |
| Requester Email | Text | always | Work email only |
| Organization | Select | always | Options from taxonomy; plus Other |
| Organization Other | Text | when Organization = Other | |
| Intake Request Type | Select | always | Taxonomy Request Type IDs |
| Clinical Program | Select | unless type is Access or Internal_IT | |
| Subprogram | Select | unless program is Platform / Cross_Program / NA | All subprogram options in one context; intake UX filters |
| Impact Bucket | Select | always | |
| Business Value USD | Number | when impact is Revenue or Cost | Annualized USD |
| Value Type | Select | with Business Value USD | |
| Source | Select | system | `vdsd` or `vdv` |
| Counterpart Key | Text | system | Linked issue key after promote |
| No PHI Acknowledgement | Checkbox / Select Yes-No | customer form | Must be Yes |

Priority uses **native Priority** (Highest/High/Medium/Low).

## Dependent rules

1. If Request Type is `Access` or `Internal_IT`, hide Clinical Program and Subprogram.
2. If Clinical Program is `Cross_Program` or `NA`, hide Subprogram.
3. If Clinical Program is `Platform`, Subprogram is optional.
4. If Impact Bucket is `Revenue` or `Cost`, require Business Value USD and Value Type.
5. Customer form requires No PHI Acknowledgement = Yes. Reject any description that looks like patient identifiers (see `scripts/submit_intake.py`).

## Fallback until fields exist

`scripts/configure_jira.py` talks to Jira REST with `ATLASSIAN_EMAIL` + `jira_admin_veridian`. If that token is rejected (current state: 401), issues still capture the contract in:

1. Description block `## Intake metadata` (key/value table)
2. Labels listed in [taxonomy.md](taxonomy.md)

## Name → ID map

Fill after a successful configure run:

| Name | Field ID | Context ID |
| --- | --- | --- |
| Requester Name | | |
| Requester Email | | |
| Organization | | |
| Organization Other | | |
| Intake Request Type | | |
| Clinical Program | | |
| Subprogram | | |
| Impact Bucket | | |
| Business Value USD | | |
| Value Type | | |
| Source | | |
| Counterpart Key | | |
| No PHI Acknowledgement | | |
