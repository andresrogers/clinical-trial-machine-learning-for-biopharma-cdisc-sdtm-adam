from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json

import pandas as pd

from clinical_trials.settings import load_program_settings
from clinical_trials.synthetic.continuity import (
    build_phase_assignments,
    build_subject_master,
    build_visit_schedule,
)
from clinical_trials.synthetic.efficacy import simulate_phase2_efficacy
from clinical_trials.synthetic.events import simulate_phase3_event_outcomes


def run_synthetic_bridge() -> None:
    settings = load_program_settings()
    seed = settings.seed

    dm = pd.read_parquet("data/derived/sdtm_alz/dm.parquet")
    subject_master = build_subject_master(dm, seed=seed)
    phase_assignments = build_phase_assignments(subject_master, seed=seed)
    visit_schedule = build_visit_schedule()
    efficacy = simulate_phase2_efficacy(subject_master, phase_assignments, seed=seed)
    outcomes = simulate_phase3_event_outcomes(subject_master, phase_assignments, seed=seed)

    out_dir = Path("data/generated/alz_program")
    out_dir.mkdir(parents=True, exist_ok=True)
    subject_master.to_parquet(out_dir / "subject_master.parquet", index=False)
    phase_assignments.to_parquet(out_dir / "phase_assignments.parquet", index=False)
    visit_schedule.to_parquet(out_dir / "visit_schedule.parquet", index=False)
    efficacy.to_parquet(out_dir / "efficacy_long.parquet", index=False)
    outcomes.to_parquet(out_dir / "event_outcomes.parquet", index=False)

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "subject_master_rows": int(len(subject_master)),
        "phase_assignments_rows": int(len(phase_assignments)),
        "visit_schedule_rows": int(len(visit_schedule)),
        "efficacy_rows": int(len(efficacy)),
        "event_outcomes_rows": int(len(outcomes)),
    }
    qc_dir = Path("artifacts/qc")
    qc_dir.mkdir(parents=True, exist_ok=True)
    (qc_dir / "synthetic_bridge_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    run_synthetic_bridge()
