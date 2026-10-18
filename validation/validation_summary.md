# 15-Feature Random Forest: Reproduction Results

Reference evaluation of the 15-feature candidate on the historical stratified random-user split.

## Reproduction checks

- Loaded the trusted saved model; confirmed 15 ordered features, 200 trees, maximum depth 5, minimum leaf size 20, seed 42, no class weights, `n_jobs=-1`, and saved threshold 0.70.
- Reconstructed the earlier documented stratified 80/20 random split on the feature-cache row order. Training: 7,542 users. Test: 1,886 users, comprising 354 retained and 1,532 churned users.
- Filled 34 missing values in each of `cart_rate` and `purchase_rate` with zero, retaining the `no_view_before` indicator. No scaling or log transform.
- Retrained from scratch. Every saved tree's node/value arrays matched exactly. Predicted probabilities on all 9,428 users agreed within 1e-14; test classifications at 0.70 matched exactly.
- Rebuilt all 15 features and the target from session events with explicit historical/outcome bounds. All matched cached values by user ID, allowing floating-point tolerance for arithmetic. Rebuilt-feature probabilities agreed within 1e-14.

The original candidate accuracy, macro F1 and AUC round to 0.7900, 0.6637 and 0.7808, respectively. Accuracy and macro F1 in this evaluation use threshold 0.70.

## Threshold comparison

| Metric | Threshold 0.50 | Threshold 0.70 | All-churn baseline |
|---|---:|---:|---:|
| Accuracy | 0.8208 | 0.7900 | 0.8123 |
| Macro F1 | 0.5582 | 0.6637 | 0.4482 |
| Retained recall | 0.1328 | 0.4718 | 0.0000 |
| Churn precision | 0.8302 | 0.8762 | 0.8123 |
| Churn recall | 0.9798 | 0.8636 | 1.0000 |
| Predicted churn | 1,808 | 1,510 | 1,886 |

Both candidate thresholds share ROC AUC 0.7808, average precision for churn 0.9304, and Brier score 0.1275, since the underlying probability scores are unchanged. Average precision is not trapezoidal PR AUC; Brier score alone does not establish calibration.

## Confusion matrix at 0.70

Rows are actual labels; columns are predicted labels. Churn is positive class 1.

| | Predicted retained | Predicted churned |
|---|---:|---:|
| Actual retained | 167 | 187 |
| Actual churned | 209 | 1,323 |

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Retained | 0.4441 | 0.4718 | 0.4575 | 354 |
| Churned | 0.8762 | 0.8636 | 0.8698 | 1,532 |

Raising the threshold reduces false churn alarms by 120 but misses 178 additional churn cases. It improves macro F1 and retained recall while reducing accuracy and churn recall. No marketing cost/benefit data establish 0.70 as economically optimal.

## Session features

Historical and recent sessions use per-user `rebuilt_session` counts. Feature checks compare the 15 candidate inputs against the reference table and independently aggregate them from session events. Source `user_session` uses a different convention and is not substituted. The [reproducibility notes](../reports/reproducibility_audit.md) describe the cached boundary audit and temporal sensitivity.

## Limits of this verification

The exact saved-tree match strongly corroborates the reconstructed historical split and training procedure, but no original split manifest was available. This remains the previously inspected development test set; numerical reproducibility does not provide a new independent generalization estimate. The run begins from session-event Parquet data, not the raw monthly CSV files. No 11- or 18-feature model, campaign effect, calibration claim or production readiness was independently validated.

See [metrics.json](metrics.json) for full precision metrics, source hashes, split hashes and environment versions, and [README.md](README.md) for rerun instructions.



## Related diagnostics

See [risk ranking and calibration](ranking_calibration/README.md) for top-K screening, baseline tie handling and probability diagnostics. The [temporal evaluation](temporal_validation/README.md) provides a separate fixed earlier/later pair with different observation and label lengths; it is not an untouched final model-selection holdout.
