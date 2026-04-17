from __future__ import annotations

from pathlib import Path
import json


def test_phase2_outputs_exist() -> None:
    assert Path("docs/phase2/index.html").exists()
    assert Path("artifacts/models/phase2_model_card.md").exists()


def test_model_metrics_contains_auc() -> None:
    payload = json.loads(
        Path("artifacts/models/phase2_model_metrics.json").read_text(encoding="utf-8")
    )
    assert "roc_auc" in payload
