from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd


def standardize_columns_to_upper(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).strip().upper() for col in out.columns]
    return out


def add_provenance(df: pd.DataFrame, source_file: str, source_system: str) -> pd.DataFrame:
    out = df.copy()
    out["source_system"] = source_system
    out["source_file"] = source_file
    out["ingested_at"] = datetime.now(UTC).isoformat()
    return out


def normalize_interim_dataframe(
    df: pd.DataFrame, source_file: str, source_system: str
) -> pd.DataFrame:
    out = standardize_columns_to_upper(df)
    out = add_provenance(out, source_file=source_file, source_system=source_system)
    return out
