# Clinical Trial Machine Learning Portfolio: CDISC SDTM ADaM Workflow for Clinical Development

> Python-first clinical trial machine learning portfolio for Phase I-III clinical development using CDISC-aligned data, SDTM/ADaM-style workflows, safety analytics, endpoint modeling, survival analysis, and interpretable ML for BioPharma.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#environment-setup)
[![R](https://img.shields.io/badge/R-optional-blueviolet.svg)](#hybrid-stack)
[![Clinical Development](https://img.shields.io/badge/Clinical-Phase%20I--III-0a7f62.svg)](#project-overview)
[![Standards](https://img.shields.io/badge/CDISC-SDTM%20%7C%20ADaM-1f4e79.svg)](#clinical-data-standards)

## Project Overview

This repository is a clinical trial data science and machine learning portfolio project designed to mirror how advanced analytics is applied in clinical development. It is structured as one end-to-end BioPharma program progressing through Phase I, Phase II, and Phase III, with clear phase gates, standards-aware datasets, interpretable models, and stakeholder-facing reporting.

The project emphasizes real industry workflow patterns over academic depth:
- Phase I clinical trial analytics: safety, tolerability, cohort review, labs, and vital signs.
- Phase II clinical trial analytics: endpoint review, responder analysis, longitudinal trends, subgroup exploration, and interpretable machine learning.
- Phase III clinical trial analytics: confirmatory endpoint analysis, survival analysis or time-to-event modeling, integrated safety-efficacy review, and final program recommendation.

## Why this repository exists

Many data science portfolios show modeling skills, but very few show how machine learning fits into regulated clinical development workflows. This repository is built to demonstrate clinical trial analytics, CDISC-aware data handling, SDTM-to-ADaM-style thinking, and decision-ready outputs relevant to Senior Data Scientist roles in BioPharma.

It is intentionally designed to show:
- Clinical trial data understanding at the patient level.
- Experience with clinical endpoints, safety domains, and time-to-event structures.
- Reproducible, analysis-ready dataset derivation.
- Interpretable ML aligned to clinical development questions.
- Reporting that can be reviewed quickly by hiring managers, biometrics partners, or advanced analytics teams.

## Clinical workflow covered

### Phase I
- Population and cohort review.
- Adverse event summaries.
- Laboratory abnormality and shift analysis.
- Vital signs review.
- Early safety gate recommendation.

### Phase II
- Endpoint derivation and responder logic.
- Longitudinal efficacy summaries.
- Subgroup exploration.
- Interpretable machine learning for response or risk prediction.
- Go / hold / refine decision package.

### Phase III
- Confirmatory endpoint dataset.
- Time-to-event or survival analysis.
- Safety and efficacy integration.
- Final program recommendation.

## Clinical data standards

This project is built around the language and structure commonly used in clinical trial data workflows:
- **CDISC** for standards awareness and interoperable structure.
- **SDTM**-like domains for harmonized clinical source data.
- **ADaM**-like datasets for analysis-ready derivations.
- Traceability, QC, and reproducibility across the full pipeline.

The repository does not claim submission-ready production delivery, but it is intentionally structured to reflect the working style and data expectations found in regulated BioPharma environments.

## Hybrid stack

### Python-first
Python is the primary language for:
- Data ingestion and harmonization.
- Validation and schema checks.
- Feature engineering.
- Statistical analysis.
- Survival analysis and time-to-event modeling.
- Machine learning and explainability.
- HTML report generation.
- Testing, packaging, and CI-friendly workflow.

### R-assisted
R is used selectively where it strengthens the industry signal, especially for:
- Optional SDTM/ADaM-style reference derivations.
- Optional pharmaverse-aligned workflow examples.
- Optional TLG-oriented outputs.

## Repository structure

```text
.
├── README.md
├── pyproject.toml
├── install_r_packages.R
├── Makefile
├── src/
├── data/
├── docs/
├── reports/
├── artifacts/
└── tests/
```

## Main deliverables

- Clinical trial portfolio documentation.
- A phase-gated development workflow.
- Public-data acquisition and curation plan.
- SDTM-like and ADaM-like dataset strategy.
- Phase I, II, and III HTML reports.
- Interpretable ML model card.
- Data lineage and QC artifacts.
- Optional causal inference appendix after MVP completion.

## Environment setup

### Python
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,reports]
```

### R layer
```bash
Rscript install_r_packages.R
```

### Quick validation
```bash
make validate
```

## Keywords and concepts

This repository is intentionally optimized for discovery around these concepts:
- clinical trial machine learning
- clinical development analytics
- clinical trial data science
- CDISC SDTM ADaM
- survival analysis in clinical trials
- safety analytics in BioPharma
- interpretable ML for healthcare and clinical research
- Phase I Phase II Phase III trial analytics

clinical trials, clinical development, machine learning, clinical data science, BioPharma, CDISC, SDTM, ADaM, survival analysis, time-to-event, safety analytics, endpoint modeling, interpretable AI, patient-level data, regulated analytics
