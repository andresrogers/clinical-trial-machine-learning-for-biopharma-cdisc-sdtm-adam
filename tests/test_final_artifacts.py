from __future__ import annotations

from pathlib import Path


def test_core_docs_exist() -> None:
    for path in [
        "docs/index.html",
        "docs/phase1/index.html",
        "docs/phase2/index.html",
        "docs/phase3/index.html",
    ]:
        assert Path(path).exists()


def test_status_files_exist() -> None:
    for path in [
        "project/status/stage_status.yml",
        "project/status/open_issues.md",
        "project/status/artifact_checklist.md",
        "project/status/schema_change_log.md",
        "project/status/source_decisions.md",
    ]:
        assert Path(path).exists()
