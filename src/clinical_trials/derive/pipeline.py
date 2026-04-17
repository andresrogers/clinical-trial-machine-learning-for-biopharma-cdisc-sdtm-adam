from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json

import pandas as pd

from clinical_trials.derive.derive_adae import derive_adae
from clinical_trials.derive.derive_adeff import derive_adeff
from clinical_trials.derive.derive_adlb import derive_adlb
from clinical_trials.derive.derive_adsl import derive_adsl
from clinical_trials.derive.derive_adtte import derive_adtte
from clinical_trials.derive.derive_advs import derive_advs


def run_adam_derivations() -> None:
    sdtm_dir = Path("data/derived/sdtm_alz")
    gen_dir = Path("data/generated/alz_program")
    out_dir = Path("data/derived/adam_like/alz_program")
    out_dir.mkdir(parents=True, exist_ok=True)

    ae = pd.read_parquet(sdtm_dir / "ae.parquet")
    lb = pd.read_parquet(sdtm_dir / "lb.parquet")
    vs = pd.read_parquet(sdtm_dir / "vs.parquet")

    subject_master = pd.read_parquet(gen_dir / "subject_master.parquet")
    phase_assignments = pd.read_parquet(gen_dir / "phase_assignments.parquet")
    efficacy_long = pd.read_parquet(gen_dir / "efficacy_long.parquet")
    event_outcomes = pd.read_parquet(gen_dir / "event_outcomes.parquet")

    adsl = derive_adsl(subject_master=subject_master, phase_assignments=phase_assignments)
    adae = derive_adae(ae=ae, adsl=adsl)
    adlb = derive_adlb(lb=lb, adsl=adsl)
    advs = derive_advs(vs=vs, adsl=adsl)
    adeff = derive_adeff(efficacy_long=efficacy_long)
    adtte = derive_adtte(event_outcomes=event_outcomes, adsl=adsl)

    adsl.to_parquet(out_dir / "adsl.parquet", index=False)
    adae.to_parquet(out_dir / "adae.parquet", index=False)
    adlb.to_parquet(out_dir / "adlb.parquet", index=False)
    advs.to_parquet(out_dir / "advs.parquet", index=False)
    adeff.to_parquet(out_dir / "adeff.parquet", index=False)
    adtte.to_parquet(out_dir / "adtte.parquet", index=False)

    qc_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "row_counts": {
            "adsl": int(len(adsl)),
            "adae": int(len(adae)),
            "adlb": int(len(adlb)),
            "advs": int(len(advs)),
            "adeff": int(len(adeff)),
            "adtte": int(len(adtte)),
        },
    }
    qc_path = Path("artifacts/qc/adam_qc_summary.json")
    qc_path.parent.mkdir(parents=True, exist_ok=True)
    qc_path.write_text(json.dumps(qc_payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run_adam_derivations()
