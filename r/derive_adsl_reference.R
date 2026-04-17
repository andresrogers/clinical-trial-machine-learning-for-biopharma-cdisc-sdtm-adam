library(arrow)
library(dplyr)

dm <- read_parquet("data/derived/sdtm_alz/dm.parquet")
subject_master <- read_parquet("data/generated/alz_program/subject_master.parquet")
phase_assignments <- read_parquet("data/generated/alz_program/phase_assignments.parquet")

adsl_ref <- subject_master %>%
  left_join(phase_assignments %>% select(program_subject_id, phase_1_flag, phase_2_flag, phase_3_flag), by = "program_subject_id") %>%
  mutate(
    trt01p = treatment_arm,
    trt01a = treatment_arm,
    ittfl = "Y",
    saffl = "Y"
  ) %>%
  left_join(dm %>% select(source_usubjid, age, sex, race), by = "source_usubjid")

write_parquet(adsl_ref, "artifacts/qc/adsl_r_reference.parquet")
