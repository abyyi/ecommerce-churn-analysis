# Data and Local Artifacts

## Source and scope

The project uses the REES46 event dataset covering October 2019–April 2020. The original local project contains these source filenames:

```text
2019-Oct.csv.gz
2019-Nov.csv.gz
2019-Dec.csv.gz
2020-Jan.csv.gz
2020-Feb.csv.gz
2020-Mar.csv.gz
2020-Apr.csv.gz
```

The precise distribution/download page and its redistribution terms were not independently verified in this handoff. No source URL or dataset license is asserted here. Obtain the matching files through an authorized source and document that source before a full raw-data rebuild. Raw files, sampled event records and trained models are excluded from this repository.

## Sampling and windows

The inspected notebook selects 100,000 distinct users by ordering `hash(user_id)` across the seven-month extract, then retains those users' events. The session cache contains 2,635,748 events. Sessions are numbered within each user: the first event starts a session, and a gap greater than 30 minutes starts another. Preserve user IDs, event ordering and the preparation environment for exact reconstruction; tied timestamps and hash implementation versions can affect reproducibility.

Eligibility: at least one purchase before 1 March 2020. Feature window: 1 October 2019–1 March 2020 exclusive. Recent window: 31 January–1 March 2020 exclusive. Outcome window: 1 March–1 May 2020 exclusive. No purchase in the outcome window means churn.

## Inputs required by the standalone validation script

| Local file | Required content |
|---|---|
| `data/sample/session_events.parquet` | Sampled events with `user_id`, `event_time`, `event_type`, `price`, `rebuilt_session`; other original columns may be present |
| `data/sample/user_features_v2.parquet` | 9,428 unique eligible users, the 15 candidate inputs and `churn`; preserve the verified row order for historical split reconstruction |
| `data/sample/churn_model_v2.pkl` | Trusted dictionary containing fitted `model`, ordered `features` and `threshold=0.7` |

The script reconstructs model inputs and labels from session events and compares them against the feature cache. It freshly fits the model and compares tree states and probabilities with the trusted saved artifact. Original input hashes and versions appear in [metrics.json](validation/metrics.json). Modified datasets may correctly fail the reproduction assertions.

The recovery notebook can restore candidate features from the session cache; a historical feature cache is created locally when needed. If the model feature reference exists, all 15 candidate inputs are compared with it. Recovery does not create or overwrite `user_features_v2.parquet` or the saved model pickle automatically.

## What is not included

The repository provides code, aggregate metrics and reports, not raw data, sampled customer records, model binaries, or a tested raw-to-model release pipeline. Earlier raw-data preparation cells remain in the exploratory notebook as a historical record. They were not rerun for this handoff, and should not be confused with the tested two-cell recovery entry point. There is no verified one-command download or raw CSV rebuild supplied here.


## Separate completed temporal backtest

The temporal backtest uses earlier and later 92-day feature windows, each with exactly 60-day no-purchase targets. The later target is [2020-03-01, 2020-04-30), excluding all of 30 April. This is not interchangeable with the original [2020-03-01, 2020-05-01) target. Cohort sizes and prevalence differ. See [the temporal design record](reports/temporal_validation/temporal_validation_addendum_en.md).

The temporal event audit also identified 196 cached session-boundary inconsistencies. An already completed in-memory, tie-invariant reconstruction changed 14 later users' feature rows without changing top-K summaries. These are diagnostic findings; original cached events/features and saved models remain unchanged.
