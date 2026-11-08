# Diagnostic views of the reliability cost — summary (Addendum 7; exploratory)

Run 2026-11-07 ≈07:05 local on the confirmatory score files (sha256 as in CONFIRM_SUMMARY.md). Code: scripts/diag_analyze.py frozen
as sha256 9337bf5b… before execution (kept as scripts/diag_analyze_v1_frozen.py); v1.1 = 44acd4a2… differs only in the figure title
and a common AUROC y-range (no number changed). Full tables: DIAG_REPORT.md; CSVs: D1_D2_discrimination.csv, D4_variety_threshold.csv;
figure: diag_figure.png/pdf. Status: **exploratory — specified after the confirmatory results were seen and before computation.**
Reading rules applied exactly as Addendum 7 §7.4; the three views are diagnostic, not additive causal components (§7.1).

## 1. Discrimination of the confidence score (D1–D3; test, 1,420 keys; paired by key)

ΔAUROC(p_max → correct) vs MSA, cells whose 95% CI excludes 0 (negative):

| variety | ALLaM | Fanar | Qwen3 | Gemma | cells |
|---|---|---|---|---|---|
| MAG | −0.045 [−.072,−.015] | −0.040 [−.063,−.014] | −0.059 [−.087,−.032] | −0.029 [−.057,−.001] | **4/4** |
| SYR | −0.056 [−.084,−.028] | −0.038 [−.063,−.012] | −0.065 [−.091,−.039] | −0.036 [−.063,−.009] | **4/4** |
| EGY | −0.023 [−.050,+.002] | −0.037 [−.060,−.015] | −0.031 [−.055,−.008] | −0.020 [−.044,+.005] | 2/4 |
| KSA | −0.012 [−.037,+.011] | −0.033 [−.057,−.010] | −0.015 [−.037,+.006] | −0.027 [−.050,−.004] | 2/4 |
| UAE | +0.002 [−.022,+.026] | −0.013 [−.035,+.010] | −0.014 [−.039,+.009] | −0.005 [−.028,+.018] | 0/4 |

MSA AUROC 0.77–0.80; ENG higher than MSA in 4/4 (+0.03…+0.07). AUGRC (accuracy and ranking together) is higher than MSA in 20/20
dialect cells (+0.013…+0.064), largest for MAG/SYR.

Reading (§7.4): in Maghrebi and Syrian the confidence score ranks correct answers less well than in MSA, in all four models
(ΔAUROC −0.03 to −0.07); in Egyptian and Saudi the difference is detectable in two models of four; in Emirati it is not detectably
different on this sample. A negative ΔAUROC is an upper bound on discrimination loss (undetected meaning changes register as errors).

## 2. Threshold transfer vs a variety-specific threshold (D4; r* = 0.20; τ_v chosen on the 808 calibration items of the variety)

| model | realised risk under τ_MSA (dialects) | realised risk under τ_v | recoverable = ans_v(τ_v) − ans_v(τ_MSA) | residual gap at equal target, ans_v(τ_v) − ans_MSA(τ_MSA) |
|---|---|---|---|---|
| ALLaM | 0.24–0.31 | 0.18–0.24 | −0.08 … −0.17 (5/5 negative) | −0.12 … −0.28 (5/5 CI < 0) |
| Fanar | 0.21–0.23 | 0.17–0.23 | −0.07 … +0.04 (EGY positive, its realised risk 0.23) | −0.04 … −0.20 (5/5) |
| Qwen3 | 0.20–0.24 | 0.17–0.20 | −0.13 … −0.01 (5/5 negative) | −0.08 … −0.34 (5/5) |
| Gemma | 0.17–0.22 | 0.16–0.22 | −0.08 … +0.02 | −0.01 … −0.20 (4/5; UAE −0.010 [−.031,+.011]) |

Across the 20 dialect cells: residual gap CI < 0 in 19/20; the recoverable contrast is negative with CI < 0 in 17/20 and positive in 2/20.
Realised risk at τ_v lies within ≈ ±0.04 of the target in every cell (0.16–0.24), i.e. the variety-chosen threshold holds the target
on test; under τ_MSA the dialect risk floated above it (up to 0.31).

Reading (§7.4): re-thresholding alone does not remove the operational gap. Choosing the threshold on the variety restores the risk
target, and doing so **answers fewer dialect questions, not more**: the gap at equal target risk (−0.04 … −0.34) is larger than the S4
gap at the transferred threshold, which understated it because the MSA threshold let the dialect error rate exceed the target
(the "double penalty" of S4). This is the same picture as P1 (oracle-matched risk) and as S2 (Mondrian conformal restores coverage at a
set-size cost): **variety-specific calibration repairs the guarantee, not the efficiency gap.**

## 3. What the three views say together (within §7.1 limits)

Dialect accuracy is lower (view a); an MSA-tuned abstention threshold over-answers on dialects and misses its risk target (view b);
correcting the threshold per variety enforces the target and widens the answered-fraction gap (view b); and in the distant varieties the
confidence score itself separates right from wrong answers less well (view c), so no threshold choice can restore parity. No fraction of
the gap is attributed to any one view. Consequence for the paper's claim: "per-dialect calibration recovers most of the gap" must be
restated as "per-dialect calibration restores the stated reliability target; the efficiency cost (fewer answers / larger sets) remains
and is largest where the confidence score is least discriminative (MAG, SYR)".

## 4. Not done, by rule
No further analysis was added on the basis of these results. The MSA-confidence selection diagnostic (review #8) is deferred and not run.
S1 and S3 move to the appendix; this figure enters the main text (Addendum 7 §7.3 D5).
