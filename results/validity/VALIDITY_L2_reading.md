# L2 — reading of the embedding-fidelity analysis (written 2026-11-07 03:50 local, after VALIDITY_L2.md; L4 not yet available)

Covariate: cosine similarity (multilingual-e5-large) between the MSA text and the dialect text (question+options). Mean by variety:
KSA .977, UAE .974, EGY .970, SYR .961, MAG .947 (ENG .891). Within-dialect terciles of the 1,420 test keys.

## What the gradient shows
Every endpoint is graded by similarity in every dialect and model (Spearman(sim, answer-changed) −0.11 to −0.22, all p<1e-4).
Pooled over models, low → high tercile: answer change MAG 42% → 23%, SYR 37% → 22%, EGY 30% → 18%, KSA 31% → 14%, UAE 29% → 14%;
ΔP1 MAG −31 → −17, SYR −27 → −13, EGY −17 → −8, KSA −17 → −5, UAE −11 → −3.

## Pre-declared rule (top-tercile effect vs full-sample effect; ≥ 2/3 → "fidelity does not account for it", < 1/3 → "it does"), ΔP1
| dialect | ALLaM | Fanar | Qwen3 | Gemma-2 | verdict |
|---|---|---|---|---|---|
| MAG | 0.59 | 0.80 | 0.68 | 0.94 | not accounted for in 3/4 (ALLaM borderline) |
| SYR | 0.37 | 0.70 | 0.83 | 1.01 | not accounted for in 3/4 |
| EGY | 0.17 | 0.67 | 0.74 | 1.03 | not accounted for in 3/4; accounted for in ALLaM |
| KSA | 0.10 | 0.45 | 0.40 | 0.74 | largely accounted for (2 models < 1/3) |
| UAE | 0.44 | 0.03 | 0.12 | 1.28* | accounted for in 2/4 (*Gemma cell is noise: ΔP1 −6 → −8) |

## Interpretation (binding for the write-up)
1. The similarity covariate conflates two things: translation drift AND the degree of dialectal departure from MSA. High-similarity items are
   both the most faithful and the least dialectal. A cost that shrinks at high similarity may therefore reflect the phenomenon itself
   (dose–response in linguistic distance), item difficulty, or translation drift; the tercile rule does not separate these. The pre-declared rule is conservative against the dialect hypothesis.
2. The layers that isolate *judged defects* rather than distance show little association with the cost: IFM's unanimous-defect filter
   (L1) moves every endpoint by ≤ 1.1 pp; GPT-6 screen flags (basic) show Δacc −1.8 pp [−8.6, +4.6] and answer change +0.8 pp [−5.6, +7.7]
   flagged vs unflagged. Similarity tracks the screen flags only weakly (flag rate 51% / 41% / 19% by tercile; Spearman −0.25).
3. Consequently: for the far dialects (MAG, SYR) and for EGY in three models, the reliability cost is present at the highest-fidelity
   tercile at ≥ 2/3 of its full-sample size — it persists under all of our automatic criteria (which support, but do not prove, that it is not a translation artefact). For KSA and UAE (and EGY
   in ALLaM) the cost is concentrated in the items that depart most from MSA; whether those items are "less faithful" or "more dialectal"
   cannot be separated without human judgement, and the paper must say so.
4. The paper's headline is therefore narrowed to what survives all layers: a material, distance-graded reliability cost for Maghrebi and
   Syrian (and mostly Egyptian) inputs; small and fidelity-sensitive costs for Saudi and Emirati inputs.
