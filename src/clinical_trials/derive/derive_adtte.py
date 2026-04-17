from __future__ import annotations

import pandas as pd


def derive_adtte(event_outcomes: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    out = event_outcomes.merge(
        adsl[["program_subject_id", "trt01a"]],
        on="program_subject_id",
        how="left",
    )
    out["paramcd"] = "TTWORSEN"
    out["aval"] = out["time_to_worsening_days"]
    out["cnsr"] = 1 - out["event_flag"]
    out["event_desc"] = out["event_type"]
    return out
