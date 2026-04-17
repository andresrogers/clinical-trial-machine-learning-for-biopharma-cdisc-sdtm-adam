from __future__ import annotations

from pathlib import Path

import pandas as pd


def compare_shapes(python_path: str, r_path: str, dataset_label: str) -> pd.DataFrame:
    py_df = pd.read_parquet(python_path)
    r_df = pd.read_parquet(r_path)
    return pd.DataFrame(
        [
            {
                "dataset": dataset_label,
                "python_path": python_path,
                "r_path": r_path,
                "python_rows": len(py_df),
                "r_rows": len(r_df),
                "row_diff": len(py_df) - len(r_df),
            }
        ]
    )


def write_default_r_python_comparisons() -> None:
    output_dir = Path("artifacts/qc")
    output_dir.mkdir(parents=True, exist_ok=True)

    adsl_cmp = compare_shapes(
        "data/derived/adam_like/alz_program/adsl.parquet",
        "artifacts/qc/adsl_r_reference.parquet",
        "adsl",
    )
    adsl_cmp.to_csv(output_dir / "r_python_comparison_adsl.csv", index=False)

    adae_cmp = compare_shapes(
        "data/derived/adam_like/alz_program/adae.parquet",
        "artifacts/qc/adae_r_reference.parquet",
        "adae",
    )
    adae_cmp.to_csv(output_dir / "r_python_comparison_adae.csv", index=False)


if __name__ == "__main__":
    write_default_r_python_comparisons()
