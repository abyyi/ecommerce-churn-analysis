# Reproducibility and Data Quality

## Evaluation scope

The standalone evaluation starts from sampled session events and a user-feature table. It verifies the 15-feature candidate and a fixed temporal design. It does not include automatic dataset download, a complete seven-month raw-CSV rebuild, or sequential execution of every exploratory notebook cell.

| Input property | Value |
|---|---:|
| Sampled event rows | 2,635,748 |
| Sampled users | 100,000 |
| Historical eligible users | 9,428 |
| Historical churned users | 7,658 |
| Historical retained users | 1,770 |
| Spending median used for segmentation | 313.78 |

The event timestamps span 2019-10-01 00:05:36 to 2020-04-30 23:59:56. [Historical metrics](../validation/metrics.json) and [temporal metrics](../validation/temporal_validation/results/metrics.json) preserve environment versions, input hashes and full-precision results. Source hashes identify the versions used for each recorded run; documentation or comment-only edits may have different current hashes without changing the recorded numerical results.

## Historical candidate checks

- Stratified 80/20 user split on the reference feature row order, seed 42: 7,542 training and 1,886 test users.
- Exact ordered 15-feature schema; undefined view-denominator ratios replaced with zero, with no-view indicator retained. No scaling or log transform.
- Fresh candidate training matches all 200 reference tree node/value arrays. Probability differences are below 1e-14; predictions at threshold 0.70 agree exactly.
- All 15 inputs and churn labels reconstructed from session events match the reference feature table, with numerical tolerance for floating-point sums.
- Accuracy 0.7900, macro F1 0.6637 and ROC AUC 0.7808 on the historical test split.

Only the 15-feature candidate has this complete reproduction record. The 11- and 18-feature scores are exploratory benchmark summaries. The test set was examined repeatedly during development, so reproduction does not establish an independent generalization estimate.

## Sessions and temporal sensitivity

Historical and recent session features count distinct `rebuilt_session` within each user. Source `user_session` is not an interchangeable identifier. Cached feature-loading checks enforce consistent session counts, unique users and reference-input alignment.

An event-level audit identifies 196 cached session-boundary inconsistencies involving tied timestamps. The main temporal evaluation retains the cached identifiers. A tie-invariant reconstruction changes no earlier-cohort feature rows and 14 later-cohort rows; AUC changes from 0.735123 to 0.735184 and macro F1 from 0.637431 to 0.637226. The three top-K results remain identical. Cache alignment therefore supports consistency, but does not establish perfect strict-30-minute session reconstruction.

## Diagnostic analysis

[Ranking and calibration methods](../validation/ranking_calibration/README.md) describe probability-based selection, a seeded 1,000-repeat tie-aware browsing baseline, and 10-quantile-bin calibration. Summary ranking values are rounded; user-level predictions and raw calibration-bin arrays are not distributed. The Brier score is 0.1275, and no additional calibration is applied. These are development-test diagnostics, not an independent validation of calibration or campaign responsiveness.

## Temporal design and limits

The fixed temporal pair uses 92-day observation and 60-day outcome windows, with 6,717 earlier training users and 6,445 later test users. All earlier labels mature by the later scoring cutoff. Later outcomes are not used for fitting, parameter search, threshold selection or probability calibration.

The later cohort includes 3,734 training-cohort customers and 2,711 unseen customers. Sampling across the full seven-month population introduces retrospective population-selection dependence. The model specification was developed on related historical data, so this is not an untouched final model-selection holdout. The original random test uses different window lengths, eligibility and prevalence; score differences cannot be attributed solely to time drift.

See the [temporal design report](temporal_validation/temporal_validation_addendum_en.md) for subgroup results, sensitivity and interpretation. Additional periods, a final untouched holdout and randomized intervention experiments remain necessary before stronger deployment or business-effect claims.
