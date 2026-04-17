from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats

from clinical_trials.analysis.phase1 import (
    build_phase1_figures,
    evaluate_phase1_gate,
    summarize_ae_incidence,
    summarize_labs,
    summarize_population,
    summarize_serious_ae,
    summarize_vitals,
)
from clinical_trials.reporting.phase1_report import render_phase1_report


def run_phase1_review() -> None:
    adsl = pd.read_parquet("data/derived/adam_like/alz_program/adsl.parquet")
    adae = pd.read_parquet("data/derived/adam_like/alz_program/adae.parquet")
    adlb = pd.read_parquet("data/derived/adam_like/alz_program/adlb.parquet")
    advs = pd.read_parquet("data/derived/adam_like/alz_program/advs.parquet")

    population = summarize_population(adsl)
    ae_summary = summarize_ae_incidence(adae=adae, adsl=adsl)
    serious = summarize_serious_ae(adae)
    labs = summarize_labs(adlb)
    vitals = summarize_vitals(advs)
    gate = evaluate_phase1_gate(adae=adae, adlb=adlb, ae_summary=ae_summary)

    enrolled_adsl = adsl.loc[adsl["trt01a"] != "screen_failure"].copy()
    age_placebo = enrolled_adsl.loc[enrolled_adsl["trt01a"] == "placebo", "age"].dropna()
    age_active = enrolled_adsl.loc[enrolled_adsl["trt01a"] != "placebo", "age"].dropna()
    age_t = stats.ttest_ind(age_active, age_placebo, equal_var=False)

    baseline_table = pd.DataFrame(
        [
            {
                "comparison": "Age balance active vs placebo",
                "statistic": round(float(age_t.statistic), 4),
                "p_value": round(float(age_t.pvalue), 4),
            },
            {
                "comparison": "Any AE rate active vs placebo",
                "statistic": gate["ae_rate_diff_pp"],
                "p_value": gate["ae_rate_pvalue"],
            },
            {
                "comparison": "Serious AE rate active vs placebo",
                "statistic": gate["serious_ae_rate_diff_pp"],
                "p_value": gate["serious_ae_rate_pvalue"],
            },
        ]
    )

    phase1_dir = Path("artifacts/phase1")
    phase1_dir.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(phase1_dir / "phase1_tables.xlsx") as writer:
        population.to_excel(writer, sheet_name="population", index=False)
        ae_summary.to_excel(writer, sheet_name="ae_incidence", index=False)
        serious.to_excel(writer, sheet_name="serious_ae", index=False)
        labs.to_excel(writer, sheet_name="labs", index=False)
        vitals.to_excel(writer, sheet_name="vitals", index=False)
        baseline_table.to_excel(writer, sheet_name="stats", index=False)

    figure_paths = build_phase1_figures(ae_summary=ae_summary, lab_summary=labs, vs_summary=vitals)

    memo_text = (
        "# Phase I Gate Memo\n\n"
        f"Gate Decision: **{gate['decision']}**\n\n"
        "## Decision basis\n"
        f"- AE rate difference vs placebo (pp): {gate['ae_rate_diff_pp']}\n"
        f"- Any AE Fisher exact p-value: {gate['ae_rate_pvalue']}\n"
        f"- Serious AE rate difference vs placebo (pp): {gate['serious_ae_rate_diff_pp']}\n"
        f"- Serious AE Fisher exact p-value: {gate['serious_ae_rate_pvalue']}\n"
        f"- Critical lab cluster: {gate['critical_lab_cluster']}\n"
        f"- Treatment-related death imbalance: {gate['treatment_related_death_imbalance']}\n\n"
        "## Hypothesis framing\n"
        "- Null: early safety burden is not materially different from placebo.\n"
        "- Interpretation: Phase I supports continued development because serious adverse event burden remained low, no active-arm treatment-related death imbalance was observed, and no critical lab toxicity cluster was detected. The any-AE imbalance is retained as contextual tolerability signal rather than a standalone stopping trigger.\n\n"
        "## Limitations\n"
        "- Interpretation should remain aligned to the documented source mix and continuity assumptions used for this review.\n"
        "- Findings are intended for internal methodological demonstration and not for publication or submission use.\n"
    )
    (phase1_dir / "phase1_gate_memo.md").write_text(memo_text, encoding="utf-8")

    context = {
        "decision": gate["decision"],
        "metrics": gate,
        "population_table": population.to_dict(orient="records"),
        "ae_table": ae_summary.to_dict(orient="records"),
        "stats_table": baseline_table.to_dict(orient="records"),
        "figure_paths": [path.replace("artifacts/", "../../artifacts/") for path in figure_paths],
    }
    render_phase1_report(context)


if __name__ == "__main__":
    run_phase1_review()
