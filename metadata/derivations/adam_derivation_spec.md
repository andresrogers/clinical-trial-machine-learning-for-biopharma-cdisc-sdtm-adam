# ADaM-like Derivation Specification

## Program
NTX-101

## Input layers
- Harmonized SDTM-like: `data/derived/sdtm_alz/*.parquet`
- Synthetic continuity bridge: `data/generated/alz_program/*.parquet`

## Dataset derivations

### ADSL
- Inputs: `subject_master`, `phase_assignments`
- Join key: `program_subject_id`
- Added fields: `trt01p`, `trt01a`, `ittfl`, `saffl`, phase flags

### ADAE
- Inputs: harmonized `ae`, derived `adsl`
- Join key: `source_usubjid`
- Added fields: `teae_flag`, `serious_flag`, `related_flag`

### ADLB
- Inputs: harmonized `lb`, derived `adsl`
- Join key: `source_usubjid`
- Added fields: `paramcd`, `aval`, `base`, `chg`

### ADVS
- Inputs: harmonized `vs`, derived `adsl`
- Join key: `source_usubjid`
- Added fields: `paramcd`, `aval`, `base`, `chg`

### ADEFF
- Inputs: synthetic `efficacy_long`
- Added fields: `paramcd=ADAS11CFB`, `aval`, `chg`

### ADTTE
- Inputs: synthetic `event_outcomes`, derived `adsl`
- Join key: `program_subject_id`
- Added fields: `paramcd=TTWORSEN`, `aval`, `cnsr`, `event_desc`

## Traceability
All outputs preserve `program_subject_id`. Source-linked datasets preserve `source_usubjid`.
