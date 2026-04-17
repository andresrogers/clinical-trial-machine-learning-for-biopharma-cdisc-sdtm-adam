from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json

import pandas as pd

from clinical_trials.ingest.rda_export import count_exported_parquet, export_rda_directory
from clinical_trials.ingest.xpt import ingest_all_xpt


def build_ingestion_row_count_table() -> pd.DataFrame:
    rows: list[dict] = []

    for parquet_path in sorted(Path("data/interim/cdisc_pilot").glob("*.parquet")):
        rows.append(
            {
                "source_family": "cdisc_pilot_xpt",
                "dataset": parquet_path.stem,
                "path": str(parquet_path),
                "rows": int(len(pd.read_parquet(parquet_path))),
            }
        )

    for parquet_path in sorted(Path("data/interim/safetydata").glob("*.parquet")):
        rows.append(
            {
                "source_family": "safetydata_rda",
                "dataset": parquet_path.stem,
                "path": str(parquet_path),
                "rows": int(len(pd.read_parquet(parquet_path))),
            }
        )

    return pd.DataFrame(rows)


def write_ingestion_qc_artifacts() -> None:
    qc_dir = Path("artifacts/qc")
    qc_dir.mkdir(parents=True, exist_ok=True)

    table = build_ingestion_row_count_table()
    table_path = qc_dir / "ingestion_row_counts.csv"
    table.to_csv(table_path, index=False)

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "cdisc_pilot_interim_files": len(list(Path("data/interim/cdisc_pilot").glob("*.parquet"))),
        "safetydata_interim_files": len(list(Path("data/interim/safetydata").glob("*.parquet"))),
        "row_count_table": str(table_path),
    }
    (qc_dir / "ingestion_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


def run_stage_02_ingestion() -> None:
    ingest_all_xpt()
    export_rda_directory(
        input_dir="data/external/safetydata",
        output_dir="data/interim/safetydata",
    )

    if count_exported_parquet("data/interim/safetydata") == 0:
        raise RuntimeError("No safetydata parquet files were exported from RDA sources")

    write_ingestion_qc_artifacts()


if __name__ == "__main__":
    run_stage_02_ingestion()
