# Model Evaluation and Reproduction

## Historical Random Forest

`validate_15_feature_model.py` reconstructs the historical random-user split, trains the 15-feature candidate, compares it with the trusted saved model, rebuilds inputs from session events and reports threshold metrics.

Use Python 3.12.14 and the pinned packages. From the repository root:

```sh
python3 -m venv .venv-validation
.venv-validation/bin/python -m pip install -r validation/requirements.txt
.venv-validation/bin/python validation/validate_15_feature_model.py \
  --project-root . \
  --output-dir validation/results
```

Local inputs:

- `data/sample/session_events.parquet`
- `data/sample/user_features_v2.parquet`
- `data/sample/churn_model_v2.pkl`

These files are excluded from Git. Load only trusted model pickles. The script uses the original feature-table row order, 80/20 stratification and seed 42. Changing input data or row order can change the split and correctly fail its assertions.

Checks cover the ordered feature schema, class encoding, cohort counts, split separation, saved-tree equality, probability agreement and event-to-feature/label consistency. Only undefined `cart_rate` and `purchase_rate` values are filled with zero; no learned imputation, scaling or log transform is used.

The output `metrics.json` includes full-precision scores at 0.50 and 0.70, class metrics, confusion matrices, ranking discrimination, Brier score, matched all-churn baseline, environment versions and input hashes. [metrics.json](metrics.json) contains the reference run, and [validation_summary.md](validation_summary.md) explains the results. Use a separate output directory for reruns.

## Ranking and calibration

[Ranking/calibration analysis](ranking_calibration/README.md) uses the same historical test set for top-K selection, a seeded browsing-rule baseline and a 10-bin calibration plot. The analysis is organized as notebook cells and requires the notebook namespace and additional plotting dependencies; it is not the standalone validation command above.

## Temporal backtest

The [temporal evaluation](temporal_validation/README.md) fits an earlier-period model with fixed settings and evaluates a later cohort. Its outcome window ends on 30 April exclusive; the historical random-user evaluation ends on 1 May exclusive. The resulting cohorts, prevalence and time windows are not interchangeable.

## Interpretation

The historical test set was examined during model development; reproducibility is not an independent generalization estimate. The temporal design provides one later-period check on related historical data. Additional untouched evaluation is needed for stronger deployment claims. Neither diagnostic estimates campaign impact.
