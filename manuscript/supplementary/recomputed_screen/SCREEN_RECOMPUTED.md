# Recomputed model-assisted screen

Computed from text-free categorical ratings. Seed 0; 2000 bootstrap replicates, clustered by question key. Original interactive-run confidence intervals are retained in the frozen historical report; the intervals below use an explicit seed.

| dialect | basic defect (Q1 or Q2 = no) | Q2 = no | Q3 = no | strict |
|---|---|---|---|---|
| UAE | 0.44 [0.33, 0.55] | 0.06 [0.01, 0.12] | 0.41 [0.31, 0.53] | 0.60 [0.49, 0.70] |
| EGY | 0.33 [0.23, 0.42] | 0.01 [0.00, 0.04] | 0.31 [0.21, 0.41] | 0.49 [0.38, 0.60] |
| KSA | 0.34 [0.24, 0.45] | 0.10 [0.04, 0.17] | 0.33 [0.23, 0.42] | 0.54 [0.42, 0.65] |
| SYR | 0.40 [0.29, 0.51] | 0.06 [0.01, 0.12] | 0.33 [0.23, 0.42] | 0.54 [0.42, 0.65] |
| MAG | 0.35 [0.25, 0.45] | 0.16 [0.09, 0.25] | 0.34 [0.24, 0.44] | 0.55 [0.44, 0.66] |
| all | 0.37 [0.31, 0.43] | 0.08 [0.05, 0.11] | 0.34 [0.29, 0.40] | 0.54 [0.47, 0.62] |

| check | observed agreement | expected | kappa | disagreements |
|---|---|---|---|---|
| Q1 meaning | 0.933 | 0.536 | 0.86 | 10 |
| Q2 answer/options | 0.707 | 0.545 | 0.36 | 44 |
| Q3 clarity | 0.953 | 0.551 | 0.90 | 7 |
| Q4 dialect membership | 0.980 | 0.980 | 0.00 | 3 |

The four values of kappa measure consistency between sessions of one model, not agreement between human annotators. Q4 has kappa zero because one session uses a single category on all double-rated pairs.
