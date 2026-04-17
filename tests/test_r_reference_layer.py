from __future__ import annotations

from pathlib import Path


def test_r_reference_outputs_exist() -> None:
    assert Path("artifacts/qc/adsl_r_reference.parquet").exists()
    assert Path("artifacts/qc/adae_r_reference.parquet").exists()


def test_r_note_explains_scope_boundary() -> None:
    text = Path("metadata/r_standards_note.md").read_text(encoding="utf-8").lower()
    assert "thin reference layer" in text
    assert "python remains primary" in text
