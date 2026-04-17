from __future__ import annotations

from clinical_trials.settings import load_program_settings, load_yaml


def test_program_config_loads() -> None:
    settings = load_program_settings()
    assert settings.program_id == "NTX-101"
    assert settings.seed == 20260416
    assert settings.indication == "mild_to_moderate_alzheimers_dementia"


def test_phase_protocols_exist() -> None:
    for path in [
        "config/phase_1_protocol.yml",
        "config/phase_2_protocol.yml",
        "config/phase_3_protocol.yml",
    ]:
        assert load_yaml(path)
