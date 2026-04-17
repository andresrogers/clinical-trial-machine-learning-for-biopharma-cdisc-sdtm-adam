from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json

import pandas as pd

from clinical_trials.validation.checks import (
    assert_allowed_values,
    assert_non_null,
    assert_ranges,
    assert_required_columns,
    assert_unique_key,
)
from clinical_trials.validation.schemas import load_schema_spec


def validate_raw_interim_dataset(dataset_name: str, rules: dict) -> dict:
    path = Path(f"data/interim/cdisc_pilot/{dataset_name}.parquet")
    df = pd.read_parquet(path)

    assert_required_columns(df, rules.get("required_columns", []))
    assert_non_null(df, rules.get("non_null_columns", []))

    if "unique_key" in rules:
        assert_unique_key(df, rules["unique_key"])
    if "allowed_values" in rules:
        assert_allowed_values(df, rules["allowed_values"])
    if "ranges" in rules:
        assert_ranges(df, rules["ranges"])

    return {
        "dataset": dataset_name,
        "path": str(path),
        "rows": int(len(df)),
        "status": "pass",
    }


def run_raw_interim_schema_validation() -> dict:
    spec = load_schema_spec("metadata/schemas/raw_interim.yml")
    dataset_rules = spec.get("datasets", {})

    results: list[dict] = []
    failures: list[dict] = []

    for dataset_name, rules in dataset_rules.items():
        try:
            results.append(validate_raw_interim_dataset(dataset_name, rules))
        except Exception as exc:  # noqa: BLE001
            failures.append({"dataset": dataset_name, "status": "fail", "error": str(exc)})

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "validated_layer": "raw_interim",
        "total_datasets": len(dataset_rules),
        "passes": len(results),
        "failures": len(failures),
        "results": results,
        "errors": failures,
    }

    qc_path = Path("artifacts/qc/schema_validation_summary.json")
    qc_path.parent.mkdir(parents=True, exist_ok=True)
    qc_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if failures:
        raise RuntimeError(f"Schema validation failed for {len(failures)} dataset(s)")

    return summary


if __name__ == "__main__":
    run_raw_interim_schema_validation()
