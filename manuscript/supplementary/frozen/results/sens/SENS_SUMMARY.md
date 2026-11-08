# Final verification package — summary (Addendum 9; run 2026-11-07 ≈18:00 local; code sens_analyze.py sha256 3973de30… frozen before execution)

Status: complete. §9.1 and §9.4 were run ≈18:00 local on the confirmatory files; §9.1b, §9.2 and §9.3 at ≈19:57 local once the rotation files
were available again (same frozen script, sha256 3973de30…, unchanged). Every new interval is reported next to the original fixed-calibration
interval; nothing replaces a pre-registered estimate.

## 9.1 Calibration sensitivity — double resampling (calibration AND test keys, independently; τ, τ_v and q̂ re-selected in every iteration; B = 1000)

Dialect cells (5 dialects × 4 models = 20) at r* = 0.20 / α = 0.30:

| quantity | original conclusion (test bootstrap, calibration fixed) | after double resampling | interval width ratio (new/original) |
|---|---|---|---|
| S4 Δanswered vs MSA | CI excludes 0 in 19/20 | **19/20 calibration-robust** (same cell non-significant both ways: ALLaM–UAE) | 0.95–1.42 |
| P2 Δcov under the MSA q̂ | 20/20 | **20/20** | 1.00–1.30 |
| P2 set-size ratio (own q̂) | excludes 1 in 20/20 | **20/20** | **2.7–4.3** |
| D4 residual gap (answered_v(τ_v) − answered_MSA(τ_MSA)) | CI < 0 in 19/20 | **14/20** | **2.2–4.5** |

Reading (rule §9.1): the operational S4 result and the conformal coverage loss are insensitive to the calibration sample (their intervals
barely widen). Two things change: (i) the **set-size-ratio intervals were understated by ≈3×** when the calibration sample was held fixed —
all 20 still exclude 1, but the paper must show the double-resampled intervals; (ii) the **D4 residual gap is sensitive in 6 cells** —
Fanar-EGY, Fanar-UAE, Qwen3-KSA, Qwen3-UAE, Gemma-EGY, Gemma-UAE (the small gaps of the Egyptian/Gulf varieties in three models) — because
τ_v chosen on 808 items is itself variable (D4 widths ×2–4.5). The large residual gaps (MAG and SYR in all four models; all five dialects in
ALLaM) remain. The realised risk at τ_v carries intervals of about ±0.06 under double resampling: a dialect-chosen threshold holds the target
only up to that sampling error.
τ_MSA across calibration resamples: medians 0.786 / 0.499 / 0.523 / 0.498 (ALLaM / Fanar / Qwen3 / Gemma), 95% ranges ≈ ±0.05–0.09.

## 9.4 D4 distance to the risk target (post hoc descriptive; r* = 0.20)

Cells that moved closer to 0.20 under τ_v: **11/20** (ALLaM 5/5, Fanar 3/5, Qwen3 2/5, Gemma 1/5). Cells with realised risk > 0.24 under τ_MSA:
4 (all ALLaM) → 0. Mean |risk − 0.20|: 0.029 → 0.017 overall, but 0.013 → 0.014 (Fanar), 0.019 → 0.016 (Qwen3), 0.017 → 0.023 (Gemma).
Reading: re-selecting the threshold per variety corrects the large transfer failures (ALLaM; Qwen3-MAG/SYR) and otherwise mostly adds
threshold noise at a cost in answered questions (e.g. Qwen3-EGY: risk 0.22 → 0.17, answered 0.53 → 0.42). The "±0.04" range is an observed
range after the fact, not a pre-specified tolerance and not a guarantee.

## What this changes in the paper (wording per reviews #9/#10)
- Per-dialect adaptation "reduces some failures of reliability transfer; where the transferred threshold was already near target it mostly
  re-trades answers for small changes in risk; a gap in answered fraction or set size remains at the targets studied".
- P2 set-size ratios are reported with the double-resampled intervals (≈3× wider; all still exclude 1).
- D4 residual gaps: "calibration-robust for MAG and SYR in all four models and for all dialects in ALLaM; not resolved for the Egyptian and
  Gulf varieties in Fanar, Qwen3 and Gemma".
## 9.1b Rotation subset — S4 Δanswered, order-averaged, under double resampling
Calibration-robust in 19/20 dialect cells; the exception is ALLaM–UAE (original −0.027 [−0.053, −0.001] → −0.026 [−0.057, +0.004]), the same
borderline cell as in the full-sample S4.

## 9.2 Re-run reproducibility (robustness k = 0 vs the confirmatory scores; 500 × 7 cells per model)
Different prediction in 0.9 / 1.3 / 1.4 / 2.0% of cells (ALLaM / Fanar / Qwen3 / Gemma). Among the disagreeing cells the median top-two
letter log-probability margin is 0.000–0.125 nats (0.50–1.75 nats over all cells) and 43–52% of them have a margin below 0.05 nats
(3–9% of all cells): the disagreements sit at near-ties. The gap estimates computed from the two runs differ by at most 0.018 (Δacc),
0.030 (ΔP1) and 0.026 (S4 Δanswered) across all dialects and models — inside the 500-key bootstrap intervals (≈ ±0.05–0.08). Reading
(§9.2 rule): numerical non-determinism of bf16 inference under different batch composition on MPS; no conclusion depends on it. The
measurement is deterministic to within near-tie flips, which is the precision the paper should state.

## 9.3 R4 paired comparison (D = dialect-vs-MSA change − within-variety one-rotation change; key bootstrap)
For the five dialects (20 cells): D < 0 with CI excluding 0 in 15, CI including 0 in 5 (ALLaM EGY/MAG/SYR/UAE, Qwen3 SYR), D > 0 in none.
So the dialect-vs-MSA answer change is not larger than the change produced by one rotation of the same question's options in any
dialect cell. Against MSA's own rotation change (D′) it is larger only for ALLaM Maghrebi (+0.058 [+0.008, +0.106]) and Syrian
(+0.048 [+0.002, +0.098]), smaller in 9 cells, not distinguishable in 9. English differs: its answer change vs MSA exceeds its own small
rotation change in 3/4 models. Reading: answer change alone does not identify a dialect-specific instability; P3 stays withdrawn, with
these paired differences reported in the appendix beside it.
