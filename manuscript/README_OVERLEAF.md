# Manuscript v1.0 — official MDPI template

Title: Risk and Coverage across Arabic Dialects in Selective Question Answering

## Compile on Overleaf
Upload the complete ZIP, select `main.tex` as the main document and use pdfLaTeX.
All generated tables and figure PDFs are included; no Python execution or network access is needed to compile.

The ten original files in `Definitions/` are byte-for-byte those supplied in `MDPI_template_ACS.zip`. A PDF conversion of the supplied EPS logo is also included for compilation.
The original geometry, typography, margin metadata and class macros are retained. No page-geometry, body-font or body-line-spacing override is applied. The file `layout_pagination.tex` controls float placement and spacing only.
Obsolete commands from the older class (hreflink, TitleCitation, AuthorCitation) have been removed from the manuscript source.
All appendix tables remain in the main PDF.

## Regenerate presentation from the archived results
Use an existing Python 3 interpreter:
    python3 tools/make_appendix_tables.py
    python3 tools/make_appendix_tables.py --check
    python3 tools/make_rotation_figure.py

The table generator uses the Python standard library. The figure generator also needs an existing pdfLaTeX/PGFPlots installation.
Neither script loads a model, accesses individual benchmark records, recomputes bootstrap statistics, or changes archived evidence.
The figure generator redraws the 20 R2 estimates and 80 rotation marks in a two-by-two layout.

## Evidence and provenance
`docs/FILE_INDEX.md` maps every appendix table to its original CSV or report.
`generated/table_provenance.json` records input and output hashes.
`generated/rotation_figure_provenance.json` records all plotted values and source hashes.
`docs/TEMPLATE_MANIFEST.json` records the supplied template archive and each original class file.

`supplementary/frozen/` is historical evidence. Its plans, instructions and recommendations are archived as documents, not executed by the manuscript build.
The selected archive does not contain original dataset texts or all individual score records. The manuscript's data-availability statement gives the public sources.

## Layout revision v0.9
This revision preserves all v0.8 manuscript prose, captions, table cells, figures, references and archived evidence. It changes only pagination and presentation. Main-text floats are packed with nearby text or figures; appendix tables may continue on the next page with repeated headers. Their font size and single-spaced rows match the original floating-table style. Appendix figures are repositioned between tables to avoid sparse pages. All appendix tables remain in the main document.

## Scientific revision inherited from v0.8
This version merges the verified v0.7 numerical displays with the documented methodological/disclosure details from the supplied v0.6.
It restores the explicit withdrawal of the P3 stand-alone interpretation and states that S4 is the primary operational evidence.
The six P1 display corrections are recorded in Appendix C. Post-hoc adaptation counts are removed from the abstract and introduction and labelled in Results and Discussion.
The archived evidence supports aggregate generated-answer risk agreement; no new item-level identity claim has been added.
The earlier Markdown manuscript is not a synchronized master: `main.tex` is the publication source for this revision.

## Submission revision v1.0
Corrects figure citation order and section references, adds explicit appendix callouts, clarifies the P1 risk reference, aligns paired model values in Table 2, and improves the start of Table A16. The official template and archived observations are preserved. Screen confidence intervals were recomputed from the original ratings with a recorded seed; Appendix E explains the change. Original screen intervals remain in the frozen historical report.

The new screening calculations are in `supplementary/recomputed_screen/`. Run `python3 tools/audit_screen.py --ratings-dir supplementary/recomputed_screen` to reproduce agreement and screening rates. `tools/audit_sensitivity.py` additionally takes the companion score repository via `--repository`. These scripts require NumPy; sensitivity also requires pandas. They do not contact a model. The private original workbook is not distributed.
