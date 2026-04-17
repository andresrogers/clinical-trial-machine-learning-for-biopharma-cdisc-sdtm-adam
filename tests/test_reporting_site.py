from __future__ import annotations

from pathlib import Path


def test_docs_home_exists() -> None:
    assert Path("docs/index.html").exists()


def test_lineage_page_exists() -> None:
    assert Path("docs/data_lineage/index.html").exists()
