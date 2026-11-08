# Claims ledger — how to read and run it

`docs/CLAIMS_LEDGER.csv` lists every numeric or countable claim in the manuscript with the information a reader needs to
judge it, and the exact source cell(s) in the frozen result files. It is the single source of numbers for the manuscript
text, tables and figures. `scripts/build_ledger.py` is the authored source (edit there, then rebuild);
`scripts/check_ledger.py` re-evaluates every row against `results/` and writes `docs/LEDGER_CHECK.md`.

```
python3 scripts/build_ledger.py && python3 scripts/check_ledger.py
```

## Columns
| column | meaning |
|---|---|
| id | stable identifier used in manuscript comments (e.g. `S4-10`) |
| section | where the claim appears in the manuscript |
| claim | the claim as worded |
| quantity | what is measured |
| comparison | what is compared with what (e.g. dialect − MSA; dialect vs the 0.20 ceiling) |
| denominator | sample the number is computed on |
| unit | fraction / pp / % / ratio / count |
| interval | FIX = paired key bootstrap over test keys, thresholds fixed (B = 2000, 95% percentile); RS = double resampling of calibration and test keys with threshold re-selection (B = 1000); KC = key-clustered CI; PT = point estimate only |
| tier | when the analysis was specified (below) |
| wording | the wording the claim is allowed to carry (ANALYSIS_PLAN §9.7, Addendum 10) |
| file / filter / expr | source file, row filter and the expression that recomputes the number |
| claimed / tol | the manuscript value and the absolute tolerance (rounding) |
| note | corrections and source changes |

## Tiers (specification timing — stated as it happened)
| tier | meaning |
|---|---|
| T1 | endpoint and decision rule fixed in ANALYSIS_PLAN.md before confirmatory scoring; analysis code frozen (sha256) before any confirmatory score file was opened (P1, P2, P3, S1, S2, S3) |
| T1b | S4: added to the frozen code during score collection, before any confirmatory score file was opened for analysis |
| T2 | addendum specified after the main confirmatory results had been seen and before its own computation (Addendum 2 screen sensitivity; Addendum 4 validity layers; Addendum 7 diagnostic; Addendum 8 robustness; Addendum 9 verification; Addendum 10 supplements) |
| T3 | exploratory / post hoc: specified after the relevant results were seen (e.g. the D4 ceiling counts, the P2 resampling range) |
| W | the claim is withdrawn; the negative test result remains documented (P3) |
| EXT | external fact (resource documentation; the independent-implementation report) |
| DSN | design parameter checked against the data files |

The documentation mechanism was a locally frozen plan with dated versions (`versions/`) and the running log `PILOT_NOTES.md`;
no public registry was used. A sha256 proves the identity of a file, not the date it existed; the only server-side timestamps
are the revision histories of the working documents. Publishing the package later does not give it an earlier registration date.

## What the check is
A consistency audit: it verifies that the manuscript's numbers, comparisons, denominators and interval types match the
frozen result files. It is not an independent re-computation of those files (that is `results/indep_check/`, an independent
implementation of P1, S4 and P2 from the written definitions), and neither is a substitute for human peer review.
Rows with an empty `expr` are "report-sourced": transcribed from a named report table (the model-assisted screen; the
independent-check comparison) and not recomputed here.
