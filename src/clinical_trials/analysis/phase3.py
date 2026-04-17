from __future__ import annotations

import numpy as np
from lifelines import CoxPHFitter
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt
import pandas as pd

from clinical_trials.reporting.plotting import (
    ARM_COLORS,
    display_arm_label,
    order_arms,
    save_figure,
    set_pharma_style,
)


def prepare_tte_analysis_frame(adtte: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    cols = ["program_subject_id", "trt01a"]
    out = adtte.merge(adsl[cols], on="program_subject_id", how="left", suffixes=("", "_adsl"))

    if "trt01a" not in out.columns and "trt01a_adsl" in out.columns:
        out["trt01a"] = out["trt01a_adsl"]

    if "trt01a" in out.columns and "trt01a_adsl" in out.columns:
        out["trt01a"] = out["trt01a"].fillna(out["trt01a_adsl"])

    if "trt01a" not in out.columns and "treatment_arm" in out.columns:
        out["trt01a"] = out["treatment_arm"]

    if "trt01a" not in out.columns:
        out["trt01a"] = "unknown"

    out["trt01a"] = (
        out["trt01a"]
        .map(lambda x: x.decode("utf-8", errors="ignore") if isinstance(x, bytes) else str(x))
        .str.strip()
        .str.lower()
    )

    out["event_observed"] = 1 - out["cnsr"]
    out["trt_active"] = out["trt01a"].ne("placebo").astype(int)
    return out


def fit_cox_model(df: pd.DataFrame) -> CoxPHFitter:
    cph = CoxPHFitter()
    model_df = df[["aval", "event_observed", "trt_active"]].dropna().copy()

    if model_df["trt_active"].nunique(dropna=True) < 2:
        raise ValueError("Cox model requires both placebo and active groups for trt_active")

    cph.fit(model_df, duration_col="aval", event_col="event_observed", robust=True)
    return cph


def build_km_plot(df: pd.DataFrame, output_path: str) -> None:
    set_pharma_style()
    kmf = KaplanMeierFitter()
    plt.figure(figsize=(7, 5))
    df_plot = df.copy()
    df_plot["arm_order"] = pd.Categorical(
        df_plot["trt01a"],
        categories=order_arms(df_plot["trt01a"].dropna().unique().tolist()),
        ordered=True,
    )
    for label, grp in df_plot.sort_values(["arm_order", "aval"]).groupby("trt01a", sort=False):
        grp = grp.sort_values("aval")
        arm_label = display_arm_label(str(label))
        kmf.fit(grp["aval"], grp["event_observed"], label=arm_label)
        color = ARM_COLORS.get(str(label), "#6B7280")
        kmf.plot(ci_show=False, color=color, linewidth=2.2)
    plt.title("Phase III Confirmatory Review: Time to Clinical Worsening")
    plt.xlabel("Days")
    plt.ylabel("Survival probability")
    save_figure(output_path)


def build_phase3_hypothesis_summary(df: pd.DataFrame) -> dict:
    placebo_df = df.loc[df["trt01a"] == "placebo"].dropna(subset=["aval", "event_observed"])
    active_df = df.loc[df["trt01a"].isin(["ntx101_low", "ntx101_high"])].dropna(
        subset=["aval", "event_observed"]
    )

    logrank = logrank_test(
        active_df["aval"],
        placebo_df["aval"],
        event_observed_A=active_df["event_observed"],
        event_observed_B=placebo_df["event_observed"],
    )

    cph = fit_cox_model(df)
    hr = float(cph.hazard_ratios_["trt_active"])
    ci_row = cph.confidence_intervals_.loc["trt_active"]
    hr_ci_low = float(np.exp(ci_row.iloc[0]))
    hr_ci_high = float(np.exp(ci_row.iloc[1]))

    active_high = df.loc[df["trt01a"] == "ntx101_high"].dropna(subset=["aval", "event_observed"])
    high_logrank = logrank_test(
        active_high["aval"],
        placebo_df["aval"],
        event_observed_A=active_high["event_observed"],
        event_observed_B=placebo_df["event_observed"],
    )
    active_low = df.loc[df["trt01a"] == "ntx101_low"].dropna(subset=["aval", "event_observed"])
    low_logrank = logrank_test(
        active_low["aval"],
        placebo_df["aval"],
        event_observed_A=active_low["event_observed"],
        event_observed_B=placebo_df["event_observed"],
    )

    return {
        "comparison": "Active vs placebo time to worsening",
        "hazard_ratio": round(hr, 3),
        "hr_ci_low": round(hr_ci_low, 3),
        "hr_ci_high": round(hr_ci_high, 3),
        "logrank_p_value": round(float(logrank.p_value), 4),
        "median_delay_days": round(
            float(active_df["aval"].median() - placebo_df["aval"].median()), 3
        ),
        "mean_difference_days": round(
            float(active_df["aval"].mean() - placebo_df["aval"].mean()), 3
        ),
        "high_dose_logrank_p_value": round(float(high_logrank.p_value), 4),
        "low_dose_logrank_p_value": round(float(low_logrank.p_value), 4),
    }
