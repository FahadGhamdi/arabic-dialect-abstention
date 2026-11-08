# Clean-folder reproduction check

Shipped package: `release`; reproduction folder: a fresh copy of the package with `data/damm.csv` added (the dataset texts are not
redistributed; see RELEASE_NOTES) and `audit_in/flags.pkl` (the screen flags in the pickled form `validity_analyze.py` reads; the same flags as
`audit/screen_flags_400.csv`). The sequence in README.md was run with `python3 -I`; no model was run. `scripts/indep_check/recompute.py` carries an
absolute project root; the copy run here had only that constant changed (diff: one line).

Files compared: 57; identical or numerically equal: 51.

Ledger audit inside the reproduction: Rows: 104 — PASS 95, FAIL/ERROR 0, report-sourced (not recomputed) 9.

| file | status | detail | |
|---|---|---|---|
| results/confirm/CONFIRM_REPORT.md | IDENTICAL |  |  |
| results/confirm/CONFIRM_SUMMARY.md | IDENTICAL |  |  |
| results/confirm/P1_selective.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/confirm/P2_conformal.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/confirm/P3_churn.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/confirm/S1_calib_efficiency.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/confirm/S2_variety_aware.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/confirm/S3_calibration.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/confirm/S4_operational_selective.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/validity/L1_ifm_filter.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/validity/L2_fidelity.csv | DIFFERS | max |Δ| = 1.00e+00 |  |
| results/validity/L4_aradice.csv | DIFFERS | max |Δ| = 3.55e-03 |  |
| results/validity/VALIDITY_L1.md | IDENTICAL |  |  |
| results/validity/VALIDITY_L2.md | IDENTICAL |  |  |
| results/validity/VALIDITY_L2_reading.md | IDENTICAL |  |  |
| results/validity/VALIDITY_L4.md | IDENTICAL |  |  |
| results/validity/VALIDITY_SUMMARY.md | IDENTICAL |  |  |
| results/diag/D1_D2_discrimination.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/diag/D4_variety_threshold.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/diag/DIAG_REPORT.md | IDENTICAL |  |  |
| results/diag/DIAG_SUMMARY.md | IDENTICAL |  |  |
| results/diag/diag_figure.pdf | TEXT DIFFERS | 1 line(s) differ (run timestamps/paths are expected to differ) |  |
| results/diag/diag_figure.png | IDENTICAL |  |  |
| results/robust/R1_order_sensitivity.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/robust/R2_gap_stability.csv | DIFFERS | max |Δ| = 6.00e-03 |  |
| results/robust/R3_s4_by_order.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/robust/R4_p3_decomposition.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/robust/R5_generation.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/robust/ROBUST_REPORT.md | TEXT DIFFERS | 4 line(s) differ (run timestamps/paths are expected to differ) |  |
| results/robust/ROBUST_SUMMARY.md | IDENTICAL |  |  |
| results/sens/S91_calibration_sensitivity.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/sens/S91_rotation_sensitivity.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/sens/S92_reproducibility.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/sens/S93_R4_paired.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/sens/S94_D4_distance.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/sens/SENS_REPORT.md | IDENTICAL |  |  |
| results/sens/SENS_SUMMARY.md | IDENTICAL |  |  |
| results/supp/S101_risk_diff.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/supp/S102_gen_selective_risk.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/supp/SUPP_REPORT.md | IDENTICAL |  |  |
| results/indep_check/INDEP_COMPARISON.md | IDENTICAL |  |  |
| results/indep_check/INDEP_NOTES.md | IDENTICAL |  |  |
| results/indep_check/P1_indep.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/P1_msa_curve_indep.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/P2_indep.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/S4_indep.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/perkey_ALLaM-7B-Instruct-preview.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/perkey_Fanar-1-9B.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/perkey_Qwen3-8B-Base.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| results/indep_check/perkey_gemma-2-9b.csv | IDENTICAL | max |Δ| = 0.00e+00 |  |
| figures/fig1_s4_transfer.png | IDENTICAL | 0.000% pixels differ |  |
| figures/fig2_d4_adaptation.png | IDENTICAL | 0.000% pixels differ |  |
| figures/fig3_p2_conformal.png | IDENTICAL | 0.000% pixels differ |  |
| figures/figA_risk_coverage.png | IDENTICAL | 0.000% pixels differ |  |
| figures/figB_rotations.png | DIFFERS | 0.021% pixels differ |  |
| figures/figC_interval_widths.png | IDENTICAL | 0.000% pixels differ |  |
| figures/figP1_matched_risk.png | IDENTICAL | 0.000% pixels differ |  |

## Files that differ

- `results/validity/L2_fidelity.csv`: DIFFERS — max |Δ| = 1.00e+00 
- `results/validity/L4_aradice.csv`: DIFFERS — max |Δ| = 3.55e-03 
- `results/diag/diag_figure.pdf`: TEXT DIFFERS — 1 line(s) differ (run timestamps/paths are expected to differ) 
- `results/robust/R2_gap_stability.csv`: DIFFERS — max |Δ| = 6.00e-03 
- `results/robust/ROBUST_REPORT.md`: TEXT DIFFERS — 4 line(s) differ (run timestamps/paths are expected to differ) 
- `figures/figB_rotations.png`: DIFFERS — 0.021% pixels differ 

## Reading of the differences (8 November 2026, clean folder, Python 3.13, pandas 2.x, numpy 2.x; the shipped files were produced partly on the author's Mac)

- `results/confirm/*`, `results/diag/*.csv`, `results/sens/*`, `results/supp/*`, `results/indep_check/*` and `results/robust/R1, R3, R4, R5` reproduce
  **byte-identically**; `results/validity/L1_ifm_filter.csv` and `VALIDITY_L1.md` likewise. All main figures reproduce pixel-identically.
- `results/validity/L2_fidelity.csv`: the within-dialect terciles are formed with `rank(method="first")`, which breaks ties in similarity by row order;
  the row order after the merge differs between pandas versions, so one item moved between terciles in 40 of 80 cells (`n` differs by 1), moving the
  tercile estimates by ≤ 0.013 and their bootstrap bounds by ≤ 0.042. The manuscript's L2 statement (ledger row L2-01: ≥ 2/3 of the full-sample ΔP1
  retained in the most-similar tercile for MAG/SYR/EGY in 3 of 4 models, KSA/UAE in ≤ 1) holds on both versions.
- `results/validity/L4_aradice.csv`: point ΔP1 differs by ≤ 0.0029 in 3 of 8 rows and the bootstrap bounds by ≤ 0.0036; this is the order of
  tied `p_max` values under a non-stable sort (4 items of 1,400). Every reported AraDiCE number (ledger rows L4-01…L4-04) is unchanged at the
  reported precision.
- `results/robust/R2_gap_stability.csv`: the same tie-order effect in one rotation (k = 3) moves two ΔP1 point values by ≤ 0.006 (3 items of 500)
  and the order-averaged values by ≤ 0.0015; the reported order-averaged ΔP1 values (ledger rows RB-05/RB-06) are unchanged at two decimals, and
  `ROBUST_REPORT.md` differs in the corresponding 4 lines only. `figures/figB_rotations.png` differs in 0.02% of pixels for the same reason.
- `results/diag/diag_figure.pdf` differs only in the PDF creation timestamp.
- The ledger consistency audit run inside the reproduction passes all 95 recomputed rows.

Consequence for a future version: use a stable sort (`kind="mergesort"`) wherever items are ordered by confidence, and fix the row order before
`rank(method="first")`; the frozen scripts are left as they ran, and the effect is documented here and in RELEASE_NOTES.md.
