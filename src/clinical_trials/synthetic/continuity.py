from __future__ import annotations

import numpy as np
import pandas as pd


def build_subject_master(dm: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = dm.copy().reset_index(drop=True)

    out["program_subject_id"] = [f"ALZ-{i:04d}" for i in range(1, len(out) + 1)]
    out["baseline_severity_group"] = rng.choice(["mild", "moderate"], size=len(out), p=[0.55, 0.45])
    out["baseline_cognitive_score"] = np.clip(rng.normal(24, 5, size=len(out)), 8, 45).round(2)
    out["data_origin"] = "synthetic_bridge"
    out["source_study_id"] = out.get("source_study_id", out.get("studyid", "CDISCPILOT01"))
    out["source_usubjid"] = out.get("source_usubjid", out.get("usubjid"))
    out["enrolled_flag"] = out["treatment_arm"].ne("screen_failure").astype(int)

    keep_cols = [
        "program_subject_id",
        "source_study_id",
        "source_usubjid",
        "age",
        "sex",
        "race",
        "treatment_arm",
        "baseline_severity_group",
        "baseline_cognitive_score",
        "enrolled_flag",
        "data_origin",
    ]
    present = [col for col in keep_cols if col in out.columns]
    return out[present]


def build_phase_assignments(subject_master: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1)
    out = subject_master[
        [
            "program_subject_id",
            "source_study_id",
            "source_usubjid",
            "treatment_arm",
            "enrolled_flag",
        ]
    ].copy()
    enrolled = out["enrolled_flag"] == 1
    out["phase_1_flag"] = enrolled.astype(int)
    out["phase_2_flag"] = (enrolled & (rng.binomial(n=1, p=0.84, size=len(out)) == 1)).astype(int)
    out["phase_3_flag"] = (
        (out["phase_2_flag"] == 1) & (rng.binomial(n=1, p=0.8, size=len(out)) == 1)
    ).astype(int)
    out["data_origin"] = "synthetic_bridge"
    return out


def build_visit_schedule() -> pd.DataFrame:
    rows: list[dict] = []

    for visit in ["screening", "baseline", "day_7", "day_14", "day_28", "follow_up"]:
        rows.append({"study_phase": "phase_1", "visit_label": visit, "visit_week": pd.NA})

    for week in [0, 4, 8, 12, 18, 24]:
        rows.append({"study_phase": "phase_2", "visit_label": f"week_{week}", "visit_week": week})

    for week in [0, 4, 8, 12, 24, 36, 52]:
        rows.append({"study_phase": "phase_3", "visit_label": f"week_{week}", "visit_week": week})

    return pd.DataFrame(rows)
