# E-commerce Customer Churn Analysis

Predicting purchase inactivity and identifying customers for retention experiments using REES46 e-commerce event data from October 2019 to April 2020.

The project combines behavioral analysis, customer segmentation, a 15-feature Random Forest, and a temporal backtest. **Churn means no recorded purchase during a specified future window**, rather than permanent departure from the platform.

[Full analysis report](reports/churn_analysis_report.md) · [Model evaluation](validation/validation_summary.md) · [Temporal validation](reports/temporal_validation/temporal_validation_addendum_en.md)

## Key findings

- Of 100,000 sampled users, 9,428 purchased during the original observation window; 7,658 made no purchase during March–April 2020.
- Users with no browsing in the preceding 30 days had a **92.88%** churn rate, compared with **69.57%** among recent browsers.
- The 2,195 inactive, higher-spending users represent a potential priority for retention experiments. Historical spending indicates past value, not responsiveness to marketing.

## Model performance

The Random Forest uses 15 behavioral features, including purchase recency, purchase frequency, spending, session activity and recent browsing. Parameters: 200 trees, maximum depth 5, minimum leaf size 20, and random seed 42.

| Evaluation | Test users | ROC AUC | Macro F1 at threshold 0.70 |
|---|---:|---:|---:|
| Stratified random user split | 1,886 | 0.7808 | 0.6637 |
| Later-period temporal backtest | 6,445 | 0.7351 | 0.6374 |

On the random split, accuracy at 0.70 is 0.7900, churn precision is 0.8762, and churn recall is 0.8636. Compared with a 0.50 threshold, 0.70 reduces false churn alarms and improves macro F1, while missing more actual churn cases. It is not an economically optimized campaign threshold.

The original test set was examined repeatedly during development. The temporal backtest provides additional evidence, but remains a single historical pair using previously selected model settings.

## High-risk customer screening

Users are ranked by predicted churn probability. Precision@K measures observed churn among the selected users; Lift@K divides that precision by the evaluation cohort's churn rate.

| Original test selection | Users | Random Forest precision | Lift | Browsing-rule precision |
|---|---:|---:|---:|---:|
| Top 10% | 188 | 97.34% | 1.1983 | 93.14% |
| Top 20% | 377 | 96.55% | 1.1886 | 93.04% |
| Top 30% | 565 | 95.93% | 1.1810 | 93.02% |

The baseline ranks customers by ascending recent 30-day view count. Its precision is averaged over 1,000 random tie resolutions with seed 42. The Random Forest achieves higher observed precision at all three selection fractions. This measures risk-screening performance; campaign effectiveness requires a separate A/B test.

## Probability calibration

The Brier score is **0.1275**. The [calibration curve](reports/figures/calibration_curve.png), based on 10 quantile bins, broadly follows the ideal diagonal, with some deviations. No additional probability calibration was applied. This check does not establish optimal calibration or reliability in future periods.

## Temporal validation

An earlier-period model is trained and evaluated at a later cutoff using the same feature formulas, model settings and threshold. All intervals are left-closed and right-open.

| Cohort | Observation window | Outcome window | Users |
|---|---|---|---:|
| Training | [2019-10-01, 2020-01-01) | [2020-01-01, 2020-03-01) | 6,717 |
| Testing | [2019-11-30, 2020-03-01) | [2020-03-01, 2020-04-30) | 6,445 |

In the later test, the highest-risk 10% have **94.25% precision** and **1.2265 lift**, versus **90.39% precision** for the browsing rule. The test contains 3,734 customers also present in training and 2,711 unseen customers, so it assesses repeated customer scoring as well as new-customer performance.

The temporal design uses 92-day observation and 60-day outcome windows; the original random split uses 152 and 61 days. Cohorts and churn prevalence also differ, so changes in scores cannot be attributed solely to time drift. See the [temporal report](reports/temporal_validation/temporal_validation_addendum_en.md) for subgroup results and session-definition sensitivity.

## Repository structure

| Location | Contents |
|---|---|
| `notebooks/` | Exploratory analysis and cached-feature recovery |
| `reports/` | Analysis report, calibration chart and temporal findings |
| `validation/` | Reproduction scripts, evaluation results and dependencies |
| `DATA.md` | Data scope and required local inputs |

## Reproduce the model evaluation

Use Python 3.12.14 and the pinned dependencies. The following local artifacts are required and excluded from Git:

```text
data/sample/session_events.parquet
data/sample/user_features_v2.parquet
data/sample/churn_model_v2.pkl
```

From the repository root:

```sh
python3 -m venv .venv-validation
.venv-validation/bin/python -m pip install -r requirements.txt
.venv-validation/bin/python validation/validate_15_feature_model.py \
  --project-root . \
  --output-dir validation/results
```

The script trains the candidate, compares it with the saved model, rebuilds features and labels from session events, and reports results at thresholds 0.50 and 0.70. Data and model artifacts are not bundled, so cloning alone is insufficient to run it. See [data requirements](DATA.md), [reproduction instructions](validation/README.md), and [temporal instructions](validation/temporal_validation/README.md).

For exploratory work, open `notebooks/01_data_quality.recovered.ipynb` from the repository root or `notebooks/` and run the first two code cells to recover features. Later analysis cells are intended to be run selectively.

## Limitations

- Purchase counts are event rows, not distinct orders; spending is not verified profit or lifetime value.
- Users were sampled across the full seven-month extract. Together with repeated test inspection and a single temporal pair, this limits claims of independent generalization.
- Reproduction starts from a sampled event cache. Full raw-data preparation and every exploratory notebook cell have not been rerun end to end.
- Cached session boundaries have known inconsistencies. The temporal sensitivity check produced nearly unchanged AUC/F1 and identical top-K summaries; details are in the temporal report.
- Behavioral associations and predicted churn do not establish intervention benefit. Retention strategies require randomized testing and cost/benefit evaluation.
