#!/usr/bin/env python3
"""Compare a clean-folder reproduction (REPRO) with the shipped result files (SHIPPED) and write docs/REPRO_CHECK.md.
Usage: python3 scripts/repro_compare.py <SHIPPED_root> <REPRO_root>
"""
import os, sys, glob, hashlib
import numpy as np, pandas as pd

SHIPPED, REPRO = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = ['results/confirm', 'results/validity', 'results/diag', 'results/robust', 'results/sens', 'results/supp', 'results/indep_check']
rows = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


for fo in FOLDERS:
    for f in sorted(glob.glob(os.path.join(SHIPPED, fo, '*'))):
        name = os.path.relpath(f, SHIPPED)
        g = os.path.join(REPRO, name)
        if not os.path.exists(g):
            rows.append((name, 'MISSING in reproduction', '', ''))
            continue
        if f.endswith('.csv'):
            a = pd.read_csv(f); b = pd.read_csv(g)
            if list(a.columns) != list(b.columns) or a.shape != b.shape:
                rows.append((name, 'SHAPE/COLUMNS DIFFER', f'{a.shape} vs {b.shape}', ''))
                continue
            maxdiff = 0.0; strdiff = 0; cells = 0
            for c in a.columns:
                if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
                    x = a[c].to_numpy(dtype=float); y = b[c].to_numpy(dtype=float)
                    m = ~(np.isnan(x) & np.isnan(y))
                    if m.any():
                        d = np.nanmax(np.abs(x[m] - y[m])) if m.sum() else 0.0
                        maxdiff = max(maxdiff, float(d) if not np.isnan(d) else 0.0)
                else:
                    strdiff += int((a[c].astype(str) != b[c].astype(str)).sum())
                cells += len(a)
            status = 'IDENTICAL' if (sha(f) == sha(g)) else ('EQUAL (numeric to 1e-9)' if maxdiff <= 1e-9 and strdiff == 0 else 'DIFFERS')
            rows.append((name, status, f'max |Δ| = {maxdiff:.2e}', f'{strdiff} text cells differ' if strdiff else ''))
        else:
            same = sha(f) == sha(g)
            if not same:
                la = open(f, encoding='utf-8', errors='replace').read().splitlines(); lb = open(g, encoding='utf-8', errors='replace').read().splitlines()
                nd = sum(1 for x, y in zip(la, lb) if x != y) + abs(len(la) - len(lb))
                rows.append((name, 'TEXT DIFFERS', f'{nd} line(s) differ (run timestamps/paths are expected to differ)', ''))
            else:
                rows.append((name, 'IDENTICAL', '', ''))

# figures: pixel comparison of PNGs
try:
    from PIL import Image
    for f in sorted(glob.glob(os.path.join(SHIPPED, 'figures', '*.png'))):
        name = os.path.relpath(f, SHIPPED); g = os.path.join(REPRO, name)
        if not os.path.exists(g):
            rows.append((name, 'MISSING', '', '')); continue
        a = np.asarray(Image.open(f).convert('RGB')); b = np.asarray(Image.open(g).convert('RGB'))
        if a.shape != b.shape:
            rows.append((name, 'SIZE DIFFERS', f'{a.shape} vs {b.shape}', ''))
        else:
            frac = float((a != b).any(axis=2).mean())
            rows.append((name, 'IDENTICAL' if sha(f) == sha(g) else ('PIXEL-IDENTICAL' if frac == 0 else 'DIFFERS'), f'{100*frac:.3f}% pixels differ', ''))
except ImportError:
    pass

# ledger audit in the reproduction
lc = os.path.join(REPRO, 'docs', 'LEDGER_CHECK.md')
ledger_line = open(lc).read().splitlines()[2] if os.path.exists(lc) else 'not run'

n_ok = sum(1 for r in rows if r[1] in ('IDENTICAL', 'EQUAL (numeric to 1e-9)', 'PIXEL-IDENTICAL'))
lines = ['# Clean-folder reproduction check', '',
         f'Shipped package: `{os.path.basename(SHIPPED)}`; reproduction folder: a fresh copy of the package with `data/damm.csv` added (the dataset texts are not',
         'redistributed; see RELEASE_NOTES) and `audit_in/flags.pkl` (the screen flags in the pickled form `validity_analyze.py` reads; the same flags as',
         '`audit/screen_flags_400.csv`). The sequence in README.md was run with `python3 -I`; no model was run. `scripts/indep_check/recompute.py` carries an',
         'absolute project root; the copy run here had only that constant changed (diff: one line).', '',
         f'Files compared: {len(rows)}; identical or numerically equal: {n_ok}.', '',
         f'Ledger audit inside the reproduction: {ledger_line}', '',
         '| file | status | detail | |', '|---|---|---|---|']
for r in rows:
    lines.append('| ' + ' | '.join(r) + ' |')
diff = [r for r in rows if r[1] not in ('IDENTICAL', 'EQUAL (numeric to 1e-9)', 'PIXEL-IDENTICAL')]
lines += ['', '## Files that differ', '']
if not diff:
    lines.append('None.')
for r in diff:
    lines.append(f'- `{r[0]}`: {r[1]} — {r[2]} {r[3]}')
open(os.path.join(ROOT, 'docs', 'REPRO_CHECK.md'), 'w').write('\n'.join(lines) + '\n')
print(f'{n_ok}/{len(rows)} identical or numerically equal; {len(diff)} differ')
for r in diff:
    print('  ', r)
