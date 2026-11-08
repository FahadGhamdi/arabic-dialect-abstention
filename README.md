# Risk and Coverage across Arabic Dialects in Selective Question Answering

Submission companion v1.0, prepared from the public repository at commit
`8e103a0dacb7762e2f4f3ba47ad48a81eb602102`. This archive includes corrections
and additions made during the submission audit; the cited historical GitHub
commit does not contain those additions. See `docs/SUBMISSION_AUDIT.md`.

## Contents

- `manuscript/`: complete Overleaf source, official supplied MDPI class,
  generated appendix tables, seven figure PDFs, bibliography and table-to-source index.
- `results/`: original individual model outputs and historical analysis results.
- `results/audit_recomputed/`: text-free ratings from 400 first-session pairs,
  150 second-session pairs and 150 adjudications; recomputed agreement, screen
  rates, associations and sensitivity results. These are LLM screening judgments.
- `scripts/`: archived scoring and analysis programs. `scripts/audit_analyze.py`
  is a new entry point for the reconstructed screen analysis; it was not the
  code used in the original interactive session.
- `tools/`: submission audit, screen reconstruction, data preparation and isolated replay.
- `verification_outputs/`: numerical outputs from the current replay, kept separate
  from historical results because some tie-sensitive statistics differ.
- `docs/`: claim ledger, checks, environment, file index and audit reports.
- `ANALYSIS_PLAN.md`, `versions/`, `PILOT_NOTES.md`: unchanged historical record.
  Original claims and obsolete paths in those records are historical, not current instructions.
- `SHA256SUMS.txt`: checksums of the current archive, excluding this manifest itself.

## Reproduce the submission without model inference

Use Python 3.11 with the existing dependencies recorded in
`requirements-analysis.txt`. No model weights are needed for these calculations.
Run from this archive's root. The commands write only the explicitly chosen
private or replay directories and generated screening outputs.

```sh
python tools/check_score_integrity.py --repository . --output score_check.json
python tools/audit_screen.py --ratings-dir results/audit_recomputed
python tools/audit_sensitivity.py --repository . --ratings-dir results/audit_recomputed
python tools/update_submission_ledger.py --repository .
python scripts/check_ledger.py
python manuscript/tools/make_appendix_tables.py --check
```

Two analyses, the S2 text router and G2 option-string extraction, require publisher
texts. Rebuild the private input from the pinned publisher snapshot; the script
verifies its checksum and all 21,945 identity/label rows against `data/damm_keys.csv`.
Neither this input nor the original screening workbook is redistributed.

```sh
python tools/prepare_damm_texts.py --skeleton data/damm_keys.csv --output-dir ../private_damm
python tools/reproduce_submission.py --repository . --work-dir ../fresh_replay --text-input ../private_damm/damm.csv
```

The replay directory must not already exist. It retains the historical analysis
code in this archive unchanged, records report/path adaptations in a diff and
recomputes all confirmatory, diagnostic, rotation/generation, calibration
sensitivity, validity and screening statistics. Inspect the file comparisons;
exact byte identity across software environments is not claimed. The current
audit ran this sequence without generating any new model judgments or inference.

For the historical Matplotlib figures, an environment with the additional
dependencies in `requirements-plots.txt` can run the replay with `--plots`.
That optional plotting path was not newly executed in the submission audit.
Figure A3's revised layout is independently generated from archived numbers by
`manuscript/tools/make_rotation_figure.py` using pdfLaTeX/PGFPlots.
All figure PDFs needed to compile the manuscript are included. In the replay,
`scripts/make_figures.py` regenerates historical layouts; use the manuscript
generator for the final A3 layout.

## Limits of reproduction

The scores and identifiers permit reanalysis, and the principal reported results
were checked. Rounded probabilities and unspecified historical tie order lead to
documented differences in some bootstrap intervals and secondary operating points.
Original immutable weight revisions and the complete inference environment were
not recorded. The current dependency record is for the submission audit, not a
retroactive record of model inference. Stored-score consistency does not prove
the provenance of a historical model run. See the detailed audit for exact scope.

The source datasets remain available from their publishers under their own terms.
Code is licensed under MIT; result tables and documentation follow `LICENSE-DATA.md`.
No DOI is asserted for this prepared archive. Journal-assigned identifiers in the
official submission template are placeholders until assigned by the publisher.
