# Historical Ranking and Calibration: Recovered Evidence

The original source cells, user-posted result tables and calibration-chart attachment were recovered directly from the **项目开发** conversation on 18 October 2026. These analyses had been completed there; the earlier local-file-only review had not located their original evidence. The saved local recovery notebook still had 99 cells and did not contain these extra ranking/calibration cells at the time of inspection. The conversation does not establish whether an expanded notebook was saved elsewhere or remained open/unsaved in the editor.

## Archived materials

- [conversation_cells.py](conversation_cells.py): source cells extracted verbatim, in analysis order, including model loading, original test split, RF ranking, the initial rule, its final 1,000-repeat tie correction, and calibration plotting. **Not a standalone pipeline:** the original code assumes the notebook namespace and notebook working directory. The initial stable rule is superseded by the randomized-tie cell.
- [conversation_evidence.json](conversation_evidence.json): source turn identifiers, exact code blocks and user-posted RF/final-rule tables. Unrelated personal conversation content is excluded.
- [reference_results.json](reference_results.json): rounded figures with corrected provenance.
- [Original calibration chart](../../reports/figures/probability_calibration_original.png), copied unchanged, and [image provenance](calibration_image_provenance.json).

The recovered code establishes seed **42** for the browsing-rule randomized tie comparisons, using 1,000 permutations per fraction with `np.lexsort`. RF ranking sorts original model probability descending; K is `int(N * fraction)`. The user-posted final table includes rule mean precision 0.9314/0.9304/0.9302 and rule mean lift 1.1466/1.1454/1.1452.

The calibration code uses `calibration_curve(..., n_bins=10, strategy="quantile")`, and the original chart shows plotted points broadly near the diagonal, with visible deviations. Original [metrics](../metrics.json) record Brier score 0.1275096330. No extra calibration was applied, optimal calibration is not established, and a raw bin table was not recovered.

**Recovery is not recomputation:** no model was loaded, trained, scored, reranked or recalibrated in this evidence-recovery task. The original verified recovery notebook, model/data caches and evaluation scripts/results remain untouched. The [temporal script](../temporal_validation/validate_temporal.py) is a separate previously completed backtest.
