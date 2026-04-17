from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv


@dataclass(slots=True)
class SourceRecord:
    source_name: str
    path: str
    format: str
    classification: str
    phase_fit: str
    domain_coverage: str
    disease_signal: str
    use_in_repo: str
    limitations: str


def write_source_inventory(records: list[SourceRecord], output_path: str | Path) -> None:
    if not records:
        raise ValueError("records must not be empty")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(records[0]).keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
