from __future__ import annotations

import pandas as pd


def derive_adeff(efficacy_long: pd.DataFrame) -> pd.DataFrame:
    out = efficacy_long.copy()
    out["paramcd"] = "ADAS11CFB"
    out["aval"] = out["adas_cog11"]
    out["chg"] = out["adas_cog11_change"]
    return out
