# Automatic validity layers — summary (2026-11-07, 05:40 local; ANALYSIS_PLAN Addendum 4; frozen code validity_analyze.py 2ec539c6…)

Question these layers answer: is the dialect reliability cost (CONFIRM_SUMMARY.md) an artefact of imperfect dialect translations?
No human raters were used; the GPT-6 screen (results/audit/AUDIT_RESULTS.md) is a model-assisted screen.

## L1 — Published external defect filter (IFM/Dialectal-Arabic-MMLU_verified; 3 LLM judges, unanimous "significant defect")
Dropping the 935 flagged dialect rows (5–6% of test keys per dialect) changes every confirmatory endpoint by ≤ 1.1 pp in all 20
dialect × model cells (e.g. Qwen3-MAG ΔP1 −27.4 → −26.3; Fanar-MAG Δanswered −15.2 → −15.6). Details: VALIDITY_L1.md.

## L2 — Embedding similarity to MSA (multilingual-e5-large), within-dialect terciles of the 1,420 test keys
The cost is graded by similarity everywhere (Spearman(sim, answer-changed) −0.11 … −0.22). Top-tercile effect as a fraction of the
full-sample ΔP1: MAG 0.59/0.80/0.68/0.94 (ALLaM/Fanar/Qwen3/Gemma), SYR 0.37/0.70/0.83/1.01, EGY 0.17/0.67/0.74/1.03,
KSA 0.10/0.45/0.40/0.74, UAE 0.44/0.03/0.12/—. Pre-declared rule (≥ 2/3 = not accounted for): MAG, SYR, EGY in 3/4 models;
KSA/UAE largely accounted for. Caveat (VALIDITY_L2_reading.md): the tercile rule is descriptive, not a causal separation of dialect from translation; similarity
can capture dialectal distance and item difficulty as well as translation drift. The defect-specific layers (L1; screen flags) show no
detectable association, with wide intervals.

## L4 — Independent resource, independent translation pipeline (AraDiCE EGY/LEV vs ArabicMMLU MSA; 1,400 test / 600 calibration)
| model | variety | Δacc | answer change | ΔP1 (matched risk) | Δcov@MSA-thr | set-size ×(own-thr) | Δanswered@τ |
|---|---|---|---|---|---|---|---|
| ALLaM | EGY | −7.0 [−9.2,−4.8] | 25.1% | −17.2 [−24,−13] | −6.7 | ×1.28 | −7.3 |
| ALLaM | LEV | −4.5 [−6.6,−2.6] | 20.4% | −13.7 [−17,−9] | −5.1 | ×1.16 | −5.3 |
| Fanar | EGY | −4.5 [−6.6,−2.4] | 23.6% | −10.9 [−16,−6] | −3.7 | ×1.18 | −3.9 |
| Fanar | LEV | −3.7 [−5.6,−1.7] | 19.1% | −6.0 [−10,−4] | −5.2 | ×1.05 | −2.9 |
| Qwen3 | EGY | −4.6 [−6.8,−2.3] | 25.6% | −15.1 [−21,−10] | −5.9 | ×1.21 | −4.1 |
| Qwen3 | LEV | −3.6 [−5.5,−1.6] | 21.3% | −10.4 [−15,−6] | −4.2 | ×1.02 | −4.4 |
| Gemma-2 | EGY | −5.2 [−7.4,−3.1] | 24.4% | −13.5 [−17,−9] | −5.6 | ×1.21 | −6.5 |
| Gemma-2 | LEV | −3.6 [−5.6,−1.6] | 21.0% | −9.2 [−13,−6] | −3.3 | ×1.09 | −5.5 |
All CIs exclude zero. Same direction and comparable magnitude to the DAMM near/mid dialects (DAMM EGY ΔP1 −9 … −15; AraDiCE EGY −11 … −17).
Two independent translation pipelines (DAMM: human translation with review; AraDiCE: machine translation with human post-editing, Mousi et al. 2025) produce the same pattern for the Egyptian and Levantine varieties. AraDiCE has no Maghrebi variety, so the strongest DAMM result (MAG) is replicated only indirectly.

## L5 — Cross-model consistency: flagged and unflagged pairs show similar degradation on the screened sample, with wide intervals (AUDIT_RESULTS.md §3).

## Overall reading (binding)
- The reliability cost of dialect input persisted across two resources and after the specified automatic sensitivity analyses (an external
  three-judge filter; our model-assisted screen; a similarity covariate). This supports, but does not prove, that translation defects do not
  explain it: defects missed by all judges, and meaning differences the similarity covariate does not capture, may still contribute.
  The flagged-vs-unflagged difference (Δacc −1.8 pp [−8.6, +4.6]) is not detectably different from zero, but its interval allows a material association.
- The cost is graded by embedding distance from MSA. It is material and robust for Maghrebi and Syrian (and, in 3/4 models, Egyptian)
  inputs; for Saudi and Emirati inputs it is small and concentrated in the items that depart most from MSA, where translation drift,
  dialectal distance and item difficulty cannot be separated without human judgement.
- What "equal reliability" means here: P1 is a descriptive comparison at the risk MSA reaches at 50% coverage (read from test labels);
  S4 is the operational evidence (threshold fixed on calibration); P2 equalises the coverage target, not the achieved coverage. All
  measure an abstention policy over option-letter scores, not abstention behaviour in free-form conversation.
- Limitation to be stated: equivalence judgements are automatic (embedding model; LLM judges, ours and IFM's); none was calibrated
  against human dialect speakers in this study; the resources' own human translation/review or post-editing is the only human validity
  evidence. The 37% rate reported by the GPT-6 screen is what that screen classified under its criteria, not an established human rate.
- Positioning (per review #7): not "the first study of dialect reliability" — calibration of Arabic dialect-ID models (WACL 2025) and the
  finding that selective prediction can magnify group disparities (Jones et al. 2020) exist. The contribution is measuring how reliability
  transfers across dialectal phrasings of the same questions, and what per-dialect calibration repairs and at what cost.
