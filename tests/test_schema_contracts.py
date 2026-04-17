from __future__ import annotations

from pathlib import Path

import yaml


def test_schema_files_exist() -> None:
    for path in [
        "metadata/schemas/raw_interim.yml",
        "metadata/schemas/harmonized_sdtm.yml",
        "metadata/schemas/adam_like.yml",
    ]:
        assert Path(path).exists()
        assert yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_identifier_policy_mentions_program_subject_id() -> None:
    text = Path("metadata/identifier_policy.md").read_text(encoding="utf-8")
    assert "program_subject_id" in text
