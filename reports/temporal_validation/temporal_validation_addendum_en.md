# Temporal Validation: Design and Results

A fixed Random Forest trained at 1 January 2020 and evaluated at 1 March 2020 achieved ROC-AUC **0.735123** and Macro F1 **0.637431** at the pre-existing 0.7 threshold. This supports useful later-period ranking within this historical sample, not proven temporal robustness or optimal calibration.

Training features: [2019-10-01, 2020-01-01); training labels: [2020-01-01, 2020-03-01). Test features: [2019-11-30, 2020-03-01); test labels: [2020-03-01, 2020-04-30). Both feature windows are 92 days and both target windows exactly 60 days. Eligibility requires an observed purchase within the respective feature window. There were 6,717 training users and 6,445 test users; test churn prevalence was 76.8503%.

All training outcomes mature before the test prediction cutoff. Later labels are constructed only after fitting and prediction. The 15 feature formulas, recent 30-day window, zero-fill policy, RF settings (200 trees, depth 5, minimum leaf 20, seed 42, all cores) and threshold remain fixed. No tuning or calibration uses later outcomes. Shared historical events between training outcomes and test features are available information at the test cutoff. Immediate data availability at cutoff is assumed.

| Target fraction | K | RF precision | RF lift | Rule precision, mean of 1,000 random tie resolutions |
|---|---:|---:|---:|---:|
| 10% | 644 | 0.942547 | 1.226471 | 0.903939 |
| 20% | 1,289 | 0.930178 | 1.210378 | 0.903968 |
| 30% | 1,933 | 0.921883 | 1.199583 | 0.904196 |

K is floor(fraction*N). The rule ranks recent_30d_views ascending; random boundary-tie selection uses equivalent hypergeometric draws without replacement (seed 42). Its exact expected precision is 0.904204 and lift 1.176578 at each fraction. Lift uses current test prevalence. No significance test or intervention-effect estimate is claimed.

The test contains 3,734 previously seen and 2,711 previously unseen training users. Their AUC values are 0.762746 and 0.694388, respectively; Macro F1 values are 0.662744 and 0.598767. Repeated scoring of existing customers is intended, but this is not an exclusively new-customer test.

Session audit found 196 event-level inconsistencies against strict >30-minute session boundaries, with tied timestamps implicated. The main result preserves cached rebuilt_session for historical comparability. A causal, tie-invariant reconstruction in memory changes no training users and 14 test users' features: AUC 0.735184, Macro F1 0.637226; all three top-K results remain identical. Existing caches and verified scores were not rewritten.

The original random-user test AUC 0.780782 and Macro F1 0.663678 are contextual benchmarks, not controlled comparisons. Its observation window was 152 rather than 92 days, and its March–April outcome window was 61 rather than exactly 60 days. Cohorts and prevalence differ; higher relative lift here does not imply higher absolute precision. Seven months of data cannot support a mature earlier 60-day target and two matched 152-day feature windows. Only one temporal pair is available.

Users were originally sampled by hashed IDs across the entire seven-month population, which creates full-period population-selection dependence. This is a conditional retrospective backtest without late-label leakage, not a fully point-in-time population-sampling study. The model specification was previously developed using related historical data; this is not an untouched model-selection holdout. No claims of permanent customer departure, cross-year stability, or pandemic causality follow.

The [temporal script](../../validation/temporal_validation/validate_temporal.py) and [reference metrics](../../validation/temporal_validation/results/metrics.json) contain the implementation, input hashes, environment versions, monthly counts, subgroup metrics and session sensitivity. [Run instructions](../../validation/temporal_validation/README.md) describe the required inputs and output-directory handling.

[Main analysis report](../churn_analysis_report.md#57-fixed-temporal-backtest)
