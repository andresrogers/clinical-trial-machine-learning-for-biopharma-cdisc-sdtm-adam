from __future__ import annotations

import pandas as pd


def _to_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)


def derive_adsl(
    subject_master: pd.DataFrame,
    phase_assignments: pd.DataFrame,
) -> pd.DataFrame:
    out = subject_master.merge(
        phase_assignments[["program_subject_id", "phase_1_flag", "phase_2_flag", "phase_3_flag"]],
        on="program_subject_id",
        how="left",
    )

    out["treatment_arm"] = out["treatment_arm"].map(_to_text).str.strip().str.lower()
    out["trt01p"] = out["treatment_arm"]
    out["trt01a"] = out["treatment_arm"]
    out["ittfl"] = "Y"
    out["saffl"] = "Y"
    return out
