from __future__ import annotations

from pathlib import Path

import pandas as pd


def test_cdisc_pilot_interim_files_exist() -> None:
    expected = [
        "dm",
        "ae",
        "lb",
        "vs",
        "ex",
        "ds",
        "adsl",
        "adae",
        "adlbc",
        "adlbh",
        "adtte",
        "advs",
    ]
    for name in expected:
        assert Path(f"data/interim/cdisc_pilot/{name}.parquet").exists()


def test_provenance_columns_present_in_dm() -> None:
    df = pd.read_parquet("data/interim/cdisc_pilot/dm.parquet")
    for col in ["source_system", "source_file", "ingested_at"]:
        assert col in df.columns
