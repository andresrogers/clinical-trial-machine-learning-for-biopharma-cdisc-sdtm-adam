from __future__ import annotations

from pathlib import Path

import pandas as pd


def test_source_inventory_has_required_columns() -> None:
    df = pd.read_csv("metadata/source_inventory.csv")
    required = {
        "source_name",
        "path",
        "format",
        "classification",
        "phase_fit",
        "domain_coverage",
        "disease_signal",
        "use_in_repo",
        "limitations",
    }
    assert required.issubset(df.columns)


def test_disease_signal_index_mentions_alzheimers() -> None:
    text = Path("metadata/disease_signal_index.md").read_text(encoding="utf-8").lower()
    assert "alzheimer" in text
    assert "xanomeline" in text
