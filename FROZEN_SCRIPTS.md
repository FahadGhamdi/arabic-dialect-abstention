# Frozen scripts and their sha256 (computed at release build, 2026-11-08 09:49 UTC)

| script | role | sha256 |
|---|---|---|
| scripts/confirm_analyze.py | confirmatory analysis (P1, P2, P3, S1, S2, S3, S4); fixed during score collection, before any confirmatory file was opened | 8ade05cd05df4c573c1f8e61ff63d62edc20ee7be13310b87f5b44ea89a2e4bc |
| scripts/confirm_analyze_v1_frozen.py | v1 of the above (before S4 was added) | d1b3396d1c34530df5a344cbc56434e0bb06ff64ff388da1b2b89607e8d13e01 |
| scripts/validity_analyze.py | automatic validity layers L1, L2, L4 (Addendum 4) | 2ec539c64b570514e7fe8cfbd44fa6eaf9d0eda36918c4a6445d09ad84bed410 |
| scripts/diag_analyze.py | diagnostic views (Addendum 7): discrimination, D4 threshold re-selection | 44acd4a251ee36f67ac7fd309a52b1977bd12666ecc5a09909255d86774ff8e8 |
| scripts/diag_analyze_v1_frozen.py | v1 of the above | 9337bf5b9b2b83be0f764a56f22103fb01f59c2c96e9d6a7f5212190893fc7f9 |
| scripts/s12_robustness.py | robustness scoring (Addendum 8): rotations and generation | 5306e881969ee1c5eab067af3dd438fac3adf3504d61e38d595a4dfd77d8df9b |
| scripts/robust_analyze.py | robustness analysis R1–R5 (Addendum 8) | 61fdd211a88e9063722ce575c708d504645844bfebb72746fc17ff3a2848b829 |
| scripts/sens_analyze.py | verification package (Addendum 9): double resampling, reproducibility, paired rotation comparison, distance table | 3973de301651a08a19eb5b0e968742655e0a43f36d6eb5b87439ac6ab944584b |
| scripts/indep_check/recompute.py | independent implementation of P1/S4/P2 from docs/METRIC_DEFINITIONS.md (Addendum 9 §9.5) | 4d69b8f21f6e2d07993dc75b00207004c34509a6eba670aace79142cddeecdd0 |
| scripts/supp_analyze.py | supplements (Addendum 10): risk differences and exceedance; generated-answer selective risk | 9d737d2020db161b62da7c3b531af045cd20ef599173871abbf1ceca545f5492 |
| scripts/make_figures.py | figures from the result files (no estimates) | 09cd071dc30e1e1cfd89dcf2a4f91d9cd6088a828389360d6f4bb96ac3f12b26 |
| scripts/build_ledger.py | authoring source of docs/CLAIMS_LEDGER.csv | 983fd4b35ec7cdb2474dd7535025f0a9f725e152e6ae55905a25d4bcf70f20b1 |
| scripts/check_ledger.py | consistency audit of the ledger against the result files | d1acdbc532a19ef348a303b3b6dda0b46b30c6b84f42b4120609257a2cf6ce9d |
| scripts/s9_score_confirm.py | confirmatory scoring of the four models (prompt, letter log-probabilities) | 44dbf0046c9c55d3850cba7ff4fd80875d3ec761dd3144211c7315e08acd78bf |
| scripts/s11_aradice_score.py | AraDiCE scoring | 6040a71e2efce0f0d7aa6bdf5062625226bc5b860647c5fe7cba95d1a79af04a |
| scripts/s10_fidelity.py | embedding similarity (multilingual-e5-large) for L2 | e62cb507e6f2330b3558b7b8263903f7fc746485f5f94a8be9f1f00dfe8d65c7 |
| scripts/prompts.py | the prompt templates | c2af9b2485a7d332bb2e1d4a8cbcf2a0970cddb3ea1733178e7c7bf75d08b9cf |
