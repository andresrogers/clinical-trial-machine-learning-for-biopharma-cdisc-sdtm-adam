# Acquisition Log

## Snapshot date
2026-04-16

## Acquisition status
- Source files are already present in this repository under `data/external/`.
- Sources are treated as immutable raw inputs.
- The project ingestion contract is:

```text
raw external data (.xpt, .rda) -> interim normalized parquet -> derived analysis datasets -> modeling/reporting artifacts
```

## Source families recorded
- CDISC pilot raw XPT and metadata
- CDISC pilot CSR narrative assets
- SafetyData RDA bundle
- clinTrialData source archive
- Pharmaverse and regulatory reference links

## Operational note
No additional source downloads were required for Stage 01.
