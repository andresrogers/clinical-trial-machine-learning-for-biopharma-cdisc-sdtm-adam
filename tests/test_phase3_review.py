from __future__ import annotations

from pathlib import Path


def test_phase3_outputs_exist() -> None:
    assert Path("docs/phase3/index.html").exists()
    assert Path("artifacts/phase3/program_recommendation_memo.md").exists()


def test_phase3_memo_has_non_submission_language() -> None:
    text = (
        Path("artifacts/phase3/program_recommendation_memo.md").read_text(encoding="utf-8").lower()
    )
    assert "not submission evidence" in text or "portfolio simulation" in text
