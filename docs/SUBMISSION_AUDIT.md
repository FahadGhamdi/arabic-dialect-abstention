# Submission reproducibility audit — v1.0

Source inspected directly: https://github.com/FahadGhamdi/arabic-dialect-abstention, commit `8e103a0dacb7762e2f4f3ba47ad48a81eb602102`.

## Findings and repairs

1. The cited commit lacked second-session/adjudication ratings and the cited screen-analysis script. The author-supplied original workbook was read without alteration. Text-free exports, standalone agreement/rate calculations and reconstructed association/sensitivity code are now included. No question text, options, notes or adjudication explanations from the workbook are redistributed.
2. All four agreement values reproduce: kappa 0.86, 0.36, 0.90 and 0.00; observed agreement 0.933, 0.707, 0.953 and 0.980; disagreements 10, 44, 7 and 3. All 1,600 binary screening flags (400 pairs × four flag definitions) match the previously published flags. This checks consistency of model screening sessions, not human equivalence judgments.
3. The missing historical interactive code was reconstructed from the documented quantities. All 80 sensitivity rows reproduce their five point estimates to floating-point precision. New percentile intervals use 2,000 replicates, seed 0, sorted question keys, with key-level clustering. The historical seed was not recorded. The paper now uses these explicit-seed screen intervals, and the original report remains archived. The overall basic-flag interval is 0.31–0.43; development is 0.25–0.40. The basic-flag accuracy association is −1.8 [−8.2, +5.1] percentage points and answer-change association +0.8 [−6.2, +7.9].
4. The README named scripts that did not create the required `damm.csv`. A new pinned, checksum-checked data-preparation script reconstructs it from the publisher snapshot and matches every key, dialect, answer and domain against the text-free skeleton. The current S2 and G2 outputs reproduce the published tables. The reconstruction does not establish an unrecorded historical inference revision.
5. The historical checksum manifest has 15 missing paths and 2 stale hashes. A complete manifest for this release replaces it; the old manifest is retained under `docs/historical/`.
6. The independent recomputation script had an absolute project root, and L2 expected an undocumented pickle of the published flags. The isolated replay supplies that equivalent input and records the path/report adaptations. The original scripts remain unchanged.
7. The manuscript source now includes its promised `tools/`, table generator and file index. All ten supplied MDPI template files are unchanged. No model weights, source question texts or private workbook are included.

The exploratory ALLaM–MAG calibration-resampling range 0.63–0.70 was quoted only in a historical summary; the script, seed and exact resampling convention were not saved. This numerical illustration and its current ledger row S2-05 were removed from the submission. The observed own-variety coverage 0.657 is reproducible and remains. The historical summary and ledger are preserved.

## Executed checks

- 16 stored-score files; 167,696 records. No duplicate scoring identities; correctness equals prediction-versus-answer comparison. Probability reconstruction agrees within 0.0001, consistent with stored rounding. Split sizes 404/808/1,420 are disjoint and exclude the 500 development and three demonstration keys.
- Seven numerical programs, including the independent check, were run in an isolated release copy. The replay records exact statuses in `REPLAY_RUN.json`; no inference was run. NumPy/pandas/SciPy/PyArrow versions are recorded in `SUBMISSION_ENVIRONMENT.json`.
- The current ledger passes 105 computable rows with zero failures; two rows remain source/report-derived. A separate check also reproduces the independent-report per-key agreements: 39,759/39,760 accepted decisions and 39,755/39,760 set-coverage decisions. Ledger agreement is a consistency check, not independent provenance evidence.
- S4 and P2 tables, P1 point estimates, S2, and primary-target D4 results reproduce. Differences in other outputs are listed below, and the recomputed CSVs are provided under `verification_outputs/`.

| Result file | Rows | Maximum absolute numeric difference | Columns differing above 1e-12 |
|---|---:|---:|---|
| results/confirm/P1_selective.csv | 28 | 0.00070422535 | d_answerable, d_lo, d_hi, aurc, d_aurc, d_aurc_lo, d_aurc_hi |
| results/confirm/P2_conformal.csv | 224 | 0 | none |
| results/confirm/P3_churn.csv | 28 | 0 | none |
| results/confirm/S1_calib_efficiency.csv | 196 | 0 | none |
| results/confirm/S2_variety_aware.csv | 280 | 0 | none |
| results/confirm/S3_calibration.csv | 28 | 0 | none |
| results/confirm/S4_operational_selective.csv | 112 | 0 | none |
| results/diag/D1_D2_discrimination.csv | 28 | 0 | none |
| results/diag/D4_variety_threshold.csv | 112 | 0.0195039 | tau_v, answered_v_thr, ans_lo, ans_hi, realised_risk_v_thr, risk_lo, risk_hi, recoverable, rec_lo, rec_hi, residual_gap, res_lo, res_hi |
| results/robust/R1_order_sensitivity.csv | 28 | 0 | none |
| results/robust/R2_gap_stability.csv | 24 | 0 | none |
| results/robust/R3_s4_by_order.csv | 24 | 0 | none |
| results/robust/R4_p3_decomposition.csv | 28 | 0 | none |
| results/robust/R5_generation.csv | 35 | 0 | none |
| results/sens/S91_calibration_sensitivity.csv | 24 | 0.013513514 | s4_d_ans_rs, s4_lo_rs, s4_width_ratio, risk_rs, d4_res_rs, d4_res_hi_rs, d4_riskv_rs, d4_riskv_hi_rs, d4_rec_rs, d4_rec_lo_rs, d4_rec_hi_rs, tau_v_median |
| results/sens/S91_rotation_sensitivity.csv | 24 | 3.05e-05 | d_ans_avg_rs, lo_rs |
| results/sens/S92_reproducibility.csv | 24 | 0.004 | d_p1_confirm |
| results/sens/S93_R4_paired.csv | 24 | 0 | none |
| results/sens/S94_D4_distance.csv | 20 | 0 | none |
| results/supp/S101_risk_diff.csv | 28 | 0.00087420814 | d_risk_rs, d_risk_rs_lo, d_risk_rs_hi, risk_rs_lo |
| results/supp/S102_gen_selective_risk.csv | 28 | 0 | none |
| results/validity/L1_ifm_filter.csv | 20 | 0.002238806 | dp1_lo, dp1_hi, kept_dp1_lo, kept_dp1_hi |
| results/validity/L2_fidelity.csv | 80 | 1 | n, sim_mean, dacc, dacc_lo, dacc_hi, chg, chg_lo, chg_hi, dp1, dp1_lo, dp1_hi, dcov, dcov_lo, dcov_hi, dans, dans_lo, dans_hi |
| results/validity/L4_aradice.csv | 8 | 0.0035535714 | dacc_lo, dacc_hi, chg_lo, chg_hi, dp1_lo, dp1_hi, dcov_lo, dcov_hi, dans_lo, dans_hi |

The largest D4 difference occurs for Qwen3–SYR at secondary target 0.15: realised risk 0.16336 in the archive versus 0.14385 in this replay; the 0.20 target used in the manuscript is unchanged. L2 uses row-order tie breaking for similarity terciles, which can move one item and alter interval bounds. The MAG count retaining at least two thirds of the full P1 gap is 3/4 in the archive and 2/4 in the current replay; SYR and EGY remain 3/4, and KSA/UAE remain 1/4. The manuscript now states the MAG count as two or three depending on tie breaking. Default confidence sorting and stored rounding also affect some resampled statistics. These differences are disclosed rather than overwritten or described as exact replication.

## What was not verified

- Historical inference was not rerun, and immutable model revisions/full original software lock are unavailable. Internal consistency cannot authenticate historical execution or rule out every possible source of error.
- The original Matplotlib figure-generation path was not newly executed because its dependencies are absent in this audit environment; no packages were installed. Figure inputs and source code are included; final PDFs were inspected, and A3 was rebuilt with the included TeX generator.
- The source workbook is author-supplied, and model screening judgments are not independently validated human labels.
- The historical GitHub commit lacks the new submission files. This companion adds those files while preserving the original score archive and reporting history.

## Historical manifest discrepancies

Missing paths: `paper/latex/main.aux`, `paper/latex/main.bbl`, `paper/latex/main.blg`, `paper/latex/main.fdb_latexmk`, `paper/latex/main.fls`, `paper/latex/main.log`, `paper/latex/main.out`, `paper/latex/main.pdf`, `paper/latex/main.tex`, `paper/latex/references.bib`, `paper/manuscript_v0.3.md`, `paper/manuscript_v0.4.md`, `paper/manuscript_v0.5.md`, `paper/references.bib`, `results/robust_interim_4models_scoring/run.log`.

Stale hashes: `PILOT_NOTES.md`, `README.md`.
