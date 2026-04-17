from __future__ import annotations

import pandas as pd


def assert_required_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise AssertionError(f"Missing required columns: {missing}")


def assert_unique_key(df: pd.DataFrame, keys: list[str]) -> None:
    if df.duplicated(keys).any():
        raise AssertionError(f"Duplicate key rows found for {keys}")


def assert_non_null(df: pd.DataFrame, columns: list[str]) -> None:
    bad = [col for col in columns if df[col].isna().any()]
    if bad:
        raise AssertionError(f"Null values found in mandatory columns: {bad}")


def assert_allowed_values(df: pd.DataFrame, mapping: dict[str, list]) -> None:
    def _normalize(value: object) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore").strip()
        return str(value).strip()

    for column, allowed in mapping.items():
        if column not in df.columns:
            continue

        observed = {_normalize(v) for v in df[column].dropna().tolist()}
        allowed_set = {_normalize(v) for v in allowed}
        if not observed.issubset(allowed_set):
            extra = sorted(observed.difference(allowed_set))
            raise AssertionError(f"Unexpected values in {column}: {extra}")


def assert_ranges(df: pd.DataFrame, ranges: dict[str, dict]) -> None:
    for column, bounds in ranges.items():
        if column not in df.columns:
            continue

        series = pd.to_numeric(df[column], errors="coerce").dropna()
        min_bound = bounds.get("min")
        max_bound = bounds.get("max")

        if min_bound is not None and (series < min_bound).any():
            raise AssertionError(f"Range violation: {column} has values below {min_bound}")
        if max_bound is not None and (series > max_bound).any():
            raise AssertionError(f"Range violation: {column} has values above {max_bound}")
