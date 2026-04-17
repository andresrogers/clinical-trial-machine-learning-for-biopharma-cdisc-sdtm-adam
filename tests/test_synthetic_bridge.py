from __future__ import annotations

import pandas as pd


def test_subject_master_contains_program_subject_id() -> None:
    df = pd.read_parquet("data/generated/alz_program/subject_master.parquet")
    assert "program_subject_id" in df.columns
    assert df["program_subject_id"].is_unique


def test_phase2_efficacy_contains_week24_rows() -> None:
    df = pd.read_parquet("data/generated/alz_program/efficacy_long.parquet")
    assert (df["visit_week"] == 24).any()
    assert "response_flag" in df.columns
