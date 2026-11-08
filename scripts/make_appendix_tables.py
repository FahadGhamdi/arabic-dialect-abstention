#!/usr/bin/env python3
"""Generate the appendix tables of the manuscript from the result files and write them into the manuscript between
marker comments, so that no appendix number is typed by hand.

Markers in the manuscript:  <!-- BEGIN TABLE A1 -->  ...  <!-- END TABLE A1 -->   (the block between them is replaced)
Usage: python3 scripts/make_appendix_tables.py [paper/manuscript_v0.4.md]
Reads results/ only. scripts/audit_text_numbers.py skips the generated blocks (they are traceable by construction).
"""
import os, re, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'paper', 'manuscript_v0.4.md')
M = ['ALLaM-7B-Instruct-preview', 'Fanar-1-9B', 'Qwen3-8B-Base', 'gemma-2-9b']
MS = ['ALLaM', 'Fanar', 'Qwen3', 'Gemma']
V = ['MAG', 'SYR', 'EGY', 'KSA', 'UAE']
VN = {'MSA': 'MSA', 'MAG': 'Moroccan (MAG)', 'SYR': 'Syrian (SYR)', 'EGY': 'Egyptian (EGY)', 'KSA': 'Saudi (KSA)', 'UAE': 'Emirati (UAE)', 'ENG': 'English (ENG)'}


def f2(x):
    s = f'{x:.2f}'
    if s == '-0.00':
        s = '0.00'
    return s.replace('-', '−')


def f3(x):
    s = f'{x:.3f}'
    if s == '-0.000':
        s = '0.000'
    return s.replace('-', '−')


def sgn2(x):
    return ('+' if x > 0 else '') + f2(x)


def sgn3(x):
    return ('+' if x > 0 else '') + f3(x)


def pts(x):
    return ('+' if x > 0 else '') + f'{100*x:.0f}'.replace('-', '−')


def table(header, rows, first=30, rest=14):
    # the dash counts set the relative column widths in pandoc's LaTeX output
    out = ['| ' + ' | '.join(header) + ' |', '|' + '-' * first + '|' + ('-' * rest + '|') * (len(header) - 1)]
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


tables = {}

# ---- A1: P1 answerable fraction at the MSA-matched risk
p1 = pd.read_csv(os.path.join(ROOT, 'results/confirm/P1_selective.csv')).set_index(['model', 'variety'])
rows = [['MSA (reference)'] + [f2(p1.loc[(m, 'MSA'), 'answerable']) for m in M],
        ['MSA risk at 50% answered (t)'] + [f3(p1.loc[(m, 'MSA'), 'msa_matched_risk']) for m in M]]
for v in V:
    rows.append([VN[v]] + [f"{f2(p1.loc[(m, v), 'answerable'])} ({sgn2(p1.loc[(m, v), 'd_answerable'])} [{f2(p1.loc[(m, v), 'd_lo'])}, {f2(p1.loc[(m, v), 'd_hi'])}])" for m in M])
tables['A1'] = ('P1: fraction of test questions answerable at the risk MSA attains when answering its 50% most confident questions (t), by variety and model; in parentheses the paired difference from MSA with its 95% key-bootstrap interval. Oracle threshold; descriptive.',
                table(['variety'] + MS, rows))

# ---- A2: P2 at alpha = 0.30
p2 = pd.read_csv(os.path.join(ROOT, 'results/confirm/P2_conformal.csv'))
p2 = p2[p2.alpha == 0.3].set_index(['model', 'variety'])
rows = [['MSA: coverage, own quantile'] + [f2(p2.loc[(m, 'MSA'), 'cov_msathr']) for m in M],
        ['MSA: mean set size'] + [f2(p2.loc[(m, 'MSA'), 'size_msathr']) for m in M]]
for v in V:
    rows.append([f'{v}: Δ coverage (points)'] + [f"{pts(p2.loc[(m, v), 'd_cov'])} [{pts(p2.loc[(m, v), 'd_cov_lo'])}, {pts(p2.loc[(m, v), 'd_cov_hi'])}]" for m in M])
    rows.append([f'{v}: set-size ratio'] + [f"{f2(p2.loc[(m, v), 'size_ratio'])} [{f2(p2.loc[(m, v), 'size_ratio_lo'])}, {f2(p2.loc[(m, v), 'size_ratio_hi'])}]" for m in M])
tables['A2'] = ('P2 at α = 0.30 (nominal coverage 0.70): coverage lost on each variety under the MSA calibration quantile (Δ coverage, percentage points, paired by key) and the mean set size each variety needs under its own quantile to reach the same nominal target, as a ratio to MSA\'s (set-size ratio); 95% intervals with the calibration sample held fixed. The double-resampled intervals are 2.7–4.3 times wider for the ratios and 0.95–1.4 times for the coverage differences (Section 4.4).',
                table(['quantity'] + MS, rows))

# ---- A3: S2 variety-aware calibration, MAG, alpha = 0.30
s2 = pd.read_csv(os.path.join(ROOT, 'results/confirm/S2_variety_aware.csv'))
s2 = s2[(s2.alpha == 0.3) & (s2.variety == 'MAG')].set_index(['model', 'method'])
meth = [('msa_only', 'MSA quantile (transferred)'), ('pooled', 'pooled calibration set'), ('text_router', 'Mondrian, variety predicted by the text classifier'),
        ('oracle', 'Mondrian, true variety label'), ('plausible_set', 'union over plausible varieties (conservative)')]
rows = []
for k, name in meth:
    rows.append([name] + [f"{f2(s2.loc[(m, k), 'coverage'])} / {f2(s2.loc[(m, k), 'set_size'])}" for m in M])
rec = []
for m in M:
    g = (s2.loc[(m, 'text_router'), 'coverage'] - s2.loc[(m, 'msa_only'), 'coverage']) / (s2.loc[(m, 'oracle'), 'coverage'] - s2.loc[(m, 'msa_only'), 'coverage'])
    rec.append(f'{100*g:.0f}%')
rows.append(['share of the oracle gain recovered by the classifier'] + rec)
racc = float(s2['router_acc'].iloc[0])
tables['A3'] = (f'S2: variety-aware calibration for the Moroccan test items at α = 0.30 (target 0.70), equal numbers of calibration keys per variety. Cells give achieved coverage / mean set size. The text classifier is a character n-gram model trained on the router split (accuracy {racc:.2f} on the seven-way variety label).',
                table(['method'] + MS, rows))

# ---- A4: accuracy and AUROC by variety
d1 = pd.read_csv(os.path.join(ROOT, 'results/diag/D1_D2_discrimination.csv')).set_index(['model', 'variety'])
rows = []
for v in ['MSA', 'MAG', 'SYR', 'EGY', 'KSA', 'UAE', 'ENG']:
    rows.append([VN[v]] + [f"{f2(d1.loc[(m, v), 'acc'])} / {f2(d1.loc[(m, v), 'auroc'])}" for m in M])
tables['A4'] = ('Accuracy / AUROC of p_max (correct versus incorrect) on the 1,420 test keys, by variety and model. The paired AUROC differences from MSA with intervals are in Table 3.',
                table(['variety'] + MS, rows))

# ---- A5: order-sensitivity rate (R1)
r1 = pd.read_csv(os.path.join(ROOT, 'results/robust/R1_order_sensitivity.csv')).set_index(['model', 'variety'])
rows = []
for v in ['MSA', 'MAG', 'SYR', 'EGY', 'KSA', 'UAE', 'ENG']:
    if v == 'MSA':
        rows.append([VN[v]] + [f2(r1.loc[(m, v), 'osr']) for m in M])
    else:
        rows.append([VN[v]] + [f"{f2(r1.loc[(m, v), 'osr'])} ({sgn2(r1.loc[(m, v), 'd_osr'])} [{f2(r1.loc[(m, v), 'd_osr_lo'])}, {f2(r1.loc[(m, v), 'd_osr_hi'])}])" for m in M])
tables['A5'] = ('Order-sensitivity rate: share of the 500 robustness keys whose chosen option changes across the four cyclic rotations, by variety and model; in parentheses the paired difference from MSA with its 95% key-bootstrap interval.',
                table(['variety'] + MS, rows))

# ---- A6: order-averaged gaps (R2)
r2 = pd.read_csv(os.path.join(ROOT, 'results/robust/R2_gap_stability.csv')).set_index(['model', 'variety'])
rows = []
for v in V:
    rows.append([f'{v}: Δ accuracy'] + [f"{sgn2(r2.loc[(m, v), 'd_acc_avg'])} [{f2(r2.loc[(m, v), 'd_acc_lo'])}, {f2(r2.loc[(m, v), 'd_acc_hi'])}]" for m in M])
    rows.append([f'{v}: Δ P1'] + [f"{sgn2(r2.loc[(m, v), 'd_p1_avg'])} [{f2(r2.loc[(m, v), 'd_p1_lo'])}, {f2(r2.loc[(m, v), 'd_p1_hi'])}]" for m in M])
tables['A6'] = ('Gaps averaged over the four option rotations (500 robustness keys): Δ accuracy and Δ P1 (variety − MSA, per variety) with 95% intervals over keys. Every difference keeps its sign in all four rotations.',
                table(['quantity'] + MS, rows))

# ---- write into the manuscript between markers
md = open(MD, encoding='utf-8').read()
n = 0
for k, (cap, tab) in tables.items():
    pat = re.compile(r'<!-- BEGIN TABLE ' + k + r' -->.*?<!-- END TABLE ' + k + r' -->', re.S)
    block = f'<!-- BEGIN TABLE {k} -->\nTable {k}. {cap}\n\n{tab}\n<!-- END TABLE {k} -->'
    if pat.search(md):
        md = pat.sub(lambda m: block, md); n += 1
    else:
        print('marker not found for', k)
open(MD, 'w', encoding='utf-8').write(md)
print(f'wrote {n} tables into {os.path.relpath(MD, ROOT)}')
