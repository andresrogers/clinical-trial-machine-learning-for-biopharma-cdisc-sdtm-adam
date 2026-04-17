from __future__ import annotations

import pandas as pd


def test_harmonized_dm_contains_program_id() -> None:
    df = pd.read_parquet("data/derived/sdtm_alz/dm.parquet")
    assert "program_id" in df.columns
    assert df["program_id"].eq("NTX-101").all()


def test_provenance_map_exists() -> None:
    df = pd.read_csv("metadata/provenance_map.csv")
    assert {"source_file", "interim_file", "harmonized_file"}.issubset(df.columns)
