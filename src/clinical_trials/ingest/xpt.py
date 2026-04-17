from __future__ import annotations

from pathlib import Path

import pandas as pd

from clinical_trials.ingest.normalize import normalize_interim_dataframe


REQUIRED_XPT_DOMAINS = (
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
)


def read_xpt_domain(path: str | Path) -> pd.DataFrame:
    return pd.read_sas(Path(path), format="xport")


def ingest_xpt_to_parquet(input_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    source_path = Path(input_path)
    df = read_xpt_domain(source_path)
    normalized = normalize_interim_dataframe(
        df,
        source_file=source_path.name,
        source_system="cdisc_pilot_xpt",
    )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_parquet(destination, index=False)
    return normalized


def ingest_all_xpt(
    input_dir: str | Path = "data/external/cdisc_pilot/raw_xpt",
    output_dir: str | Path = "data/interim/cdisc_pilot",
) -> dict[str, int]:
    input_root = Path(input_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    row_counts: dict[str, int] = {}
    for domain in REQUIRED_XPT_DOMAINS:
        input_path = input_root / f"{domain}.xpt"
        output_path = output_root / f"{domain}.parquet"
        frame = ingest_xpt_to_parquet(input_path=input_path, output_path=output_path)
        row_counts[domain] = len(frame)

    return row_counts
