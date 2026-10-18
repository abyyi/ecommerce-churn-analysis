# E-commerce Customer Churn Analysis

A customer behavior analysis and Random Forest churn prediction project using REES46 event data from October 2019 to April 2020.

The project defines **churn as no observed purchase during March–April 2020**, among customers who purchased before 1 March 2020. This measures purchase inactivity during a fixed window, not permanent customer departure.

## Key findings

- The development sample contains 100,000 users; 9,428 historical buyers form the eligible cohort. Of these, 7,658 churned and 1,770 retained.
- Customers with no browsing events in the preceding 30 days had 92.88% observed churn, versus 69.57% among recent browsers.
- Inactive customers with higher historical spending account for 2,195 users and have 92.39% observed churn. They are a candidate segment for retention experiments; no marketing effect has been established.
- The saved 15-feature Random Forest was reproduced through fresh training on its reconstructed historical split. All 200 tree states match the saved artifact; probability differences are below floating-point tolerance.
- Owner-confirmed historical top-10% screening achieves **97.34% precision / 1.1983 lift**, versus **93.14% mean precision** for a simple recent-browsing rule with 1,000 randomized tie resolutions. This measures outcome-risk concentration, not marketing ROI.
- A completed fixed temporal backtest achieves **AUC 0.7351 / macro F1 0.6374**, with **94.25% top-10% precision / 1.2265 lift** in the later cohort. It supports later-period ranking within this sample, not a claim of proven long-term robustness.

## Reproduced candidate results

Training: 7,542 users. Test: 1,886 users, including 354 retained and 1,532 churned. Split: stratified random user split, 80/20, seed 42; **not temporal validation**.

| Metric | Threshold 0.50 | Threshold 0.70 |
|---|---:|---:|
| Accuracy | 0.8208 | 0.7900 |
| Macro F1 | 0.5582 | 0.6637 |
| Churn precision | 0.8302 | 0.8762 |
| Churn recall | 0.9798 | 0.8636 |
| Retained recall | 0.1328 | 0.4718 |

ROC AUC is **0.7808** at either decision threshold because probability scores are unchanged. At 0.70, the confusion matrix (rows actual, columns predicted; retained then churned) is `[[167, 187], [209, 1323]]`. A matched all-churn baseline achieves accuracy 0.8123 and macro F1 0.4482.

Raising the threshold improves macro F1 and reduces false churn alarms, while reducing churn recall. The chosen threshold is not proven optimal for marketing profit.

**Evaluation caveat:** the historical test set was inspected repeatedly during development. Successful reproduction confirms numerical consistency, not an independent estimate of generalization. The 11- and 18-feature experiments in the report remain owner-reported.

## Risk-screening value and calibration

| Historical test selection | Users | RF precision | RF lift | Browsing-rule mean precision |
|---|---:|---:|---:|---:|
| Top 10% | 188 | 97.34% | 1.1983 | 93.14% |
| Top 20% | 377 | 96.55% | 1.1886 | 93.04% |
| Top 30% | 565 | 95.93% | 1.1810 | 93.02% |

The rule ranks lower `recent_30d_views` as higher risk, averaging 1,000 random tie resolutions. Original source cells and user-posted result tables have been recovered from the 项目开发 conversation; [the evidence archive](validation/ranking_calibration/README.md) preserves them without rerunning the calculations. The original-test Brier score is **0.1275**. The [original calibration chart](reports/figures/probability_calibration_original.png) has also been recovered and visually checked; its points broadly follow the ideal diagonal, with deviations. No extra calibration was applied and optimal calibration is not claimed; raw bin values were not recovered.

## Fixed temporal backtest

| Cohort | Observation window | Label window | Users |
|---|---|---|---:|
| Earlier training | [2019-10-01, 2020-01-01) | [2020-01-01, 2020-03-01) | 6,717 |
| Later testing | [2019-11-30, 2020-03-01) | [2020-03-01, 2020-04-30) | 6,445 |

All intervals are left-closed/right-open; observation windows last 92 days and label windows 60 days. Eligibility is a purchase within the respective observation window. The earlier-period model uses the fixed 15-feature RF configuration and threshold 0.70; it is a separate earlier fit, not a new evaluation of the saved original fitted model.

The later test contains 4,953 churned and 1,492 retained users (76.8503% churn). It achieves **AUC 0.7351** and **macro F1 0.6374**.

| Later test selection | K | RF precision | RF lift | Browsing-rule mean precision |
|---|---:|---:|---:|---:|
| Top 10% | 644 | 94.25% | 1.2265 | 90.39% |
| Top 20% | 1,289 | 93.02% | 1.2104 | 90.40% |
| Top 30% | 1,933 | 92.19% | 1.1996 | 90.42% |

Lift uses each evaluation cohort's own prevalence. The RF exceeds the rule descriptively at all fractions, without a significance or intervention-effect claim. Of later users, 3,734 overlap with training and 2,711 are unseen; this is not a new-customer-only test. Unseen-user AUC is 0.6944.

**Comparability limits:** the original test uses 152 observation days and 61 outcome days; the temporal design uses 92/60 days, excludes 30 April, and changes user composition and prevalence. Score differences cannot be attributed wholly to time drift. The seven-month sampling universe and previously selected settings also prevent treating this single pair as an untouched final holdout.

[Temporal design and sensitivity details](reports/temporal_validation/temporal_validation_addendum_en.md) · [Completed temporal metrics](validation/temporal_validation/results/metrics.json) · [Temporal reproduction instructions](validation/temporal_validation/README.md)

## Repository guide

```text
reports/
  churn_analysis_report.md      Formal English analysis report
  reproducibility_audit.md      Verification scope and remaining limitations
  temporal_validation/         English design addendum and Chinese review
validation/
  validate_15_feature_model.py  Fresh fit, saved-model comparison and feature checks
  requirements.txt             Pinned validation dependencies
  metrics.json                 Verified historical results and input hashes
  validation_summary.md        Threshold comparison and interpretation
  ranking_calibration/         Recovered source cells, posted results and image provenance
  temporal_validation/         Existing backtest script, instructions and metrics
notebooks/
  01_data_quality.recovered.ipynb
notebook_fix/
  README.md                    Session consistency fix and execution evidence
DATA.md                        Local inputs and data preparation limitations
GITHUB_UPLOAD.md               Upload checklist
requirements.txt               Includes the validation dependency list
```

## Reproduce the candidate

Verified environment: Python 3.12.14. The validation script requires three local inputs, which are excluded from Git:

```text
data/sample/session_events.parquet
data/sample/user_features_v2.parquet
data/sample/churn_model_v2.pkl
```

See [DATA.md](DATA.md) for provenance and preparation scope. This public repository does not include the dataset or trained pickle, so cloning alone is not sufficient to execute the reproduction. Use the verified local artifacts to reproduce the saved model; do not load a pickle from an untrusted source.

From the repository root:

```sh
python3 -m venv .venv-validation
.venv-validation/bin/python -m pip install -r requirements.txt
.venv-validation/bin/python validation/validate_15_feature_model.py \
  --project-root . \
  --output-dir validation/results
```

The script freshly trains the candidate, checks agreement with the saved model, rebuilds the 15 model inputs and target from session events, and exports metrics at 0.50 and 0.70. It leaves the input files unchanged. Generated rerun results are ignored by Git; the historical checked results are preserved in `validation/metrics.json`.

[Detailed reproduction instructions](validation/README.md) · [Validation results](validation/validation_summary.md)

## Recovery notebook

The notebook is an exploratory record with a focused recovery entry point, not a fully sequential production pipeline. With the local event cache present, launch Jupyter from the repository root or `notebooks/`, restart the kernel and run the **first two code cells**. Jupyter is an optional local tool and is not included in the validation dependency lock.

The recovery entry point restores historical features and regenerates recent features. Both historical and recent sessions count reconstructed sessions (`rebuilt_session`) per user, using the existing 30-minute-gap session construction. It checks session counts and compares all 15 model inputs with the saved feature cache when present. A mismatch raises an error rather than silently replacing validated inputs.

The recovery table contains the candidate inputs, but does not recreate every additional column in the full feature cache. It does not automatically overwrite that cache or retrain the model. Later notebook cells are historical exploratory steps and should be run selectively; raw-data scanning cells are not required for recovery. The GitHub notebook has outputs cleared and portable root detection.

## Interpretation and limitations

- Features use events before 1 March 2020; labels use purchases from 1 March to 1 May 2020 exclusive. This feature/label separation does not turn a random split into temporal validation.
- Purchase counts are event rows, not distinct orders. Historical spending sums purchase-event prices; it is not verified profit or lifetime value.
- Data preparation starts from an existing sampled event cache for the verified run. A full seven-month raw-CSV rebuild and end-to-end exploratory notebook execution have not been completed in this review.
- Profile and segment differences are observational associations. Retention recommendations need randomized A/B testing and incremental cost/benefit evaluation.
- A fixed single temporal backtest is complete; additional independent windows and an untouched final holdout remain future work. No production-readiness or intervention-effect claim is made.
- A later audit found 196 cached event-level session-boundary inconsistencies. Previously completed tie-invariant sensitivity testing changed 14 later test users, with nearly identical AUC/F1 and unchanged top-K results. No verified cache or model was rewritten; matching the cache is not proof of perfect session boundaries.

Read the [full analysis report](reports/churn_analysis_report.md) for model comparisons, customer profiles, segmentation, proposed experiments and limitations.
