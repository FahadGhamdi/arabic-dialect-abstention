# Model-assisted translation-equivalence screen (GPT-6 Astra Extra High) — results and pre-registered sensitivity analyses (2026-11-07)

Input: `audit/adjudication_DAMM_audit_1.xlsx` as returned (rater 1: 400 pairs = 80 keys × 5 dialects; rater 2: 150 pairs = 30 keys × 5;
third-rater adjudication on all 150 double-rated pairs). Analysis code: `scripts/audit_analyze.py` (this file was produced from the
interactive run recorded in PILOT_NOTES.md; the script reproduces it). **Rater identity (confirmed by the PI): all ratings were produced by GPT-6 Astra Extra High (two independent sessions as 'raters', a third as adjudicator). This is a model-assisted screen, not a human audit; the κ values below measure within-model consistency across sessions.**

## 1. Defect rates (rater 1, all 400 pairs; key-clustered 95% CIs over 80 keys)

| dialect | basic defect (Q1 or Q2 = no) | Q2 = no (answer/options invalid) | Q3 = no (hint/ambiguity added) | strict (any non-yes in Q1–Q3) |
|---|---|---|---|---|
| UAE | 0.44 [0.33, 0.55] | 0.06 [0.01, 0.11] | 0.41 [0.31, 0.53] | 0.60 [0.49, 0.70] |
| EGY | 0.33 [0.23, 0.42] | 0.01 [0.00, 0.04] | 0.31 [0.21, 0.41] | 0.49 [0.39, 0.60] |
| KSA | 0.34 [0.24, 0.44] | 0.10 [0.04, 0.17] | 0.33 [0.23, 0.44] | 0.54 [0.42, 0.65] |
| SYR | 0.40 [0.30, 0.51] | 0.06 [0.01, 0.11] | 0.33 [0.23, 0.44] | 0.54 [0.44, 0.65] |
| MAG | 0.35 [0.25, 0.45] | 0.16 [0.09, 0.25] | 0.34 [0.24, 0.44] | 0.55 [0.44, 0.65] |
| all | 0.37 [0.31, 0.44] | 0.08 | 0.34 | 0.54 |

By source: pilot keys 0.32 [0.26, 0.39]; confirmatory-test keys 0.45 [0.33, 0.57] (Q1 = no 0.32 vs 0.41). Q2 "unsure" is frequent (29%).
Reading: by the raters' strict meaning criterion (any change of conditions/negation/quantities/terms), about a third of the dialect
versions are not faithful paraphrases; the gold answer remains valid in ≈92% (MAG 84%, KSA 90%); about a third add a hint or an ambiguity.
The resource's own documentation reports a ≈5% error rate from a 32-item/dialect check; our criterion is much stricter and our rate is not comparable to it.

## 2. Inter-rater agreement (150 double-rated pairs; Cohen's κ, 3 categories)

| check | observed agreement | expected | κ | disagreements |
|---|---|---|---|---|
| Q1 meaning | 0.933 | 0.536 | **0.86** | 10 |
| Q2 answer/options | 0.707 | 0.545 | **0.36** | 44 (almost all yes ↔ unsure) |
| Q3 clarity | 0.953 | 0.551 | **0.90** | 7 |
| Q4 dialect membership | 0.980 | 0.980 | 0.00 (no variance: 'yes' everywhere) | 3 |

Basic-defect rate on the 150 pairs: rater 1 0.34, rater 2 0.32, both-agree 0.30, either 0.36, third-rater adjudication 0.33. The two
raters agree closely on what changes meaning; they differ mainly in how often they say "unsure" about answer validity.

## 3. Are the flags where the models fail? (400 pairs × 4 models = 1,600 pair-model observations)

| | n | MSA acc → dialect acc | Δacc | answer change | Δp_true |
|---|---|---|---|---|---|
| unflagged (basic) | 1,008 | 0.510 → 0.465 | −4.5 pp | 26.9% | −0.031 |
| flagged (basic) | 592 | 0.517 → 0.454 | −6.2 pp | 27.7% | −0.040 |
| unflagged (strict) | 732 | 0.570 → 0.541 | −2.9 pp | 24.0% | −0.033 |
| flagged (strict) | 868 | 0.464 → 0.394 | −7.0 pp | 29.8% | −0.035 |

Flagged − unflagged, key-clustered 95% CI: basic Δacc −1.8 pp [−8.6, +4.6], answer change +0.8 pp [−5.6, +7.7];
strict Δacc −4.2 pp [−11.5, +2.7], answer change +5.8 pp [−1.7, +13.2]; Q2-invalid Δacc −3.8 pp [−13.4, +5.8], answer change +7.0 pp [−4.1, +19.7].
Reading: on this sample, flagged and unflagged pairs show degradation of the same order; the difference is not detectably different from zero,
but the intervals are wide enough to allow a material association. This is a sensitivity result, not evidence of independence. Note also that UAE has the highest meaning-change rate (44%) and the smallest model cost.

## 4. Pre-registered sensitivity analyses (ANALYSIS_PLAN Addendum 2 §B) on the 80 audited keys, per dialect, mean over the 4 models

(i) Exclusion of flagged pairs (basic): remaining keys per dialect 45–54.

| dialect | Δacc orig → excl | answer change orig → excl | Δcov@MSA-thr (α=.30) orig → excl | Δanswered @τ(r*=.20) orig → excl | ΔP1 (matched risk) orig → excl |
|---|---|---|---|---|---|
| UAE | −3.1 → −1.1 | 22.2 → 19.4% | −2.8 → 0.0 | −7.8 → −6.7 | −14.4 → −12.8 |
| EGY | −6.3 → −3.2 | 27.2 → 25.0% | −5.3 → −3.7 | −6.9 → −5.6 | −15.6 → −14.8 |
| KSA | −6.3 → −6.6 | 22.5 → 24.5% | −4.1 → −3.3 | −5.3 → −6.1 | −12.5 → −16.0 |
| SYR | −4.7 → −6.3 | 33.4 → 34.9% | −5.0 → −3.6 | −7.8 → −7.8 | −18.8 → −20.8 |
| MAG | −5.3 → −4.8 | 30.6 → 30.3% | −8.1 → −3.8 | −16.9 → −20.2 | −20.0 → −9.6 |

(ii) "No-defect" counterfactual (flagged dialect pairs replaced by the MSA row — the most favourable scenario for the artefact hypothesis;
by construction it removes ≈37% (basic) / ≈54% (strict) of any effect): answer change falls to 11–21% (basic) and 7–15% (strict); Δacc to
−0.6…−4.4 (basic); ΔP1 to −12…−17 (basic). Fraction of the original answer-change effect remaining under cf_basic: 56–67% per model,
i.e. ≈ (1 − f) — exactly what is expected if flags are unrelated to the effect.

(iii) The f/(1−f) worst-case bound for fixed-rule proportions is **uninformative** at these defect rates (f_upper ≈ 0.44–0.57 → bound ≥ 0.8);
it is reported only to say so. The evidence against the artefact explanation is §3 and §4(i), not a bound.

Caveat: 80 keys; per-dialect cells rest on 45–80 keys and are very noisy. For MAG under exclusion (52 keys), ΔP1 per model is +12 / −8 / −17 / −25 pp
with CIs of roughly ±40 pp, and Δcov −8.1 → −3.8 has CIs spanning zero; these are reported with their uncertainty and neither confirm nor
refute a reduction. Answer change on the unflagged MAG pairs stays 25–35%.

## 5. What this changes

- **The "content-controlled / same content" premise must be weakened in all claims**: the dialect versions are human translations of the
  same question, but by the GPT-6 screen's strict meaning criterion about a third were classified as altering conditions, quantities or terms, ≈8% as
  invalidating the gold answer (≈16% for MAG) — rates under that screen's criteria, not established human rates. This is a finding about the resource and a limitation of every study that uses it as a paired benchmark.
- **The reliability-cost result persisted on the pairs the screen judged faithful** (answer change 19–35%; equal-risk answerable fraction
  −10 to −21 pp on 45–54 keys with wide CIs; operational answered fraction −6 to −20 pp). This supports, with the 80-key caveat, that the
  screened defects do not account for it; it does not establish independence from undetected meaning differences.
- **Decision (plan §6, Addendum 1 §B)**: the held-out pattern is material and survives the sensitivity analyses that the plan allows us to
  run; the defect rate is not low, so the write-up must carry the resource finding prominently and avoid "content-controlled" as a selling
  point. Proceed to a limited-claims draft (Findings via ARR) **after the rater-identity question is settled**: if the raters were not human
  dialect speakers, this audit is reported as a model-assisted screen and a human audit of at least the 30 test keys is still required.
- Not yet done and not planned before the draft: new models, interpretability, a second resource.
