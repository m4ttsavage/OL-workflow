# Custom fields (VDSD and VDV)

Created **once as global fields**, then added to the shared SUP JSM screens used by both classic projects. **No prefixes.** Option maps live in [`config/field-ids.json`](../config/field-ids.json).

Native JSM already has a field named **Request Type** (`customfield_10010`) for portal request types. Our taxonomy field is a separate select named **Intake Request Type** in Jira (display still “Request Type” on the public forms). Native **Organizations** (`customfield_10002`) is the JSM customer-org picker; our **Organization** field is a brand/department select. `scripts/intake_payload.py` sets `customfield_10002` from [`config/jsm-customers-created.json`](../config/jsm-customers-created.json) when that file exists.

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
| No PHI Acknowledgement | Radio Yes/No | customer form | Must be Yes |

Priority uses **native Priority** (Highest/High/Medium/Low).

## Dependent rules

1. If Request Type is `Access` or `Internal_IT`, hide Clinical Program and Subprogram.
2. If Clinical Program is `Cross_Program` or `NA`, hide Subprogram.
3. If Clinical Program is `Platform`, Subprogram is optional.
4. If Impact Bucket is `Revenue` or `Cost`, require Business Value USD and Value Type.
5. Customer form requires No PHI Acknowledgement = Yes. Reject any description that looks like patient identifiers (see `scripts/submit_intake.py`).

## Scripts

```bash
python scripts/configure_jira.py      # create fields + options; rewrite config/field-ids.json
python scripts/associate_screens.py   # add fields to SUP screens 10010/10011/10012
python scripts/backfill_fields.py      # write fields onto seeded VDSD/VDV issues
```

`scripts/intake_payload.jira_fields` sets `customfield_*` when `config/field-ids.json` is present, and still writes labels plus the `## Intake metadata` description table.

Seeded issues **VDSD-1..8** and **VDV-1..5** were backfilled from `config/seed-requests.json` (August 2026).

## Name → ID map

| Name | Field ID | Context ID |
| --- | --- | --- |
| Requester Name | customfield_10078 | 10184 |
| Requester Email | customfield_10079 | 10185 |
| Organization | customfield_10080 | 10186 |
| Organization Other | customfield_10081 | 10187 |
| Intake Request Type | customfield_10082 | 10188 |
| Clinical Program | customfield_10083 | 10189 |
| Subprogram | customfield_10084 | 10190 |
| Impact Bucket | customfield_10085 | 10191 |
| Business Value USD | customfield_10086 | 10192 |
| Value Type | customfield_10087 | 10193 |
| Source | customfield_10088 | 10194 |
| Counterpart Key | customfield_10089 | 10195 |
| No PHI Acknowledgement | customfield_10090 | 10196 |
