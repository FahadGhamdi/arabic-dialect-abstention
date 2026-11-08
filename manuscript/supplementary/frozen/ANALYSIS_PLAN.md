# Pre-registered analysis plan — confirmatory test (frozen 2026-11-04, before any confirmatory scoring)

Project: *The Cost of Equal Reliability: content-controlled dialect shift in Arabic LLM uncertainty* (working title).
Pilot: 500 keys (data/pilot_keys.json), results in results/stageA (v2) and results/stageB. Everything below is decided
before the held-out items are scored; deviations will be listed in a dated "Deviations" section at the end of this file.

## 1. Data and splits (fixed)
- Source: MBZUAI/Dialectal-Arabic-MMLU (CC-BY-4.0); 3,135 complete keys (7 varieties, 4 options).
- Held-out pool: 2,632 keys = complete keys − 500 pilot keys − 3 shot keys (data/confirm_keys.json).
- Pre-allocated split (data/confirmatory_splits.json, seed 20261105, stratified by domain,
  sha256 f0bfc16b2655e5e15033baac9ea6fbc2924ec004862b10e3439ff4808bb8c545):
  router_train = 404 keys · calibration = 808 keys · **test = 1,420 keys**.
- All primary endpoints are computed on **test** only. Calibration supplies conformal thresholds; router_train trains
  variety predictors. No key appears in more than one part; all 7 variants of a key stay together.

## 2. Scoring protocol (identical to pilot; scripts/s9_score_confirm.py)
- Models: ALLaM-7B-Instruct-preview, Fanar-1-9B, Qwen3-8B-Base, gemma-2-9b (bf16, Apple MPS). No model is added or
  removed before the decision in §6.
- Prompt: 3 fixed MSA demonstrations (English demonstrations for ENG), header + "السؤال: … الإجابة:", option-letter
  log-probabilities (variants " A"/"A" combined by logsumexp), softmax over the 4 letters. p_true = probability of the
  gold letter; confidence = p_max; conformity score = 1 − p_true.

## 3. Primary endpoints (per model; each dialect vs MSA, paired by key)
- **P1 Equal-risk answerable fraction**: selective risk reached by MSA at 50% coverage on test; for each variety the
  largest coverage whose selective risk ≤ that level. Report Δ vs MSA with 95% paired bootstrap CI over test keys
  (B = 2,000), plus AURC and ΔAURC.
- **P2 Cost of matched coverage**: at α ∈ {0.20, 0.30} (primary 0.30; full grid 0.05–0.40 reported):
  (a) coverage of each variety under the MSA threshold fitted on calibration (Δ vs MSA, CI);
  (b) set size under the variety's own threshold fitted on calibration, with the achieved coverage shown alongside;
  ratio to MSA's own-threshold set size, CI over test keys.
- **P3 Item-level instability**: answer-change rate and correctness-change rate vs MSA (CI), ✗→other-✗ counted
  separately; A_any and A_strict across the 5 dialects.

## 4. Secondary endpoints
- **S1 Calibration efficiency**: n ∈ {25, 50, 100, 150, 200, 250, 400} own-variety calibration items drawn from the
  calibration part, coverage and set size on test; report mean, 2.5/97.5 percentiles, P(|cov − target| ≤ 0.05),
  P(cov ≥ target − 0.05), and the Beta(n+1−l, l) reference. **No single n will be declared "sufficient"**; the
  curve and the probabilities are the result.
- **S2 Variety-aware calibration with predicted groups** (equal key budget; units stated explicitly: MSA-only uses the
  808 MSA items; pooled uses 808 × 7 items; Mondrian/text-router use 808 items per variety; the text router is
  trained on router_train 404 × 7 texts): MSA-only, pooled, oracle Mondrian, char n-gram text router, plausible-set
  conservative. Evaluated per TRUE variety on test: coverage, set size, worst-dialect coverage. The internal
  (hidden-state) router is **not** part of the confirmatory evaluation; its pilot result (no consistent practical
  advantage over the text router on three models) is reported as a controlled negative.
- **S3 Calibration**: multiclass Brier, ECE, mean confidence per variety.

## 5. Statistical reporting rules
- Effect sizes with CIs everywhere; no binary "success" thresholds. Uncertainty over test keys is the inferential
  unit (1,420 independent questions); split-repetition variability, where shown, is labelled as such.
- Clustering: the 7 variants of a key are not independent. Per-variety calibration uses one variant per key per
  group and is standard split conformal; pooled and routed calibration mix variants of the same key and their
  guarantees are stated as empirical, with the hierarchical-exchangeability caveat (Dunn et al.) in the paper.
- Sensitivity analyses (reported, not used to select results): (i) exclude pairs flagged by the human audit
  (pilot keys only; §7); (ii) ENG-shot vs MSA-shot prompting is NOT varied here (out of scope);
  (iii) per-domain-category breakdown (STEM / humanities / social / other) as descriptive only.
- Multiplicity: 5 dialects × 4 models × 2 α values are all reported; the paper's claims are about the pattern
  (direction and magnitude across models), not about any single CI excluding zero.

## 6. Decision rule after the confirmatory test (what the paper will claim)
- If P1/P2 reproduce the pilot pattern (MAG/SYR/KSA cost well outside CI in ≥ 3 of 4 models, UAE/EGY small) and the
  audit defect rate is low enough that the sensitivity analysis leaves the pattern intact → write up as a diagnostic
  + remedy-cost paper (Findings via ARR as the first target).
- If the pattern shrinks substantially (e.g. MAG Δ answerable within −10 pp for Fanar/Qwen3) or the audit shows a
  defect rate that can account for it → report honestly as a negative/qualified result; do not expand the project.

## 7. Human data audit (runs in parallel; audit/AUDIT_PROTOCOL.md)
50 pilot keys × 5 dialects = 250 pairs, chosen by seed 20261104 stratified by MMLU category, blind to all model
outputs; four checks (meaning, answer/options, clarity, dialect membership); 20 keys (100 pairs) double-rated;
disagreements adjudicated by a third rater; agreement reported. No retroactive correction or exclusion of items
from the main analyses; the audit feeds a defect-rate estimate and the pre-registered sensitivity analysis (§5-i).

## 8. Code freeze
- Scoring: scripts/s9_score_confirm.py, scripts/run_confirm.sh (this file's commit).
- Analysis: scripts/confirm_analyze.py, frozen 2026-11-04 ~21:30 local, before any confirm_scores_*.csv existed in full
  (ALLaM scoring was ~55% through; no confirmatory file was opened). sha256 = d1b3396d1c34530df5a344cbc56434e0bb06ff64ff388da1b2b89607e8d13e01.
  Smoke-tested only on pilot scores with a synthetic split. Derives from scripts/stageA_measure.py (v2) and scripts/stageB_router.py.

## Deviations
(none) — Execution note (2026-11-05 08:10 local): confirm_analyze.py v2 (sha256 8ade05cd…, verified identical on the Mac and on the staged copy) was run in the cloud workspace on byte-identical copies of the four confirm_scores_*.csv files and data/confirmatory_splits.json (sha256 f0bfc16b…), B=2,000. Outputs: results/confirm/. The human audit (§7) is still pending; no conclusion is final before it.


---
## Addendum 1 (dated 2026-11-04, ~23:30 local; written after external review #5 — i.e. DURING score collection (ALLaM done, Qwen3 ≈30%) and BEFORE any confirmatory file was opened for analysis; not 'before scoring started')

### A. Freeze log (what was frozen when)
| item | frozen at (local) | state of scoring at that moment | sha256 |
|---|---|---|---|
| data/confirmatory_splits.json | 20:50 | before scoring started | f0bfc16b2655e5e15033baac9ea6fbc2924ec004862b10e3439ff4808bb8c545 |
| scripts/s9_score_confirm.py + run_confirm.sh | 20:55 | before scoring started | (in repo) |
| scripts/confirm_analyze_v1_frozen.py (v1) | ~21:30 | ALLaM ≈55% scored; **no confirm file opened** | d1b3396d1c34530df5a344cbc56434e0bb06ff64ff388da1b2b89607e8d13e01 |
| scripts/confirm_analyze.py (v2 = v1 + S4 operational selective endpoint; nothing else changed) | ~23:30 | ALLaM done, Qwen3 ≈30%; **no confirm file opened for analysis** | 8ade05cd05df4c573c1f8e61ff63d62edc20ee7be13310b87f5b44ea89a2e4bc |
"Opened" means read by any analysis code or by a person; the scoring process only appends to those files. v1 is kept unchanged; v2 is the version that will be run.

### B. Decision rule — one rule, no binary gate (supersedes the wording of §6)
The paper's claim is about effect sizes with uncertainty, reported for all 5 dialects × 4 models × α ∈ {0.20, 0.30}. There is no automatic
"3 of 4 models" condition. What we will write depends on the magnitude that survives: a cost that is practically material (as a
pre-declared reference: ≥ 10 pp in the answerable fraction at matched risk, or a set-size ratio ≥ 1.15 at achieved coverage ≈ 0.70, for
a dialect in a model) will be described as such; smaller or uncertain costs will be described as small or inconclusive. Consistency across
models and dialects is reported as a finding, not used as a gate. The project is not expanded regardless of outcome until the audit is in.

### C. Interpretation limits for the endpoints (binding on the write-up)
- **P1** is a descriptive comparison of risk–coverage curves: the MSA risk level is read from test labels, so it is not an operational
  threshold a user could choose in advance. The bootstrap recomputes the risk level and the selection inside every resample (implemented).
- **S4 (new)** is the operational counterpart: a confidence threshold chosen on calibration MSA for a target risk, applied unchanged to
  every variety on test; we report answered fraction and realised risk per variety.
- **P2** with the same α for every variety means equal *target* coverage; "cost of equal reliability" is interpreted only through the
  *achieved* coverage that is reported next to the set size.
- All CIs condition on the fixed calibration part and the fixed router; they quantify test-key sampling uncertainty only, not the
  variability of re-collecting calibration data or retraining the router.

### D. Human audit (protocol v2; audit/AUDIT_PROTOCOL.md)
- Sample extended with 30 keys from the confirmatory **test** part (seed 20261106), fixed now: 400 pairs from 80 keys; 150 double-rated.
- Defect definitions fixed now: basic = Q1 or Q2 "no"; strict = any "no"/"unsure" in Q1–Q3; "unsure" is never counted as valid; Q3 analysed separately.
- Sensitivity: (a) exclusion of flagged pairs (pilot); (b) for the confirmatory test, exclusion within the audited 30 keys **plus a conservative
  bound**: removing a fraction f of pairs cannot move any proportion-type endpoint by more than f, so we report Δ ± f_upper (upper 95% CI of the
  dialect's defect rate, clustered by key) as a worst-case that allows defects to concentrate where models fail. Random deletion at the defect rate is **not** used.
- Ordering: the audit may be completed after the computational results are in (sample and policy are fixed; raters never see model outputs),
  but no conclusion is stated and no manuscript is written before it is complete.

### E. Theory wording (binding)
- The Beta(n+1−l, l) reference in S1 is an interpretive reference under exchangeability for a fresh point; realised test coverage adds
  test-set noise, and repeated draws from one fixed calibration pool are not independent replications. Agreement with it is not a proof of correctness.
- Group-conditional validity: with a fixed router, calibration per predicted group can give a guarantee for the *predicted* groups; this
  is not a guarantee per *true* dialect. Pooled calibration mixes the 7 dependent variants of a key; its coverage is reported as empirical.


---
## Addendum 2 (dated 2026-11-05, ~11:30 local; written AFTER the confirmatory main results were inspected and BEFORE any human-audit data existed — post-results, pre-audit)

### A. Version history of this file (kept; the earlier versions are the dated copies sent in the project chat and are not rewritten)
| version | time (local) | content | where the copy lives |
|---|---|---|---|
| v1 | 2026-11-04 ~21:30 | §1–8 without the analysis-code hash; sent to the PI in chat | chat attachment (first ANALYSIS_PLAN.md); Mac copy overwritten |
| v1b | 2026-11-04 ~21:35 | + sha256 of confirm_analyze v1 | Mac copy overwritten |
| v2 | 2026-11-04 ~23:30 | + Addendum 1 (freeze log, decision rule, interpretation limits, S4, audit v2, sensitivity, theory wording); sent to the PI in chat | chat attachment (second ANALYSIS_PLAN.md) |
| v3 | 2026-11-05 08:06 | + execution note under "Deviations" (after the run) | — |
| v4 | 2026-11-05 ~11:30 | + this Addendum 2 | ANALYSIS_PLAN.md (this file); from now on every version is also saved as ANALYSIS_PLAN_v<n>_<timestamp>.md |
A hash proves file identity, not freeze time or non-inspection; the sequence above and the chat copies are the record.

### B. Correction of the sensitivity plan (replaces Addendum 1 §D "conservative bound"; nothing has been computed with either rule yet)
- The bound "removing a fraction f of pairs cannot move an endpoint by more than f" is valid only for endpoints that are plain proportions
  over a fixed item set under a FIXED rule — i.e. P2 coverage under the MSA threshold, S4 answered fraction (exact bound f/(1−f)·max(p,1−p)
  for a proportion p), and P3 answer-change rate. It is NOT valid for P1 (largest coverage under a risk constraint is non-linear: a few
  items can move the cut-off a lot), nor for set-size ratios, nor for S4 realised risk (a proportion over the answered subset, whose
  removal fraction can exceed f). For those endpoints no bound is claimed.
- What will be done, for all endpoints, once audit data exist:
  (i) exclusion of pairs flagged defective (basic definition; then strict), on the pilot keys and on the 30 audited test keys;
  (ii) a "no-defect" counterfactual on the audited keys only: each flagged dialect pair is replaced by the MSA row of the same key
  (i.e. the dialect version is assumed to have behaved exactly like MSA — the most favourable scenario for the hypothesis that
  translation defects explain the gap), and P1/P2/P3/S4 are recomputed on those keys; reported descriptively next to the original;
  (iii) for the plain-proportion endpoints only, the f/(1−f) bound using the upper 95% limit of the dialect's defect rate (clustered by key);
  (iv) Q3 (added hint / new ambiguity) analysed separately: exclusion of Q3-flagged pairs reported as a further sensitivity row;
  (v) "unsure" is never counted as valid.
- Defect rates are reported per dialect with key-clustered CIs; 400 pairs from 80 keys are 80 clusters, not 400 observations. The audit
  estimates the defect rate of the resource for our items; it does not certify the whole resource.

### C. Reporting rules adopted after review #6 (presentation only; no analysis changed)
- P1 Δ is reported as the plug-in difference with the percentile bootstrap CI (an earlier table showed the bootstrap mean; max discrepancy 1.4 pp).
- P2 is "one target coverage for all varieties"; achieved MSA and dialect coverages are shown beside every size ratio.
- S4: realised-risk differences are reported with paired CIs; the "double penalty" statement is restricted to the cells whose CI excludes zero.
- S2: recovery fractions are reported per model for both pooled and router (no general ordering claimed).
- Wording: "recurs across the four models studied", never "model-independent"; "most, not all, of the coverage gap"; predicted-group
  guarantees stated conditionally (fixed router + within-group exchangeability; pooled dependent variants → empirical).
- The ALLaM-MAG 0.657 observation and its calibration-resampling / swap check are labelled exploratory.


---
## Addendum 3 (dated 2026-11-07; execution note for the human-audit analyses — no rule changed)
- Audit files received 2026-11-07 (adjudication workbook with rater 1: 400 pairs, rater 2: 150, third-rater decisions on 150).
- Analyses run exactly as Addendum 2 §B: (i) exclusion of flagged pairs on the 80 audited keys; (ii) MSA-replacement counterfactual on the
  audited keys (basic and strict flags); (iii) f/(1−f) bound — reported as uninformative at f_upper ≈ 0.44–0.57. Plus the descriptive
  flagged-vs-unflagged comparison of model degradation (§3 of results/audit/AUDIT_RESULTS.md), which was implied by §B(i) but is listed here
  explicitly as a presentation choice made after seeing the audit data.
- Outcome: basic defect rate 0.37 [0.31, 0.44] (Q2-invalid 0.08; Q3 0.34); κ Q1 0.86, Q2 0.36, Q3 0.90; degradation on unflagged pairs ≈
  on all pairs (Δacc −4.5 vs −6.2 pp; answer change 26.9 vs 27.7%). Per §6: proceed to a limited-claims draft with the resource finding stated prominently.
- Rater identity (confirmed by the PI 2026-11-07): GPT-6 Astra Extra High, not human raters. The audit is therefore a model-assisted screen (Addendum 4).


---
## Addendum 4 (dated 2026-11-07, ~23:50 local; written BEFORE any of the analyses below were run) — automatic validity layers replacing the human audit

Context: no human raters are available. The returned "audit" (Addendum 3) was produced by a language model and is henceforth called the
**model-assisted screen** (produced with GPT-6 Astra Extra High, per the PI; two sessions acted as 'rater 1' and 'rater 2' and a third as adjudicator — so the reported κ is within-model consistency, not inter-annotator agreement). The content-equivalence question is addressed by the following automatic layers.

### L1 Published external filter (no new computation)
IFM/Dialectal-Arabic-MMLU_verified removes 935 dialect rows (EGY 180, KSA 175, MAG 195, SYR 184, UAE 201) that three LLM judges
(GPT-5.6 Sol, Gemini 3.8 Flash, Claude Opus 5) unanimously flagged as having a significant defect; only items that strong baselines
answered incorrectly were screened. Exclusion list: data/ifm_excluded.json. **Analysis:** recompute P1/P2/P3/S4 on the confirmatory test
after dropping, per dialect, the keys whose dialect row is excluded (paired on the remaining keys). Reported next to the original.
Expected direction if defects drive the effect: the cost shrinks materially; the filter is biased towards model-failed items, so a
small shrinkage is expected even under the null and is interpreted as such.

### L2 Embedding fidelity covariate (scripts/s10_fidelity.py)
Cosine similarity (intfloat/multilingual-e5-large, mean pooling) between the MSA text and each variety's text — question, options,
question+options — for all 3,135 keys × 6 varieties. **Analysis (fixed now):** within each dialect, split test keys into fidelity
terciles by sim_all; recompute Δacc, answer change, P2 Δcov@MSA-thr (α=.30) and S4 Δanswered (r*=.20) per tercile; report the
top-tercile values with CIs and the Spearman correlation between sim_all and per-key degradation indicators (answer change,
p_true drop). Also report the model-assisted-screen flag rate per tercile as a check that the covariate tracks the screen.
If the effect in the top tercile is ≥ 2/3 of the full-sample effect, fidelity does not account for it; if it is < 1/3, it does.

### L4 Cross-resource replication (scripts/s11_aradice_score.py; data/aradice_splits.json, seed 20261107)
AraDiCE (QCRI; ArabicMMLU translated to Egyptian and Levantine) with MBZUAI ArabicMMLU MSA: 10,118 parallel 4-option items with an
identical key; 2,000 sampled stratified by Group: 600 calibration / 1,400 test; 3 fixed MSA shots from the complement; same four models,
same prompt/scoring. **Endpoints:** P1, P2 (α .20/.30), P3, S4 for EGY and LEV vs MSA. Same reporting rules as the main study.
A different translation pipeline producing the same ordering and comparable magnitudes is evidence against translation artefacts as
the explanation; a null here is reported as a limit on generality.

### L5 Cross-model consistency (already computed, Addendum 3 §3)
Flagged pairs (model-assisted screen) are not where the models degrade most; kept as reported.

### What remains open without humans (to be written in the limitations)
The equivalence judgements are automatic (an embedding model and language-model judges, ours and IFM's); none has been calibrated
against human dialect speakers in this study. The resource's own human translation/review process is the only human validity evidence.

Code freeze for this addendum: s10_fidelity.py, s11_aradice_score.py, run_layer2_4.sh and data/aradice_splits.json are committed
before the job is launched; the analysis script for L1/L2/L4 is scripts/validity_analyze.py, sha256 = 2ec539c64b570514e7fe8cfbd44fa6eaf9d0eda36918c4a6445d09ad84bed410, frozen 2026-11-07 ~03:20 local (fidelity embedding job started 03:08; no L2/L4 output existed; L1 uses only already-seen confirmatory scores and the published exclusion list).

---
## Addendum 5 (dated 2026-11-07, 05:45 local; execution note for Addendum 4 — no rule changed)
- L1 run 03:20 (before L2/L4 outputs existed), L2 run 03:38 (fidelity.csv complete; AraDiCE ALLaM in progress, not read), L4 run 05:35
  (all four aradice_scores files complete, 6,000 rows each). validity_analyze.py unchanged (2ec539c6…).
- Outcome: L1 ≤ 1.1 pp change everywhere; L2 top-tercile retention ≥ 2/3 for MAG/SYR/EGY in 3/4 models, < 2/3 for KSA/UAE; L4 replicates
  (all CIs exclude 0; EGY ΔP1 −11…−17, LEV −6…−14). Reading in results/validity/VALIDITY_SUMMARY.md.
- Post-hoc note recorded for transparency: the L2 rule treated embedding similarity as "fidelity"; it also measures dialectal distance.
  This confound was not anticipated in Addendum 4. The rule is applied as written (conservative against the dialect hypothesis) and the
  confound is stated in the paper; no alternative rule is introduced after the fact.
- Decision (§6 + Addendum 1 §B): proceed to a limited-claims draft (Findings via ARR). Claims restricted to what survives all layers.


---
## Addendum 6 (dated 2026-11-07, after external review #7; wording rules only, no analysis changed)
- Claims use "persisted across two resources and after the specified automatic sensitivity analyses, with undetected meaning differences
  possibly contributing" — never "translation does not explain it", never "model-independent", never "content-controlled", never "human audit".
- Non-significant differences are "not detectably different on this sample"; 80-key results always carry their CIs (MAG ΔP1 after exclusion:
  +12/−8/−17/−25 pp, CIs ≈ ±40 pp). The similarity-tercile rule is descriptive, not causal (similarity may track dialectal distance and difficulty).
- AraDiCE is machine translation with human post-editing (Mousi et al. 2025), not human translation; it replicates EGY/LEV only (no MAG).
- "Equal reliability": P1 descriptive; S4 operational; P2 equal target coverage; all over option-letter scores, not free-form abstention.
- Positioning: measuring reliability transfer across dialectal phrasings and what per-dialect calibration repairs at what cost; cite WACL 2025
  (dialect-ID calibration) and Jones et al. 2020 (selective prediction and group disparity). α=0.1 null stays visible in the main text.
- Paper structure (doc §20): confirmatory results + S4 + AraDiCE + calibration trade-off in the body; internal router and representation
  interventions in appendices; the pilot described as development only.


---
## Addendum 7 (dated 2026-11-07, ~06:45 local; written AFTER the confirmatory results were seen and BEFORE any quantity below was computed) — exploratory diagnostic of the sources of the reliability cost

Status: **exploratory** (the data have been analysed under Addenda 1–5; freezing this addendum fixes the analysis before its numbers are
seen but does not restore an unseen-data status). Motivated by external review #8 (2026-11-07). The paper labels every result of this
addendum "exploratory; specified after the confirmatory results were seen and before computation".

### 7.1 Purpose and interpretive limit
Three descriptive views of the dialect reliability cost: (a) lower accuracy; (b) failure of threshold transfer (an MSA-chosen threshold
applied to a dialect); (c) weaker ranking of correct above incorrect answers by the confidence score. They are **diagnostic views, not
additive causal components**: no fraction of the gap will be attributed to a source, and failure of threshold transfer is not by itself
evidence of probability miscalibration (difficulty and confidence distributions may shift together).

### 7.2 Data and score
Confirmatory test keys (1,420) for all estimates; calibration keys (808) for thresholds; confidence s = p_max (as in every analysis);
correctness from the letter-logit prediction; four models; varieties MSA, EGY, SYR, KSA, UAE, MAG (ENG in the CSVs, not in the figure).
Uncertainty: paired bootstrap over test keys, B = 2000, numpy default_rng(0), percentile 95% CIs; thresholds held fixed.

### 7.3 Quantities (per model × variety, on test)
- **D1 AUROC** of s for correctness (Mann–Whitney; ties count ½): discrimination of the confidence score within the variety.
- **D2 AUGRC** (Traub et al. 2024): area under the generalized risk–coverage curve, GR(c) = (#errors among the ⌈c·n⌉ highest-confidence
  items)/n; computed as the mean of GR over the n empirical coverage steps. Lower is better; it combines accuracy and ranking by design
  and is reported next to the AURC already in P1 (no new AURC computation).
- **D3** paired differences (variety − MSA) of AUROC and AUGRC with CIs.
- **D4 S4 extension (variety-specific threshold):** for r* ∈ {0.15, 0.20, 0.25, 0.30} (primary 0.20), τ_v is chosen on the calibration
  items of variety v by the S4 rule (lowest confidence whose cumulative calibration risk ≤ r*) and applied to the test items of
  variety v. Reported with CIs: answered fraction and realised risk at τ_v; the **recoverable contrast** answered_v(τ_v) − answered_v(τ_MSA)
  (what re-thresholding alone changes for that variety); the **residual gap** answered_v(τ_v) − answered_MSA(τ_MSA) (the gap that remains
  when each variety has its own threshold at the same target). τ_v from 808 items is itself noisy; the realised risk at τ_v on test says
  whether the dialect-chosen threshold holds the target.
- **D5 Figure "Diagnostic views of the reliability cost"**: one row per model, three panels — accuracy; AUROC with CI; answered fraction
  at r* = 0.20 under τ_MSA and under τ_v with realised risk annotated. This figure enters the main text; S1 and S3 move to the appendix.

### 7.4 Reading rules (fixed now)
- ΔAUROC CI excluding 0 and negative → "the confidence score ranks correct answers less well in this variety"; CI including 0 → "not
  detectably different on this sample"; magnitudes and CIs reported either way. A negative ΔAUROC is an **upper bound** on discrimination
  loss, because undetected meaning changes (gold answer no longer valid) register as errors whatever the confidence.
- D4: residual-gap CI excluding 0 → "re-thresholding alone does not remove the operational gap"; the recoverable contrast is reported as
  is, with no percentage attribution across sources.
- Whatever the outcome, **no further analysis is added on its basis**. The MSA-confidence selection diagnostic proposed in review #8 is
  deferred (not conditional on these results, not run).
- Code: scripts/diag_analyze.py, frozen before execution; sha256 recorded in the freeze line below. Outputs: results/diag/{D1_D2_discrimination.csv,
  D4_variety_threshold.csv, DIAG_REPORT.md, diag_figure.(png|pdf)}.

---
## Addendum 8 (dated 2026-11-07, ~06:45 local; written BEFORE any scoring under permuted option order or any generation was run) — measurement robustness: option order and answer extraction

### 8.1 Question
Whether the dialect gaps depend on (i) the position of the options (position bias of letter-logit MCQ scoring) and (ii) reading the answer
from letter logits rather than from generated text. This is a check on the measurement, not on content validity.

### 8.2 Design (fixed)
- **Subset:** 500 keys drawn uniformly without replacement from the 1,420 confirmatory test keys with numpy default_rng(20261107);
  stored in data/robust_keys.json (sha256 logged in PILOT_NOTES). Power: paired Δacc SE ≈ 2–3 pp, so small UAE/KSA gaps may not be
  resolvable; the subset is for stability of the MAG/SYR/EGY pattern and for the order-sensitivity rates.
- **Orderings:** k = 0, 1, 2, 3 cyclic shifts — the option at original index i is displayed at position (i + k) mod 4 with the gold index
  shifted accordingly; the three MSA (or ENG) shots keep their original order; prompt template, truncation and letter-logit scoring exactly as
  scripts/s9_score_confirm.py. k = 0 is re-scored in the same run (it also yields a re-run reproducibility rate against confirm_scores_*.csv).
- **Varieties/models:** all seven varieties, four models; 500 × 7 × 4 = 14,000 rows per model (scripts/s12_robustness.py; resumable).
- **G1 (all four models):** from the identical k = 0 prompt, greedy decoding of ≤ 8 new tokens; extraction: regex `^\s*\(?([A-D])(?=[\s.):،]|$)`
  on the generated text → letter, else "unextractable". Reported per variety: extractable rate, agreement with the letter-logit prediction,
  accuracy of the generated letter; paired Δ vs MSA. (Expected to be close to the logit decision for base models — reported as such.)
- **G2 (ALLaM-7B-Instruct-preview only — the only instruction-tuned checkpoint; Fanar-1-9B and gemma-2-9b have no chat template, and Qwen3-8B-Base's tokenizer ships one but the checkpoint is not chat-tuned):** the same k = 0 prompt text as the single user
  turn through the tokenizer's chat template, greedy ≤ 32 new tokens. Extraction rules in order: (1) the G1 regex at the start of the
  response; (2) `الإجابة(?: الصحيحة)?(?: هي)?\s*[:：]?\s*\(?([A-D])\b` or `[Aa]nswer(?: is)?\s*[:：]?\s*\(?([A-D])\b`; (3) exactly one of the four
  option texts (whitespace-normalised) occurs in the response; (4) else "unextractable". The first-step letter log-probabilities under the
  chat template are recorded as well (letter-logit under the chat condition). G2 differs from the measurement in two respects at once
  (template and decoding): it is a usage-validity check, not a decoding isolation.

### 8.3 Quantities (per model × variety, subset; paired key bootstrap B = 2000, default_rng(0))
- **R1 order-sensitivity rate** OSR_v: fraction of keys whose predicted option (by content) is not identical under the four orderings; Δ vs MSA
  with CI. Also the accuracy of the content-level majority vote across orderings (ties → the k = 0 prediction).
- **R2 gap stability:** Δacc_k(v) and ΔP1_k(v) (P1 at the MSA-matched risk, §3, computed within ordering k on the subset) for each k; the
  order-averaged gap with CI. Reading rule: "order-robust" if the order-averaged gap's CI excludes 0 and the four per-order gaps share its sign;
  otherwise "order-sensitive" (reported as such).
- **R3 S4 at the original τ_MSA** (r* = 0.20, from calibration under k = 0, as in CONFIRM_REPORT): Δanswered_k(v) per ordering and
  order-averaged (the threshold is fixed from the original ordering; stated).
- **R4 P3 decomposition (descriptive):** answer-change rate dialect-vs-MSA within the same ordering (as P3) compared with (a) the within-variety
  across-order change rate (k = 0 vs k = 1 prediction, the position-noise floor) and (b) the answer change computed on majority-vote predictions.
- **R5 generation agreement** (G1, G2) as in §8.2, with the G2 unextractable rate per variety reported as a quantity in its own right.

### 8.4 Reporting
All quantities reported whatever their direction, with CIs; subset power stated; no further orderings, decoding settings or models added on
the basis of these results. Scoring code scripts/s12_robustness.py and data/robust_keys.json are committed before the job is launched;
the analysis script scripts/robust_analyze.py is frozen (sha256 in PILOT_NOTES) before any output of the job is opened.

Freeze line (Addendum 7): scripts/diag_analyze.py sha256 = 9337bf5b9b2b83be0f764a56f22103fb01f59c2c96e9d6a7f5212190893fc7f9, frozen 2026-11-07 ~06:55 local, before execution; results/diag/ did not exist.

Freeze line (Addendum 8): data/robust_keys.json sha256 = 0b9697c028cfd87280b0bb2280287ce0b8b03df40f5382017d762a188f23929d (500 keys, seed 20261107);
scripts/s12_robustness.py sha256 = 5306e881969ee1c5eab067af3dd438fac3adf3504d61e38d595a4dfd77d8df9b (k=0 prompts verified byte-identical to
s9_score_confirm.py for all 3,500 rows before launch); scripts/run_robust.sh; job launched 2026-11-07 ~07:25 local. G2 wording above corrected
before launch (Qwen3-8B-Base tokenizer template noted). robust_analyze.py to be frozen before any output is opened.


---
## Addendum 9 (dated 2026-11-07, ~17:50 local; written AFTER reviews #9 and #10 and BEFORE any quantity below was computed) — final verification package

Status: sensitivity and verification analyses on already-analysed data; **exploratory/sensitivity, specified before computation**. Nothing here
replaces a pre-registered estimate: each new interval is reported NEXT TO the original fixed-calibration interval, whatever its width.

### 9.1 Calibration sensitivity (double resampling with threshold re-selection)
For each of B = 1000 iterations (numpy default_rng(1)): resample the 808 calibration keys with replacement and, independently, the 1,420 test
keys with replacement; all varieties of a key travel together (pairing preserved). In each iteration re-apply the SAME rules as the frozen
confirmatory code to the resampled calibration keys — S4 threshold τ (lowest confidence whose cumulative calibration risk ≤ r*; τ = 1.01 → nothing
answered, when no confidence meets the target), the variety-specific τ_v (Addendum 7 D4), and the conformal q̂ (⌈(n+1)(1−α)⌉-th smallest
score) — then evaluate on the resampled test keys. Quantities (per model × variety): S4 answered fraction, Δanswered vs MSA and realised risk
at r* = 0.20; D4 answered(τ_v), realised risk(τ_v), recoverable contrast and residual gap; P2 coverage under the MSA q̂ (α = 0.30), Δcov vs MSA,
set size under own q̂ and the size ratio. Report: percentile 95% intervals side by side with the original (test-only bootstrap, calibration
fixed) intervals and the ratio of widths. Reading rule: an original conclusion is "calibration-robust" when the double-resampling interval
still excludes 0 (or 1 for ratios); otherwise it is reported as "sensitive to the calibration sample" — no re-interpretation beyond that.
For the rotation subset (Addendum 8 R3): the same double resampling (calibration keys → τ; the 500 subset keys with their four orderings as one
unit → Δanswered per ordering and order-averaged).

### 9.2 Re-run reproducibility diagnostic (Addendum 8 k = 0 vs confirmatory scores)
On the 500 × 7 cells per model: (a) share of cells with a different prediction; (b) distribution of the top-two letter log-probability margin
(from the confirmatory logits) in the disagreeing cells vs all cells — median and the share with margin < 0.05 nats; (c) the per-variety Δacc
and ΔP1 (k = 0, subset) computed from the confirmatory scores vs from the re-run, and the maximum absolute difference; (d) S4 answered fraction
at the original τ from both runs. Reading: differences concentrated at near-ties and gap estimates within the bootstrap noise = numerical
(bf16/MPS batch-composition) non-determinism; anything else is reported as unexplained.

### 9.3 R4 paired comparison (Addendum 8)
Per model × dialect, per key: I₁ = [prediction under the dialect ≠ prediction under MSA, k = 0] and I₂ = [prediction under the same variety
at k = 0 ≠ at k = 1]; D = I₁ − I₂; mean D with a key-bootstrap 95% CI (B = 2000, default_rng(0)); also D′ with I₂ taken from MSA's own
rotation change. Reading: CI including 0 or negative → "dialect-vs-MSA change is not larger than the change under one option rotation";
positive and excluding 0 → "larger", reported as such. This is a comparison perturbation, not a subtractable noise component.

### 9.4 D4 distance-to-target table (post-hoc descriptive, computed 2026-11-07 ~17:30 before this addendum from the existing D4 output)
Per cell at r* = 0.20: |realised risk − 0.20| under τ_MSA vs under τ_v, whether the cell moved closer, and the answered fractions under both.
Already observed: 11/20 cells closer; cells with risk > 0.24 under τ_MSA: 4 → 0; mean distance 0.029 → 0.017. Reported with coverage, labelled
post hoc; the ±0.04 range is an observed range, not a pre-specified tolerance or a guarantee.

### 9.5 Independent computational check (not a human audit)
A written definition of P1, S4 and P2 (docs/METRIC_DEFINITIONS.md) is handed to a separate implementation (a fresh agent that is not shown
scripts/confirm_analyze.py or results/confirm/). It recomputes, per model: the S4 τ at r* ∈ {0.15, 0.20, 0.25, 0.30}, the conformal q̂ at
α ∈ {0.20, 0.30}, P1's MSA-matched risk and per-variety answerable fractions, S4 answered fractions and realised risks, P2 coverage and set sizes,
and the per-key answered/covered indicators. Comparison at the level of thresholds, denominators and per-variety values (tolerance 1e-9 on
thresholds, 1e-6 on fractions); any discrepancy is reported and resolved against the written definition. Named in the paper as "a computational
check by an independent implementation", not as an audit.

### 9.6 Code
scripts/sens_analyze.py (9.1–9.4) frozen before execution; sha256 in the freeze line below. Independent implementation: scripts/indep_check/
(written by the separate agent) with its own hash recorded after the comparison.

Freeze line (Addendum 9): scripts/sens_analyze.py sha256 = 3973de301651a08a19eb5b0e968742655e0a43f36d6eb5b87439ac6ab944584b, frozen 2026-11-07 ~17:55 local before execution; results/sens/ did not exist.
Execution note: the Mac link dropped at ~17:50 local; §9.1 (confirmatory part) and §9.4 run first on the local mirror of the confirmatory
files (identical hashes); §9.1b, §9.2 and §9.3 need the robust_scores files from the Mac and run when the link returns, with the same frozen script.

### 9.7 Wording rules adopted from reviews #9 and #10 (binding; extend Addendum 6)
- Never "repairs/restores the guarantee"; distinguish an empirically targeted threshold, a statistical guarantee with a stated procedure, and
  the marginal conformal coverage guarantee under its assumptions. Per-dialect adaptation "reduces some failures of reliability transfer;
  where the transferred threshold was already near target it mostly trades answers for small changes in risk; a gap in answered fraction or
  set size remains at the targets studied". The "±0.04" figure is an observed range, not a tolerance or a guarantee.
- D4 compares policies at the SAME NOMINAL TARGET, never "at equal risk" (the descriptive risk matching is P1); realised risk is shown next to
  the answered fraction.
- No "no threshold restores parity" from AUROC; "re-selecting the threshold with the policy tested did not remove the efficiency gap at the
  operating point studied". No "upper bound" on discrimination loss; "the interpretation of the AUROC difference remains affected by pair and
  label validity".
- Order robustness: "the gaps persist under the four cyclic rotations" (not "do not depend on option order"; no claim about all permutations
  or the absence of interaction). P3 vs rotation: "answer change alone does not identify dialect-specific instability, because one option
  rotation produces comparable or larger change" (a comparison perturbation, not a subtractable noise floor); order-sensitivity rise in
  dialects is a secondary correlational result.
- Calibration-sample variability: "a possible explanation", never "shown to be".
- Every count is attributed to one named metric; no blanket "19–20 of 20".
- AraDiCE replicates EGY/LEV only; dialect names instead of "near/distant"; "graded by embedding similarity to MSA" is a secondary result.
- "A computational check by an independent implementation", never "audit"; reviews by language-model sessions are not independent referees.
- Central narrative: applying an MSA-calibrated answer policy to dialectal versions changes coverage and risk; threshold adaptation brings the
  empirical risk toward the target where transfer failed badly, at a cost in coverage; confidence indicators and robustness tests show the
  limits of that adaptation.


---
## Addendum 10 (dated 2026-11-08, ~01:30 local; written after external review #11 of draft v0.1 and BEFORE computation) — two small supplements from stored outputs

### 10.1 Risk differences and target exceedance with uncertainty (supplements §9.1)
For S4 at r* = 0.20, per model × dialect: (a) the paired realised-risk difference vs MSA, Δrisk = risk_v(τ) − risk_MSA(τ), with (i) the
fixed-calibration test bootstrap (B = 2000, default_rng(0); already in CONFIRM_SUMMARY, re-derived here) and (ii) the §9.1 double resampling
(B = 1000, default_rng(1)); (b) exceedance of the target: the realised risk of the dialect under τ_MSA against 0.20, with the same two
intervals. Reading rules: "higher risk than MSA" only where the Δrisk interval excludes 0; "exceeds the target" only where the lower bound
of the realised-risk interval is above 0.20; point estimates above 0.20 are reported as such, separately. The two questions are kept apart
in every statement (abstract, introduction, conclusion).

### 10.2 Selective risk of the generated answers on the set the original threshold accepts (supplements Addendum 8 G1)
On the 500-key subset, k = 0, per model × variety: items accepted by the original τ_MSA (r* = 0.20, from calibration k = 0); among them,
error rate of the letter-logit answer vs error rate of the G1 generated letter (extraction rule 1; unextractable counted as an error), with
the paired difference and a key-bootstrap CI (B = 2000, default_rng(0)); also the accepted fraction. Reading: if the paired difference's
interval includes 0 (or is small relative to the dialect gaps), the S4 statements carry over to the generated answers on this prompt; if not,
S4 is stated for the letter-logit policy only. Code: scripts/supp_analyze.py, frozen (sha256 below) before execution.
Freeze line (Addendum 10): scripts/supp_analyze.py sha256 = 9d737d2020db161b62da7c3b531af045cd20ef599173871abbf1ceca545f5492, frozen 2026-11-08 ~01:35 local before execution.

## Erratum (dated 2026-11-08, ~11:00 local; no rule or analysis changed)
- The header of Addendum 4 reads "dated 2026-11-07, ~23:50 local". The project log (PILOT_NOTES_addendum_2026-11-05_07.md, "Pivot to
  automatic validity layers (2026-11-07, 03:00–03:30 local)") and Addendum 5 (execution note, 05:45 the same morning) place its writing
  at 03:00–03:30 on 7 November; "~23:50" is a clock error. The header is left as written; this note is the correction.
- The released confirmatory result files store the mean of the bootstrap differences in the columns d_answerable, d_answered and d_cov.
  From manuscript v0.5 the point estimates of these contrasts are the sample differences (e.g. answerable(v) − answerable(MSA)); the
  percentile intervals are unchanged. Found in the external review of draft v0.4; see Appendix C of the manuscript and RELEASE_NOTES §12.
