# Synthetic Generation Specification

## Purpose
Provide the minimum deterministic bridge needed to connect public-source structure to a continuous Alzheimer's program narrative across Phase I, Phase II, and Phase III.

## Seed and determinism
- Global seed source: `config/program_config.yml`
- Seed value: `20260416`
- All synthetic modules derive deterministic random streams from this seed.

## Outputs
- `data/generated/alz_program/subject_master.parquet`
- `data/generated/alz_program/phase_assignments.parquet`
- `data/generated/alz_program/visit_schedule.parquet`
- `data/generated/alz_program/efficacy_long.parquet`
- `data/generated/alz_program/event_outcomes.parquet`

## Data-origin policy
- Every synthetic output includes `data_origin = synthetic_bridge`.
- Synthetic outputs preserve linkage fields:
  - `source_study_id`
  - `source_usubjid`
  - `program_subject_id`

## Endpoint assumptions
- Phase II endpoint: `ADAS_COG11 change from baseline at Week 24`
- Responder logic: `adas_cog11_change <= -3` at Week 24 and no early safety discontinuation before Week 12
- Phase III endpoint: `time_to_clinical_worsening`
- Event definition: cognitive worsening event or protocol-defined efficacy failure equivalent

## Scope boundaries
- Do not overwrite public source data.
- Do not generate unsupported disease narratives.
- Do not expand synthetic domains beyond explicit continuity gaps.
