from __future__ import annotations

import pandas as pd


def test_adsl_exists_and_has_flags() -> None:
    df = pd.read_parquet("data/derived/adam_like/alz_program/adsl.parquet")
    assert {"program_subject_id", "ittfl", "saffl"}.issubset(df.columns)


def test_adeff_contains_response_flag() -> None:
    df = pd.read_parquet("data/derived/adam_like/alz_program/adeff.parquet")
    assert {"paramcd", "chg", "response_flag"}.issubset(df.columns)


def test_adtte_contains_censoring_field() -> None:
    df = pd.read_parquet("data/derived/adam_like/alz_program/adtte.parquet")
    assert {"aval", "cnsr", "event_desc"}.issubset(df.columns)
