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

## Pivot to automatic validity layers (2026-11-07, 03:00–03:30 local)
- PI confirmed: the "audit" was produced by GPT-6 Astra Extra High (two sessions + adjudicator) → relabelled model-assisted screen everywhere; κ = within-model consistency.
- Addendum 4 pre-registered: L1 IFM external filter (published 3-judge exclusion list, 935 rows), L2 embedding fidelity covariate (multilingual-e5-large), L4 AraDiCE replication (2,000 items, 600/1,400 split, seed 20261107), L5 cross-model consistency. validity_analyze.py frozen (2ec539c6…).
- L1 result: dropping the 935 IFM-flagged rows (≈5–6% of test keys per dialect) moves every endpoint by ≤ 1.1 pp in all 20 dialect×model cells (e.g. Qwen3 MAG ΔP1 −27.4 → −26.3; Fanar MAG Δanswered −15.2 → −15.6). External, model-based, zero-cost evidence that flagged defects do not drive the cost.
- Chain launched 03:08 (fidelity embeddings, then AraDiCE for 4 models); Terminal window closed after launch.
