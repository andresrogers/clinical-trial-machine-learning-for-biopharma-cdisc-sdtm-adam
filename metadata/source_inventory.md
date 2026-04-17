# Source Inventory

This file records all currently available source families and decisions for the `NTX-101` Alzheimer’s program.

## Source classification summary

| Source name | Path | Classification | Role in repo |
|---|---|---|---|
| cdisc_pilot_raw_xpt | `data/external/cdisc_pilot/raw_xpt` | core | Primary raw clinical structure for ingestion and interim parquet conversion |
| cdisc_pilot_metadata_xml | `data/external/cdisc_pilot/metadata/define.xml` | reference_only | Metadata context for standards awareness |
| cdisc_pilot_metadata_pdf | `data/external/cdisc_pilot/metadata/define.pdf` | reference_only | Human-readable standards context |
| cdisc_pilot_csr_pdf | `data/external/cdisc_pilot/csr/cdiscpilot01.pdf` | reference_only | Clinical report context |
| cdisc_pilot_csr_narratives | `data/external/cdisc_pilot/csr/narratives.txt` | reference_only | Disease signal evidence for Alzheimer’s narrative lock |
| safetydata_rda_bundle | `data/external/safetydata` | supplemental | Additional safety and ADaM-like example structures |
| clintrialdata_archive | `data/external/clintrialdata/clinTrialData_0.1.3.tar.gz` | reference_only | Optional package-based reference source |
| pharmaverse_links | `docs/reference/pharmaverse/links.txt` | reference_only | Workflow reference links |
| regulatory_links | `docs/reference/regulatory/links.txt` | reference_only | Standards and guidance links |
| download_archives | `data/external/archives` | rejected | Download artifacts only |

## Notes
- Core analytics should begin from parquet files generated from `cdisc_pilot_raw_xpt`.
- Supplemental safety enrichment comes from RDA-parsed SafetyData objects.
- Sources in `reference_only` are for framing, standards literacy, and traceability, not direct model training input.
