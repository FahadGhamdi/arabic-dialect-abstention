# Independent computational check — comparison (Addendum 9 §9.5; 2026-11-07 ≈18:00 local)

Independent implementation: scripts/indep_check/recompute.py (sha256 4d69b8f21f6e2d07…), written by a separate agent from docs/METRIC_DEFINITIONS.md
and the raw score files only (it did not open the frozen analysis code or any report). Comparison against the frozen confirmatory outputs
(results/confirm/*.csv, confirm_analyze.py 8ade05cd…), point values:

| quantity | cells compared | max absolute difference | reading |
|---|---|---|---|
| P1: t50 and answerable fraction, all varieties | 28 | 0.0 | identical |
| S4: τ, answered fraction, realised risk at r* = 0.15 / 0.20 / 0.25 | 84 | τ ≤ 1e-5; fractions ≤ 7.0e-4 (= one item of 1,420); risk ≤ 1.0e-3 | agree to one boundary item |
| S4 at r* = 0.30 | 28 | τ 3.3e-3 (Fanar); answered ≤ 1.06e-2 | input-precision effect, see below |
| P2 (α = 0.20, 0.30): q̂, coverage under MSA q̂, Δcov, size under MSA q̂ | 56 | ≤ 1.5e-3 | agree to 1–2 boundary items |
| P2: coverage and size under own q̂, size ratio | 56 | size ≤ 8.5e-3; ratio ≤ 7.1e-3 | boundary items at the rounded log-probabilities |
| per-key S4 answered indicator (r* = 0.20), 4 × 9,940 cells | 39,760 | 1 mismatch (Fanar) | agree |
| per-key conformal coverage indicator (α = 0.30) | 39,760 | 5 mismatches in total | agree |

Source of the residual differences (documented by the independent implementer): the stored lA..lD are rounded to 4 decimals while the
p_max / p_true columns carry 5 decimals from full-precision logits; the independent run recomputed probabilities from lA..lD (its primary
choice), which re-orders near-tied calibration items. For Fanar at r* = 0.30 this moves K from 634 to 632 and τ from 0.3757 to 0.3790
(answered fractions by ≤ 0.011). Using the stored columns instead, the implementer reports ≤ 7e-4 differences everywhere. r* = 0.30 is a
secondary target; the primary (0.20) agrees to one item. Tie handling: no tie sits at the ⌈n/2⌉ or K-th position except that Qwen3's τ(0.15)
depends on the order within a mixed tie group (0.6148 vs 0.6147; one item).

Verdict: the frozen implementation of P1, S4 and P2 is reproduced by an independent implementation from the written definitions, within
the precision of the stored inputs. This is a computational check by an independent implementation, not an audit: both implementations read
the same definitions and the same stored scores; it does not test the scoring itself (prompting, letter extraction) or the validity of the data.
Recommendation for the release: store option log-probabilities at full precision (or state the 4-decimal rounding), and state the tie rule.
