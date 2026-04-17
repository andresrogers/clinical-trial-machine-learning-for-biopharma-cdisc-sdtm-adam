# Identifier Policy

## Core principles
- `STUDYID` remains the source study identifier from original clinical datasets.
- `USUBJID` is the stable source person-level identifier for all raw/interim and harmonized source-linked datasets.
- `program_subject_id` is introduced for the synthetic continuity bridge and derived program-level datasets.
- All bridge and derived outputs should retain both `source_usubjid` and `program_subject_id` whenever possible.

## Visit ordering policy
- Use visit number fields when available (`VISITNUM`, `AVISITN`, `visit_week`).
- Retain actual/nominal visit labels (`VISIT`, `AVISIT`, `visit_label`).
- Preserve date fields as source context where available.

## Cross-layer key expectations
- Raw/interim key baseline: `STUDYID + USUBJID`
- Harmonized key baseline: `source_study_id + source_usubjid`
- Program-level derived key baseline: `program_subject_id`

## Constraint
No derived dataset may drop source identity without explicit documentation in the schema change log.
