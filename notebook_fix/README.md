# Recovery Notebook Session Consistency

The original recovery notebook was fixed on 15 October 2026 and prepared for GitHub on 18 October 2026. The public notebook has outputs cleared and discovers the project root from the current directory or its parent, instead of using a personal absolute path.

## Fix

Recent sessions now count distinct `rebuilt_session` within each user during 31 January–29 February 2020. This agrees with the historical features and the verified model cache. The earlier recovery code used source `user_session` IDs, which produced different counts for 2,468 eligible users.

Recovery checks reconstructed-session pairs, unique users, session-count consistency, duplicate column suffixes and all 15 model inputs against the existing reference cache when present. Repeated recovery is safe. A failed check stops before replacing the validated `user_features_v2` table; it never overwrites the saved model or model feature cache.

## Verification evidence

[check_results.json](check_results.json) records cold-cache, warm-cache, repeated-run and deliberate wrong-session regression tests, plus unchanged threshold-0.70 model metrics. [installed_verification.json](installed_verification.json) records the successful original-path two-cell execution from 15 October; its hash refers to that historical revision, before the later output/path cleanup.

The 18 October portable version was additionally checked from an isolated repository path. The full exploratory notebook and seven raw source files were not rerun end to end.

Backups remain in the local chat workspace and are deliberately excluded from the GitHub package.


## Later audit qualification

The separate completed temporal audit identified 196 event-level inconsistencies in cached session boundaries. The fix documented above corrects the choice of session **field** and checks consistency with that cache; it does not certify that every cached boundary exactly follows the strict 30-minute rule. The existing temporal sensitivity run changed 14 later-test users' features with unchanged top-K results. No new session reconstruction or cache rewrite was performed during report integration. See [the temporal addendum](../reports/temporal_validation/temporal_validation_addendum_en.md).
