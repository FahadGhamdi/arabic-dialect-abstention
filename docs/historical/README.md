# Uneven transfer of MSA-calibrated abstention policies to Arabic dialects — code, scores and results

Companion repository of the manuscript *Uneven Transfer of MSA-Calibrated Abstention Policies to Arabic Dialects: Coverage, Risk, and the Limits of Per-Dialect Adaptation* (F. AlGhamdi, Al-Baha University; under preparation for submission to *Applied Sciences*, November 2026). A tagged release of this repository will be archived on Zenodo at submission and the DOI added here and in the paper.

**Licence.** Code (`scripts/`) under the MIT License (`LICENSE`); result tables, figures, documents and logs under CC BY 4.0 (`LICENSE-DATA.md`). The source datasets are not redistributed: DialectalArabicMMLU and AraDiCE are available from their authors under their own terms; this repository holds key lists, splits and model outputs only.

This repository contains everything needed to re-derive every number, table and figure in the manuscript from the stored
model outputs, together with the analysis plan and its dated addenda, the project log, the claims ledger and its audit,
and the independent computational check. It does **not** redistribute the source datasets' texts.

## Layout

| path | content |
|---|---|
| `ANALYSIS_PLAN.md`, `versions/` | the analysis plan with all addenda; dated versions v4–v11 (v1–v3 predate the versioning and are summarised in the plan's history section) |
| `PILOT_NOTES.md` | the running project log (decisions, freezes, runs, corrections) |
| `FROZEN_SCRIPTS.md`, `SHA256SUMS.txt` | sha256 of the frozen analysis scripts and of every file in this package |
| `scripts/` | scoring scripts (how the score files were produced; need the models and the datasets), analysis scripts (run on the stored scores), figure and ledger scripts |
| `data/` | key lists and splits: `confirmatory_splits.json` (router 404 / calibration 808 / test 1,420; seed 20261105), `pilot_keys.json` (500 development keys), `robust_keys.json` (500 robustness keys), `ifm_excluded.json` (the external filter's exclusion list), `aradice_splits.json`, `damm_keys.csv` (text-free skeleton of the DialectalArabicMMLU table: dialect, qid, key, answer, domain) |
| `results/confirm_scores_<model>.csv` | per-item scores of the confirmatory run: option-letter log-probabilities (4 decimals), derived p_true / p_max (5 decimals), prediction, correctness |
| `results/robust_scores_<model>.csv`, `results/robust_gen_<model>.csv` | the robustness runs: four option rotations (k = 0..3) and the generated answers (G1; G2 for ALLaM) |
| `results/aradice_scores_<model>.csv` | the AraDiCE replication scores |
| `results/fidelity.csv` | embedding similarity between each dialect version and its MSA original (multilingual-e5-large) |
| `results/confirm/`, `validity/`, `diag/`, `robust/`, `sens/`, `supp/`, `indep_check/`, `audit/` | the result tables and reports, as produced by the frozen scripts |
| `docs/` | metric definitions given to the independent implementer; the claims ledger (`CLAIMS_LEDGER.csv`), its README and audit (`LEDGER_CHECK.md`); reference verification; reproduction check (`REPRO_CHECK.md`) |
| `figures/` | all figures (PNG 600 dpi and PDF) |

## Reproducing the tables and figures (no model runs)

```
python3 scripts/confirm_analyze.py        # results/confirm/   (S2's text router needs data/damm.csv, see below)
python3 scripts/validity_analyze.py all   # results/validity/
python3 scripts/diag_analyze.py           # results/diag/
python3 scripts/robust_analyze.py         # results/robust/    (needs data/damm.csv for the option strings)
python3 scripts/sens_analyze.py           # results/sens/
python3 scripts/supp_analyze.py           # results/supp/
python3 scripts/make_figures.py           # figures/
python3 scripts/build_ledger.py && python3 scripts/check_ledger.py   # docs/LEDGER_CHECK.md
```

Run from the package root (the scripts read `results/` and `data/` relative to the working directory, or `ADA_RES` / `ADA_DATA`).
`docs/REPRO_CHECK.md` records a clean-folder run of exactly this sequence and the comparison with the shipped result files.

**`data/damm.csv`** (the DialectalArabicMMLU items with texts) is not redistributed. Rebuild it from the public dataset with
`scripts/s1_data.py` and `scripts/s2_damm.py`; its text-free skeleton `data/damm_keys.csv` is included so that the key
bookkeeping can be checked. Two analyses read the texts: the character n-gram variety router of S2 (`confirm_analyze.py`)
and the option strings used to map generated answers in `robust_analyze.py`. Everything else runs from the score files alone.

## Datasets and models

DialectalArabicMMLU (Altakrori et al., LREC 2026), AraDiCE (Mousi et al., COLING 2025) and ArabicMMLU (Koto et al., Findings
of ACL 2024) are available from their authors under their own terms. Models: ALLaM-7B-Instruct-preview, Fanar-1-9B (a continual
pre-training of Gemma-2-9B), Qwen3-8B-Base, gemma-2-9b; all open weights, run locally in bf16 (see `RELEASE_NOTES.md`).

## Specification record

The plan was frozen locally with dated versions and a running log; no public registry was used. `ANALYSIS_PLAN.md` states for
each addendum when it was written relative to the results it concerns; the manuscript's Table 1 summarises the tiers. A sha256
proves the identity of a file, not the date it existed.
