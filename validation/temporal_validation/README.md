# Fixed Temporal Backtest — Completed Result

This directory preserves the already completed backtest. The report-integration task did **not** execute this script, refit any model, regenerate probabilities or rerun validation. The script and [results/metrics.json](results/metrics.json) are unchanged.

## Design and inputs

Earlier features [2019-10-01, 2020-01-01), labels [2020-01-01, 2020-03-01); later features [2019-11-30, 2020-03-01), labels [2020-03-01, 2020-04-30). Observation windows are 92 days and label windows exactly 60 days, ending before 30 April. Fixed RF: 200 trees, depth 5, minimum leaf 20, seed 42, all cores; 15 historical feature formulas and threshold 0.70.

The script requires existing private local files: `data/sample/session_events.parquet`, `data/sample/user_features_v2.parquet`, `data/sample/churn_model_v2.pkl`, `notebooks/01_data_quality.recovered.ipynb`, `validation/validate_15_feature_model.py` and `validation/metrics.json`. Only the event Parquet is used to fit this backtest; the other artifacts are included in before/after integrity checks. None of these private data/model inputs is redistributed here.

## Instructions for a future explicitly requested rerun

Use Python 3.12.14 and `validation/requirements.txt`. From the repository root, after setting up the environment described in the main README:

```sh
.venv-validation/bin/python validation/temporal_validation/validate_temporal.py \
  --project-root . \
  --output-dir validation/temporal_validation/new_results
```

**Running this command fits earlier-period Random Forest models, including a session-sensitivity fit.** It should not be run merely to update the documentation. The output directory must not already exist. Preserve the completed `results/metrics.json`; new rerun directories matching `new_results*` are ignored by Git. Before/after protected-file hashes must match within that run; no input file is overwritten. The fixed reference results remain tied to their recorded historical hashes, so a legitimately edited non-data artifact can have a different hash in a later run without changing the historical result.

## Recorded outputs and limits

Metrics include cohort windows, prevalence, full-precision AUC/F1, top-K and tie handling, seen/unseen-user diagnostics, monthly event summaries, session-boundary audit, sensitivity results, input hashes and environment versions. RF and rule top-K metrics use the script's documented boundary-tie expectations; the rule also records a seeded 1,000-draw equivalent randomized-tie mean.

This is a fixed single retrospective temporal pair with repeated customers and seven-month population-selection dependence, not an untouched final model-selection holdout. It also differs from the original random-user experiment in window lengths and cohort composition. See the [English design addendum](../../reports/temporal_validation/temporal_validation_addendum_en.md) and [integrated report](../../reports/churn_analysis_report.md#57-fixed-temporal-backtest).
