from __future__ import annotations

from pathlib import Path


def test_phase1_outputs_exist() -> None:
    assert Path("docs/phase1/index.html").exists()
    assert Path("artifacts/phase1/phase1_gate_memo.md").exists()


def test_phase1_gate_memo_mentions_limitations() -> None:
    text = Path("artifacts/phase1/phase1_gate_memo.md").read_text(encoding="utf-8").lower()
    assert "limitations" in text
