from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_phase2_efficacy(
    subject_master: pd.DataFrame,
    phase_assignments: pd.DataFrame,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 2)
    weeks = [0, 4, 8, 12, 18, 24]
    week_fraction = {0: 0.00, 4: 0.18, 8: 0.35, 12: 0.55, 18: 0.78, 24: 1.00}

    phase2_subjects = phase_assignments.loc[
        phase_assignments["phase_2_flag"] == 1, "program_subject_id"
    ]
    base = subject_master.loc[subject_master["program_subject_id"].isin(phase2_subjects)].copy()

    arm_week24_mean = {
        "placebo": -2.80,
        "ntx101_low": -2.90,
        "ntx101_high": -3.00,
    }
    disc_prob = {"placebo": 0.01, "ntx101_low": 0.02, "ntx101_high": 0.025}

    rows: list[dict] = []
    for _, row in base.iterrows():
        baseline = float(row["baseline_cognitive_score"])
        arm = str(row.get("treatment_arm", "placebo"))
        severity = str(row.get("baseline_severity_group", "moderate"))
        age = float(row.get("age", 75))

        severity_effect = -0.28 if severity == "moderate" else 0.12
        age_effect = -0.02 * ((age - 75) / 5)
        subject_trait = rng.normal(0, 0.35)
        target_week24_change = (
            arm_week24_mean.get(arm, arm_week24_mean["placebo"])
            + severity_effect
            + age_effect
            + subject_trait
            + rng.normal(0, 0.25)
        )

        early_safety_disc = int(rng.binomial(1, disc_prob.get(arm, 0.02)))

        for week in weeks:
            progress = week_fraction[week]
            visit_noise = rng.normal(0, 0.25 if week < 24 else 0.15)
            score = baseline + (target_week24_change * progress) + visit_noise
            rows.append(
                {
                    "program_subject_id": row["program_subject_id"],
                    "study_phase": "phase_2",
                    "visit_week": week,
                    "adas_cog11": round(score, 2),
                    "baseline_adas_cog11": baseline,
                    "early_safety_discontinuation_before_week12": early_safety_disc,
                    "treatment_arm": arm,
                    "data_origin": "synthetic_bridge",
                }
            )

    df = pd.DataFrame(rows)
    df["adas_cog11_change"] = (df["adas_cog11"] - df["baseline_adas_cog11"]).round(2)
    df["response_flag"] = (
        (df["visit_week"] == 24)
        & (df["adas_cog11_change"] <= -3)
        & (df["early_safety_discontinuation_before_week12"] == 0)
    ).astype(int)
    return df
