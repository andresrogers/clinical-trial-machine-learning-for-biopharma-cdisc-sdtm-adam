from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from clinical_trials.reporting.plotting import (
    ARM_COLORS,
    display_arm_label,
    order_arms,
    save_figure,
    set_pharma_style,
)


def _to_text(series: pd.Series) -> pd.Series:
    return series.map(lambda x: x.decode("utf-8", errors="ignore") if isinstance(x, bytes) else x)


def summarize_population(adsl: pd.DataFrame) -> pd.DataFrame:
    enrolled = adsl.loc[adsl["trt01a"] != "screen_failure"].copy()
    out = (
        enrolled.groupby("trt01a", dropna=False)
        .agg(subjects=("program_subject_id", "nunique"), mean_age=("age", "mean"))
        .reset_index()
    )
    out["mean_age"] = out["mean_age"].round(2)
    return out


def summarize_ae_incidence(adae: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    adsl = adsl.loc[adsl["trt01a"] != "screen_failure"].copy()
    adae = adae.loc[adae["trt01a"] != "screen_failure"].copy()
    total = (
        adsl.groupby("trt01a", dropna=False)["program_subject_id"].nunique().rename("n_subjects")
    )
    ae = (
        adae.groupby("trt01a", dropna=False)["program_subject_id"]
        .nunique()
        .rename("subjects_with_ae")
    )
    out = pd.concat([total, ae], axis=1).fillna(0).reset_index()
    out["ae_rate_pct"] = (100 * out["subjects_with_ae"] / out["n_subjects"]).round(2)
    return out


def summarize_serious_ae(adae: pd.DataFrame) -> pd.DataFrame:
    adae = adae.loc[adae["trt01a"] != "screen_failure"].copy()
    if "serious_flag" not in adae.columns:
        adae = adae.copy()
        adae["serious_flag"] = (
            _to_text(adae.get("aeser", pd.Series(index=adae.index)))
            .astype(str)
            .str.upper()
            .eq("Y")
            .astype(int)
        )

    out = (
        adae.groupby("trt01a", dropna=False)
        .agg(
            serious_events=("serious_flag", "sum"),
            subjects_with_serious=(
                "program_subject_id",
                lambda s: s[adae.loc[s.index, "serious_flag"] == 1].nunique(),
            ),
        )
        .reset_index()
    )
    return out


def summarize_labs(adlb: pd.DataFrame) -> pd.DataFrame:
    adlb = adlb.loc[adlb["trt01a"] != "screen_failure"].copy()
    out = (
        adlb.groupby(["paramcd", "trt01a"], dropna=False)
        .agg(mean_chg=("chg", "mean"), std_chg=("chg", "std"), n=("program_subject_id", "nunique"))
        .reset_index()
    )
    # decode bytes to text if necessary (some source XPTs store paramcd as bytes)
    out["paramcd"] = _to_text(out.get("paramcd", out.index)).astype(str)
    out["mean_chg"] = out["mean_chg"].round(3)
    out["std_chg"] = out["std_chg"].round(3)
    return out


def summarize_vitals(advs: pd.DataFrame) -> pd.DataFrame:
    advs = advs.loc[advs["trt01a"] != "screen_failure"].copy()
    out = (
        advs.groupby(["paramcd", "trt01a"], dropna=False)
        .agg(mean_chg=("chg", "mean"), p95_aval=("aval", lambda s: s.quantile(0.95)))
        .reset_index()
    )
    out["paramcd"] = _to_text(out.get("paramcd", out.index)).astype(str)
    out["mean_chg"] = out["mean_chg"].round(3)
    out["p95_aval"] = out["p95_aval"].round(3)
    return out


def phase1_gate_decision(
    ae_rate_diff_pp: float,
    serious_ae_rate_diff_pp: float,
    critical_lab_cluster: bool,
    treatment_related_death_imbalance: bool,
) -> str:
    if treatment_related_death_imbalance or serious_ae_rate_diff_pp >= 10:
        return "STOP"
    if critical_lab_cluster and serious_ae_rate_diff_pp >= 5:
        return "STOP"
    if serious_ae_rate_diff_pp >= 5 or critical_lab_cluster or ae_rate_diff_pp >= 20:
        return "HOLD"
    return "GO"


def evaluate_phase1_gate(adae: pd.DataFrame, adlb: pd.DataFrame, ae_summary: pd.DataFrame) -> dict:
    adae = adae.loc[adae["trt01a"] != "screen_failure"].copy()
    adlb = adlb.loc[adlb["trt01a"] != "screen_failure"].copy()
    ae_summary = ae_summary.loc[ae_summary["trt01a"] != "screen_failure"].copy()

    placebo = ae_summary.loc[ae_summary["trt01a"] == "placebo", "ae_rate_pct"]
    placebo_rate = float(placebo.iloc[0]) if len(placebo) else 0.0
    active_max = float(
        ae_summary.loc[ae_summary["trt01a"] != "placebo", "ae_rate_pct"].max() or 0.0
    )
    ae_rate_diff_pp = active_max - placebo_rate

    serious_flag = (
        adae.get("serious_flag", pd.Series(0, index=adae.index)).fillna(0).astype(int).eq(1)
    )
    subject_counts = ae_summary.set_index("trt01a")["n_subjects"]
    serious_subjects_by_arm = (
        adae.loc[serious_flag].groupby("trt01a")["program_subject_id"].nunique()
    )
    placebo_subjects = int(subject_counts.get("placebo", 0))
    placebo_serious_subjects = int(serious_subjects_by_arm.get("placebo", 0))
    placebo_serious_rate = (
        100 * placebo_serious_subjects / placebo_subjects if placebo_subjects else 0.0
    )

    active_serious_rates = []
    for arm, n_subjects in subject_counts.items():
        if arm == "placebo" or not n_subjects:
            continue
        arm_serious_subjects = int(serious_subjects_by_arm.get(arm, 0))
        active_serious_rates.append(100 * arm_serious_subjects / n_subjects)
    active_max_serious_rate = max(active_serious_rates) if active_serious_rates else 0.0
    serious_ae_rate_diff_pp = active_max_serious_rate - placebo_serious_rate

    adlb_non_null = adlb.dropna(subset=["chg", "trt01a"])
    if len(adlb_non_null):
        threshold = adlb_non_null["chg"].std() * 3
        if pd.isna(threshold) or threshold == 0:
            threshold = 5.0
        abnormal = (adlb_non_null["chg"].abs() >= threshold).astype(int)
        cluster = adlb_non_null.assign(abnormal=abnormal).groupby("trt01a")["abnormal"].mean()
        placebo_cluster = float(cluster.get("placebo", 0.0))
        active_cluster = float(cluster.drop(labels=["placebo"], errors="ignore").max() or 0.0)
        critical_lab_cluster = (active_cluster - placebo_cluster) >= 0.05
    else:
        critical_lab_cluster = False

    death_flag = (
        _to_text(adae.get("aesdth", pd.Series(index=adae.index))).astype(str).str.upper().eq("Y")
    )
    related_flag = (
        adae.get("related_flag", pd.Series(0, index=adae.index)).fillna(0).astype(int).eq(1)
    )
    death_by_arm = (
        adae.loc[death_flag & related_flag].groupby("trt01a")["program_subject_id"].nunique()
    )
    placebo_deaths = int(death_by_arm.get("placebo", 0))
    active_series = death_by_arm.drop(labels=["placebo"], errors="ignore")
    active_max = active_series.max() if len(active_series) else 0
    if pd.isna(active_max):
        active_max = 0
    active_deaths = int(active_max)
    treatment_related_death_imbalance = (active_deaths - placebo_deaths) >= 1

    decision = phase1_gate_decision(
        ae_rate_diff_pp=ae_rate_diff_pp,
        serious_ae_rate_diff_pp=serious_ae_rate_diff_pp,
        critical_lab_cluster=critical_lab_cluster,
        treatment_related_death_imbalance=treatment_related_death_imbalance,
    )

    placebo_row = ae_summary.loc[ae_summary["trt01a"] == "placebo"]
    placebo_subjects = int(placebo_row["n_subjects"].iloc[0]) if len(placebo_row) else 0
    placebo_ae = int(placebo_row["subjects_with_ae"].iloc[0]) if len(placebo_row) else 0
    active_subjects = int(ae_summary.loc[ae_summary["trt01a"] != "placebo", "n_subjects"].sum())
    active_ae = int(ae_summary.loc[ae_summary["trt01a"] != "placebo", "subjects_with_ae"].sum())
    active_serious_subjects = int(
        serious_subjects_by_arm.drop(labels=["placebo"], errors="ignore").sum()
    )

    contingency = pd.DataFrame(
        [
            [active_ae, max(active_subjects - active_ae, 0)],
            [placebo_ae, max(placebo_subjects - placebo_ae, 0)],
        ],
        index=["active", "placebo"],
        columns=["ae", "no_ae"],
    )
    _, pvalue = stats.fisher_exact(contingency)

    serious_contingency = pd.DataFrame(
        [
            [active_serious_subjects, max(active_subjects - active_serious_subjects, 0)],
            [placebo_serious_subjects, max(placebo_subjects - placebo_serious_subjects, 0)],
        ],
        index=["active", "placebo"],
        columns=["serious_ae", "no_serious_ae"],
    )
    _, serious_pvalue = stats.fisher_exact(serious_contingency)

    return {
        "decision": decision,
        "ae_rate_diff_pp": round(ae_rate_diff_pp, 3),
        "serious_ae_rate_diff_pp": round(serious_ae_rate_diff_pp, 3),
        "critical_lab_cluster": bool(critical_lab_cluster),
        "treatment_related_death_imbalance": bool(treatment_related_death_imbalance),
        "ae_rate_pvalue": round(float(pvalue), 4),
        "serious_ae_rate_pvalue": round(float(serious_pvalue), 4),
        "active_ae_rate_pct": round(100 * active_ae / active_subjects, 2)
        if active_subjects
        else 0.0,
        "placebo_ae_rate_pct": round(100 * placebo_ae / placebo_subjects, 2)
        if placebo_subjects
        else 0.0,
        "active_serious_ae_rate_pct": round(100 * active_serious_subjects / active_subjects, 2)
        if active_subjects
        else 0.0,
        "placebo_serious_ae_rate_pct": round(100 * placebo_serious_subjects / placebo_subjects, 2)
        if placebo_subjects
        else 0.0,
    }


def build_phase1_figures(
    ae_summary: pd.DataFrame, lab_summary: pd.DataFrame, vs_summary: pd.DataFrame
) -> list[str]:
    set_pharma_style()
    fig_dir = Path("artifacts/phase1/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    output_files: list[str] = []

    ae_plot = ae_summary.copy()
    ae_plot["order_key"] = pd.Categorical(
        ae_plot["trt01a"], categories=order_arms(ae_plot["trt01a"].tolist()), ordered=True
    )
    ae_plot = ae_plot.sort_values("order_key")

    plt.figure(figsize=(8, 4.5))
    plt.bar(
        [display_arm_label(x) for x in ae_plot["trt01a"]],
        ae_plot["ae_rate_pct"],
        color=[ARM_COLORS.get(x, "#6B7280") for x in ae_plot["trt01a"]],
        edgecolor="#D0D7DE",
    )
    plt.title("Phase I Safety Review: Any AE Incidence by Arm")
    plt.ylabel("Subjects with >=1 AE (%)")
    plt.xlabel("")
    plt.ylim(0, max(100, float(ae_plot["ae_rate_pct"].max()) + 5))
    p1 = fig_dir / "ae_incidence.png"
    save_figure(p1)
    output_files.append(str(p1))

    lab_plot = lab_summary.copy()
    preferred = ["CREAT", "PLAT", "URATE", "CK", "VITB12", "ALP"]
    available_params = list(lab_plot["paramcd"].astype(str).unique())

    # Build a sensible left-to-right ordering: prefer the 'preferred' list where available,
    # otherwise pick the top parameters by absolute mean change across arms.
    pref_in_data = [p for p in preferred if p in available_params]
    if pref_in_data:
        param_order = pref_in_data
    else:
        # compute overall absolute mean change per param and sort descending
        abs_mean = (
            lab_plot.assign(abs_mean=lambda df: df["mean_chg"].abs())
            .groupby("paramcd", dropna=False)["abs_mean"]
            .mean()
            .sort_values(ascending=False)
        )
        param_order = list(abs_mean.index.astype(str))[:12]

    # Ensure a consistent x-axis across arms by pivoting to a param x arm matrix
    lab_plot["order_key"] = pd.Categorical(
        lab_plot["trt01a"], categories=order_arms(lab_plot["trt01a"].tolist()), ordered=True
    )
    pivot = lab_plot.sort_values(["paramcd", "order_key"]).pivot(index="paramcd", columns="trt01a", values="mean_chg")
    pivot = pivot.reindex(param_order)

    plt.figure(figsize=(10, 5.2))
    for arm in pivot.columns:
        y = pivot[arm].values
        plt.plot(
            param_order,
            y,
            marker="o",
            linewidth=2.0,
            color=ARM_COLORS.get(arm, "#6B7280"),
            label=display_arm_label(str(arm)),
        )
    plt.title("Phase I Safety Review: Mean Lab Change by Parameter")
    plt.ylabel("Mean change")
    plt.xlabel("Lab parameter")
    plt.xticks(rotation=45, ha="right")
    plt.legend(loc="best")
    p2 = fig_dir / "lab_mean_change.png"
    save_figure(p2)
    output_files.append(str(p2))

    vs_plot = vs_summary.loc[
        vs_summary["paramcd"].isin(["SYSBP", "DIABP", "PULSE", "TEMP", "RESP"])
    ].copy()
    if vs_plot.empty:
        vs_plot = vs_summary.sort_values("mean_chg", key=lambda s: s.abs(), ascending=False).head(
            12
        )
    vs_plot["order_key"] = pd.Categorical(
        vs_plot["trt01a"], categories=order_arms(vs_plot["trt01a"].tolist()), ordered=True
    )
    vs_plot = vs_plot.sort_values(["paramcd", "order_key"])

    plt.figure(figsize=(10, 5.2))
    for arm, grp in vs_plot.groupby("trt01a"):
        grp = grp.sort_values("paramcd")
        plt.plot(
            grp["paramcd"].astype(str),
            grp["mean_chg"],
            marker="o",
            linewidth=2.0,
            color=ARM_COLORS.get(arm, "#6B7280"),
            label=display_arm_label(str(arm)),
        )
    plt.title("Phase I Safety Review: Mean Vital Sign Change by Parameter")
    plt.ylabel("Mean change")
    plt.xlabel("Vital sign parameter")
    plt.xticks(rotation=45, ha="right")
    plt.legend(loc="best")
    p3 = fig_dir / "vitals_mean_change.png"
    save_figure(p3)
    output_files.append(str(p3))

    return output_files
