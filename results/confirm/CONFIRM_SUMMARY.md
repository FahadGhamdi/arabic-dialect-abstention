# Confirmatory results — summary (pre-registered; test = 1,420 held-out keys; thresholds from 808 calibration keys; B=2,000 paired bootstrap over test keys)

Analysis code: scripts/confirm_analyze.py (sha256 8ade05cd…, fixed during score collection — after scoring had started, before any confirmatory file was opened for analysis; v1→v2 change = S4 only). Run 2026-11-05 ≈08:10 local on the staged copies of the four confirm_scores_*.csv files (18,424 rows each, no duplicates/NaN). No deviations from ANALYSIS_PLAN.md.

## P1 — answerable fraction at the risk MSA attains at 50% coverage (Δ vs MSA, pp [95% CI])

| dialect | ALLaM-7B | Fanar-1-9B | Qwen3-8B | Gemma-2-9b |
|---|---|---|---|---|
| UAE | 0.42 (-8 [-12, -4]) | 0.43 (-7 [-10, -5]) | 0.43 (-7 [-13, -2]) | 0.44 (-6 [-15, -2]) |
| EGY | 0.41 (-9 [-14, -5]) | 0.36 (-14 [-19, -9]) | 0.40 (-10 [-18, -5]) | 0.35 (-15 [-19, -11]) |
| KSA | 0.39 (-11 [-15, -6]) | 0.38 (-12 [-16, -8]) | 0.44 (-6 [-14, -2]) | 0.37 (-13 [-17, -10]) |
| SYR | 0.31 (-19 [-24, -15]) | 0.34 (-16 [-21, -13]) | 0.31 (-19 [-23, -13]) | 0.32 (-18 [-25, -14]) |
| MAG | 0.26 (-24 [-31, -17]) | 0.29 (-21 [-28, -14]) | 0.23 (-27 [-32, -21]) | 0.32 (-18 [-24, -13]) |
| ENG | 0.62 (+12 [+7, +18]) | 0.69 (+19 [+15, +25]) | 0.83 (+33 [+27, +40]) | 0.78 (+28 [+23, +34]) |
| matched risk | 0.203 | 0.149 | 0.156 | 0.194 |

Δ shown = plug-in estimate (dialect − MSA on the full test set) with the percentile bootstrap CI; the bootstrap mean of Δ differs from the plug-in by ≤ 1.4 pp because the statistic is non-linear (an earlier version of this table showed the bootstrap mean). All 20 dialect×model CIs exclude zero. Compared with the pilot (n=500): same ordering (MAG ≈ SYR > KSA ≈ EGY > UAE), tighter intervals; ALLaM's MAG cost is larger than in the pilot (−24 vs −11 pp).

## P2 — conformal at α=0.30 (one target coverage, 0.70, for all varieties): coverage loss under the MSA threshold, and set-size ratio at the own-variety threshold with the ACHIEVED coverage shown (MSA achieved: ALLaM 0.68, Fanar 0.69, Qwen3 0.70, Gemma 0.71)

| dialect | ALLaM-7B | Fanar-1-9B | Qwen3-8B | Gemma-2-9b |
|---|---|---|---|---|
| UAE | Δcov -4 [-6, -2]; size ×1.08 [1.05, 1.10] @cov 0.67 | Δcov -3 [-5, -1]; size ×1.12 [1.10, 1.15] @cov 0.70 | Δcov -3 [-5, -1]; size ×1.12 [1.09, 1.15] @cov 0.70 | Δcov -3 [-5, -1]; size ×1.10 [1.08, 1.13] @cov 0.71 |
| EGY | Δcov -4 [-6, -2]; size ×1.11 [1.08, 1.13] @cov 0.69 | Δcov -3 [-5, -1]; size ×1.13 [1.11, 1.16] @cov 0.70 | Δcov -4 [-6, -2]; size ×1.18 [1.15, 1.21] @cov 0.72 | Δcov -5 [-7, -3]; size ×1.11 [1.08, 1.13] @cov 0.70 |
| KSA | Δcov -5 [-7, -3]; size ×1.12 [1.09, 1.14] @cov 0.68 | Δcov -5 [-7, -3]; size ×1.16 [1.14, 1.19] @cov 0.71 | Δcov -3 [-5, -1]; size ×1.17 [1.14, 1.20] @cov 0.72 | Δcov -4 [-5, -1]; size ×1.10 [1.07, 1.12] @cov 0.70 |
| SYR | Δcov -6 [-9, -4]; size ×1.20 [1.17, 1.23] @cov 0.69 | Δcov -8 [-10, -6]; size ×1.18 [1.15, 1.21] @cov 0.68 | Δcov -6 [-9, -4]; size ×1.22 [1.19, 1.25] @cov 0.71 | Δcov -9 [-11, -7]; size ×1.23 [1.20, 1.26] @cov 0.70 |
| MAG | Δcov -8 [-10, -5]; size ×1.17 [1.14, 1.20] @cov 0.66 | Δcov -10 [-13, -8]; size ×1.25 [1.22, 1.28] @cov 0.69 | Δcov -13 [-15, -11]; size ×1.32 [1.29, 1.36] @cov 0.69 | Δcov -8 [-10, -6]; size ×1.21 [1.18, 1.24] @cov 0.69 |

At α=0.20 the same ordering holds with smaller losses (MAG Δcov −3 to −8 pp; size ×1.19–1.31). Note: own-threshold coverage on test is 0.66–0.72 (target 0.70); ALLaM-MAG is lowest (0.657). Exploratory check (not pre-registered): resampling the calibration part gives a 2.5–97.5% range of 0.63–0.70 for that number, and swapping roles (threshold from test, evaluated on calibration) gives 0.73 — consistent with calibration-sample fluctuation, not evidence of a systematic shift. Nothing is built on it.

## P3 — instability vs MSA (test)

| dialect | answer changed (4 models) | correctness changed |
|---|---|---|
| UAE | 21–23% | 14–16% |
| EGY | 23–26% | 16–18% |
| KSA | 20–24% | 15–17% |
| SYR | 28–31% | 21–22% |
| MAG | 29–34% | 22–24% |
| A_any / A_strict / MSA acc | ALLaM-7B 0.74/0.30/0.59; Fanar-1-9B 0.76/0.34/0.61; Qwen3-8B 0.78/0.34/0.63; Gemma-2-9b 0.73/0.33/0.59 | |

## S4 — operational: confidence threshold τ chosen on calibration MSA for target risk 0.20, applied unchanged on test

| variety | ALLaM-7B | Fanar-1-9B | Qwen3-8B | Gemma-2-9b |
|---|---|---|---|---|
| MSA | answered 0.52 (+0), risk 0.21 | answered 0.56 (+0), risk 0.19 | answered 0.59 (+0), risk 0.20 | answered 0.47 (+0), risk 0.18 |
| UAE | answered 0.50 (-1), risk 0.26 | answered 0.51 (-5), risk 0.20 | answered 0.53 (-5), risk 0.21 | answered 0.44 (-3), risk 0.19 |
| EGY | answered 0.48 (-4), risk 0.25 | answered 0.47 (-8), risk 0.21 | answered 0.53 (-6), risk 0.22 | answered 0.40 (-7), risk 0.22 |
| KSA | answered 0.46 (-5), risk 0.24 | answered 0.48 (-7), risk 0.22 | answered 0.52 (-7), risk 0.20 | answered 0.40 (-7), risk 0.21 |
| SYR | answered 0.46 (-5), risk 0.31 | answered 0.43 (-13), risk 0.23 | answered 0.47 (-12), risk 0.23 | answered 0.35 (-12), risk 0.22 |
| MAG | answered 0.40 (-11), risk 0.28 | answered 0.41 (-15), risk 0.21 | answered 0.38 (-21), risk 0.24 | answered 0.29 (-18), risk 0.17 |
| ENG | answered 0.58 (+7), risk 0.18 | answered 0.71 (+15), risk 0.16 | answered 0.75 (+16), risk 0.12 | answered 0.70 (+23), risk 0.16 |

A deployed MSA-tuned abstention rule gives dialect users fewer answers in all four models (MAG: −11 to −21 pp answered). Whether it also raises their realised error rate depends on the model and dialect — paired Δrisk (dialect − MSA, pp [95% CI], computed after the main run with the same bootstrap): SYR +9.3 [+6.0,+12.5] / +3.7 [+0.9,+7.0] / +3.1 [+0.1,+6.2] / +4.2 [+0.8,+7.7] (ALLaM/Fanar/Qwen3/Gemma); MAG +6.7 [+3.3,+10.3] / +1.8 [−1.3,+5.0] / +3.5 [+0.2,+6.8] / −0.2 [−3.7,+3.4]. The 'double penalty' is therefore established for SYR in all four models and for MAG in ALLaM (marginal in Qwen3), and not for MAG in Fanar or Gemma.

## S2 — variety-aware calibration with predicted groups (text router acc 0.638; α=0.30; per TRUE variety on test; Δ vs MSA-only in pp [CI])

| model | pooled | oracle Mondrian | text router | plausible-set (conservative) | set size MSA/MAG: msa_only → oracle → text → plausible |
|---|---|---|---|---|---|
| ALLaM-7B | MAG +3.2 [+2.3,+4.2]; worst +2.9 | MAG +5.1 [+3.9,+6.3]; worst +5.0 | MAG +2.6 [+1.8,+3.5]; worst +2.7 | MAG +10.0 [+8.5,+11.5]; worst +9.8 | 1.31/1.36 → 1.31/1.53 → 1.30/1.45 → 1.59/1.73 |
| Fanar-1-9B | MAG +5.2 [+4.1,+6.5]; worst +5.1 | MAG +10.2 [+8.7,+11.8]; worst +8.7 | MAG +7.0 [+5.6,+8.4]; worst +6.8 | MAG +9.3 [+7.9,+10.8]; worst +9.0 | 1.23/1.17 → 1.23/1.54 → 1.24/1.43 → 1.43/1.52 |
| Qwen3-8B | MAG +4.6 [+3.5,+5.8]; worst +4.6 | MAG +11.6 [+9.9,+13.3]; worst +11.5 | MAG +9.4 [+7.8,+10.9]; worst +9.4 | MAG +11.6 [+9.9,+13.3]; worst +11.6 | 1.18/1.14 → 1.18/1.56 → 1.23/1.48 → 1.50/1.56 |
| Gemma-2-9b | MAG +3.1 [+2.2,+4.0]; worst +3.1 | MAG +6.8 [+5.6,+8.2]; worst +7.3 | MAG +6.0 [+4.7,+7.3]; worst +5.7 | MAG +9.9 [+8.4,+11.5]; worst +9.2 | 1.42/1.44 → 1.42/1.72 → 1.45/1.67 → 1.67/1.85 |

Reading: per-variety calibration with true labels recovers +5 to +12 pp on MAG (all CIs exclude zero); the text router recovers 51% / 69% / 81% / 88% of that gain (ALLaM / Fanar / Qwen3 / Gemma) at set sizes close to the oracle's; pooled calibration recovers 63% / 51% / 40% / 46% — so on ALLaM pooled (+3.2) is ahead of the text router (+2.6), and there is no general superiority of the router over pooled calibration. Recovering most of the oracle gain is not the same as matching the oracle: coverage and set sizes still differ. The plausible-set variant reaches the highest coverage but by being conservative everywhere (MSA coverage 0.75–0.79, set sizes +0.2–0.3), so it is not a free improvement. None of this is a new method; it quantifies what a known remedy buys and costs here.

## S1 — calibration efficiency (α=0.30, MAG): P(|coverage − 0.70| ≤ 0.05) on the 1,420-item test for n own-dialect calibration items

| model | n=25 | 50 | 100 | 150 | 200 | 250 | 400 |
|---|---|---|---|---|---|---|---|
| ALLaM-7B | 0.31 (cov 0.70) | 0.46 (cov 0.67) | 0.52 (cov 0.67) | 0.63 (cov 0.67) | 0.68 (cov 0.67) | 0.65 (cov 0.66) | 0.73 (cov 0.66) |
| Fanar-1-9B | 0.40 (cov 0.72) | 0.58 (cov 0.69) | 0.70 (cov 0.69) | 0.84 (cov 0.69) | 0.87 (cov 0.69) | 0.89 (cov 0.69) | 0.97 (cov 0.69) |
| Qwen3-8B | 0.45 (cov 0.72) | 0.65 (cov 0.70) | 0.80 (cov 0.69) | 0.87 (cov 0.69) | 0.93 (cov 0.69) | 0.97 (cov 0.69) | 1.00 (cov 0.69) |
| Gemma-2-9b | 0.42 (cov 0.73) | 0.63 (cov 0.71) | 0.83 (cov 0.70) | 0.89 (cov 0.70) | 0.94 (cov 0.70) | 0.98 (cov 0.70) | 1.00 (cov 0.69) |

With a larger test set the picture is clearer: n=50 lands within ±5 pp only 46–65% of the time; n≈150–200 reaches 63–93%. The ALLaM-MAG plateau at 0.66–0.67 shares its cause with the P2 note (all draws come from the same calibration pool), so it says nothing about calibration size.

## What this does and does not establish (binding per ANALYSIS_PLAN Addendum 1)

- Established on held-out data, within one resource (DialectalArabicMMLU) and one task format (4-option MCQ, letter scoring, 3 MSA shots): dialect shift imposes a material cost in reliable prediction that recurs across the four models studied — at MSA-matched risk, 23–32% of MAG questions are answerable vs 50% for MSA; conformal sets must be 17–32% larger for MAG at achieved coverage ≈ 0.69; 29–34% of MAG answers change. UAE/EGY costs are smaller but no longer indistinguishable from zero.
- The remedy's value is quantified, not invented: per-dialect calibration (true labels, or a 64%-accurate text classifier) closes most but not all of the coverage gap at the measured set-size cost; a per-predicted-group guarantee would require a fixed router and exchangeable calibration items within each predicted group; our calibration pools dependent variants of the same question, so the result is reported as empirical (see Dunn et al. on hierarchical data) and is in any case not a per-true-dialect guarantee.
- Not yet established: that the dialect versions preserve meaning/answer/options — pending the human audit (400 pairs; 150 of them from this test part). No conclusion is final before it. CIs condition on the fixed calibration part and router.
- Exploratory (not pre-registered): the ALLaM-MAG under-coverage (0.657) is within calibration-sample variability (see P2 note); the S1 plateau for ALLaM-MAG shares that cause (draws from one fixed calibration pool) and is not evidence of a shift.