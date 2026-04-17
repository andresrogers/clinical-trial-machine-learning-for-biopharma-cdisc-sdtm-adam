# Final Validation Report — ALZ-XM-001 Portfolio

## Environment summary
- Python package validation executed via `make validate`.
- Required Python analytics/reporting dependencies imported successfully.
- Optional R layer scripts executed for reference derivations.

## Data lineage summary
- Raw external inputs (`.xpt`, `.rda`) ingested into parquet interim layer.
- Harmonized SDTM-like parquet outputs produced under `data/derived/sdtm_alz/`.
- Synthetic continuity bridge outputs produced under `data/generated/alz_program/`.
- ADaM-like analysis datasets produced under `data/derived/adam_like/alz_program/`.
- Lineage manifest generated at `artifacts/lineage/lineage_manifest.csv`.

## Test results
- Full suite executed with `pytest -q`.
- Result: passing (see `artifacts/qc/test_summary.txt`).

## Lint results
- Repository lint executed with `ruff check .`.
- Result: passing (see `artifacts/qc/lint_summary.txt`).

## Open known limitations
- SafetyData RDA conversion may flatten some source-specific attributes not represented in flat tabular outputs.
- Cox model may be unstable in certain synthetic draws with low treatment-group variance; implementation logs this and still provides KM and event summaries.
- Portfolio outputs are educational and exploratory.

## Portfolio honesty statement
This repository is portfolio simulation work built from public structural sources and synthetic continuity assumptions. It is not sponsor production work, not GxP validated, and not regulatory submission evidence.

## Remaining non-MVP items
- Optional causal appendix remains deferred.
- Optional advanced dashboard layer remains out of MVP scope.
