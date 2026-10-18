# Risk Ranking and Probability Calibration

These analyses evaluate the 15-feature Random Forest on the historical 1,886-user test set. The observed churn rate is 81.23% when rounded.

## Risk-screening method

[ranking_calibration_cells.py](ranking_calibration_cells.py) contains notebook-style cells for loading the model, reconstructing the stratified random test split, ranking predicted probabilities, comparing a browsing baseline and plotting calibration. Run them in order from the project `notebooks/` directory with `user_features_v2` already available in the notebook namespace. The cells require NumPy, pandas, scikit-learn, Matplotlib and notebook display. Matplotlib is an additional plotting dependency outside the pinned standalone-validation environment.

Model probabilities are sorted descending; K is `int(N * fraction)` for fractions 0.10, 0.20 and 0.30. The baseline sorts `recent_30d_views` ascending, resolving equal view counts with `np.random.default_rng(42)` and 1,000 random permutations per fraction. The reported baseline precision is the mean across these permutations. User IDs are used for association only, not as model features.

| Fraction | K | RF precision | RF lift | Baseline mean precision |
|---|---:|---:|---:|---:|
| 10% | 188 | 0.9734 | 1.1983 | 0.9314 |
| 20% | 377 | 0.9655 | 1.1886 | 0.9304 |
| 30% | 565 | 0.9593 | 1.1810 | 0.9302 |

The values in [reference_results.json](reference_results.json) are rounded summary statistics; they are not user-level prediction outputs. The standalone reproduction script reports threshold metrics and does not export this top-K table. The cell-oriented analysis is a separate entry point.

## Probability calibration

The Brier score is 0.1275. The [calibration curve](../../reports/figures/calibration_curve.png) uses 10 quantile bins; its settings appear in [calibration_config.json](calibration_config.json). No additional probability calibration is applied. A near-diagonal curve is a diagnostic, not proof of optimal or time-stable calibration. Raw per-bin arrays are not included.

These diagnostics reuse the development test set. They do not provide an independent holdout estimate or quantify incremental campaign benefit. See the [main report](../../reports/churn_analysis_report.md) and [temporal evaluation](../temporal_validation/README.md) for interpretation and limitations.
