# GitHub Upload Checklist

This handoff prepares files only; it does not create a remote repository, choose a license or publish to GitHub.

## Included

- Project README, data notes, this checklist and `.gitignore`.
- Formal English report and reproducibility audit.
- Reproduction script, pinned dependencies, aggregate metrics and validation summary.
- Preserved temporal-validation script and completed `validation/temporal_validation/results/metrics.json`, plus the English design addendum and Chinese review.
- Original ranking/rule/calibration source cells, posted result tables and unchanged calibration-chart attachment recovered from the source conversation; no new scoring or curve generation.
- Cleaned recovery notebook and session-fix evidence.

## Excluded

- `data/`, model pickle and Parquet files.
- Original local scratch notebook and the oddly named exported historical Python file.
- Notebook backups, cell outputs, customer-level IDs/predictions, virtual environments, secrets and temporary files.

## Before publishing

1. Use the prepared folder as the upload root, so `README.md` is at the repository root. For command-line Git, stage the reviewed files explicitly and inspect the staged file list.
2. Preserve `validation/metrics.json` and `validation/temporal_validation/results/metrics.json` as completed historical outputs. Only run training/validation after a separate explicit request; future reruns go to ignored `validation/results/` or new temporal `new_results*` directories.
3. Confirm dataset distribution/access terms and the exact source link before adding any dataset download instructions or sharing data files.
4. Choose a code license if you wish to grant reuse rights. None was selected on your behalf.
5. Preview README links and the analysis report in GitHub. The notebook is an exploratory record; the standalone validation script is the checked model reproduction entry point.
6. Publish only after reviewing the file list. A newly created remote and a first push are separate from this prepared handoff.

The matching original local project also contains excluded data and historical files. The `.gitignore` excludes those known artifacts, while the standalone package contains only the intended upload files.

This integration only edits documentation and upload preparation. Completed validation scripts/results and private data/model inputs are unchanged. The new temporal results directory is intentionally included in the upload; future rerun directories are ignored.
