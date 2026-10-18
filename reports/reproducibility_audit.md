# Reproducibility Audit

Review date: 15 October 2026.

## Scope

Read-only review of the local `ecommerce-churn-analysis` project. The original recovery notebook was subsequently corrected in place; data files and model artifacts were not changed. This report package is a standalone handoff for placement in the repository's `reports/` directory.

Reviewed: `notebooks/01_data_quality.ipynb`, `notebooks/01_data_quality.recovered.ipynb`, `data/sample/session_events.parquet`, and `data/sample/user_features_v2.parquet`. The raw monthly files, recovery cache and model pickle were inventoried; raw data were not rescanned and the trusted local pickle was subsequently loaded for the candidate reproduction described below.

## Independently checked against Parquet caches

Queries used DuckDB 1.5.6 from an existing local dependency directory.

| Check | Result |
|---|---|
| Session-event rows | 2,635,748 |
| Distinct sampled users | 100,000 |
| Minimum event timestamp | 2019-10-01 00:05:36 |
| Maximum event timestamp | 2020-04-30 23:59:56 |
| Feature-cache rows / distinct users | 9,428 / 9,428 |
| Cached churn-label sum | 7,658 |
| Eligible users recomputed from historical purchase events | 9,428 |
| Churn recomputed using March–April purchase events | 7,658 |
| Cohort spending median | 313.78 |
| Profile medians by outcome | Match every supplied value to displayed precision |
| Four activity/value segment summaries | Match every supplied count, churn rate and median |
| Recent browsing group | 4,712 users; 3,278 churned; 69.57% |
| No recent browsing group | 4,716 users; 4,380 churned; 92.88% |

The cohort and churn counts were recomputed from event data independently of the feature table. Profile and segment statistics were recomputed from the existing feature cache; the follow-up validation rebuilt all 15 model inputs and labels from session events and matched them to the feature cache. A raw-CSV-to-cache integrity audit was not performed.

## Follow-up candidate reproduction

The trusted saved pickle was loaded with scikit-learn 1.9.1. Its exact feature list, hyperparameters and threshold were recovered. A separately exported earlier analysis script under `notebooks/` documents an 80/20 stratified random split with seed 42 and zero-filling of missing event ratios. Applying that split to the original feature-cache row order yields 7,542 training and 1,886 test users.

Fresh training reproduces all 200 saved trees' node/value arrays exactly. All-user predicted probabilities agree within 1e-14; threshold-0.70 test classifications agree exactly. Differences at about 1e-16 come from floating-point accumulation and do not affect the reproduced scores.

All 15 features were independently rebuilt from `session_events.parquet` and matched to the model cache by user ID (floating tolerance 1e-8 absolute / 1e-10 relative). Labels also match. Rebuilt-feature scores agree within 1e-14. Model, feature-cache and event-cache SHA-256 hashes, environment versions and reconstructed split-user hashes are recorded in [metrics.json](../validation/metrics.json).

**Session-definition finding:** cached `recent_30d_sessions` exactly matches distinct per-user `rebuilt_session` counts in the recent window. Counting source `user_session` instead differs for 2,468 eligible users. The recovered notebook previously used that conflicting source-session definition. Its original project file has now been corrected to use reconstructed sessions and validate event-level counts plus all 15 cached inputs. Cold-cache, warm-cache, repeat execution and deliberate wrong-session regression checks passed. The actual original-path recovery cells were also run successfully; see [the fix record](../notebook_fix/README.md).

The candidate's threshold-0.70 accuracy 0.7900, macro F1 0.6637 and AUC 0.7808 reproduce the supplied results. Full results, error tradeoffs and execution instructions appear in [the validation summary](../validation/validation_summary.md).

## Remaining limitations

- The 96-cell original notebook and 99-cell recovered notebook were inspected, but not run end to end. The recovery entry point was subsequently made portable and tested from the repository root and notebook directory. Historical exploratory cells still have working-directory and state assumptions; optional notebook installation steps remain outside standalone validation.
- Historical features precede 1 March 2020. The original label SQL omits the 1 May upper bound; the validation script supplies explicit outcome-window bounds.
- Original train/test user-ID manifests were unavailable. The reconstructed split is strongly corroborated by exact saved-tree reproduction; it is not a newly untouched holdout.
- Repeated historical test inspection remains a generalization limitation even after successful numerical reproduction.
- The 11- and 18-feature experiments were not retrained or independently verified.
- Seven raw monthly files were not rescanned, and sampling/session reconstruction from those CSV files was not repeated.
- The original calibration chart and source plotting cells were subsequently recovered from the source conversation; no additional calibration was applied. Original Brier score is available. No optimal-calibration, economic-threshold or campaign-effect claim follows.

## Reproduction artifacts

Use [the validation README](../validation/README.md) for the standalone script, pinned dependencies and metrics. The recovery notebook was updated; existing source data/model files were left unchanged. A completed single temporal backtest is now integrated; further independent temporal windows, an untouched final holdout and randomized marketing experiments remain future work.

## Repository preparation — 18 October 2026

The repository includes a project README, data notes, pinned standalone-validation dependencies, aggregate results and a cleaned recovery notebook. Personal absolute paths and saved notebook outputs were removed from the upload version. Its two recovery cells passed cold-cache execution from a separate repository root and warm-cache execution from `notebooks/`, and wrong-session regression was blocked. Candidate validation was rerun successfully against the original local inputs, reproducing the same 0.70 confusion matrix and reported metrics. The [portability evidence](../notebook_fix/portability_check.json) records these checks. No remote publication was performed.


## Completed-result integration — 18 October 2026

The latest document update read the existing temporal script, metrics and bilingual addenda without running them. Historical top-K/rule results were initially transcribed from the owner's handoff. The original source cells, user-posted tables and chart attachment have since been recovered directly from the 项目开发 conversation and preserved in [the evidence archive](../validation/ranking_calibration/README.md); a raw calibration bin table remains unavailable. The existing Brier value supports 0.1275, but not optimal calibration. The temporal JSON independently supports the integrated windows, 6,717/6,445 cohort sizes, AUC 0.7351, macro F1 0.6374 and later top-K/rule comparison.

The temporal audit records 196 cached event-level session-boundary inconsistencies, distinct from the recovery field mismatch. Its already completed tie-invariant sensitivity run changed 14 later-user feature rows; top-K results stayed the same and AUC/F1 were nearly unchanged. Cache agreement guards remain useful, but do not certify strict raw-session correctness. No source data, saved model, verified notebook, original reproduction script/metrics or temporal script/metrics was edited in this integration. Only documentation, a provenance transcription, ignore rules and the upload manifest were updated or added.


## Source-conversation evidence recovery — 18 October 2026

Direct inspection of the 项目开发 conversation found original RF ranking cells and their posted table, the seed-42 rule tie-resolution cells and final posted table, the quantile-bin calibration plotting cells, and the original calibration image attachment. The earlier local-file search was incomplete as a provenance check; absence from the saved 99-cell recovery notebook was not evidence that the analyses had not been performed. Exact extracted cells and output tables, relevant source-turn identifiers and the unchanged chart are now bundled. We did not establish where an expanded notebook was saved or whether it remained in editor memory. No analysis code was executed during recovery and no verified model/data artifact was changed.
