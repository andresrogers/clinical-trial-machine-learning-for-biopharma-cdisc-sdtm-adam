from __future__ import annotations

from clinical_trials.settings import load_program_settings


def main() -> None:
    settings = load_program_settings()
    print(settings.program_id)


if __name__ == "__main__":
    main()
