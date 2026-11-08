# Ledger consistency audit

Rows: 107 — PASS 105, FAIL/ERROR 0, report-sourced (not recomputed) 2.

A consistency audit compares the manuscript's numbers and their stated comparison/denominator/interval type with the
frozen result files; it is not an independent re-computation (that is Appendix C / results/indep_check).

| id | §/tier | claim | file | computed | claimed | status |
|---|---|---|---|---|---|---|
| AC-01 | §3.1/§3.3 / T1 | MSA accuracy 0.59/0.61/0.63/0.59 | results/diag/D1_D2_discrimination.csv | [0.59, 0.61, 0.63, 0.59] | [0.59, 0.61, 0.63, 0.59] | **PASS** |
| AC-02 | §3.3 / T1 | MAG accuracy 0.49/0.53/0.52/0.50; SYR 0.53/0.53/0.58/0.50 | results/diag/D1_D2_discrimination.csv | [[0.49, 0.53, 0.52, 0.5], [0.53, 0.53, 0.58, 0.5]] | [[0.49, 0.53, 0.52, 0.5], [0.53, 0.53, 0.58, 0.5]] | **PASS** |
| AC-03 | §3.3 / T1 | dialect accuracy lower than MSA in every cell (20/20) | results/diag/D1_D2_discrimination.csv | 20 | 20 | **PASS** |
| AU-01-EGY | §3.3 table / T2 | ΔAUROC EGY with CIs (ALLaM/Fanar/Qwen3/Gemma) | results/diag/D1_D2_discrimination.csv | [-0.023, -0.05, 0.002, -0.037, -0.06, -0.015, -0.031, -0.055, -0.008, -0.02, -0.044, 0.005] | [-0.023, -0.05, 0.002, -0.037, -0.06, -0.015, -0.031, -0.055, -0.008, -0.02, -0.044, 0.005] | **PASS** |
| AU-01-KSA | §3.3 table / T2 | ΔAUROC KSA with CIs (ALLaM/Fanar/Qwen3/Gemma) | results/diag/D1_D2_discrimination.csv | [-0.012, -0.037, 0.011, -0.033, -0.057, -0.01, -0.015, -0.037, 0.006, -0.027, -0.05, -0.004] | [-0.012, -0.037, 0.011, -0.033, -0.057, -0.01, -0.015, -0.037, 0.006, -0.027, -0.05, -0.004] | **PASS** |
| AU-01-MAG | §3.3 table / T2 | ΔAUROC MAG with CIs (ALLaM/Fanar/Qwen3/Gemma) | results/diag/D1_D2_discrimination.csv | [-0.045, -0.072, -0.015, -0.04, -0.063, -0.014, -0.059, -0.087, -0.032, -0.029, -0.057, -0.001] | [-0.045, -0.072, -0.015, -0.04, -0.063, -0.014, -0.059, -0.087, -0.032, -0.029, -0.057, -0.001] | **PASS** |
| AU-01-SYR | §3.3 table / T2 | ΔAUROC SYR with CIs (ALLaM/Fanar/Qwen3/Gemma) | results/diag/D1_D2_discrimination.csv | [-0.056, -0.084, -0.028, -0.038, -0.063, -0.012, -0.065, -0.091, -0.039, -0.036, -0.063, -0.009] | [-0.056, -0.084, -0.028, -0.038, -0.063, -0.012, -0.065, -0.091, -0.039, -0.036, -0.063, -0.009] | **PASS** |
| AU-01-UAE | §3.3 table / T2 | ΔAUROC UAE with CIs (ALLaM/Fanar/Qwen3/Gemma) | results/diag/D1_D2_discrimination.csv | [0.002, -0.022, 0.026, -0.013, -0.035, 0.01, -0.014, -0.039, 0.009, -0.005, -0.028, 0.018] | [0.002, -0.022, 0.026, -0.013, -0.035, 0.01, -0.014, -0.039, 0.009, -0.005, -0.028, 0.018] | **PASS** |
| AU-02 | §3.3 / T2 | ΔAUROC CIs excluding 0: MAG 4/4, SYR 4/4, EGY 2/4, KSA 2/4, UAE 0/4 | results/diag/D1_D2_discrimination.csv | [4, 4, 2, 2, 0] | [4, 4, 2, 2, 0] | **PASS** |
| AU-03 | Abstract/§1 / T2 | ΔAUROC −0.03 to −0.07 for MAG and SYR in all four models | results/diag/D1_D2_discrimination.csv | [[-0.06, -0.03], 8] | [[-0.06, -0.03], 8] | **PASS** |
| AU-04 | §3.3 / T2 | MSA AUROC 0.77–0.80 | results/diag/D1_D2_discrimination.csv | [0.77, 0.8] | [0.77, 0.8] | **PASS** |
| AU-05 | §3.3 / T2 | AUGRC worse than MSA in all 20 cells (CI excludes 0) | results/diag/D1_D2_discrimination.csv | 20 | 20 | **PASS** |
| AUD-01 | §3.2 / App. E / T2 | 400 pairs = 80 keys × 5 dialects; 150 double-rated | results/audit_recomputed/SCREEN_RECOMPUTED.json | [400, 80, 150] | [400, 80, 150] | **PASS** |
| AUD-02 | §3.2 / App. E / T2 | basic defect rate 0.37 [0.31, 0.43]; UAE 0.44, EGY 0.33 | results/audit_recomputed/rates_recomputed.csv | [0.37, 0.31, 0.43] | [0.37, 0.31, 0.43] | **PASS** |
| AUD-03 | §3.2 / App. E / T2 | invalidating the gold answer 0.08 overall (MAG 0.16); hint/ambiguity 0.34 | results/audit_recomputed/SCREEN_RECOMPUTED.json | [0.08, 0.16, 0.34] | [0.08, 0.16, 0.34] | **PASS** |
| AUD-04 | §3.2 / App. E / T2 | κ: 0.86 meaning, 0.36 answer validity, 0.90 clarity (within-model consistency) | results/audit_recomputed/agreement_recomputed.csv | [0.86, 0.36, 0.9, 0.0] | [0.86, 0.36, 0.9, 0] | **PASS** |
| AUD-05 | §3.2 / App. E / T2 | 1,600 pair×model observations; Δacc −4.5 (unflagged) vs −6.2 (flagged); difference −1.8 [−8.2, +5.1]; answer change 26.9% vs 27.7% | results/audit_recomputed/association_recomputed.csv | [-4.5, -6.2, -1.8, -8.2, 5.1] | [-4.5, -6.2, -1.8, -8.2, 5.1] | **PASS** |
| AUD-06 | §3.2 / App. E / T2 | after excluding flagged pairs (80 keys) operational answered fraction −6 to −20 pp; MAG per-model ΔP1 interval widths 38–94 pp | results/audit_recomputed/sensitivity_recomputed.csv | [-20.0, -6.0] | [-20, -6] | **PASS** |
| AUD-07 | §3.2 / App. E / EXT | resource documentation reports ≈5% error from a 32-item/dialect check | results/audit/AUDIT_RESULTS.md |  | "5%" | **report-sourced** |
| COR-01 | Appendix C / T1 | largest P1 estimator difference: Gemma–UAE −0.064 (sample difference) vs −0.078 (bootstrap mean) | results/confirm/P1_selective.csv | [-0.064, -0.078] | [-0.064, -0.078] | **PASS** |
| COR-02 | Appendix C / §2.5 / T1 | six P1 differences changed at the second decimal under the correction | results/confirm/P1_selective.csv | 6 | 6 | **PASS** |
| COR-03 | Appendix C / T1 | S4 and P2 contrasts agree to the third decimal between the two estimators | results/confirm/S4_operational_selective.csv | 0.001 | 0.001 | **PASS** |
| D01 | §2 Methods / DSN | 3,135 DAMM questions (keys) | data/damm_keys.csv | 3135 | 3135 | **PASS** |
| D02 | §2 Methods / DSN | development sample 500 keys | data/pilot_keys.json | 500 | 500 | **PASS** |
| D03 | §2 Methods / DSN | router 404 / calibration 808 / test 1,420 keys; seed 20261105 | data/confirmatory_splits.json | [404, 808, 1420, 20261105] | [404, 808, 1420, 20261105] | **PASS** |
| D04 | §2 Methods / DSN | AraDiCE 600 calibration / 1,400 test parallel items | data/aradice_splits.json | [600, 1400] | [600, 1400] | **PASS** |
| D05 | §2 Methods / T2 | IFM filter: 935 flagged dialect rows in the resource, of which 387 fall on test keys (5–6% of test keys per dialect) | results/validity/L1_ifm_filter.csv | [387, [5.0, 6.0]] | [387, [5.0, 6.0]] | **PASS** |
| D4-01 | §3.3 / T2 | realised risk under τ_v: 0.16–0.24 over 20 cells (r*=0.20) | results/diag/D4_variety_threshold.csv | [0.16, 0.24] | [0.16, 0.24] | **PASS** |
| D4-02 | §3.3 / T2 | realised risk under τ_MSA: 0.17–0.31 over 20 cells | results/diag/D4_variety_threshold.csv | [0.17, 0.31] | [0.17, 0.31] | **PASS** |
| D4-03 | §3.3 / T2 | answered(τ_v) − answered(τ_MSA) negative with CI<0 in 17/20 | results/diag/D4_variety_threshold.csv | 17 | 17 | **PASS** |
| D4-04 | §3.3 / T2 | residual gap −0.04 to −0.34; CI<0 in 19/20 (fixed) | results/diag/D4_variety_threshold.csv | [[-0.34, -0.01], 19] | [[-0.34, -0.01], 19] | **PASS** |
| D4-05 | §3.3/§3.4 / T2 | residual gap calibration-robust in 14/20 (not Fanar EGY/UAE, Qwen3 KSA/UAE, Gemma EGY/UAE); RS widths 2.2–4.5× | results/sens/S91_calibration_sensitivity.csv | [14, ['Fanar-EGY', 'Fanar-UAE', 'Qwen3-KSA', 'Qwen3-UAE', 'gemma-EGY', 'gemma-UAE'], [2.2, 4.5]] | [14, ["Fanar-EGY", "Fanar-UAE", "Qwen3-KSA", "Qwen3-UAE", "gemma-EGY", "gemma-UAE"], [2.2, 4.5]] | **PASS** |
| D4-06 | §3.3 / T3 | cells with realised risk above 0.24 under τ_MSA: 4 (all ALLaM) → 0 under τ_v | results/sens/S94_D4_distance.csv | [4, 4, 0] | [4, 4, 0] | **PASS** |
| D4-07 | §3.3 / T3 | cells with realised risk above 0.20 under τ_MSA vs under τ_v (ceiling framing; point estimates) | results/sens/S94_D4_distance.csv | [18, 7] | [18, 7] | **PASS** |
| D4-08 | §3.3 / T2 | Qwen3–EGY: risk 0.22 → 0.17, answered 0.53 → 0.42 | results/sens/S94_D4_distance.csv | [0.22, 0.17, 0.53, 0.42] | [0.22, 0.17, 0.53, 0.42] | **PASS** |
| D4-09 | §3.3 / T3 | post-hoc observed range of realised risk under τ_v: within ±0.04 of 0.20 | results/sens/S94_D4_distance.csv | 0.04 | 0.04 | **PASS** |
| D4-10 | §3.3 (dropped in v0.3) / T3 | closer to 0.20 in 11/20 cells (distance framing; superseded by D4-06/07) | results/sens/S94_D4_distance.csv | 11 | 11 | **PASS** |
| IC-01 | §3.1/App. C / EXT | independent implementation reproduces P1 exactly; S4 (r*≤0.25) and P2 to one boundary item; per-key 39,759/39,760 (S4) and 39,755/39,760 (coverage); Fanar r*=0.30 τ 0.3757 vs 0.3790 | results/indep_check/INDEP_COMPARISON.md |  | "see INDEP_COMPARISON.md" | **report-sourced** |
| L1-01 | §3.2 / T2 | IFM filter changes every endpoint by at most 1.5 pp (1.45, ALLaM–SYR ΔP1) in all 20 cells | results/validity/L1_ifm_filter.csv | 1.45 | 1.45 | **PASS** |
| L2-01 | §3.2 / T2 | Most-similar tercile retains >=2/3 of full P1 gap: MAG 2 or 3 of 4 (row-order sensitive), SYR/EGY 3 of 4, KSA/UAE at most 1. | results/validity/L2_fidelity.csv | True | true | **PASS** |
| L4-01 | §3.2 / T2 | AraDiCE: accuracy drops 3.6–7.0 pp | results/validity/L4_aradice.csv | [3.6, 7.0] | [3.6, 7.0] | **PASS** |
| L4-02 | §3.2 / T2 | AraDiCE ΔP1: EGY −11 to −17 pp; LEV −6 to −14 pp | results/validity/L4_aradice.csv | [[-17.0, -11.0], [-14.0, -6.0]] | [[-17, -11], [-14, -6]] | **PASS** |
| L4-03 | §3.2 / T2 | AraDiCE Δcov under MSA q̂: −3 to −7 pp; set size ×1.02–1.28 | results/validity/L4_aradice.csv | [[-7.0, -3.0], [1.02, 1.28]] | [[-7, -3], [1.02, 1.28]] | **PASS** |
| L4-04 | §3.2 / T2 | AraDiCE: all intervals (Δacc, ΔP1, Δcov, Δanswered) exclude 0 | results/validity/L4_aradice.csv | 32 | 32 | **PASS** |
| P1-01 | §3.1 / T1 | MSA matched risk t50 per model | results/confirm/P1_selective.csv | [0.203, 0.149, 0.156, 0.194] | [0.203, 0.149, 0.156, 0.194] | **PASS** |
| P1-02 | Abstract/§3.1 / T1 | MAG answerable 0.26/0.29/0.23/0.32 | results/confirm/P1_selective.csv | [0.26, 0.29, 0.23, 0.32] | [0.26, 0.29, 0.23, 0.32] | **PASS** |
| P1-03 | §3.1 / Table A1 / T1 | MAG Δ −0.24 [−.31,−.17] / −0.21 [−.28,−.14] / −0.27 [−.32,−.21] / −0.18 [−.24,−.13] | results/confirm/P1_selective.csv | [-0.24, -0.31, -0.17, -0.21, -0.28, -0.14, -0.27, -0.32, -0.21, -0.18, -0.24, -0.13] | [-0.24, -0.31, -0.17, -0.21, -0.28, -0.14, -0.27, -0.32, -0.21, -0.18, -0.24, -0.13] | **PASS** |
| P1-04 | Abstract/§3.1 / T1 | MAG and SYR answerable on a quarter to a third (0.23–0.34) | results/confirm/P1_selective.csv | [0.23, 0.34] | [0.23, 0.34] | **PASS** |
| P1-05 | §3.1 / T1 | SYR answerable 0.31–0.34; Δ −0.16 to −0.19 | results/confirm/P1_selective.csv | [[0.31, 0.34], [-0.19, -0.16]] | [[0.31, 0.34], [-0.19, -0.16]] | **PASS** |
| P1-06 | §3.1 / T1 | EGY 0.35–0.41 (Δ −0.09 to −0.15); KSA 0.37–0.44 (−0.06 to −0.13); UAE 0.42–0.44 (−0.06 to −0.08) | results/confirm/P1_selective.csv | [[0.35, 0.41], [-0.15, -0.09], [0.37, 0.44], [-0.13, -0.06], [0.42, 0.44], [-0.08, -0.06]] | [[0.35, 0.41], [-0.15, -0.09], [0.37, 0.44], [-0.13, -0.06], [0.42, 0.44], [-0.08, -0.06]] | **PASS** |
| P1-07 | §3.1 / T1 | all 20 P1 intervals exclude 0 | results/confirm/P1_selective.csv | 20 | 20 | **PASS** |
| P1-08 | §2.6 / Table A1 / T1 | MSA P1 is ≈0.50, not exactly: 0.5007/0.5000/0.5014/0.5014 | results/confirm/P1_selective.csv | [0.5007, 0.5, 0.5014, 0.5014] | [0.5007, 0.5, 0.5014, 0.5014] | **PASS** |
| P2-01 | Abstract/§3.1 / T1 | coverage under MSA q̂ falls 8/11/13/8 pp (MAG) at α=0.30 | results/confirm/P2_conformal.csv | [-8.0, -10.0, -13.0, -8.0] | [-8, -10, -13, -8] | **PASS** |
| P2-02 | §3.1 / T1 | coverage falls 6/8/6/9 pp (SYR); other dialects 3–5 pp | results/confirm/P2_conformal.csv | [[-6.0, -8.0, -6.0, -9.0], [-5.0, -3.0]] | [[-6, -8, -6, -9], [-5, -3]] | **PASS** |
| P2-03 | Abstract/§3.1 / T1 | MAG+SYR coverage loss range 6–13 pp | results/confirm/P2_conformal.csv | [6.0, 13.0] | [6, 13] | **PASS** |
| P2-04 | Abstract/§3.1 / T1 | own-q̂ set-size ratio MAG ×1.17/1.25/1.32/1.21; SYR ×1.18–1.23; Gulf ×1.08–1.17 | results/confirm/P2_conformal.csv | [[1.17, 1.25, 1.32, 1.21], [1.18, 1.23], [1.08, 1.17]] | [[1.17, 1.25, 1.32, 1.21], [1.18, 1.23], [1.08, 1.17]] | **PASS** |
| P2-05 | Abstract / T1 | sets 17–32% larger (MAG and SYR, α=0.30) | results/confirm/P2_conformal.csv | [17.0, 32.0] | [17, 32] | **PASS** |
| P2-06 | §3.1/§3.4 / T2 | size-ratio RS intervals 2.7–4.3× wider; all 20 still exclude 1 | results/sens/S91_calibration_sensitivity.csv | [[2.7, 4.3], 20] | [[2.7, 4.3], 20] | **PASS** |
| P2-07 | §3.1 / T2 | Δcov RS intervals 20/20 exclude 0; widths 1.00–1.30× | results/sens/S91_calibration_sensitivity.csv | [20, [1.0, 1.3]] | [20, [1.0, 1.3]] | **PASS** |
| P2-08 | §3.1 / T1 | at α=0.10 coverage differences are ≤1.7 pp and 19 of 20 intervals include 0 | results/confirm/P2_conformal.csv | [1, 1.7] | [1, 1.7] | **PASS** |
| P2-09 | §3.1 / T1 | own-threshold coverage ALLaM–MAG 0.657 (lowest), target 0.70 | results/confirm/P2_conformal.csv | 0.657 | 0.657 | **PASS** |
| RB-01 | §3.4 / T2 | re-scoring the original order reproduces the confirmatory prediction in 98–99% of cells; 0.9–2.0% differ | results/sens/S92_reproducibility.csv | [0.9, 2.0] | [0.9, 2.0] | **PASS** |
| RB-02 | §3.4 / T2 | median top-two margin among disagreeing cells ≤0.13 nats vs 0.5–1.75 overall; 43–52% of them below 0.05 nats | results/sens/S92_reproducibility.csv | [0.12, [0.5, 1.75], [43.0, 52.0]] | [0.13, [0.5, 1.75], [43, 52]] | **PASS** |
| RB-03 | §3.4 / T2 | gap estimates from the two runs differ by ≤0.03 (Δacc, ΔP1, S4 Δanswered) | results/sens/S92_reproducibility.csv | 0.03 | 0.03 | **PASS** |
| RB-04 | §3.4 / T2 | Δacc and ΔP1 order-robust (sign in all 4 orderings; averaged CI excludes 0) in 20/20 cells each | results/robust/R2_gap_stability.csv | [20, 20] | [20, 20] | **PASS** |
| RB-05 | §3.4 / T2 | order-averaged ΔP1 (ALLaM/Fanar/Qwen3/Gemma): MAG −0.21/−0.22/−0.25/−0.24; SYR −0.19/−0.20/−0.20/−0.25 | results/robust/R2_gap_stability.csv | [[-0.21, -0.22, -0.25, -0.24], [-0.19, -0.2, -0.19, -0.25]] | [[-0.21, -0.22, -0.25, -0.24], [-0.19, -0.2, -0.19, -0.25]] | **PASS** |
| RB-06 | §3.4 / T2 | order-averaged ΔP1 ranges: EGY −0.13 to −0.15; KSA −0.10 to −0.15; UAE −0.08 to −0.13 | results/robust/R2_gap_stability.csv | [[-0.15, -0.13], [-0.15, -0.1], [-0.13, -0.08]] | [[-0.15, -0.13], [-0.15, -0.1], [-0.13, -0.08]] | **PASS** |
| RB-07 | §3.4 / T2 | S4 Δanswered at the original τ_MSA, order-averaged, excludes 0 in 20/20 | results/robust/R3_s4_by_order.csv | 20 | 20 | **PASS** |
| RB-08 | §3.4 / T2 | order-averaged S4 Δanswered calibration-robust in 19/20 (ALLaM–UAE borderline) | results/sens/S91_rotation_sensitivity.csv | [19, ['ALLaM-UAE']] | [19, ["ALLaM-UAE"]] | **PASS** |
| RB-09 | §3.4 / T2 | OSR MSA 0.43/0.45/0.45/0.58; MAG 0.51/0.61/0.57/0.72; SYR 0.52/0.58/0.52/0.70 (ALLaM/Fanar/Qwen3/Gemma) | results/robust/R1_order_sensitivity.csv | [[0.43, 0.45, 0.45, 0.58], [0.51, 0.61, 0.57, 0.72], [0.52, 0.58, 0.52, 0.7]] | [[0.43, 0.45, 0.45, 0.58], [0.51, 0.61, 0.57, 0.72], [0.52, 0.58, 0.52, 0.7]] | **PASS** |
| RB-10 | §3.4 / T2 | ΔOSR vs MSA excludes 0: MAG, SYR, EGY 4/4; KSA 3/4; UAE 1/4; ENG lower than MSA in 4/4 | results/robust/R1_order_sensitivity.csv | [4, 4, 4, 3, 1, 4] | [4, 4, 4, 3, 1, 4] | **PASS** |
| RB-11 | App. D / W | P3 answer change vs MSA 20–34% (dialects, test); within-variety one-rotation change 24–48%; MSA alone 27–38% | results/confirm/P3_churn.csv | [20.0, 34.0] | [20, 34] | **PASS** |
| RB-12 | App. D / W | within-variety one-rotation change 24–48%; MSA 27–38% | results/robust/R4_p3_decomposition.csv | [[24.0, 48.0], [27.0, 38.0]] | [[24, 48], [27, 38]] | **PASS** |
| RB-13 | App. D / T2 | paired D = (dialect-vs-MSA change) − (within-variety rotation change): CI<0 in 15/20, includes 0 in 5, >0 in 0 | results/sens/S93_R4_paired.csv | [15, 5, 0] | [15, 5, 0] | **PASS** |
| RB-14 | App. D / T2 | against MSA’s own rotation change (D′) larger only for ALLaM MAG +0.06 [+0.01,+0.11] and SYR +0.05 [+0.00,+0.10] | results/sens/S93_R4_paired.csv | [['ALLaM-MAG', 'ALLaM-SYR'], [0.06, 0.05]] | [["ALLaM-MAG", "ALLaM-SYR"], [0.06, 0.05]] | **PASS** |
| RB-15 | §3.4 / T2 | G1 agreement with letter-logit choice: ALLaM 97–100%, Fanar 94–97%, Qwen3 94–96%, Gemma 90–97%; unextractable ≤0.8% | results/robust/R5_generation.csv | [[97.0, 100.0], [94.0, 97.0], [94.0, 96.0], [90.0, 97.0], 0.8] | [[97, 100], [94, 97], [94, 96], [90, 97], 0.8] | **PASS** |
| RB-16 | §3.4 / T2 | G1 generated accuracy within 0.012 of letter-logit accuracy in every cell | results/robust/R5_generation.csv | 0.014 | 0.014 | **PASS** |
| RB-17 | §3.4 / T2 | G2 (ALLaM chat template): unextractable ≤0.4%; generated = first-token argmax 99–100%; agreement with raw-prompt choice 82–92%; generated accuracy 0.53–0.66 | results/robust/R5_generation.csv | [0.4, [99.0, 100.0], [82.0, 92.0], [0.53, 0.66]] | [0.4, [99, 100], [82, 92], [0.53, 0.66]] | **PASS** |
| RB-18 | §3.4 / T2 | on items accepted by τ_MSA the generated letter equals the logit choice in 27/28 cells; exception Fanar–ENG −0.003 [−0.008, +0.000] | results/supp/S102_gen_selective_risk.csv | [27, ['Fanar-ENG'], [-0.003, -0.008, 0.0]] | [27, ["Fanar-ENG"], [-0.003, -0.008, 0.0]] | **PASS** |
| RB-19 | §3.4 / T2 | S4 and Δcov RS interval widths 0.95–1.4× the fixed-calibration widths | results/sens/S91_calibration_sensitivity.csv | [0.95, 1.42] | [0.95, 1.42] | **PASS** |
| S2-01 | §3.1 / T1 | MAG coverage msa_only 0.61/0.59/0.57/0.62 → pooled 0.64/0.64/0.62/0.66 → text 0.63/0.66/0.66/0.68 → oracle 0.66/0.69/0.69/0.69 (α=0.30) | results/confirm/S2_variety_aware.csv | [[0.61, 0.59, 0.57, 0.62], [0.64, 0.64, 0.62, 0.65], [0.63, 0.66, 0.66, 0.68], [0.66, 0.69, 0.69, 0.69]] | [[0.61, 0.59, 0.57, 0.62], [0.64, 0.64, 0.62, 0.65], [0.63, 0.66, 0.66, 0.68], [0.66, 0.69, 0.69, 0.69]] | **PASS** |
| S2-02 | §3.1 / T1 | MAG mean set size 1.36/1.17/1.14/1.44 (msa_only) → 1.53/1.54/1.56/1.72 (oracle) | results/confirm/S2_variety_aware.csv | [[1.36, 1.17, 1.14, 1.44], [1.53, 1.54, 1.56, 1.72]] | [[1.36, 1.17, 1.14, 1.44], [1.53, 1.54, 1.56, 1.72]] | **PASS** |
| S2-03 | §3.1 / T1 | text classifier recovers 51/69/81/88% of the oracle gain (MAG) | results/confirm/S2_variety_aware.csv | [51.0, 68.0, 81.0, 88.0] | [51, 69, 81, 88] | **PASS** |
| S2-04 | §3.1 / T1 | ALLaM–MAG stays below target with the true label (0.657) | results/confirm/S2_variety_aware.csv | 0.657 | 0.657 | **PASS** |
| S4-01 | Abstract/§3.1 / T1b | MSA answered fraction 0.52/0.56/0.59/0.47 at r*=0.20 | results/confirm/S4_operational_selective.csv | [0.52, 0.56, 0.59, 0.47] | [0.52, 0.56, 0.59, 0.47] | **PASS** |
| S4-02 | §3.1 / T1b | MSA realised risk 0.21/0.19/0.20/0.18 | results/confirm/S4_operational_selective.csv | [0.21, 0.19, 0.2, 0.18] | [0.21, 0.19, 0.2, 0.18] | **PASS** |
| S4-03-EGY | §3.1 table / T1b | Δ answered vs MSA, EGY: [-0.04, -0.08, -0.06, -0.07] | results/confirm/S4_operational_selective.csv | [-0.04, -0.08, -0.06, -0.07] | [-0.04, -0.08, -0.06, -0.07] | **PASS** |
| S4-03-KSA | §3.1 table / T1b | Δ answered vs MSA, KSA: [-0.05, -0.07, -0.07, -0.07] | results/confirm/S4_operational_selective.csv | [-0.05, -0.07, -0.07, -0.07] | [-0.05, -0.07, -0.07, -0.07] | **PASS** |
| S4-03-MAG | §3.1 table / T1b | Δ answered vs MSA, MAG: [-0.11, -0.15, -0.21, -0.18] | results/confirm/S4_operational_selective.csv | [-0.11, -0.15, -0.21, -0.18] | [-0.11, -0.15, -0.21, -0.18] | **PASS** |
| S4-03-SYR | §3.1 table / T1b | Δ answered vs MSA, SYR: [-0.05, -0.13, -0.12, -0.12] | results/confirm/S4_operational_selective.csv | [-0.05, -0.13, -0.12, -0.12] | [-0.05, -0.13, -0.12, -0.12] | **PASS** |
| S4-03-UAE | §3.1 table / T1b | Δ answered vs MSA, UAE: [-0.01, -0.05, -0.05, -0.03] | results/confirm/S4_operational_selective.csv | [-0.01, -0.05, -0.05, -0.03] | [-0.01, -0.05, -0.05, -0.03] | **PASS** |
| S4-04-EGY | §3.1 table / T1b | realised risk for the dialect user, EGY: [0.25, 0.21, 0.22, 0.22] | results/confirm/S4_operational_selective.csv | [0.25, 0.21, 0.22, 0.22] | [0.25, 0.21, 0.22, 0.22] | **PASS** |
| S4-04-KSA | §3.1 table / T1b | realised risk for the dialect user, KSA: [0.24, 0.22, 0.2, 0.21] | results/confirm/S4_operational_selective.csv | [0.24, 0.22, 0.2, 0.21] | [0.24, 0.22, 0.2, 0.21] | **PASS** |
| S4-04-MAG | §3.1 table / T1b | realised risk for the dialect user, MAG: [0.28, 0.21, 0.24, 0.17] | results/confirm/S4_operational_selective.csv | [0.28, 0.21, 0.24, 0.17] | [0.28, 0.21, 0.24, 0.17] | **PASS** |
| S4-04-SYR | §3.1 table / T1b | realised risk for the dialect user, SYR: [0.31, 0.23, 0.23, 0.22] | results/confirm/S4_operational_selective.csv | [0.31, 0.23, 0.23, 0.22] | [0.31, 0.23, 0.23, 0.22] | **PASS** |
| S4-04-UAE | §3.1 table / T1b | realised risk for the dialect user, UAE: [0.26, 0.2, 0.21, 0.19] | results/confirm/S4_operational_selective.csv | [0.26, 0.2, 0.21, 0.19] | [0.26, 0.2, 0.21, 0.19] | **PASS** |
| S4-05 | Abstract/§3.1 / T1b | answers fewer dialect questions in every model (point estimates <0 in 20/20) | results/confirm/S4_operational_selective.csv | 20 | 20 | **PASS** |
| S4-06 | §3.1 / T1b | Δanswered CI excludes 0 in 19/20 cells; exception ALLaM–UAE | results/confirm/S4_operational_selective.csv | [19, ['ALLaM-UAE']] | [19, ["ALLaM-UAE"]] | **PASS** |
| S4-07 | §3.1 / T2 | Δanswered calibration-robust in 19/20 under double resampling (same cell) | results/sens/S91_calibration_sensitivity.csv | [19, ['ALLaM-UAE']] | [19, ["ALLaM-UAE"]] | **PASS** |
| S4-08 | §3.1 / T2 | Δrisk vs MSA: MAG ALLaM +6.7 [+3.3,+10.3], Qwen3 +3.5 [+0.2,+6.8] (pp) | results/supp/S101_risk_diff.csv | [6.7, 3.1, 10.1, 3.5, 0.3, 7.0] | [6.7, 3.1, 10.1, 3.5, 0.3, 7.0] | **PASS** |
| S4-09 | §3.1 / T2 | Δrisk vs MSA, SYR: +9.3/+3.7/+3.1/+4.2 pp, all CIs exclude 0 | results/supp/S101_risk_diff.csv | [[9.3, 3.7, 3.1, 4.2], 4] | [[9.3, 3.7, 3.1, 4.2], 4] | **PASS** |
| S4-10 | Abstract/§1/§3.1 / T2 | risk higher than MSA (fixed-cal CI excludes 0): SYR 4/4, MAG 2/4 (ALLaM, Qwen3), EGY 2/4, KSA 1/4, UAE 1/4 | results/supp/S101_risk_diff.csv | [4, 2, 2, 1, 1] | [4, 2, 2, 1, 1] | **PASS** |
| S4-11 | §1/§3.1 / T2 | under double resampling: SYR 3/4 (Gemma drops), MAG 2/4 | results/supp/S101_risk_diff.csv | [3, 2, ['gemma']] | [3, 2, ["gemma"]] | **PASS** |
| S4-12 | §3.1 / T2 | point estimates above 0.20 in 18/20 dialect cells; Qwen3–KSA by 0.0003 | results/supp/S101_risk_diff.csv | [18, 0.0003] | [18, 0.0003] | **PASS** |
| S4-13 | Abstract/§1/§3.1 / T2 | exceeds 0.20 with confidence (fixed-cal lower bound >0.20): ALLaM’s five dialects only; range 0.24–0.31 | results/supp/S101_risk_diff.csv | [5, 5, [0.24, 0.31]] | [5, 5, [0.24, 0.31]] | **PASS** |
| S4-14 | §3.1 / T2 | under double resampling only ALLaM–MAG and ALLaM–SYR exceed 0.20 with confidence | results/supp/S101_risk_diff.csv | ['ALLaM-MAG', 'ALLaM-SYR'] | ["ALLaM-MAG", "ALLaM-SYR"] | **PASS** |
| S4-15 | §3.1 / T1b | MSA realised risk is itself above 0.20 for ALLaM (0.21) and at 0.20 for Qwen3 — point estimates | results/confirm/S4_operational_selective.csv | [0.213, 0.191, 0.2, 0.176] | [0.213, 0.191, 0.2, 0.176] | **PASS** |
