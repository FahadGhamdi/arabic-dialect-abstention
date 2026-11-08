# Independent computational check — notes (Addendum 9 §9.5)

Implementation: `scripts/indep_check/recompute.py`, written from `docs/METRIC_DEFINITIONS.md`, `data/confirmatory_splits.json` and the four `results/confirm_scores_<tag>.csv` files only. No existing analysis script, plan or report was opened. Point values only (no bootstrap).

## (a) Ambiguities / interpretation choices

1. **`correct` cannot be reproduced from the rounded `lA..lD`; the file column is used.** The definitions say `pred = argmax(lA..lD)`, but the CSV carries the log-probs to 4 decimals and many rows have two or more options tied at that maximum. Recomputing the argmax (first index on ties) reproduces the file's `pred` for ALLaM and gemma but not for Fanar and Qwen3; every mismatch is on a tie row and the file's `pred` is always one of the tied options (for Qwen3 it coincides in 1121/1132 tie rows with the option whose with-space variant `l*_sp` is larger, i.e. the file's argmax was taken at full precision where the tie is broken below the 4th decimal). Primary results therefore take errors from the file's `correct` column; p_max/p_true/p_o do not depend on which tied option is the prediction, so this mixes nothing else. Per model:

   - ALLaM-7B-Instruct-preview: argmax ties in lA..lD = 508 rows; recomputed-vs-file pred mismatches = 0 (off tie rows: 0; file pred not a tied max: 0); `correct` flips = 0
   - Fanar-1-9B: argmax ties in lA..lD = 87 rows; recomputed-vs-file pred mismatches = 37 (off tie rows: 0; file pred not a tied max: 0); `correct` flips = 19
   - Qwen3-8B-Base: argmax ties in lA..lD = 1132 rows; recomputed-vs-file pred mismatches = 796 (off tie rows: 0; file pred not a tied max: 0); `correct` flips = 541
   - gemma-2-9b: argmax ties in lA..lD = 90 rows; recomputed-vs-file pred mismatches = 0 (off tie rows: 0; file pred not a tied max: 0); `correct` flips = 0
   Sensitivity (if one *did* recompute `correct` with first-index tie-breaking), max abs change per table: ALLaM-7B-Instruct-preview: P1 0.00e+00; S4 0.00e+00; P2 0.00e+00 | Fanar-1-9B: P1 0.00e+00; S4 1.16e-03 (realised_risk, KSA, r*=0.25: 0.2787 vs 0.2799); P2 0.00e+00 | Qwen3-8B-Base: P1 8.45e-03 (answerable, ENG: 0.8303 vs 0.8387); S4 1.41e-02 (answered, EGY, r*=0.25: 0.6824 vs 0.6965); P2 0.00e+00 | gemma-2-9b: P1 0.00e+00; S4 0.00e+00; P2 0.00e+00.

2. **Probabilities recomputed from lA..lD (primary) vs. the `p_max`/`p_true` columns.** Primary results use p_o = softmax(lA..lD) recomputed from the four log-probability columns (s = recomputed p_max; nonconformity 1 − recomputed p_true; set sizes from the recomputed p_o), which is the literal definition and keeps P2 internally consistent (the true option is in the own-threshold set iff the coverage indicator is 1). Max |recomputed − column|: ALLaM-7B-Instruct-preview: p_true 5.0e-06, p_max 5.0e-06; Fanar-1-9B: p_true 2.9e-05, p_max 2.9e-05; Qwen3-8B-Base: p_true 2.9e-05, p_max 2.9e-05; gemma-2-9b: p_true 2.5e-05, p_max 2.6e-05 (all within the 1e-4 stated in the definitions). Re-running the pipeline with the file columns for s and p_true (set sizes still from the recomputed p_o) changes the output tables by at most (cell where the max occurs in parentheses):

   - ALLaM-7B-Instruct-preview: P1 0.00e+00; S4 4.84e-06 (tau, MSA, r*=0.2: 0.8047 vs 0.8047); P2 1.41e-03 (size_msathr, UAE, α=0.3: 1.3014 vs 1.3000)
   - Fanar-1-9B: P1 0.00e+00; S4 1.06e-02 (answered, EGY, r*=0.3: 0.7296 vs 0.7190); P2 1.03e-05 (qhat_v, SYR, α=0.2: 0.7835 vs 0.7835)
   - Qwen3-8B-Base: P1 0.00e+00; S4 7.04e-04 (answered, MAG, r*=0.15: 0.2704 vs 0.2711); P2 8.45e-03 (size_ownthr, MAG, α=0.3: 1.5725 vs 1.5641)
   - gemma-2-9b: P1 0.00e+00; S4 1.02e-03 (realised_risk, UAE, r*=0.25: 0.2399 vs 0.2410); P2 7.04e-04 (size_msathr, ENG, α=0.3: 1.2908 vs 1.2915)
   These are boundary effects: items sitting exactly on τ or q̂ (each worth 1/1420 = 7.0e-4), or near-tied calibration items being re-ordered so that K moves. The notable case is Fanar at r*=0.30, where the calibration cumulative risk hovers at the target: K/τ = ALLaM-7B-Instruct-preview 574/0.59395 (recomputed) vs 574/0.59395 (columns), Fanar-1-9B 634/0.37568 (recomputed) vs 632/0.37895 (columns), Qwen3-8B-Base 670/0.39418 (recomputed) vs 670/0.39418 (columns), gemma-2-9b 541/0.38674 (recomputed) vs 541/0.38673 (columns). So agreement of the probabilities to 1e-4 does not guarantee agreement of τ(0.30) to better than ~3e-3 or of the answered fractions to better than ~1e-2 for Fanar; a comparison against the primary analysis should allow for this.

3. **Ties in s.** The definitions allow 'any fixed order'. I sort by s descending with `key` ascending as the deterministic tie-breaker (stable mergesort). Tie counts (items sharing an s value with another item / tie groups) and whether a tie straddles the decisive boundary:

   - ALLaM-7B-Instruct-preview: MSA test (P1): 80 items in 39 groups, tie at the k50=710 boundary: False; MSA calibration (S4): 24 items in 12 groups, tie at the K-th item boundary per r*: {'0.15': False, '0.20': False, '0.25': False, '0.30': False}
   - Fanar-1-9B: MSA test (P1): 8 items in 4 groups, tie at the k50=710 boundary: False; MSA calibration (S4): 0 items in 0 groups, tie at the K-th item boundary per r*: {'0.15': False, '0.20': False, '0.25': False, '0.30': False}
   - Qwen3-8B-Base: MSA test (P1): 302 items in 135 groups, tie at the k50=710 boundary: False; MSA calibration (S4): 110 items in 53 groups, tie at the K-th item boundary per r*: {'0.15': False, '0.20': False, '0.25': False, '0.30': False}
   - gemma-2-9b: MSA test (P1): 2 items in 1 groups, tie at the k50=710 boundary: False; MSA calibration (S4): 0 items in 0 groups, tie at the K-th item boundary per r*: {'0.15': False, '0.20': False, '0.25': False, '0.30': False}
   Sensitivity: re-running with errors-first ('pessimistic') or correct-first ('optimistic') tie order changes the P1/S4 tables by at most:

   - ALLaM-7B-Instruct-preview: pessimistic P1 0.00e+00; S4 0.00e+00; optimistic P1 1.41e-03 (answerable, UAE: 0.4190 vs 0.4204); S4 0.00e+00
   - Fanar-1-9B: pessimistic P1 0.00e+00; S4 0.00e+00; optimistic P1 0.00e+00; S4 0.00e+00
   - Qwen3-8B-Base: pessimistic P1 7.04e-04 (answerable, EGY: 0.4042 vs 0.4035); S4 0.00e+00; optimistic P1 0.00e+00; S4 7.04e-04 (answered, MAG, r*=0.15: 0.2704 vs 0.2711)
   - gemma-2-9b: pessimistic P1 0.00e+00; S4 0.00e+00; optimistic P1 0.00e+00; S4 0.00e+00
   Thresholds that depend on the tie order: Qwen3-8B-Base τ(0.15) 0.614767 [K=361] -> 0.614669 [K=362] (optimistic). (The 'tie at boundary' flags above only test whether the K-th item is tied with the next one; a tie group that *starts* right after K with mixed outcomes can also let K extend into it under a different order, which is what happens here.)

4. **Ceilings and ratio comparisons done exactly.** ⌈c·n⌉, ⌈n/2⌉ and ⌈(n_cal+1)(1−α)⌉ are computed with exact rational arithmetic (`fractions.Fraction`), not floating point, so e.g. 0.05·1420 cannot round to 71.0000…1 and be ceiled to 72. Likewise the conditions r_k ≤ r*, r_k ≤ t50 are evaluated as exact integer inequalities (E_k·den ≤ num·k), so a cumulative risk exactly equal to the target counts as meeting it.

5. **t50 and τ are the k-th order statistic, not an interpolated quantile.** t50 = r_{⌈n/2⌉}; τ = s of the K-th item in the calibration MSA ordering (the lowest confidence still meeting the target); 1.01 when no k qualifies. 's ≥ τ' is applied inclusively on test.

6. **Duplicate rule.** 'Exact duplicate (dialect, key) rows' was read as rows sharing the same (dialect, key) pair; the first occurrence is kept. Counts dropped per model are in (b) (also shown: how many of them were fully identical rows).

7. **Complete keys.** A key is complete if, after duplicate dropping, it appears for all seven varieties {MSA, EGY, SYR, KSA, UAE, MAG, ENG}. Calibration and test lists were intersected with the complete keys; `router_train` keys are ignored.

8. **q̂ cap.** If ⌈(n_cal+1)(1−α)⌉ > n_cal the largest calibration nonconformity is used; the index actually used is listed in (b). (With n_cal = 808: α=0.20 → 648, α=0.30 → 567; no capping needed.)

9. **Per-key files** contain test keys only (the only split on which the three indicators are evaluated), all seven varieties, columns exactly as specified; `s` is the recomputed p_max and `correct` is the file column (see 1–2).

10. **Extra file.** `P1_msa_curve_indep.csv` holds the 20-point MSA risk–coverage curve (k = ⌈c·n⌉ and risk), which the definitions ask to compute but the specified output CSVs do not carry.

11. **Realised risk with nothing answered** is NaN (written as an empty cell in the CSV).

## (b) Sizes

| model | raw rows | dup (dialect,key) dropped | keys in file | complete keys | calibration used (listed) | test used (listed) | n_cal MSA | n_test MSA | q̂ index α=0.20 / 0.30 (of n_cal) |
|---|---|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | 18424 | 0 (fully identical: 0) | 2632 | 2632 | 808 (808) | 1420 (1420) | 808 | 1420 | 648 / 567 (of 808) |
| Fanar-1-9B | 18424 | 0 (fully identical: 0) | 2632 | 2632 | 808 (808) | 1420 (1420) | 808 | 1420 | 648 / 567 (of 808) |
| Qwen3-8B-Base | 18424 | 0 (fully identical: 0) | 2632 | 2632 | 808 (808) | 1420 (1420) | 808 | 1420 | 648 / 567 (of 808) |
| gemma-2-9b | 18424 | 0 (fully identical: 0) | 2632 | 2632 | 808 (808) | 1420 (1420) | 808 | 1420 | 648 / 567 (of 808) |

Dialects present in every file: EGY, ENG, KSA, MAG, MSA, SYR, UAE. Calibration/test overlap: 0, 0, 0, 0. Complete keys in no split (router_train excluded): 0, 0, 0, 0.

## (c) Key numbers

### t50, S4 τ per r* (K = number of calibration-MSA items answered), q̂_MSA per α

| model | t50 | τ(0.15) [K] | τ(0.20) [K] | τ(0.25) [K] | τ(0.30) [K] | q̂_MSA(0.20) | q̂_MSA(0.30) |
|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | 0.20282 | 0.89614 [308] | 0.80474 [405] | 0.67065 [496] | 0.59395 [574] | 0.87853 | 0.75211 |
| Fanar-1-9B | 0.14930 | 0.57923 [367] | 0.50125 [450] | 0.43593 [537] | 0.37568 [634] | 0.75556 | 0.70820 |
| Qwen3-8B-Base | 0.15634 | 0.61477 [361] | 0.52308 [486] | 0.44839 [580] | 0.39418 [670] | 0.77050 | 0.69103 |
| gemma-2-9b | 0.19437 | 0.54588 [311] | 0.49815 [380] | 0.44780 [442] | 0.38674 [541] | 0.77516 | 0.73419 |

### MAG and SYR: P1 answerable, S4 at r*=0.20, P2 at α=0.30

| model | variety | P1 answerable (Δ vs MSA) | S4 answered (Δ) | S4 realised risk | P2 cov@q̂_MSA (Δcov) | P2 size own | size ratio |
|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | MSA | 0.5007 (+0.0000) | 0.5155 (+0.0000) | 0.2131 | 0.6817 (+0.0000) | 1.3106 | 1.0000 |
| ALLaM-7B-Instruct-preview | MAG | 0.2641 (-0.2366) | 0.4028 (-0.1127) | 0.2797 | 0.6063 (-0.0754) | 1.5324 | 1.1693 |
| ALLaM-7B-Instruct-preview | SYR | 0.3141 (-0.1866) | 0.4627 (-0.0528) | 0.3059 | 0.6183 (-0.0634) | 1.5768 | 1.2031 |
| Fanar-1-9B | MSA | 0.5000 (+0.0000) | 0.5577 (+0.0000) | 0.1907 | 0.6937 (+0.0000) | 1.2310 | 1.0000 |
| Fanar-1-9B | MAG | 0.2887 (-0.2113) | 0.4056 (-0.1521) | 0.2083 | 0.5894 (-0.1042) | 1.5423 | 1.2529 |
| Fanar-1-9B | SYR | 0.3352 (-0.1648) | 0.4324 (-0.1254) | 0.2280 | 0.6134 (-0.0803) | 1.4521 | 1.1796 |
| Qwen3-8B-Base | MSA | 0.5014 (+0.0000) | 0.5873 (+0.0000) | 0.2002 | 0.7000 (+0.0000) | 1.1838 | 1.0000 |
| Qwen3-8B-Base | MAG | 0.2275 (-0.2739) | 0.3796 (-0.2077) | 0.2356 | 0.5690 (-0.1310) | 1.5725 | 1.3284 |
| Qwen3-8B-Base | SYR | 0.3127 (-0.1887) | 0.4655 (-0.1218) | 0.2315 | 0.6345 (-0.0655) | 1.4486 | 1.2237 |
| gemma-2-9b | MSA | 0.5014 (+0.0000) | 0.4690 (+0.0000) | 0.1757 | 0.7049 (+0.0000) | 1.4211 | 1.0000 |
| gemma-2-9b | MAG | 0.3190 (-0.1824) | 0.2873 (-0.1817) | 0.1740 | 0.6239 (-0.0810) | 1.7211 | 1.2111 |
| gemma-2-9b | SYR | 0.3176 (-0.1838) | 0.3458 (-0.1232) | 0.2179 | 0.6176 (-0.0873) | 1.7528 | 1.2334 |

### Full P1 answerable fraction, all varieties

| model | MSA | EGY | SYR | KSA | UAE | MAG | ENG |
|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | 0.5007 | 0.4106 | 0.3141 | 0.3908 | 0.4190 | 0.2641 | 0.6239 |
| Fanar-1-9B | 0.5000 | 0.3613 | 0.3352 | 0.3789 | 0.4261 | 0.2887 | 0.6944 |
| Qwen3-8B-Base | 0.5014 | 0.4042 | 0.3127 | 0.4430 | 0.4338 | 0.2275 | 0.8303 |
| gemma-2-9b | 0.5014 | 0.3528 | 0.3176 | 0.3732 | 0.4373 | 0.3190 | 0.7775 |

### S4 answered fraction / realised risk at r*=0.20, all varieties

| model | MSA | EGY | SYR | KSA | UAE | MAG | ENG |
|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | 0.5155 / 0.2131 | 0.4768 / 0.2482 | 0.4627 / 0.3059 | 0.4620 / 0.2378 | 0.5014 / 0.2584 | 0.4028 / 0.2797 | 0.5831 / 0.1824 |
| Fanar-1-9B | 0.5577 / 0.1907 | 0.4754 / 0.2074 | 0.4324 / 0.2280 | 0.4845 / 0.2166 | 0.5056 / 0.2047 | 0.4056 / 0.2083 | 0.7099 / 0.1587 |
| Qwen3-8B-Base | 0.5873 / 0.2002 | 0.5268 / 0.2193 | 0.4655 / 0.2315 | 0.5204 / 0.2003 | 0.5324 / 0.2077 | 0.3796 / 0.2356 | 0.7458 / 0.1190 |
| gemma-2-9b | 0.4690 / 0.1757 | 0.3993 / 0.2222 | 0.3458 / 0.2179 | 0.3951 / 0.2121 | 0.4352 / 0.1926 | 0.2873 / 0.1740 | 0.6979 / 0.1554 |

### P2 coverage under q̂_MSA / mean set size under own q̂ at α=0.30, all varieties

| model | MSA | EGY | SYR | KSA | UAE | MAG | ENG |
|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | 0.6817 / 1.311 | 0.6451 / 1.449 | 0.6183 / 1.577 | 0.6345 / 1.462 | 0.6387 / 1.411 | 0.6063 / 1.532 | 0.7261 / 1.127 |
| Fanar-1-9B | 0.6937 / 1.231 | 0.6599 / 1.394 | 0.6134 / 1.452 | 0.6401 / 1.432 | 0.6613 / 1.383 | 0.5894 / 1.542 | 0.7599 / 0.920 |
| Qwen3-8B-Base | 0.7000 / 1.184 | 0.6634 / 1.400 | 0.6345 / 1.449 | 0.6704 / 1.387 | 0.6676 / 1.325 | 0.5690 / 1.573 | 0.8141 / 0.835 |
| gemma-2-9b | 0.7049 / 1.421 | 0.6592 / 1.575 | 0.6176 / 1.753 | 0.6697 / 1.557 | 0.6746 / 1.570 | 0.6239 / 1.721 | 0.7951 / 0.966 |

### MSA risk–coverage curve on test (P1 step 1), risk at c = 0.05 … 1.00

| model | 0.05 | 0.10 | 0.15 | 0.20 | 0.25 | 0.30 | 0.35 | 0.40 | 0.45 | 0.50 | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | 0.80 | 0.85 | 0.90 | 0.95 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALLaM-7B-Instruct-preview | 0.042 | 0.056 | 0.070 | 0.060 | 0.087 | 0.108 | 0.129 | 0.153 | 0.183 | 0.203 | 0.228 | 0.255 | 0.273 | 0.297 | 0.319 | 0.344 | 0.366 | 0.376 | 0.399 | 0.411 |
| Fanar-1-9B | 0.028 | 0.035 | 0.033 | 0.042 | 0.051 | 0.066 | 0.076 | 0.106 | 0.136 | 0.149 | 0.183 | 0.210 | 0.247 | 0.261 | 0.286 | 0.307 | 0.335 | 0.349 | 0.368 | 0.387 |
| Qwen3-8B-Base | 0.028 | 0.028 | 0.042 | 0.053 | 0.070 | 0.082 | 0.091 | 0.114 | 0.139 | 0.156 | 0.186 | 0.204 | 0.230 | 0.247 | 0.265 | 0.283 | 0.301 | 0.329 | 0.350 | 0.370 |
| gemma-2-9b | 0.042 | 0.049 | 0.052 | 0.077 | 0.093 | 0.106 | 0.133 | 0.155 | 0.172 | 0.194 | 0.227 | 0.257 | 0.281 | 0.305 | 0.325 | 0.344 | 0.366 | 0.387 | 0.400 | 0.413 |
