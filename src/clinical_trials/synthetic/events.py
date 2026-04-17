from __future__ import annotations

import numpy as np
import pandas as pd


def _event_scale_for_arm(arm: str) -> float:
    if arm == "ntx101_high":
        return 272.0
    if arm == "ntx101_low":
        return 234.0
    return 170.0


def simulate_phase3_event_outcomes(
    subject_master: pd.DataFrame,
    phase_assignments: pd.DataFrame,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 3)
    phase3_subjects = set(
        phase_assignments.loc[phase_assignments["phase_3_flag"] == 1, "program_subject_id"].tolist()
    )

    rows: list[dict] = []
    for _, row in subject_master.iterrows():
        pid = row["program_subject_id"]
        if pid not in phase3_subjects:
            continue

        arm = str(row.get("treatment_arm", "unknown"))
        severity = str(row.get("baseline_severity_group", "moderate"))
        age = float(row.get("age", 75))

        severity_factor = 0.92 if severity == "moderate" else 1.04
        age_factor = max(0.84, 1 - 0.012 * ((age - 75) / 5))
        subject_factor = float(np.exp(rng.normal(0, 0.18)))
        scale = _event_scale_for_arm(arm) * severity_factor * age_factor / subject_factor
        time = float(max(1.0, rng.exponential(scale=scale)))
        event_flag = int(time <= 364)

        rows.append(
            {
                "program_subject_id": pid,
                "source_study_id": row.get("source_study_id", pd.NA),
                "source_usubjid": row.get("source_usubjid", pd.NA),
                "study_phase": "phase_3",
                "time_to_worsening_days": round(min(time, 364.0), 2),
                "event_flag": event_flag,
                "event_type": "clinical_worsening" if event_flag == 1 else "no_event",
                "censor_reason": "administrative_censoring" if event_flag == 0 else "",
                "treatment_arm": arm,
                "data_origin": "synthetic_bridge",
            }
        )

    return pd.DataFrame(rows)
