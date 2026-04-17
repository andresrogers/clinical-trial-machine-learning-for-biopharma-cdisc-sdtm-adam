# Phase II Model Card

## Use case
Predict Phase II Week 24 responder status for exploratory program gating support.

## Primary model
- logistic_regression

## Inputs
- Numeric: ['age', 'baseline_cognitive_score', 'chg_week12', 'early_safety_discontinuation_before_week12']
- Categorical: ['sex', 'race', 'baseline_severity_group', 'treatment_arm']

## Exclusions / leakage controls
- No post-Week-24 features used.
- Outcome-defining fields at Week 24 excluded from predictors.
- Training features documented explicitly in this card.

## Benchmarking
- Conservative benchmark set includes logistic regression, elastic net, and random forest.
- Logistic regression remains primary for interpretability and sponsor-style transparency.

## Threshold logic
- Primary classification threshold: 0.495
- Threshold selected from the training ROC curve to preserve clinically useful sensitivity while improving specificity over the default 0.50 cutoff.

## Metrics
- threshold: 0.49486759833336047
- roc_auc: 0.8679435483870968
- pr_auc: 0.8445948674535199
- brier: 0.14488192162648167
- sensitivity: 0.8064516129032258
- specificity: 0.75
- ppv: 0.7575757575757576
- npv: 0.8
- f1: 0.78125
- n_test: 63
- responder_diff_pp: 19.073
- gate_decision: GO
- primary_model: logistic_regression
- primary_endpoint_pvalue: 0.0019
- threshold_rationale: Training ROC threshold maximizing specificity with sensitivity >= 0.78

## Limitations
- Findings should be interpreted within the documented source-mix and continuity assumptions used for this integrated review.
- Predictive performance may vary if endpoint prevalence or follow-up assumptions materially change.
