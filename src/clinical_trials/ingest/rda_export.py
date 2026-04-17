from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


def export_rda_directory(
    input_dir: str | Path, output_dir: str | Path
) -> subprocess.CompletedProcess:
    cmd = [
        "Rscript",
        "r/export_safetydata_to_parquet.R",
        str(Path(input_dir)),
        str(Path(output_dir)),
    ]
    env = os.environ.copy()
    env.setdefault("RETICULATE_PYTHON", sys.executable)
    result = subprocess.run(cmd, check=False, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"R export failed: {result.stderr.strip()}")
    return result


def count_exported_parquet(output_dir: str | Path) -> int:
    return len(list(Path(output_dir).glob("*.parquet")))
