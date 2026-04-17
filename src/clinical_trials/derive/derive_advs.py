from __future__ import annotations

import pandas as pd


def derive_advs(vs: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    out = vs.merge(
        adsl[["program_subject_id", "source_usubjid", "trt01a"]],
        on="source_usubjid",
        how="left",
    )

    out["paramcd"] = out.get("vstestcd", "VSPARAM")
    out["aval"] = pd.to_numeric(out.get("vsstresn"), errors="coerce")

    baseline = (
        out.loc[out.get("vsblfl", "").astype(str).str.upper().eq("Y")]
        .groupby(["program_subject_id", "paramcd"], dropna=False)["aval"]
        .first()
        .reset_index()
        .rename(columns={"aval": "base"})
    )
    out = out.merge(baseline, on=["program_subject_id", "paramcd"], how="left")
    out["chg"] = out["aval"] - out["base"]
    return out
