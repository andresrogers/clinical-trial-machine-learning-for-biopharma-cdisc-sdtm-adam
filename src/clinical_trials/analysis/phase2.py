from __future__ import annotations

import pandas as pd
from scipy import stats


def derive_week24_responder_set(adeff: pd.DataFrame) -> pd.DataFrame:
    wk24 = adeff.loc[adeff["visit_week"] == 24].copy()
    wk24["response_flag"] = wk24["response_flag"].astype(int)
    return wk24


def build_phase2_model_dataset(adsl: pd.DataFrame, adeff: pd.DataFrame) -> pd.DataFrame:
    wk24 = derive_week24_responder_set(adeff)[["program_subject_id", "response_flag"]]
    wk12 = (
        adeff.loc[
            adeff["visit_week"] == 12,
            ["program_subject_id", "chg", "early_safety_discontinuation_before_week12"],
        ]
        .rename(columns={"chg": "chg_week12"})
        .drop_duplicates(subset=["program_subject_id"])
    )
    baseline_cols = [
        "program_subject_id",
        "age",
        "sex",
        "race",
        "baseline_severity_group",
        "baseline_cognitive_score",
        "treatment_arm",
    ]
    baseline = adsl[baseline_cols].drop_duplicates(subset=["program_subject_id"])

    out = baseline.merge(wk12, on="program_subject_id", how="left").merge(
        wk24, on="program_subject_id", how="inner"
    )
    out["early_safety_discontinuation_before_week12"] = (
        out["early_safety_discontinuation_before_week12"].fillna(0).astype(int)
    )
    return out


def build_phase2_hypothesis_summary(adeff: pd.DataFrame) -> pd.DataFrame:
    wk24 = adeff.loc[adeff["visit_week"] == 24].copy()
    placebo = wk24.loc[wk24["treatment_arm"] == "placebo", "chg"].dropna()
    rows: list[dict] = []

    for arm in ["ntx101_low", "ntx101_high"]:
        active = wk24.loc[wk24["treatment_arm"] == arm, "chg"].dropna()
        if len(active) and len(placebo):
            stat = stats.ttest_ind(active, placebo, equal_var=False)
            diff = float(active.mean() - placebo.mean())
            se = float(active.std(ddof=1) / max(len(active) ** 0.5, 1)) if len(active) > 1 else 0.0
            ci_low = diff - 1.96 * se
            ci_high = diff + 1.96 * se
        else:
            stat = type("obj", (), {"statistic": float("nan"), "pvalue": float("nan")})()
            diff = float("nan")
            ci_low = float("nan")
            ci_high = float("nan")

        rows.append(
            {
                "comparison": f"{arm} vs placebo",
                "mean_difference_chg": round(diff, 3),
                "t_statistic": round(float(stat.statistic), 4),
                "p_value": round(float(stat.pvalue), 4),
                "approx_ci_low": round(float(ci_low), 3),
                "approx_ci_high": round(float(ci_high), 3),
            }
        )

    return pd.DataFrame(rows)
