library(arrow)
library(dplyr)

ae <- read_parquet("data/derived/sdtm_alz/ae.parquet")
adsl <- read_parquet("data/derived/adam_like/alz_program/adsl.parquet")

adae_ref <- ae %>%
  left_join(adsl %>% select(program_subject_id, source_usubjid, trt01a, saffl), by = "source_usubjid") %>%
  mutate(
    teae_flag = 1,
    serious_flag = as.integer(ifelse(toupper(as.character(aeser)) == "Y", 1, 0))
  )

write_parquet(adae_ref, "artifacts/qc/adae_r_reference.parquet")
