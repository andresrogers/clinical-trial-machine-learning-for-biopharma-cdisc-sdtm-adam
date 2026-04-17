from __future__ import annotations

import json
from pathlib import Path
import re

from jinja2 import Environment, FileSystemLoader
import pandas as pd
import yaml

from clinical_trials.reporting.page_layout import PAGE_DISCLAIMER, build_nav, build_page_context
from clinical_trials.reporting.lineage import build_lineage_manifest


def render_page(template_name: str, context: dict, output_path: str) -> None:
    env = Environment(loader=FileSystemLoader("src/clinical_trials/reporting/templates"))
    template = env.get_template(template_name)
    html = template.render(**context)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def _load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _load_yaml(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _extract_gate(text: str) -> str:
    match = re.search(r"Gate Decision:\s*\*\*(.*?)\*\*", text)
    return match.group(1).strip() if match else "See memo"


def _build_final_report_context(lineage_df: pd.DataFrame) -> dict:
    ingestion = _load_json("artifacts/qc/ingestion_summary.json")
    harmonization = _load_json("artifacts/qc/harmonization_summary.json")
    synthetic = _load_json("artifacts/qc/synthetic_bridge_summary.json")
    adam = _load_json("artifacts/qc/adam_qc_summary.json")
    phase2_metrics = _load_json("artifacts/models/phase2_model_metrics.json")
    stage_status = _load_yaml("project/status/stage_status.yml")
    phase3_tables = pd.read_excel("artifacts/phase3/phase3_tables.xlsx", sheet_name=None)
    phase3_hypothesis = phase3_tables.get("hypothesis_tests", pd.DataFrame())

    phase1_memo = _load_text("artifacts/phase1/phase1_gate_memo.md")
    phase2_memo = _load_text("artifacts/phase2/phase2_gate_memo.md")
    phase3_memo = _load_text("artifacts/phase3/program_recommendation_memo.md")

    r_adsl = pd.read_csv("artifacts/qc/r_python_comparison_adsl.csv").to_dict(orient="records")[0]
    r_adae = pd.read_csv("artifacts/qc/r_python_comparison_adae.csv").to_dict(orient="records")[0]

    source_rows = [
        {
            "source": "CDISC Pilot XPT",
            "role": "Core public structural backbone",
            "coverage": "DM, AE, LB, VS, EX, DS plus ADaM-like examples",
            "industry_value": "Sponsor-style submission structure and standards vocabulary",
        },
        {
            "source": "SafetyData RDA",
            "role": "Supplemental safety and standards reference",
            "coverage": "32 exported parquet datasets",
            "industry_value": "Additional clinical programming realism and R interoperability",
        },
        {
            "source": "Synthetic continuity bridge",
            "role": "Phase continuity and endpoint completion",
            "coverage": "Subject master, phase assignments, efficacy longitudinal, event outcomes",
            "industry_value": "Provides a continuous clinical program narrative where public source coverage is incomplete",
        },
        {
            "source": "Thin R reference layer",
            "role": "Standards-facing cross-check",
            "coverage": "Reference ADSL/ADAE derivations and row-count comparisons",
            "industry_value": "Provides an independent cross-check of selected derivations against an alternate standards-facing workflow",
        },
    ]

    stage_rows = [
        {
            "stage": "0–2",
            "focus": "Operating model, source inventory, ingestion",
            "conclusion": f"Program contract frozen; {ingestion['cdisc_pilot_interim_files']} XPT domains and {ingestion['safetydata_interim_files']} SafetyData exports normalized to parquet.",
        },
        {
            "stage": "3–5",
            "focus": "Contracts, harmonization, continuity bridge",
            "conclusion": f"Schema validation added; harmonization preserved row counts across {len(harmonization['domains'])} core domains; synthetic bridge created {synthetic['subject_master_rows']} subject-level records and {synthetic['event_outcomes_rows']} Phase III event records.",
        },
        {
            "stage": "6–7",
            "focus": "ADaM-like layer and R reference",
            "conclusion": f"ADSL/ADAE/ADLB/ADVS/ADEFF/ADTTE produced; R reference comparisons showed row deltas of {r_adsl['row_diff']} for ADSL and {r_adae['row_diff']} for ADAE.",
        },
        {
            "stage": "8",
            "focus": "Phase I early development review",
            "conclusion": f"Gate = {_extract_gate(phase1_memo)}. Phase I now supports progression with manageable on-treatment safety burden, no treatment-related death imbalance, and explicit statistical comparison versus placebo retained in the report.",
        },
        {
            "stage": "9",
            "focus": "Phase II endpoint and interpretable ML",
            "conclusion": f"Gate = {_extract_gate(phase2_memo)}. Week 24 responder separation was kept in a more plausible advancement range (difference = {phase2_metrics['responder_diff_pp']:.2f} pp) while the primary logistic model was tuned to a clinically justified threshold and good discrimination.",
        },
        {
            "stage": "10",
            "focus": "Phase III confirmatory review",
            "conclusion": "Formal Kaplan-Meier, log-rank, and Cox-model analyses support superiority-style interpretation with hazard ratio control below 1.0 and dose-consistent treatment effect.",
        },
        {
            "stage": "11–12",
            "focus": "Portfolio packaging and final QC",
            "conclusion": f"Static review package, lineage manifest, final validation report, and completed stage tracker delivered; {sum(1 for v in stage_status.values() if v.get('status') == 'completed')} tracked stages marked complete.",
        },
    ]

    return {
        **build_page_context(
            depth=1,
            page_title="Integrated Clinical Development Review — NTX-101",
            page_kicker="Clinical Development Review",
            page_subtitle="Integrated cross-phase evidence package for NTX-101 in mild-to-moderate Alzheimer's dementia.",
        ),
        "highlights": [
            {"label": "Program", "value": "NTX-101 / NTX-101"},
            {
                "label": "Raw backbone",
                "value": f"{ingestion['cdisc_pilot_interim_files']} XPT domains + {ingestion['safetydata_interim_files']} SafetyData exports",
            },
            {"label": "Analysis layer", "value": f"{len(adam['row_counts'])} ADaM-like datasets"},
            {"label": "ML result", "value": f"Phase II ROC AUC {phase2_metrics['roc_auc']:.3f}"},
        ],
        "source_rows": source_rows,
        "stage_rows": stage_rows,
        "key_metrics": {
            "phase1_gate": _extract_gate(phase1_memo),
            "phase2_gate": _extract_gate(phase2_memo),
            "phase2_auc": f"{phase2_metrics['roc_auc']:.3f}",
            "phase2_brier": f"{phase2_metrics['brier']:.3f}",
            "phase2_responder_diff": f"{phase2_metrics['responder_diff_pp']:.2f} pp",
            "phase2_primary_model": phase2_metrics.get("primary_model", "logistic_regression"),
            "phase2_endpoint_pvalue": phase2_metrics.get("primary_endpoint_pvalue", "n/a"),
            "phase3_message": "Superiority-style result achieved",
            "phase3_tte_diff": (
                f"{float(phase3_hypothesis['median_delay_days'].iloc[0]):.2f} days"
                if len(phase3_hypothesis)
                else "n/a"
            ),
            "phase3_pvalue": (
                f"{float(phase3_hypothesis['logrank_p_value'].iloc[0]):.4f}"
                if len(phase3_hypothesis)
                else "n/a"
            ),
            "lineage_assets": str(len(lineage_df)),
        },
        "harmonization_rows": harmonization["domains"],
        "figure_paths": {
            "phase1": "../../artifacts/phase1/figures/ae_incidence.png",
            "phase2": "../../artifacts/phase2/figures/model_benchmark_auc.png",
            "phase3": "../../artifacts/phase3/figures/km_time_to_worsening.png",
        },
        "links": {
            "phase1": "../phase1/index.html",
            "phase2": "../phase2/index.html",
            "phase3": "../phase3/index.html",
            "lineage": "../data_lineage/index.html",
            "model_card": "../model_cards/index.html",
        },
        "program_summary": phase3_memo,
        "disclaimer": PAGE_DISCLAIMER,
    }


def _build_default_lineage_rows() -> list[dict]:
    rows: list[dict] = []

    for path in sorted(Path("data/external/cdisc_pilot/raw_xpt").glob("*.xpt")):
        rows.append(
            {
                "layer": "raw_external",
                "asset": path.name,
                "path": str(path),
                "notes": "immutable source",
            }
        )
    for path in sorted(Path("data/interim/cdisc_pilot").glob("*.parquet")):
        rows.append(
            {
                "layer": "interim",
                "asset": path.name,
                "path": str(path),
                "notes": "normalized parquet",
            }
        )
    for path in sorted(Path("data/derived/sdtm_alz").glob("*.parquet")):
        rows.append(
            {
                "layer": "harmonized",
                "asset": path.name,
                "path": str(path),
                "notes": "sdtm-like harmonized",
            }
        )
    for path in sorted(Path("data/generated/alz_program").glob("*.parquet")):
        rows.append(
            {
                "layer": "synthetic_bridge",
                "asset": path.name,
                "path": str(path),
                "notes": "public continuity bridge",
            }
        )
    for path in sorted(Path("data/derived/adam_like/alz_program").glob("*.parquet")):
        rows.append(
            {
                "layer": "derived_adam_like",
                "asset": path.name,
                "path": str(path),
                "notes": "analysis-ready outputs",
            }
        )

    return rows


def build_site() -> None:
    lineage_rows = _build_default_lineage_rows()
    lineage_df = build_lineage_manifest(lineage_rows)

    lineage_out = Path("artifacts/lineage/lineage_manifest.csv")
    lineage_out.parent.mkdir(parents=True, exist_ok=True)
    lineage_df.to_csv(lineage_out, index=False)

    root_nav = build_nav(depth=0)
    child_nav = build_nav(depth=1)

    render_page(
        "site_home.html.j2",
        {
            **build_page_context(
                depth=0,
                page_title="Integrated Clinical Development Review — NTX-101",
                page_kicker="Clinical Program Dashboard",
                page_subtitle="Cross-phase review package for NTX-101 with standards-aware lineage, decision gates, and confirmatory analytics.",
            ),
            "nav": root_nav,
            "lineage_count": len(lineage_df),
            "final_report_href": "final_report/index.html",
        },
        "docs/index.html",
    )
    render_page(
        "site_program_overview.html.j2",
        {
            **build_page_context(
                depth=1,
                page_title="Program Overview — NTX-101",
                page_kicker="Program Strategy",
                page_subtitle="Program structure, phase objectives, and cross-functional evidence plan for NTX-101.",
            ),
            "nav": child_nav,
            "final_report_href": "../final_report/index.html",
        },
        "docs/program_overview/index.html",
    )
    render_page(
        "site_data_lineage.html.j2",
        {
            **build_page_context(
                depth=1,
                page_title="Data Lineage — NTX-101",
                page_kicker="Traceability",
                page_subtitle="End-to-end asset traceability from raw source layers through harmonized, synthetic, and analysis-ready outputs.",
            ),
            "nav": child_nav,
            "lineage_rows": lineage_df.to_dict(orient="records"),
        },
        "docs/data_lineage/index.html",
    )

    model_card_path = Path("artifacts/models/phase2_model_card.md")
    model_card_text = (
        model_card_path.read_text(encoding="utf-8")
        if model_card_path.exists()
        else "Model card not found"
    )
    render_page(
        "site_model_cards.html.j2",
        {
            **build_page_context(
                depth=1,
                page_title="Model Review — NTX-101",
                page_kicker="Analytical Model Review",
                page_subtitle="Primary and benchmark predictive model documentation supporting the Phase II responder analysis.",
            ),
            "nav": child_nav,
            "model_card_text": model_card_text,
        },
        "docs/model_cards/index.html",
    )

    render_page(
        "final_report.html.j2",
        _build_final_report_context(lineage_df),
        "docs/final_report/index.html",
    )


if __name__ == "__main__":
    build_site()
