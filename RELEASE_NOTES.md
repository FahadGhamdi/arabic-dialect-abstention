# Release notes — facts a re-user of these files should know

1. **Precision of the stored scores.** The option-letter log-probabilities `lA..lD` (and the space-variant columns `lA_sp..lD_sp`)
   are stored with four decimals; `p_true` and `p_max` were computed from the full-precision logits and stored with five. Recomputing
   probabilities from the rounded log-probabilities re-orders a few near-tied items. The independent implementation documented one
   material consequence: for Fanar-1-9B at target risk 0.30 the calibration cut-off moves by two items (τ 0.3757 vs 0.3790; answered
   fractions differ by ≤ 0.011). At the primary target (0.20) the two implementations agree to one item (`results/indep_check/INDEP_COMPARISON.md`).
   Future runs should store full-precision log-probabilities.

2. **Merging of letter variants.** Each option letter's probability is the sum of the probabilities of its with-space and without-space
   token variants, i.e. a log-sum-exp of the two log-probabilities, then renormalised over the four letters.

3. **Tie rule.** Items are sorted by confidence in descending order with a stable sort; the S4 threshold is the confidence of the K-th
   item, K being the largest prefix length whose empirical risk is ≤ the target. No tie sits at the ⌈n/2⌉ or K-th position in the
   confirmatory files except Qwen3-8B-Base at target 0.15, where τ depends on the order within a mixed tie group (0.6148 vs 0.6147; one item).

4. **Re-scoring differences.** Re-scoring the original option order on the 500 robustness keys reproduced the confirmatory prediction in
   99.1 / 98.6 / 98.7 / 98.0% of cells (ALLaM / Fanar / Qwen3 / Gemma; `results/sens/S92_reproducibility.csv`). The differing cells sit at
   near-ties (median top-two margin ≤ 0.13 nats). This is the observed rate in the specified re-scoring on one machine (Apple-silicon MPS,
   bf16, batched inference); it is consistent with numerical non-determinism under different batch composition, the cause was not isolated,
   and it is not a general bound.

5. **Gemma-2 attention.** gemma-2-9b was run with eager attention (the implementation the model card recommends for this architecture);
   its generation run was about ten times slower than the other models'.

6. **Shared base.** Fanar-1-9B is a continual pre-training of Gemma-2-9B; the four checkpoints come from three base families.

7. **Bootstrap seeds.** Fixed-calibration intervals: paired key bootstrap, B = 2000, `numpy.random.default_rng(0)`; double resampling
   (calibration and test keys, thresholds re-selected): B = 1000, `default_rng(1)`; the Addendum 10 risk-difference intervals use B = 2000,
   `default_rng(0)` and therefore differ slightly from the post-hoc intervals printed in `results/confirm/CONFIRM_SUMMARY.md`
   (the manuscript uses the Addendum 10 values).

8. **Corrections made after the ledger audit (8 November 2026).** `results/validity/VALIDITY_SUMMARY.md` states that the IFM filter changes
   every endpoint by ≤ 1.1 points; the largest change is 1.45 points (ALLaM–Syrian ΔP1), as the manuscript now says. The summary files are
   left as produced; the ledger (`docs/CLAIMS_LEDGER.csv`) is the source of the manuscript's numbers.

9. **What the generated-answer files contain.** `robust_gen_<model>.csv` holds the short generated continuation (≤ 8 tokens for G1,
   ≤ 32 for G2) and the extracted letter; no dataset text.

10. **Model-assisted screen.** The translation-equivalence screen in `results/audit/` was produced by GPT-6 sessions (two as raters, a
    third as adjudicator); its κ values measure within-model consistency across sessions, not inter-annotator agreement. The rating
    workbooks contain item texts and are not included; `audit/screen_flags_400.csv` holds the flags per pair.

11. **Tie order in re-runs.** A clean-folder re-run (docs/REPRO_CHECK.md) reproduced every confirmatory, diagnostic, verification and supplement
    table byte for byte. Three files moved by tie-order effects under a different pandas/numpy build: the L2 terciles (one item per cell,
    `rank(method="first")` after a merge), the AraDiCE ΔP1 point values (≤ 0.003; tied `p_max` under a non-stable sort) and one rotation's ΔP1
    in R2 (≤ 0.006). No reported number changed at its reported precision; the ledger audit passes on both versions.
