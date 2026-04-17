from __future__ import annotations

from pathlib import Path


def test_safetydata_export_has_outputs() -> None:
    files = list(Path("data/interim/safetydata").glob("*.parquet"))
    assert len(files) > 0


def test_ingestion_qc_files_exist() -> None:
    assert Path("artifacts/qc/ingestion_summary.json").exists()
    assert Path("artifacts/qc/ingestion_row_counts.csv").exists()
