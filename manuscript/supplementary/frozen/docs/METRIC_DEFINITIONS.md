# Metric definitions for the independent computational check (Addendum 9 §9.5)

Written 2026-11-07 from ANALYSIS_PLAN.md. The independent implementation works from THIS file and the raw score files only.

## Inputs
- `results/confirm_scores_<tag>.csv`, one file per model (`tag` ∈ ALLaM-7B-Instruct-preview, Fanar-1-9B, Qwen3-8B-Base, gemma-2-9b).
  Columns: `model, dialect, domain, qid, key, answer, lA, lB, lC, lD, lA_sp, lB_sp, lC_sp, lD_sp, pred, correct, p_true, p_max, n_tok`.
  `dialect` ∈ {MSA, EGY, SYR, KSA, UAE, MAG, ENG}. `key` identifies a question across varieties. `lA..lD` are the combined log-probabilities of
  the four option letters (already log-sum-exp over the with-space / without-space token variants). `answer` is the gold option index 0–3.
  `pred` = argmax of (lA, lB, lC, lD). `correct` = 1 if pred == answer. Define the option probabilities p_o = softmax(lA, lB, lC, lD).
  `p_true` = p_answer; `p_max` = max_o p_o (these columns may be used directly or recomputed; both are expected to agree to 1e-4).
  Drop exact duplicate (dialect, key) rows if any (keep the first).
- `data/confirmatory_splits.json`: lists `calibration` (808 keys) and `test` (1,420 keys); `router_train` (404) is not used here.
- Use only keys that are present for ALL seven varieties in the model's file ("complete keys"); restrict calibration and test to those.

## Confidence and nonconformity
- Confidence s = p_max.
- Conformal nonconformity score of an item = 1 − p_true; of a candidate option o = 1 − p_o.

## P1 — answerable fraction at the MSA-matched risk (test keys only; descriptive)
1. For MSA on the test keys: sort items by s descending (ties: any fixed order; report if ties exist). For k = 1..n, cumulative risk
   r_k = (number of errors among the top-k) / k. Risk–coverage curve on the grid c ∈ {0.05, 0.10, …, 1.00} (20 points): risk at c =
   r_{⌈c·n⌉}. t50 = the curve value at c = 0.50.
2. For each variety v on the test keys: sort by s descending; answerable(v; t50) = (largest k with r_k ≤ t50) / n, or 0 if no k qualifies.
3. Report t50, answerable(v) for all seven varieties, and Δ = answerable(v) − answerable(MSA).

## S4 — operational selective prediction (threshold from calibration MSA, applied to test)
1. On the calibration keys, MSA items only: sort by s descending; r_k as above; K = largest k with r_k ≤ r*; τ = s of the K-th item in that
   order (i.e. the lowest confidence still meeting the target). If no k qualifies, τ = 1.01 (nothing is answered). Compute for
   r* ∈ {0.15, 0.20, 0.25, 0.30}.
2. On the test keys, for each variety v: answered fraction = mean(s ≥ τ); realised risk = error rate among the answered items (NaN if none);
   Δanswered = answered(v) − answered(MSA).
3. Report τ per r*, and per variety the answered fraction and realised risk.

## P2 — split-conformal prediction sets (thresholds from calibration, evaluated on test)
1. For a variety v and level α: q̂_v = the ⌈(n_cal + 1)(1 − α)⌉-th smallest value of (1 − p_true) over the calibration items of v (capped at
   the largest value when ⌈(n_cal+1)(1−α)⌉ > n_cal). Compute for α ∈ {0.20, 0.30}.
2. Coverage under the MSA threshold: for each variety v on test, cov_MSA-thr(v) = mean[(1 − p_true) ≤ q̂_MSA]; Δcov = cov(v) − cov(MSA).
3. Set size under the own threshold: size_v(item) = number of options o with (1 − p_o) ≤ q̂_v; mean over test items; coverage under own
   threshold = mean[(1 − p_true) ≤ q̂_v]; size ratio = mean size_v(own) / mean size_MSA(own).
4. Report q̂ per (α, variety), coverage under MSA threshold, mean set size under MSA threshold, coverage and mean size under own threshold,
   and the size ratio.

## Outputs expected from the independent implementation
`results/indep_check/P1_indep.csv` (model, variety, t50, answerable, d_answerable), `results/indep_check/S4_indep.csv`
(model, target_risk, tau, variety, answered, realised_risk, d_answered), `results/indep_check/P2_indep.csv`
(model, alpha, variety, qhat_v, qhat_msa, cov_msathr, d_cov, size_msathr, cov_ownthr, size_ownthr, size_ratio), plus per-key indicator files
`results/indep_check/perkey_<tag>.csv` (key, variety, s, correct, answered_at_tau_r020, covered_at_qmsa_a030, setsize_own_a030).
No bootstrap is required for the check; point values only.
