from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json

import pandas as pd

from clinical_trials.harmonize.map_cdisc import add_standard_columns, normalize_columns


REQUIRED_DOMAINS = ("dm", "ae", "lb", "vs", "ex", "ds")


def harmonize_domain(input_path: str | Path, output_path: str | Path) -> tuple[int, int]:
    df = pd.read_parquet(input_path)
    in_rows = len(df)
    df = normalize_columns(df)
    df = add_standard_columns(df)
    out_rows = len(df)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destination, index=False)
    return in_rows, out_rows


def run_harmonization(
    interim_dir: str | Path = "data/interim/cdisc_pilot",
    output_dir: str | Path = "data/derived/sdtm_alz",
) -> None:
    interim_root = Path(interim_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    provenance_rows: list[dict] = []
    summary_rows: list[dict] = []

    for domain in REQUIRED_DOMAINS:
        input_path = interim_root / f"{domain}.parquet"
        output_path = output_root / f"{domain}.parquet"

        in_rows, out_rows = harmonize_domain(input_path, output_path)
        provenance_rows.append(
            {
                "source_file": f"{domain}.xpt",
                "interim_file": str(input_path),
                "harmonized_file": str(output_path),
            }
        )
        summary_rows.append(
            {
                "domain": domain,
                "input_rows": in_rows,
                "output_rows": out_rows,
                "row_delta": out_rows - in_rows,
            }
        )

    metadata_dir = Path("metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(provenance_rows).to_csv(metadata_dir / "provenance_map.csv", index=False)

    qc_dir = Path("artifacts/qc")
    qc_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "domains": summary_rows,
    }
    (qc_dir / "harmonization_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    run_harmonization()
