# Veridian Dynamics intake taxonomy

Source of truth: [`config/taxonomy.json`](../config/taxonomy.json).
Customer project: **VDSD**. Engineering project: **RND** (team-managed software). Unused: KAN, VD, SAM1, **VDV**.

Do not collect patient or clinical data. Name, work email, and organization only.

## Request Type

Always required. Independent of Clinical Program.

| ID | Label | Program required | RND work type |
| --- | --- | --- | --- |
| Feature | Feature | yes | Feature |
| Bug | Bug | yes | Task |
| Incident | Incident | yes | Task |
| Operational_Change | Operational change | yes | Task |
| Access | Access | no | Task |
| Question | Question | yes | Task |
| Compliance | Compliance | yes | Task |
| New_Program_Launch | New program launch | yes | Feature |
| Pharmacy_Fulfillment | Pharmacy / fulfillment | yes | Task |
| Clinical_Ops | Clinical operations | yes | Task |
| Internal_IT | Internal IT | no | Task |

## Clinical Program and Subprogram

Required unless Request Type is `Access` or `Internal_IT`.
Subprogram is required unless program is `Platform`, `Cross_Program`, or `NA` (Platform still offers optional subprograms).

| Program | Subprograms |
| --- | --- |
| Peptides | NAD+, Sermorelin, B-12 MIC, Category 1 peptide |
| Medical weight loss | GLP-1 program, Care coaching, Aftercare / maintenance, Nutrition / registered dietitian |
| Hormones | HRT launch, Lab testing, At-home test kits, Ongoing monitoring |
| Sexual health | Erectile dysfunction, 3-in-1 combination, 4-in-1 combination |
| Diagnostics | At-home collection, Whole health panel |
| Sleep testing | Home ring test, Oral device, Prescription treatment |
| Dietitians | Registered dietitian visits, GLP-1 aftercare |
| Dermatology | Acne, Hair loss, Men, Women |
| Microdosing | GLP-1 microdosing, Metabolic support |
| Supplements | White-label line, Daily essentials, Targeted formula |
| Mental health | New protocol, Capacity, Workflow, Other |
| Behavioral health | New protocol, Capacity, Workflow, Other |
| Urgent care | New protocol, Capacity, Workflow, Other |
| Platform | Storefront, Intakes, Portal, Provider network, RCM / payer, CCM / RPM |
| Cross-program | (none) |
| N/A | (none) |

IDs are in `config/taxonomy.json`. Use those IDs in labels (`program:Medical_Weight_Loss`) and API payloads.

## Impact Bucket

| ID | Label | Business value required |
| --- | --- | --- |
| Patient_Safety_NonPHI | Patient safety (no PHI) | no |
| Clinical_Quality_NonPHI | Clinical quality (no PHI) | no |
| Revenue | Revenue | yes |
| Cost | Cost | yes |
| Brand | Brand | no |
| Operations | Operations | no |
| Compliance | Compliance | no |

When value is required, capture **Business Value USD** (annualized estimate) and **Value Type** (`Revenue`, `Cost_savings`, `Cost_avoidance`, `Retention`).

## Organization

- **VDSD (customer):** Northstar Wellness, Harbor Peak Health, Lumen Clinic, Atlas Fitness Care, Cedar Ridge Telehealth, Summit Peak Wellness, Other
- **RND (internal):** IT, Clinical Ops, CS, RCM, People, Finance, Engineering, Veridian Dynamics Internal

JSM Organizations (portal sharing) and plus-addressed customers live in [`config/jsm-customers.json`](../config/jsm-customers.json). Seed with `python scripts/seed_jsm_customers.py`. Emails are `matthewmsavage+[org-slug]@gmail.com` (and `…-[role]` for a second contact). Live IDs after a seed: [`config/jsm-customers-created.json`](../config/jsm-customers-created.json).

## Priority

| SLA band | Jira native Priority |
| --- | --- |
| P1 | Highest |
| P2 | High |
| P3 | Medium |
| P4 | Low |

## Label encoding

Use these labels on every intake issue so both projects stay queryable:

- `source:vdsd` or `source:rnd` (legacy `source:vdv` on leftover VDV issues)
- `type:{Request Type id}`
- `program:{Clinical Program id}`
- `sub:{Subprogram id}`
- `impact:{Impact Bucket id}`
- `org:{slug}` (spaces to `-`, lowercase)
