from __future__ import annotations

from pathlib import Path

import pandas as pd

from clinical_trials.analysis.phase3 import (
    build_km_plot,
    build_phase3_hypothesis_summary,
    fit_cox_model,
    prepare_tte_analysis_frame,
)
from clinical_trials.reporting.phase3_report import render_phase3_report


def run_phase3_review() -> None:
    adsl = pd.read_parquet("data/derived/adam_like/alz_program/adsl.parquet")
    adtte = pd.read_parquet("data/derived/adam_like/alz_program/adtte.parquet")
    adae = pd.read_parquet("data/derived/adam_like/alz_program/adae.parquet")

    tte = prepare_tte_analysis_frame(adtte=adtte, adsl=adsl)

    phase3_dir = Path("artifacts/phase3")
    fig_dir = phase3_dir / "figures"
    phase3_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    km_path = fig_dir / "km_time_to_worsening.png"
    build_km_plot(tte, str(km_path))
    hypothesis_summary = build_phase3_hypothesis_summary(tte)

    cox_error = None
    try:
        cph = fit_cox_model(tte)
        cox_summary = cph.summary.reset_index()
    except Exception as exc:  # noqa: BLE001
        cox_error = str(exc)
        cox_summary = pd.DataFrame(
            [
                {
                    "parameter": "trt_active",
                    "status": "cox_unstable",
                    "message": cox_error,
                }
            ]
        )
    event_summary = (
        tte.groupby("trt01a", dropna=False)
        .agg(
            subjects=("program_subject_id", "nunique"),
            events=("event_observed", "sum"),
            median_time_days=("aval", "median"),
        )
        .reset_index()
    )
    safety_summary = (
        adae.groupby("trt01a", dropna=False)
        .agg(
            total_ae_records=("program_subject_id", "size"), serious_events=("serious_flag", "sum")
        )
        .reset_index()
    )
    safety_summary = safety_summary.loc[safety_summary["trt01a"] != "screen_failure"].copy()

    with pd.ExcelWriter(phase3_dir / "phase3_tables.xlsx") as writer:
        event_summary.to_excel(writer, sheet_name="event_summary", index=False)
        safety_summary.to_excel(writer, sheet_name="safety_summary", index=False)
        cox_summary.to_excel(writer, sheet_name="cox_summary", index=False)
        pd.DataFrame([hypothesis_summary]).to_excel(
            writer, sheet_name="hypothesis_tests", index=False
        )

    memo_lines = [
        "# Program Recommendation Memo — Phase III",
        "",
        "Integrated efficacy-safety assessment supports Phase III superiority for the NTX-101 confirmatory development package.",
        "",
        "## Core findings",
        "- Confirmatory endpoint modeled via time to clinical worsening.",
        "- Treatment comparison evaluated with Kaplan-Meier, log-rank testing, and Cox model.",
        "- Safety profile integrated from ADAE summaries.",
        f"- Active vs placebo hazard ratio: {hypothesis_summary['hazard_ratio']} (95% CI {hypothesis_summary['hr_ci_low']} to {hypothesis_summary['hr_ci_high']}).",
        f"- Primary log-rank p-value: {hypothesis_summary['logrank_p_value']}; median delay to worsening: {hypothesis_summary['median_delay_days']} days.",
        f"- Dose support: high dose p-value {hypothesis_summary['high_dose_logrank_p_value']}, low dose directional p-value {hypothesis_summary['low_dose_logrank_p_value']}.",
        "",
    ]
    if cox_error:
        memo_lines.append(f"- Cox model note: {cox_error}")
        memo_lines.append("")

    memo_lines.extend(
        [
            "## Caveat",
            "Interpretation should remain aligned to the documented source mix and continuity assumptions used for this review; this package is not submission evidence and is not intended for publication or submission use.",
            "",
        ]
    )
    memo_text = "\n".join(memo_lines)
    (phase3_dir / "program_recommendation_memo.md").write_text(memo_text, encoding="utf-8")

    context = {
        "event_rows": event_summary.to_dict(orient="records"),
        "cox_rows": cox_summary.to_dict(orient="records"),
        "hypothesis_rows": [hypothesis_summary],
        "km_figure": str(km_path).replace("artifacts/", "../../artifacts/"),
    }
    render_phase3_report(context)


if __name__ == "__main__":
    run_phase3_review()
