from __future__ import annotations

from pathlib import Path


def assert_required_artifacts(paths: list[str]) -> None:
    missing = [path for path in paths if not Path(path).exists()]
    if missing:
        raise AssertionError(f"Missing final artifacts: {missing}")
