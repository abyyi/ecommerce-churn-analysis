# Candidate Model Reproduction

This package reconstructs the historical random test split, retrains the saved 15-feature Random Forest, compares it with the trusted local saved artifact, rebuilds features from session-event data, and exports evaluation at thresholds 0.50 and 0.70. It does not create a new untouched holdout or rerun raw CSV preparation.

## Run

Use Python 3.12.14 and the supplied dependency versions. From the repository root after copying this folder into `validation/`:

```sh
python3 -m venv .venv-validation
.venv-validation/bin/python -m pip install -r validation/requirements.txt
.venv-validation/bin/python validation/validate_15_feature_model.py \
  --project-root . \
  --output-dir validation/results
```

Required existing files under the project root:

- `data/sample/user_features_v2.parquet`
- `data/sample/session_events.parquet`
- `data/sample/churn_model_v2.pkl`

Only load a pickle from a trusted source. The script leaves these inputs unchanged. The verified run used the original local project inputs; their hashes are in `metrics.json`.

Assertions check feature schema, class encoding, candidate threshold, cohort counts, non-overlapping splits, exact saved-tree reproduction, numerical probability agreement, event-cache feature reconstruction and label reconstruction. Changed inputs can legitimately cause an assertion to fail; investigate rather than relaxing the checks to match a score.

Output: `metrics.json`, with feature order, full estimator settings, preprocessing, versions, source hashes, split hashes, two threshold evaluations and a matched majority baseline. No user-level predictions or user IDs are included in this package.

See [validation_summary.md](validation_summary.md) for the completed run. The earlier source-session definition in the recovery notebook was inconsistent with the model cache. Both the corrected original notebook and this script now use `rebuilt_session` for recent sessions, as confirmed by event-level reconstruction. See [the fix record](../notebook_fix/README.md).


## Additional completed checks integrated on 18 October

- [Historical ranking/calibration evidence](ranking_calibration/README.md): original historical source cells, posted top-K/rule outputs and chart recovered from the source conversation, with no calculations repeated.
- [Fixed temporal backtest](temporal_validation/README.md): preserved standalone script and completed results, separate from the historical reproduction above. The report update did not execute either training script.

The temporal script's label window ends at 30 April exclusive, whereas the original reproduction ends at 1 May exclusive; do not combine their prevalence or interpret score changes as a controlled time-drift comparison.
