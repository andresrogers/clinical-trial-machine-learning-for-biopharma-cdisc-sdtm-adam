from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class ProgramSettings:
    program_id: str
    indication: str
    molecule: str
    seed: int
    raw_sources: dict
    working_directories: dict
    phase_studies: dict
    portfolio_disclaimer: str
    asset_type: str | None = None
    asset_rationale: str | None = None


def load_yaml(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_program_settings(path: str | Path = "config/program_config.yml") -> ProgramSettings:
    payload = load_yaml(path)
    return ProgramSettings(**payload)
