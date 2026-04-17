from __future__ import annotations

import pandas as pd


def build_lineage_manifest(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)
