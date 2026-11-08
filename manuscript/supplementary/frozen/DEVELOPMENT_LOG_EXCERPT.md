# Historical excerpt from the supplied v0.4 development log

Original lines 1--140 follow verbatim. Provisional interpretations are superseded by the v0.5 reporting amendment.

# Arabic-Dialect-Abstention — pilot log (started 2026-11-04)

## Purpose
Early go/no-go tests for a new paper. Candidate hypotheses tested on paired (content-controlled) dialect data,
no new dataset construction, inference only, Mac (MPS, 137 GB RAM).

## Data
- MBZUAI/Dialectal-Arabic-MMLU (LREC 2026; CC-BY-4.0): 3,135 MMLU-Redux items × {ENG, MSA, EGY, SYR, KSA, UAE, MAG}; `qid` parallel within `domain`.
- Pilot subset: 500 keys, stratified by domain, seed 0 (`data/pilot_keys.json`); 3 fixed MSA demonstrations from the complement.
- Replication set available: QCRI AraDiCE ArabicMMLU-egy/lev aligned to MBZUAI/ArabicMMLU by `ID` (14,455 shared items) — `data/raw_*.jsonl`.

## Protocol (scoring)
- Prompt: fixed Arabic instruction + 3 MSA shots + test item; options labelled A–D; score next-token log-probs of letters (" A"/"A" variants, logsumexp), softmax over 4.
- Models (local cache): ALLaM-7B-Instruct-preview, Fanar-1-9B (base), Qwen3-8B-Base, gemma-2-9b. bf16, MPS, batch 8.
- Outputs: `results/scores_<model>.csv` (per item: letter log-probs, pred, correct, p_true, p_max).

## Pre-declared signals
- H1 (uncertainty): MSA-calibrated split-conformal coverage (α=.10) drops ≥3pp on MAG or SYR in ≥2/4 models, and own-dialect (Mondrian) calibration recovers it.
- H2: confidence does not fall as much as accuracy (Δ(conf−acc) > 0.03 on distant dialects).
- Secondary: item-level churn, cross-model shared flips, probe transfer, transient correctness (logit lens), mending recovery.

## Results log
### ALLaM-7B-Instruct-preview (n=500)
- Accuracy: MSA .558; EGY .542; UAE .558; KSA .514*; SYR .518; MAG .506*; ENG .642 (* paired CI excludes 0).
- Conformal coverage @MSA-cal: .900–.914 on all dialects (set size grows 2.51→2.84 MAG). H1 NOT supported. α=.05/.20 similar.
- Δ(conf−acc): ≤ +0.03 (KSA). H2 NOT supported.
- Churn: answer changed vs MSA on 17% (UAE, EGY) to 23–24% (SYR, MAG) of items; UAE net Δacc = 0 yet 43↔43 flips.
- Selective prediction: MSA-set threshold transfers; selective accuracy −4pp on SYR/KSA with lower coverage (appropriate abstention).

(continued below as runs complete)

### Fanar-1-9B (base) (n=500)
- Accuracy: MSA .584; UAE .576; EGY .546; KSA .544; SYR .538; MAG .500 (−8.4*); ENG .700 (+11.6*).
- Calibration excellent (ECE .05–.09; mean conf ≈ acc); Δ(conf−acc) ≈ 0 on every dialect → confidence tracks dialect difficulty.
- Churn vs MSA: 16% (UAE) – 23% (MAG, SYR). Cross-model (ALLaM∩Fanar) shared MSA✓→D✗ flips = 1.5–2.7× chance → partly item-driven, mostly model-specific.
- Selective prediction at an MSA-set threshold: coverage falls 0.50→0.33 on MAG (abstention disparity) while selective accuracy stays within ~5pp.

### Regime-dependence of conformal coverage (both models, cross-fitted bootstrap, Δ vs MSA)
- α=.10 (sets ≈2.3–2.8/4): no coverage loss on any dialect (sets grow instead).
- α=.30 (sets ≈1.4): Fanar MAG −9.6 [−13.8,−5.2], SYR −7.3, KSA −7.1, EGY −4.4, UAE −1.8 (ns); ALLaM −2 to −3 (ns), significant at α=.40 (−4 to −6).
- Set sizes do NOT grow in the informative regime (1.37→1.38): coverage loss is silent. ENG gains +5 to +13 ("English premium").
→ H1 holds only in the informative regime; H2 (overconfidence on dialects) does not hold. Dialect ordering: UAE ≈ MSA < EGY ≈ KSA ≈ SYR < MAG.

### Qwen3-8B-Base (n=500)
- Accuracy: MSA .632; UAE .606; EGY .576*; KSA .576*; SYR .554*; MAG .500 (−13.2*); ENG .746 (+11.5*).
- H2 appears here: Δ(conf−acc) = +.05 MAG, +.03 SYR/EGY/KSA → the multilingual model's confidence falls less than its accuracy on dialects (relative overconfidence), unlike Arabic-centric Fanar (≈0).
- Churn 15–24%; net losses strongly significant (McNemar p<.005 for SYR/KSA/MAG/EGY). Cross-model shared flips 1.5–3.0× chance (3 models).

### gemma-2-9b (base; Fanar's parent) — preliminary on 436/500 keys (run killed at the longest prompts; resume queued)
- Accuracy: MSA .557; UAE .541; EGY .514; KSA .495; SYR .491; MAG .463 (−9.4); ENG .697 (+14.0).
- Fanar on the SAME 436 keys: MSA .576 (+1.9 vs Gemma); gaps MAG −9.9, EGY −5.1, SYR −4.6, KSA −3.9, UAE −0.3.
→ Arabic continued pretraining (Gemma-2 → Fanar, 1T tokens) raises MSA ~2pp but does NOT narrow the relative dialect gap (MAG identical). Mirrors the "inherited circuit" finding in the code-switching paper.
- Δ(conf−acc) small for both Gemma and Fanar (≤ +.03): the relative overconfidence seen in Qwen3 is model-specific, not an Arabic-centric vs multilingual distinction. (Correct earlier wording accordingly.)

### ALLaM internals — logit lens at the answer position (n=3500 rows)
- The answer crystallises late: lens accuracy ≈ .25–.30 through L24, jumps to ≈ .55 at L28 (of 32).
- The MSA−dialect gap in p(correct) is ≈ 0 at every layer ≤ L26 and opens at L27 (MAG +.049 → +.066 at L31; SYR/KSA ≈ +.04–.05; EGY +.03; UAE ≈ 0). The English premium opens at the same layer (−.08).
- Flip items (MSA✓→D✗) never form the correct decision in the dialect run (p_correct ≈ .2–.3 at L29–31 vs .72–.86 in the MSA run): no late override → the "knowledge present but not surfaced" picture (medical-domain paper) is NOT what we see at the last token.
- "Transient correctness" is uninformative here (baseline ≈ 60% even for MSA-wrong items).
→ Mending sweep refocused on L16,24,26–30 (decision-forming layers), conditions mend vs random, last position.

### ALLaM internals — probes
- Dialect-vs-MSA decodability at the answer position: 92–99% (all layers, incl. final): the model clearly "knows" the input is dialectal.
- MSA-trained correctness probe transfers to dialects with no loss (AUROC .65–.70 at L31 everywhere; weaker than p_max .72–.75 with n=400 training items).

### Mending (ALLaM, mean-difference vector MSA−D at last position, scale 1.0, L16–30): NULL
- Δacc within ±0.8pp, indistinguishable from random vectors, 0/37 flips recovered (MAG). ||v|| ≈ 5–8% of ||h||. Second pass (scales 4, 8; reverse control; all positions) queued as run_s8b.sh.

### Self-routed variety-aware conformal calibration (pilot, ALLaM L24, numpy, 4 splits) — POSITIVE
- 7-way variety probe on the hidden state (no labels at test time), routing each item to its variety threshold.
- α=.30 coverage: MAG .648 (MSA-cal) → .677 (self-routed) vs .680 (oracle labels); SYR .667→.687 (.691); KSA .652→.675 (.674); EGY .690→.709 (.710); ENG sets shrink 1.46→1.17 at nominal coverage.
→ Label-free restoration of group-conditional coverage; expected to matter more for Fanar/Qwen (larger gaps). Candidate "method" contribution.

### Mending pass 2 (ALLaM, MAG, L27–28, scales 4/8, last position): NULL / harmful
- mend s=8 @L27: Δacc −3.2pp; reverse s=8 @L27: Δacc +3.2pp with lower agreement-with-MSA and lower p_true → pure perturbation noise, no directional effect. flip-recovered ≤ .23 matched by reverse/random.
→ A single mean-difference direction (MSA−dialect) at the answer position does not carry the dialect gap. Consistent with: dialect identity is decodable (92–99%) in directions ~orthogonal to the decision. Closed as a method; keep as a negative control in the paper.

## Decision (2026-11-04, end of pilot day)
GO: "Dialect shift as a reliability shift" — paired behavioral + uncertainty-regime + churn + self-routed variety-aware conformal calibration (+ mechanistic section: where the gap opens, decodability, probe transfer, mending null).
NO-GO: (i) naïve "conformal breaks under dialect shift at α=.1"; (ii) text-level/representation-level normalization as the fix; (iii) "knows-but-fails" framing.

## Corrective cycle after external review (2026-11-04, evening) — Stage A / Stage B
Bugs confirmed from the review and fixed before any re-measurement:
- s6 logit lens re-applied the final RMSNorm to the last hidden state (280/3500 letter disagreements vs original scores, mean |Δp_true| .037). Fixed in s6_internals.py; ALL calibration/selective analyses below use ORIGINAL scores (s3) only. Lens numbers in the earlier sections are indicative only.
- "Churn" conflated correctness change with answer change. Now reported separately (A4).
- selfroute.py calibrated thresholds on TRUE labels and routed by PREDICTED labels → optimistic. Replaced by stageB_router.py (grouped 3-way split; thresholds on predicted groups; equal-budget baselines).
- Brier was partial → multiclass Brier (A5).

### Stage A (scripts/stageA_measure.py; B=1000 paired bootstrap over keys; results/stageA/)
- A1 answerable fraction at the risk MSA attains at 50% coverage (Δ vs MSA, pp):
  MAG −11 ALLaM [−18,−2] / −28 Fanar [−36,−17] / −29 Gemma2 [−42,−20] / −32 Qwen3 [−40,−23];
  SYR −10/−20/−19/−18; KSA −7/−15/−17/−11; EGY/UAE ≈ 0 except Qwen3 (−13); ENG +24..+35.
  Matched risk levels: ALLaM .276, Fanar .176, Gemma2 .260, Qwen3 .184. ΔAURC significant for MAG/SYR/KSA in all four models.
- A2 set-size ratio (own-threshold, matched coverage) at α=.30: MAG 1.16/1.25/1.21/1.35 (all CIs > 1); UAE ≈ 1.0. Ratio grows with α (≈1.1 at .05 → 1.2–1.4 at .40). Δcov at the MSA threshold, α=.30: Fanar MAG −9.5 [−13.8,−5.2]; Qwen3 MAG −13.4 [−18.2,−8.6]; ALLaM small.
- A3 calibration efficiency (α=.30, 200 splits, held-out 250): n_cal=50 own-dialect items already give coverage .70–.71 (target .70); n=25 gives .73 (conservative). The label-based fix is cheap.
- A4 answer change 20–34% (MAG 32–33% in every model) vs correctness change 15–24%; remainder is wrong→other-wrong. A_any .70–.76 vs A_strict .30–.33 (MSA .56–.63).
- A5 multiclass Brier: MSA .50–.62, MAG .60–.67, ENG .35–.51.

### Stage B (scripts/stageB_router.py; ALLaM L31; 10 grouped 3-way splits 150/175/175; α=.2/.3)
- Router accuracy (7-way, R=150 keys×7): internal (hidden L31, LR) .59 < text char-n-gram .63. Confusions MSA↔UAE/KSA, SYR↔EGY/KSA.
- Coverage at α=.30, MAG: MSA-only .646, pooled .651, oracle Mondrian .667, text router .649, internal router .673, plausible-set .674; split SD ≈ .04 → all within noise; set sizes 1.58–1.69.
→ On ALLaM the internal router adds nothing demonstrable over a text router or 50-item Mondrian calibration. Fanar/Qwen3 (gaps 10–13pp) are the informative test; internals being recomputed (ADA_LENS=0, BS=2) then stageB runs automatically (run_stageAB.sh).

### Framing after correction
Keep: "cost of maintaining equal reliability under dialect shift" (A1/A2) + instability (A4) + cheap fix (A3). Drop as a claimed contribution: internal self-routing (unless Fanar/Qwen3 show a clear, equal-budget gain), mending, "knows dialect is harder". Next gate (not started): blind human audit of 50 items × 5 dialects (meaning/answer/clarity/dialect), pre-allocated splits of the remaining 2,632 items for confirmation.

### Stage B — Fanar (L40) and Qwen3 (L34), 10 grouped splits each; ALLaM extended to 30 splits (20:09 local)
- MSA-threshold MAG coverage at α=.30: Fanar .604, Qwen3 .537 (target .70); ALLaM .671.
- Oracle Mondrian: ΔMAG +.095 (Fanar), +.143 (Qwen3); Δworst-dialect +.063 / +.115 (±.02–.03). Pooled: ≈ +.04 only.
- Text router (char n-gram, acc .63): ΔMAG +.098 / +.134 — ≈ oracle. Internal router (acc .57 / .52): +.105 / +.118. Plausible-set conservative: best worst-dialect coverage at +.02–.04 set size.
- Set-size cost of restored coverage matches Stage A A2 (MAG 1.38→1.72 Fanar; 1.20→1.74 Qwen3).
→ Per-variety calibration is necessary and works even with a ~60%-accurate predictor; the internal router is NOT better than a text router → not a contribution. Report as controlled negative. Title/claims updated accordingly (results/stageB/STAGE_B_REPORT.md).

### After external review #4 (2026-11-04, ~21:00)
- Accepted: "removes the gap" → "substantially narrows where large; Qwen3 stays at 0.67–0.68 even with true labels; ALLaM nothing to recover". "50 items suffice" → distributional statement (P(|cov−0.70|≤0.05) ≈ 0.52–0.54 at n=50; 0.72–0.78 at n=150–200; Beta(n+1−l,l) reference matches). "any cheap predictor" → "the simple text classifier we tested". Internal router: "no consistent practical advantage justifying its cost" (ALLaM: higher coverage but larger sets).
- Fixed: A2 cross-fitting now splits KEYS first, bootstraps within fold (no key in both calibration and evaluation); cov@own-thr reported next to size (=0.700). Results unchanged within 0.01 (MAG size ratio 1.16/1.24/1.36/1.21; Δcov Fanar −9.3, Qwen3 −13.3). Stage A report v2 regenerated.
- Noted as limitations: Stage B CIs = split variability on 500 keys; budget unit = keys; hierarchical dependence of the 7 variants → guarantees only for per-variety true-label calibration.
- Pre-registered: ANALYSIS_PLAN.md (primary P1–P3, secondary S1–S3, decision rule, code freeze), data/confirmatory_splits.json (404/808/1,420; sha256 f0bfc16b…). Confirmatory scoring started 20:57 (scripts/run_confirm.sh; 4 models, ≈1 day).
- Human audit package: audit/DAMM_translation_audit_50x5.xlsx (50 pilot keys × 5 dialects, seed 20261104, stratified by MMLU category, blind to model outputs; 20 keys double-rated) + AUDIT_PROTOCOL.md.

### After external review #5 (2026-11-04, ~23:30)
- Audit package rebuilt (v2): separate rater files (rater2 sees no rater-1 data), summary denominators = rated rows only, "unsure" counted once per pair over Q1–Q4, adjudication by pair id (INDEX/MATCH) with per-check agreement + Cohen's κ; +30 confirmatory-TEST keys (seed 20261106) → 400 pairs / 80 keys; formulas verified against an independent Python computation on synthetic ratings. v1 workbook moved to audit/superseded_v1/.
- ANALYSIS_PLAN Addendum 1: freeze log with timestamps/hashes (v1 d1b3396d…, v2 8ade05cd…), single non-binary decision rule, interpretation limits (P1 descriptive; new S4 operational threshold chosen on calibration; P2 = equal target coverage; CIs condition on fixed calibration/router), audit v2 definitions and conservative bound (Δ ± f_upper), theory wording (Beta as reference; predicted-group vs true-dialect guarantee).
- Decision on ordering: human audit may be the last step (sample/policy fixed, raters blind by construction), but no conclusion/manuscript before it completes.

## Confirmatory test executed (2026-11-05 08:10 local) — pre-registered analysis, frozen code (8ade05cd…), test n=1,420
- P1 answerable at MSA-matched risk (Δ vs MSA, pp): MAG −24/−20/−27/−18 (ALLaM/Fanar/Qwen3/Gemma); SYR −19/−17/−19/−19; KSA −11/−12/−6/−13; EGY −10/−14/−11/−15; UAE −8/−7/−7/−8. All 20 CIs exclude 0. Ordering as in pilot; ALLaM-MAG larger than pilot.
- P2 α=.30: Δcov@MSA-thr MAG −8/−10/−13/−8; size ratio at own thr MAG ×1.17/1.25/1.32/1.21 (achieved cov .66–.69); SYR ×1.18–1.23; UAE ×1.08–1.12 (all CIs > 1). ALLaM-MAG own-thr coverage .657 (cal→test transfer imperfect; flag as exploratory).
- P3 answer change 20–34% (MAG 29–34%), correctness change 14–24%; A_any .73–.78 vs A_strict .30–.34.
- S4 operational (τ from calibration MSA, r*=.20): MSA realised risk .18–.21; MAG answered −11 to −21 pp AND realised risk .21–.28 in 3/4 models (double penalty).
- S2: oracle Mondrian +5.1/+10.2/+11.6/+6.8 pp on MAG; text router (acc .638) +2.6/+7.0/+9.4/+6.0 at ≈ oracle set sizes; pooled < half; plausible-set highest but conservative everywhere (MSA cov .75–.79, +0.2–0.3 set size).
- S1: P(|cov−.70|≤.05) at n=50: .46–.65; n=150: .63–.89; n=400: .73–1.00.
- Status: pattern confirmed on held-out data; NO final conclusion until the human audit (400 pairs) is in. Outputs in results/confirm/ (CONFIRM_SUMMARY.md). Doc section 17 added (rev 26).
### After external review #6 (2026-11-05 ~11:30)
- Doc (rev 27): removed "≈50 items suffice" (sections 1, 12), "content fixed literally" → "same question, human-translated; meaning preservation under audit", "any loss attributable to surface alone" → conditional on translation validity, "model-independent" → "recurs across the four models studied"; P1 table now plug-in Δ (5 cells changed ≤1.4 pp, note added); P2 shows achieved coverages and labels the ALLaM-MAG 0.657 check as exploratory (cal-resampling range 0.63–0.70; swap 0.73 → sampling fluctuation); S4 restricted to cells with paired Δrisk CI > 0 (SYR all four; MAG ALLaM; marginal Qwen3); S2 recovery fractions per model (pooled 63/51/40/46%, router 51/69/81/88%); guarantee wording conditional; audit now 80 keys × 5.
- ANALYSIS_PLAN Addendum 2 (post-results, pre-audit): version history; sensitivity plan corrected (f/(1−f) bound only for fixed-rule proportions; P1/size-ratio/realised-risk via exclusion + MSA-replacement counterfactual on audited keys; Q3 separate; unsure never valid); reporting rules.
- Mac link down at the time of these edits; files staged locally and sent to the PI; to be committed to the Mac when the link returns.

## Human audit received and analysed (2026-11-07)
- Defect rates (rater 1, 400 pairs): basic 0.37 [0.31,0.44] (UAE .44, SYR .40, MAG .35, KSA .34, EGY .33); Q2-invalid 0.08 (MAG .16); Q3 0.34; strict 0.54. Pilot keys .32 vs test keys .45.
