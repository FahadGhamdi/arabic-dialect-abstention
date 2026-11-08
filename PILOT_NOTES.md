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
- Agreement: κ Q1 .86, Q2 .36 (yes↔unsure), Q3 .90, Q4 n/a. Third-rater basic .33 on the 150.
- Flags vs model behaviour (1,600 pair×model): Δacc −4.5 (unflagged) vs −6.2 (flagged); answer change 26.9 vs 27.7%; clustered CI of difference includes 0.
- Sensitivity on 80 audited keys: exclusion leaves answer change 19–35%, ΔP1 −10…−21, Δanswered −6…−20; MAG Δcov −8.1→−3.8 (noise-level). Counterfactual residual ≈ (1−f). Bound vacuous.
- Decision: write-up proceeds (limited claims; resource finding prominent; drop "content-controlled" as a premise) once rater identity is confirmed. results/audit/AUDIT_RESULTS.md; ANALYSIS_PLAN Addendum 3.

## Automatic validity layers complete (2026-11-07 05:45)
- L2: cost graded by e5 similarity; top-tercile retention ≥2/3 for MAG/SYR/EGY in 3/4 models; KSA/UAE largely confined to low-similarity items; similarity conflates fidelity and dialectal distance (flag rate by tercile 51/41/19%; Spearman −0.25).
- L4 AraDiCE (1,400 test): Δacc −3.6…−7.0; answer change 19–26%; ΔP1 EGY −11…−17, LEV −6…−14; Δcov −3…−7; size ×1.02–1.28; all CIs exclude 0.
- Decision: write-up (Findings), narrowed claim: distance-graded reliability cost, robust for MAG/SYR (mostly EGY), small/fidelity-sensitive for KSA/UAE; equivalence judgements automatic (stated limitation). Doc section 19 (rev 29).

### Review #7 applied (2026-11-07): wording rules (Addendum 6), doc reading guide + §18/§19 rewording + §20 paper structure (rev 30); AraDiCE = MT + human post-editing; limitations list fixed.

## Review #8 (2026-11-07, two rounds): diagnostic + measurement-robustness package adopted
- Reviewer's corrections accepted: numbers not "immune" (CIs conditional on a fixed calibration set; code not externally audited); confirmatory
  MAG figure is 23–32% vs 50% (not "a fifth vs a half"); "equal budget" = equal calibration keys, not equal cost; similarity analysis does not
  isolate dialect from translation; the three diagnostic views are NOT additive causal components; one cyclic shift ≠ position balance;
  letter-only generation on base models is near-tautological; no result-conditional analyses (MSA-confidence selection deferred, not conditional).
- **Addendum 7 (exploratory diagnostic) and Addendum 8 (measurement robustness) written and frozen ~06:45 local** (ANALYSIS_PLAN v9,
  versions/ANALYSIS_PLAN_v9_2026-11-07_addenda7-8.md). Freeze hashes: diag_analyze.py 9337bf5b… (v1, kept as diag_analyze_v1_frozen.py);
  robust_keys.json 0b9697c0… (500 test keys, seed 20261107); s12_robustness.py 5306e881… (k=0 prompts verified byte-identical to
  s9_score_confirm.py for all 3,500 rows with a stubbed-torch dry run before launch); **robust_analyze.py 61fdd211a88e9063722ce575c708d504645844bfebb72746fc17ff3a2848b829,
  frozen 06:48 local, smoke-tested on synthetic files only; no robust_scores_*/robust_gen_* file opened.**
- Diagnostic run 07:05 local (23 s; results/diag/). Outcome (DIAG_SUMMARY.md): ΔAUROC vs MSA negative with CI excluding 0 for MAG and SYR in 4/4
  models (−0.03…−0.07), EGY 2/4, KSA 2/4, UAE 0/4; AUGRC higher in 20/20 dialect cells. D4 (r*=.20): τ_v restores the risk target (realised
  0.16–0.24 vs 0.17–0.31 under τ_MSA) and answers FEWER dialect questions (recoverable contrast negative in 17/20); residual gap at equal
  target −0.04…−0.34, CI<0 in 19/20. Reading: "variety-specific calibration repairs the guarantee, not the efficiency gap". Figure v1.1 =
  title/axis cosmetics only (diag_analyze.py 44acd4a2…), numbers unchanged.
- Robustness job launched 06:45 local via RUN_JOB.command (job.sh → run_robust.sh → s12_robustness.py; caffeinate; resumable; logs/robust.log);
  ALLaM ETA ≈30 min scoring + generation; whole chain ≈12–15 h. Terminal window closed after launch.
- Incident: device_commit_files served a STALE copy for a previously used staged path (ANALYSIS_PLAN.md came back as the 20,603-byte
  Addendum-4 version); detected by hash check and restored from the versioned copy within one minute. Rule from now on: fresh staged
  paths per commit and a hash check after every commit.

## Robustness job — interim run on ALLaM only (2026-11-07 09:25 local; scheduled check-in)
- Chain healthy: ALLaM ROBUST DONE 08:34 local (score 4,407 s; G1 1,067 s; G2 1,067 s); Qwen3 scoring ≈49% at 09:22. No exit-137 so far.
- Frozen scripts/robust_analyze.py (61fdd211…, unchanged) run in the device VM on an isolated copy of ALLaM's files only
  (robust_scores/robust_gen/confirm_scores) → results/robust_interim_ALLaM/ (ROBUST_REPORT.md + R1–R5 CSVs). Final run on all four
  models will overwrite nothing here; it writes results/robust/.
- ALLaM outcome: re-run reproducibility 99.1% identical predictions (mean |Δp_max| 0.009). R2: Δacc and ΔP1 order-robust for all five
  dialects (same sign in 4/4 orderings; order-averaged CIs exclude 0; MAG ΔP1 −0.21 [−.29,−.15], SYR −0.19, EGY −0.13, KSA −0.10,
  UAE −0.08). R3: S4 Δanswered order-averaged CIs exclude 0 for all five. R1: order-sensitivity rate MSA 0.43 vs dialects 0.46–0.52
  (ΔOSR CI>0 for EGY/KSA/MAG/SYR; UAE not). **R4: P3 answer change vs MSA (0.23–0.32) is of the same size as the within-variety
  change under one option rotation (0.24–0.31)** — for this model P3 cannot be read as content-driven instability; it is at the
  level of position noise. Pending the other three models before any rewording of P3 in the doc/paper. R5: G1 agreement with
  letter-logit 97–99.6%, unextractable ≤0.8%; G2 (chat template) agreement with raw-prompt logit 82–92%, generated answer = chat
  first-token argmax 99–100%, unextractable ≤0.4%, generated accuracy under chat 0.53–0.66 with the same dialect ordering.

## Reviews #9 and #10 (2026-11-07 evening) and the final verification package (Addendum 9)
- Review #9 corrections accepted: "repairs the guarantee" withdrawn; D4 is a same-nominal-target comparison; AUROC does not imply "no threshold
  restores parity" and has no proven upper bound; order check = "persists under four rotations"; P3-vs-rotation is a comparison perturbation;
  ALLaM-MAG 0.657 = possible calibration fluctuation, not shown; 98–99% re-run agreement needs a diagnostic; **numeric error in the expert brief
  fixed: MAG double penalty is 2/4 (ALLaM, Qwen3 marginal), not 3/4** — the results files were always 2/4.
- Review #10 accepted: per-cell distance-to-target before/after (computed from the existing D4 output ≈17:30: closer in 11/20; risk>0.24 cells
  4→0; mean distance 0.029→0.017); calibration sensitivity design constraints; "computational check by an independent implementation" (not an
  audit); our "nine reviews changed no number" statement withdrawn; LRE characterisation withdrawn (Findings first on audience/content fit only).
- Addendum 9 frozen ~17:55 local (plan v10; sens_analyze.py 3973de30…). Run ~18:00 on the local mirror (confirmatory part): S4 Δanswered
  calibration-robust 19/20 (unchanged), P2 Δcov 20/20, P2 size ratio 20/20 but intervals ≈3× wider (2.7–4.3), D4 residual gap 14/20 (was 19/20;
  sensitive: Fanar EGY/UAE, Qwen3 KSA/UAE, Gemma EGY/UAE; widths ×2.2–4.5). results/sens/SENS_SUMMARY.md. §9.1b/9.2/9.3 pending the Mac link
  (dropped ~17:50 local; gemma G1 state unknown until it returns). Independent implementation check (§9.5) launched 18:05 as a separate agent
  from docs/METRIC_DEFINITIONS.md.
- Docs: main doc rev 43 (§21 reworded, §22 added, reading guide), expert brief rev 23 (six corrections + §11).
- Independent computational check (§9.5) complete 18:05 local: P1 identical; S4 (r*≤0.25) and P2 agree to one boundary item; per-key S4 indicator
  1 mismatch / 39,760, coverage indicator 5 / 39,760; only Fanar r*=0.30 differs materially (τ 0.3757 vs 0.3790; ≤0.011 answered) because the
  stored lA..lD are rounded to 4 decimals while p_max/p_true carry 5 — an input-precision effect, documented. results/indep_check/INDEP_COMPARISON.md.
  Release note: store log-probs at full precision and state the tie rule.
- Draft v0.1 of the manuscript written as a Claude Doc (English; all sections; §5 flagged pending until this check — now cleared; Gemma G1 and
  §9.1b/9.2/9.3 still pending the Mac link).
- 19:57 local (link back): §9.1b/9.2/9.3 run with the unchanged frozen sens_analyze.py. 9.1b: rotation-subset S4 calibration-robust 19/20
  (ALLaM–UAE borderline, as before). 9.2: re-run disagreements 0.9–2.0% of cells, concentrated at near-ties (median top-2 margin ≤0.125 nats
  vs 0.5–1.75 overall; 43–52% below 0.05 nats); gap estimates differ ≤0.03 — numerical non-determinism, no conclusion affected. 9.3: for the
  five dialects D ≤ 0 everywhere (CI<0 in 15/20, includes 0 in 5/20, >0 in 0/20); vs MSA's own rotation change larger only for ALLaM MAG/SYR
  (+0.05/+0.06); P3 remains withdrawn. Gemma G1 log last advanced 604/3500 at ≈17:16 local; gen file last written 17:59 local — consistent with
  the Mac sleeping when the link dropped (17:48–19:55); job state checked after sync.

## Robustness job — CLOSED (2026-11-08 01:10 local)
- Chain finished 01:06 local (gemma G1 32,733 s; the process survived the Mac's sleep 17:48–19:55 and resumed). Final frozen
  robust_analyze.py (61fdd211…) run on all four models → results/robust/; R1–R4 CSVs identical (cmp) to the interim four-model run.
- Gemma G1: agreement with the letter-logit choice 0.902–0.968 across varieties, unextractable 0, generated accuracy within ±0.012 of logit
  accuracy, same dialect ordering. Four-model G1 range: 0.90–1.00. ROBUST_SUMMARY.md finalised in results/robust/.
- All Addendum 8 and Addendum 9 items are now complete; nothing is running on the Mac.

## Addendum 10 — review #11 supplements (2026-11-08 ~01:40 local)
- External review #11 (on draft v0.1) accepted in full: seven wording/claim points plus two computations from stored outputs. Addendum 10
  written and frozen BEFORE computation (scripts/supp_analyze.py sha256 9d737d20…); no new experiment; outputs in results/supp/.
- 10.1 (S4, r*=0.20, τ_MSA): paired Δrisk vs MSA excludes 0 for SYR 4/4 fixed-cal / 3/4 double-resampled (Gemma drops, +0.042 [−0.000,+0.084]),
  MAG 2/4 both ways (ALLaM, Qwen3), EGY 2/4 fixed / 1/4 double, KSA and UAE ≤1/4. Exceeding the 0.20 target: point estimates above 0.20 in
  18/20 dialect cells (Qwen3–KSA by 0.0003), but the interval lower bound is above 0.20 only for ALLaM's five dialects (fixed-cal; 0.24–0.31)
  and for ALLaM–MAG and ALLaM–SYR (double resampling). Rule: "higher risk than MSA" and "exceeds the target" are separate statements.
- 10.2 (500-key subset, k=0): on the items accepted by τ_MSA, the G1 generated letter has the same selective risk as the letter-logit choice in
  27/28 cells (paired difference 0.000); the exception is Fanar–ENG −0.003 [−0.008, +0.000]. All G1 disagreements lie below the threshold.
  S4 statements therefore hold for the generated answers on this prompt; no new generation run needed.
- Draft v0.2 (Claude Doc rev 34): "higher than MSA" vs "exceeds target" separated in abstract/intro/§5/conclusion; "than the policy promises"
  removed; "produced sets 17–32% larger at the same nominal target"; "no positive difference reached significance"; bf16 wording softened;
  P1 exception to "nothing tuned on test"; "every alternative"; log-sum-exp wording; 37% not a resource error estimate; central-message
  sentence in the abstract; figures plan. Remaining before LaTeX: full references, figures, freeze log in the appendix, venue decision.
- Main doc rev 49 (§22.5), expert brief rev 29 (§11.5). Nothing running on the Mac.

## Submission preparation — opened 2026-11-08 ~02:40 local (after external review #12 of the execution plan)
- Venue decision by the researcher: Applied Sciences (MDPI). Execution plan written as a Claude Doc (YA9nPZeLHP5u5cmbh2CtsX) and reviewed
  externally (review #12). Accepted: readiness criterion instead of confidence; claims ledger first and richer (comparison, denominator,
  unit, interval type, analysis tier, allowed wording); Figure 1 = S4 only, P1 separate; three-tier pre-specification table (specified
  before confirmatory results / addendum specified after main results and before its computation / exploratory; P3 = claim withdrawn,
  negative result documented); clean-folder reproduction check of the release package; no "withdrawn claims" section in the main text;
  0.20 is a ceiling, not a value to approach (D4 presentation re-framed by counting cells above the ceiling under tau_MSA vs tau_v — a
  presentation change from existing columns, no new analysis); GenAI disclosure split (data checking vs code/writing); "<=2%" ->
  "observed 0.9–2.0% choice differences in the specified re-scoring". Not adopted: the reviewer's title wording (principle accepted;
  three alternatives offered to the researcher; option 1 used provisionally in v0.3).
- Documentation mechanism stated as it happened: plan frozen locally with dated versions + this log; no public registry; sha256 proves
  identity not date; the only server-side timestamps are the Claude Docs revision histories. Recommendation for future work: OSF.
- Overnight work (no model runs; cloud workspace on a complete mirror; Mac not required): claims ledger -> references -> figures ->
  IMRaD restructuring (v0.3) -> release package + reproduction check -> PDF -> final ledger re-check. Mirror completed at 02:35 local by
  staging results/validity L2/L4, aradice_scores_*, stage A/B reports, audit files and early-stage scripts from the Mac.
- 02:45 local — Claims ledger built (docs/CLAIMS_LEDGER.csv, 104 rows; scripts/build_ledger.py + scripts/check_ledger.py → docs/LEDGER_CHECK.md;
  95 recomputed rows PASS, 9 report-sourced). The audit found these v0.2 inconsistencies, corrected in v0.3: ΔAUROC MAG/SYR range −0.03 to −0.06
  (not −0.07); IFM filter: 935 = resource-wide flagged rows, 387 on test keys (v0.2 said "dropping the 935 rows"); residual-gap range −0.01 to
  −0.34 (not −0.04); L1 largest endpoint change 1.45 pp (ALLaM–SYR ΔP1), not ≤1.1 pp — this also corrects VALIDITY_SUMMARY.md; P2 Δcov MAG
  Fanar −10 (not −11); S2 pooled Gemma 0.65 (not 0.66); S4 Δanswered Qwen3–UAE −0.05 (not −0.06); G1 generated-vs-logit accuracy within 0.014
  over all cells (0.012 held for Gemma only); Δrisk CIs now from the frozen Addendum 10 run (S101) instead of the post-hoc CONFIRM_SUMMARY
  bootstrap (ALLaM–MAG [+3.1,+10.1], Qwen3–MAG [+0.3,+7.0]); R1/R2 sentences used model order ALLaM/Qwen3/Fanar/Gemma — standardised.
  Ceiling framing for D4 (review #12): dialect cells with realised risk above 0.20 — 18/20 under τ_MSA, 7/20 under τ_v (point estimates).
- P2 at α=0.10: one of 20 Δcov intervals excludes 0 (v0.2 said all include 0); largest |Δcov| 1.7 pp — corrected in v0.3.
- 03:00 local — References verified one by one (paper/references.bib, 29 entries; docs/REFERENCES_CHECK.md). Two substantive corrections for the
  manuscript: (i) DialectalArabicMMLU is Altakrori et al. (LREC 2026; arXiv 2510.27543), not "Robinson et al. 2025", and it extends
  MMLU-Redux, not ArabicMMLU; its MAG label is the Moroccan dialect (v0.3: "Moroccan (MAG)"); QC = translator/reviewer/adjudicator per dialect,
  32-item Likert check per dialect with "about 5%" inaccuracies, second review round for UAE and SYR. (ii) Fanar-1-9B (Fanar Prime) is a
  continual pre-training of Gemma-2-9B (Fanar paper §architecture) — the four checkpoints come from three base families; stated in v0.3
  Methods and Limitations. Added El-Yaniv & Wiener 2010, Vovk 2012 (conditional validity), Kamath et al. 2020, Zheng et al. 2023 (LLM-judge
  biases), Robinson et al. 2023 (letter scoring), Gema et al. 2025 (MMLU-Redux). IFM dataset card could not be re-fetched from the workspace;
  to re-check before submission.
- 03:05 local — Figures drawn from the frozen result files only (scripts/make_figures.py sha256 4ce6f7ba26b30fd5…; figures/ PNG 600 dpi + PDF):
  fig1 S4 operating points (4 models; MSA hollow, dialects, ENG; fixed-calibration intervals; 0.20 line), fig2 D4 arrows from tau_MSA to
  tau_v, fig3 P2 coverage loss and set-size ratio with fixed (thick) and double-resampled (thin) intervals, figP1 matched-risk differences,
  figA risk–coverage curves with S4 points and the P1 reference, figB per-rotation ΔP1, figC interval-width ratios. Colours from a
  CVD-validated categorical palette; identity also carried by marker shape and direct labels. In-figure titles carry no claims
  (captions in the manuscript).
- 03:15 local — Manuscript v0.3 written in MDPI IMRaD structure (paper/manuscript_v0.3.md, 6.2k words body; abstract 202 words; keywords;
  Featured Application; Table 1 = three-tier specification timing + withdrawn claim; §3.7 GenAI disclosure split into measurement vs
  preparation; ceiling framing of D4; standard model order everywhere; Moroccan (MAG); Fanar/Gemma shared base disclosed; Discussion 5.1 in
  three bounded statements; no "withdrawn claims" section; appendices A–F listed; back matter with placeholders for the author).
  Text-level audit (scripts/audit_text_numbers.py): every number in the body is covered by the ledger. Review copy published as a Claude Doc
  (J5MaopHbuxk9gsJhoFbHDd) with author–date citations; LaTeX numbered version to follow.
- 03:25 local — Release package assembled (scripts/build_release.py → release/, 185+ files, ≈35 MB; README, RELEASE_NOTES, FROZEN_SCRIPTS.md,
  SHA256SUMS; no dataset texts). Clean-folder reproduction (run_repro: confirm → validity → diag → robust → sens → supp → indep → figures →
  ledger; 3 min, python3 -I): 51/57 files identical or numerically equal; L2 terciles, AraDiCE ΔP1 and one R2 rotation move by tie-order
  effects (≤0.013 / ≤0.003 / ≤0.006), no reported number changes, ledger passes inside the reproduction (docs/REPRO_CHECK.md).
  LaTeX: paper/latex/main.tex built from the markdown by scripts/build_latex.py with the MDPI class (Sept 2024, rticles distribution); compiles
  to a 15-page PDF (soul.sty stand-in and placeholder logo PDFs in this environment only; the journal's class and logos replace them).

### 2026-11-08 (08:20–08:25 local) — manuscript v0.4: natural voice, expanded related work, reference verification
- `paper/manuscript_v0.4.md` replaces v0.3 as the master. Changes: bold run-in labels removed from the body; formulaic
  framing sentences removed; Related Work rewritten as five paragraphs (selective classification; conformal prediction
  under shift; self-knowledge and abstention in LMs; dialect robustness and Arabic resources; measurement weaknesses);
  Discussion restructured into 5.1 findings vs prior work, 5.2 implications, 5.3 limitations (prose), 5.4 future work.
  Abstract 204 words. No number changed; audit_text_numbers: 559 numbers, all covered by the ledger (the audit now also
  tokenises interval bounds written as "−.091", strips headings, and lists 281 — DIALECTBENCH's variety count — as a
  quoted literature fact).
- 39 references added (68 in total). Each verified on its ACL Anthology / PMLR / NeurIPS / arXiv / journal page; table in
  docs/REFERENCES_CHECK.md. Four sentences were adjusted to match the sources: Ahuja et al. 2022 (miscalibration under
  zero-shot transfer on low-resource / typologically distant languages; a few target-language examples reduce it);
  Kantharuban et al. 2023 (economic, social and linguistic correlates); DIALECTBENCH ("Arabic among them" removed — not
  stated on the paper's page); Shah et al. 2022 is selective *regression*. AceGPT is NAACL 2024, not EMNLP.
- Cite-key check: 68 cited, 68 in references.bib, none missing, none unused.
- scripts/build_latex.py now reads v0.4 and strips the leading "Proceedings of the " from booktitles in the LaTeX copy of the
  bib (mdpi.bst adds "In Proceedings of the" itself, which had produced "In Proceedings of the Proceedings of the …" in the
  v0.3 PDF). PDF: 19 pages, 68 numbered references, no undefined citations, one 14.7 pt overfull line in §2.
- Release rebuilt with v0.4 included next to v0.3 (build_release.py).

### 2026-11-08 (09:00–09:40 local) — v0.4: number density, page layout, appendix tables
- Dense per-model series moved out of the body into six appendix tables (A1 P1; A2 P2 at α=0.30; A3 S2 for MAG; A4 accuracy/AUROC;
  A5 order-sensitivity; A6 order-averaged gaps). The tables are generated from the result files by scripts/make_appendix_tables.py
  and written into the manuscript between marker comments; no appendix number is typed by hand, and audit_text_numbers skips the
  generated blocks and now audits figure captions (previously it dropped them with the figure include). The body keeps the range
  and direction (e.g. "0.23–0.32 across the four models") with a pointer to the table; every range endpoint is a ledger value.
- Table 1 re-cut into shorter rows (the tall "Addenda" row could not break across pages and left a third of a page empty).
- Appendix figures added to the appendix itself: Figure A1 (P1 differences), A2 (risk–coverage curves), A3 (rotations),
  A4 (interval-width ratios); text references renumbered accordingly (old A2→A3, A3→A4). make_figures.py: the risk–coverage panel
  titles were overflowing into the neighbouring panel (now two lines); the in-figure title of the P1 figure removed for
  consistency with Figures 1–3. Only figP1_matched_risk and figA_risk_coverage changed.
- LaTeX build: tables are now floating `table` environments in \footnotesize built from pandoc's longtables (the earlier
  caption-in-a-separate-table trick counted every table twice: Table 2 printed as "Table 3", Table 3 as "Table 5"); figures float
  [tbp] with relaxed float parameters; appendices are real \section s (the class prints "Appendix A" etc.); one \FloatBarrier before
  the references. Result: 22 pages, no half-empty pages, one 14.7 pt overfull line in §2.
- Audits after the change: 528 numbers in the body and captions, all covered; ledger PASS 95; cite keys 68/68.
- Review doc (Claude Docs, "Manuscript v0.4 — review draft") updated in place: Table 1, the six edited sentences, the appendices.

### 2026-11-08 (09:10 local) — commit to the Mac
- commit_2026-11-08_v04.zip (sha256 5e68ae89…9de92) staged under _staged/ and unpacked into the project: 58 files verified against
  _staged/MANIFEST_commit_2026-11-08_v04.txt (PILOT_NOTES.md and results/audit/AUDIT_RESULTS.md written in place, since the bridge forbids deletion;
  the latter is the 2026-11-07 wording revision that had not reached the Mac). Frozen analysis scripts untouched (hashes identical on both sides).

### 2026-11-08 (09:50–10:05 local) — public repository, author block
- Public repository created and pushed: https://github.com/FahadGhamdi/arabic-dialect-abstention, commit 90a717c (191 files = the release
  package without paper/; MIT for scripts/, CC BY 4.0 for the rest; CITATION.cff with ORCID). The manuscript folder is held back until
  the arXiv decision. The Claude GitHub app was installed for this one repository only. Next: tag + Zenodo DOI at submission.
- Author block entered (F. AlGhamdi, Computer Science Department, Al-Baha University, Albaha 65779; fghamdi@bu.edu.sa; ORCID
  0000-0002-4161-2658); Funding "no external funding"; Author Contributions omitted (single author, as in the author's Electronics
  paper); Data Availability and Supplementary Materials point to the repository with the commit pinned and an "accessed on" date.
  PDF 22 pages; Overleaf zip refreshed; review doc updated.

### 2026-11-08 (10:20–11:30 local) — external review of v0.4 (Codex session; package "v0.5/v0.6") checked and applied → manuscript v0.5
Checked against the frozen scripts and result files before anything was taken over:
- CONFIRMED and applied: the d_answerable / d_answered / d_cov columns written by confirm_analyze.py are means of the bootstrap replicates
  (np.mean(da) etc.), not sample differences. S4 and P2 agree to 3 dp either way (max |Δ| 0.0006 / 0.0005); P1 differs by up to 0.014
  (Gemma–UAE −0.064 sample vs −0.078 bootstrap mean). The reviewer's 28 sample points equal my recomputation exactly. From v0.5 the
  point estimates are the sample differences: ledger rows P1-03/05/06, S4-03, P2-01/02/03, L2-01 re-expressed with a plug() helper in
  check_ledger.py; rows P1-08, COR-01..03 added; make_appendix_tables.py and make_figures.py (Figure 3, Figure A1) switched; six P1
  values change at 2 dp; intervals, counts and conclusions unchanged. No result file touched. Ledger: PASS 99.
- CONFIRMED and applied: development seed is 0 (scripts/s3_score.py SEED=0); 20261104 and 20261106 are the screen's sample seeds;
  three demonstration keys explain 3,135 − 500 − 3 = 2,632; scoring details (letter-ID aggregation, bf16/MPS, left padding, 2,048 max
  length, prompts sorted by length, no pinned revisions) now stated in §3.3; the screen's 0.37 is the composite basic flag (Q1 or Q2 = no),
  Q2 "unsure" on 29%; L4 size ratios have no intervals; confirm_analyze sorts with the default (unstable) sort — RELEASE_NOTES §3 corrected,
  §12 added; the timing record now says "before the confirmatory analysis", with plan v1/code v1 at ≈21:30 after scoring began at 20:57
  (Table 1 wording, §3.5, Appendix A Table A7); "our shift is milder than Kamath's" removed (no common scale); DAMM entry gets its DOI.
- RESOLVED differently from the reviewer: the Addendum 4 header time (≈23:50) is a clock error — the log places the writing at 03:00–03:30
  on 7 Nov and the execution note at 05:45; stated so in Appendix A and in an erratum appended to ANALYSIS_PLAN.md (header left as written).
- NOT adopted: the reviewer's prose (hedge-heavy, defensive) — substance taken, text kept in the manuscript's own voice; the compact
  16 mm-margin layout over the MDPI class (journal geometry must not be altered; our build already fills pages with floating tables and
  figures); the external "reporting amendment" layer (the correction lives in the pipeline: ledger, generators, notes); the title
  "Risk and Coverage across Arabic Dialects in Selective Question Answering" left for the author to decide (the reviewer says the author
  chose it); the 21 extra appendix tables — useful, to be generated from the result files by make_appendix_tables.py in the next pass
  rather than copied.
- Disclosure (§3.7) now names Claude Fable 5.1 (claude-fable-5-1) via Claude Code for 4–8 Nov sessions, GPT-6 Astra for review sessions
  (version per session not recorded) and the Codex-run review that found the estimator issue.
