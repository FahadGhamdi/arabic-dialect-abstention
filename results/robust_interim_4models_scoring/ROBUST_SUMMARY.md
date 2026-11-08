# Measurement robustness — summary (Addendum 8; pre-registered)

Status 2026-11-07 16:50 local: scoring under four option orderings complete for all four models (14,000 rows each); G1 generation complete
for ALLaM, Qwen3, Fanar; G2 complete for ALLaM; **gemma-2-9b G1 still running (≈10× slower than the other models under eager attention;
ETA ≈22:30 local)** — its R5 row will be appended by the final run (results/robust/), which will not change R1–R4. Analysis code
scripts/robust_analyze.py frozen at sha256 61fdd211… before any output was opened; this summary is from an isolated run on
snapshots of the completed files (results/robust_interim_4models_scoring/). Subset: 500 confirmatory test keys (seed 20261107); B = 2000 key bootstrap.
Re-run reproducibility of k=0 against the confirmatory scores: identical prediction 99.1 / 98.6 / 98.7 / 98.0 % (ALLaM / Qwen3 / Fanar / Gemma).

## R2 — the gaps do not depend on option order (reading rule §8.3)

ΔP1 (variety − MSA, answerable fraction at the MSA-matched risk), averaged over the four orderings, with key-bootstrap CI; verdict counts
"order-robust" = CI excludes 0 and the four per-order gaps share the sign:

| variety | ALLaM ΔP1 avg [CI] | Qwen3 ΔP1 avg [CI] | Fanar ΔP1 avg [CI] | Gemma ΔP1 avg [CI] | verdicts (Δacc / ΔP1) |
|---|---|---|---|---|---|
| EGY | -0.130 [-0.21,-0.07] | -0.142 [-0.22,-0.07] | -0.153 [-0.22,-0.09] | -0.149 [-0.21,-0.11] | 4/4 · 4/4 robust |
| SYR | -0.192 [-0.26,-0.14] | -0.195 [-0.32,-0.12] | -0.203 [-0.30,-0.14] | -0.248 [-0.34,-0.19] | 4/4 · 4/4 robust |
| KSA | -0.097 [-0.17,-0.05] | -0.121 [-0.20,-0.04] | -0.123 [-0.19,-0.06] | -0.153 [-0.22,-0.11] | 4/4 · 4/4 robust |
| UAE | -0.076 [-0.14,-0.01] | -0.089 [-0.17,-0.03] | -0.103 [-0.17,-0.05] | -0.131 [-0.19,-0.06] | 4/4 · 4/4 robust |
| MAG | -0.205 [-0.28,-0.15] | -0.253 [-0.32,-0.21] | -0.224 [-0.28,-0.16] | -0.237 [-0.29,-0.18] | 4/4 · 4/4 robust |

All 20 Δacc cells and all 20 ΔP1 cells are order-robust (per-order values in ROBUST_REPORT.md). S4 at the original τ_MSA (r* = 0.20),
order-averaged, excludes 0 in 20/20 cells:

| variety | ALLaM S4 Δanswered avg [CI] | Qwen3 S4 Δanswered avg [CI] | Fanar S4 Δanswered avg [CI] | Gemma S4 Δanswered avg [CI] |
|---|---|---|---|---|
| EGY | -0.039 [-0.07,-0.01] | -0.058 [-0.08,-0.03] | -0.074 [-0.10,-0.05] | -0.056 [-0.08,-0.03] |
| SYR | -0.045 [-0.08,-0.01] | -0.106 [-0.14,-0.08] | -0.119 [-0.15,-0.09] | -0.119 [-0.14,-0.09] |
| KSA | -0.066 [-0.09,-0.04] | -0.053 [-0.08,-0.03] | -0.069 [-0.09,-0.05] | -0.067 [-0.09,-0.04] |
| UAE | -0.027 [-0.05,-0.00] | -0.044 [-0.07,-0.02] | -0.054 [-0.08,-0.03] | -0.035 [-0.05,-0.02] |
| MAG | -0.099 [-0.13,-0.07] | -0.193 [-0.23,-0.16] | -0.164 [-0.19,-0.13] | -0.160 [-0.19,-0.13] |

Reading: the dialect reliability cost is not an artefact of where the correct option sits. (Power note: 500 keys; UAE ΔP1 CIs reach −0.01.)

## R1 — the choice is less stable to option order under dialectal phrasing

Order-sensitivity rate OSR = fraction of keys whose content-level prediction differs across the four orderings; in brackets ΔOSR vs MSA:

| variety | ALLaM | Qwen3 | Fanar | Gemma | ΔOSR CI>0 |
|---|---|---|---|---|---|
| MSA | 0.43 | 0.45 | 0.45 | 0.58 | — |
| EGY | 0.48 (+0.05) | 0.50 (+0.05) | 0.52 (+0.07) | 0.64 (+0.06) | 4/4 |
| SYR | 0.52 (+0.09) | 0.52 (+0.07) | 0.58 (+0.13) | 0.70 (+0.12) | 4/4 |
| KSA | 0.48 (+0.05) | 0.49 (+0.04) | 0.54 (+0.09) | 0.66 (+0.08) | 3/4 |
| UAE | 0.46 (+0.03) | 0.48 (+0.03) | 0.52 (+0.07) | 0.62 (+0.04) | 1/4 |
| MAG | 0.51 (+0.08) | 0.57 (+0.12) | 0.61 (+0.16) | 0.72 (+0.13) | 4/4 |
| ENG | 0.37 (-0.06) | 0.26 (-0.19) | 0.34 (-0.11) | 0.37 (-0.21) | 0/4 (all <0) |

Reading: OSR rises with the dialect's distance from MSA (MAG/SYR highest, UAE lowest; English lowest of all), in every model; the
ordering mirrors the accuracy and AUROC gaps. This is the measurement-level counterpart of the discrimination result in Addendum 7.

## R4 — P3 ("answer change vs MSA") is at or below the position-noise floor

P3 answer-change rate (k = 0) next to the within-variety change caused by one option rotation (k = 0 vs k = 1):

| variety | ALLaM: P3 k=0 · floor | Qwen3: P3 k=0 · floor | Fanar: P3 k=0 · floor | Gemma: P3 k=0 · floor |
|---|---|---|---|---|
| EGY | 0.25 · 0.26 | 0.20 · 0.31 | 0.25 · 0.36 | 0.24 · 0.41 |
| SYR | 0.31 · 0.29 | 0.29 · 0.32 | 0.29 · 0.39 | 0.33 · 0.46 |
| KSA | 0.23 · 0.30 | 0.21 · 0.29 | 0.21 · 0.35 | 0.23 · 0.42 |
| UAE | 0.23 · 0.24 | 0.21 · 0.31 | 0.26 · 0.32 | 0.23 · 0.42 |
| MAG | 0.32 · 0.31 | 0.29 · 0.37 | 0.31 · 0.39 | 0.31 · 0.48 |
| MSA (floor only) | — · 0.27 | — · 0.29 | — · 0.28 | — · 0.38 |

Reading: in all four models the dialect-vs-MSA answer change (0.20–0.33) is no larger than the change produced by rotating the options
of the SAME question in the SAME variety (0.24–0.48; MSA's own floor 0.27–0.38). **P3 therefore cannot be presented as content-driven
instability and is withdrawn as a stand-alone claim.** The instability statement that survives is R1 (above): under dialectal phrasing
the models' choice is less stable to option order. Majority-vote predictions do not change this picture (ROBUST_REPORT.md).

## R5 — reading the answer from letter logits matches what the models generate

G1 (greedy ≤ 8 tokens from the identical prompt), agreement of the generated letter with the letter-logit prediction, per variety:

- ALLaM: agreement 0.974–0.996, unextractable ≤ 0.008
- Fanar: agreement 0.944–0.970, unextractable ≤ 0.000
- Qwen3: agreement 0.938–0.962, unextractable ≤ 0.000
- Gemma: pending.

G2 (ALLaM, chat template, greedy ≤ 32 tokens, fixed extraction rules): unextractable ≤ 0.4 % in every variety; generated answer =
first-token argmax under the chat template in 99–100 %; agreement with the raw-prompt logit prediction and accuracies:
MSA: agr 0.85, gen acc 0.62 vs logit 0.62; EGY: agr 0.86, gen acc 0.58 vs logit 0.58; KSA: agr 0.87, gen acc 0.57 vs logit 0.55; MAG: agr 0.82, gen acc 0.53 vs logit 0.51; SYR: agr 0.85, gen acc 0.53 vs logit 0.54; UAE: agr 0.88, gen acc 0.56 vs logit 0.54; ENG: agr 0.92, gen acc 0.66 vs logit 0.64.
Reading: the letter-logit measurement reflects the models' generated answers on the same prompt (near-tautological for base models,
as anticipated) and, for the one instruction-tuned model, the dialect ordering is unchanged under chat-style use. G2 differs from the
measurement in template and decoding at once (usage-validity check, not a decoding isolation).

## Consequences for the paper (within Addendum 6/8 wording rules)
- Keep: P1, S4, P2, S2, the Addendum 7 diagnostic; add one sentence that all gaps are order-robust (this file).
- Withdraw P3 as a headline; replace by R1 (order sensitivity +5 to +16 pp in MAG/SYR, 4/4 models) with the noise-floor table in the appendix.
- Limitations: letter-logit MCQ remains the measurement; G1/G2 show it matches generation on this prompt, not that generative dialect
  behaviour is characterised; order robustness was checked on 500 keys and four cyclic shifts (not all 24 permutations).
