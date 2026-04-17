from __future__ import annotations

import pandas as pd


ARM_MAP = {
    "placebo": "placebo",
    "xanomeline low dose": "ntx101_low",
    "xanomeline high dose": "ntx101_high",
    "xanomeline": "ntx101_high",
    "screen failure": "screen_failure",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).strip().lower() for col in out.columns]
    return out


def _canonical_treatment(value: object) -> str:
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="ignore").strip().lower()
    else:
        text = str(value).strip().lower()
    if text in ARM_MAP:
        return ARM_MAP[text]
    if "xanomeline" in text and "low" in text:
        return "ntx101_low"
    if "xanomeline" in text and "high" in text:
        return "ntx101_high"
    if "xanomeline" in text:
        return "ntx101_high"
    if "screen" in text and "failure" in text:
        return "screen_failure"
    if text in {"", "nan", "none"}:
        return "unknown"
    return text.replace(" ", "_")


def add_standard_columns(df: pd.DataFrame, phase_label: str = "public_backbone") -> pd.DataFrame:
    out = df.copy()

    out["program_id"] = "NTX-101"
    out["phase_label"] = phase_label

    out["source_study_id"] = out["studyid"] if "studyid" in out.columns else pd.NA
    out["source_usubjid"] = out["usubjid"] if "usubjid" in out.columns else pd.NA

    treatment_source_col = next(
        (col for col in ["arm", "trta", "trtp", "trt01a", "extrt"] if col in out.columns),
        None,
    )
    if treatment_source_col is None:
        out["treatment_arm"] = "unknown"
    else:
        out["treatment_arm"] = out[treatment_source_col].map(_canonical_treatment)

    visit_source_col = next((col for col in ["visit", "avisit"] if col in out.columns), None)
    if visit_source_col is None:
        out["visit_label"] = pd.NA
    else:
        out["visit_label"] = out[visit_source_col]

    return out
