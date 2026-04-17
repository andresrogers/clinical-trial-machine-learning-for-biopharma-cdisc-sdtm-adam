from __future__ import annotations

import pandas as pd


def derive_adae(ae: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["program_subject_id", "source_usubjid", "trt01a", "saffl"]
    out = ae.merge(
        adsl[key_cols],
        left_on="source_usubjid",
        right_on="source_usubjid",
        how="left",
    )

    if "aeser" in out.columns:
        out["serious_flag"] = out["aeser"].astype(str).str.upper().eq("Y").astype(int)
    else:
        out["serious_flag"] = 0

    if "aerel" in out.columns:
        out["related_flag"] = (
            out["aerel"]
            .astype(str)
            .str.lower()
            .str.contains("related|possible|probable", regex=True)
        ).astype(int)
    else:
        out["related_flag"] = 0

    out["teae_flag"] = 1
    return out
