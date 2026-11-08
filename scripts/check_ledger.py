#!/usr/bin/env python3
"""Consistency audit of the claims ledger (docs/CLAIMS_LEDGER.csv) against the frozen result files.

Reads every ledger row, evaluates its `expr` on the filtered source file and compares with `claimed`
within `tol`. Writes docs/LEDGER_CHECK.md. This is a consistency audit (manuscript text vs stored
outputs), not an independent re-computation of the outputs themselves.

Row columns:
  id, section, claim, quantity, comparison, denominator, unit, interval, tier, wording,
  file, filter, expr, claimed, tol, note
`filter`: "col=value; col=value" (numeric values parsed as float; "col in a|b|c" for sets).
`expr`  : Python expression over `df` (filtered frame; `D` = full frame; `J` = json object for .json files).
          Helpers: M (model order), pick(df,col) -> values in M order; rng(df,col,nd) -> [min,max] rounded;
          plug(D,col,v,extra) -> plug-in col(v)−col(MSA) per model; plugall(D,col,extra,vs) -> over varieties;
          cnt(mask) -> int; rd(x,nd) -> rounded scalar/list; pp(x) -> 100*x.
`claimed`: JSON scalar or list. `tol`: absolute tolerance (per element). Empty expr => "report-sourced" row
          (value transcribed from a named report table; not recomputed here).
"""
import csv, json, math, sys, os
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = ['ALLaM-7B-Instruct-preview', 'Fanar-1-9B', 'Qwen3-8B-Base', 'gemma-2-9b']
DIAL = ['EGY', 'KSA', 'MAG', 'SYR', 'UAE']


def pick(df, col, by='model', order=None):
    order = order or M
    s = df.set_index(by)[col]
    return [float(s.loc[m]) for m in order]


def rng(df, col, nd=2):
    return [round(float(df[col].min()), nd), round(float(df[col].max()), nd)]


def cnt(mask):
    return int(np.asarray(mask).sum())


def plug(D, col, v, extra=None):
    """Plug-in paired difference col(v) − col(MSA) per model (M order) on the FULL frame D, optionally restricted by a
    dict of column=value conditions (e.g. {'target_risk': 0.2}). This is the sample point estimate; the released
    d_* columns of confirm_analyze.py are bootstrap means and are no longer used as point estimates (2026-11-08)."""
    d = D
    for k, val in (extra or {}).items():
        d = d[np.isclose(d[k], val)] if isinstance(val, (int, float)) else d[d[k] == val]
    out = []
    for m in M:
        a = d[(d.model == m) & (d.variety == v)][col].iloc[0]
        b = d[(d.model == m) & (d.variety == 'MSA')][col].iloc[0]
        out.append(float(a - b))
    return out


def plugall(D, col, extra=None, vs=None):
    """plug() over several varieties, flattened per variety in M order."""
    return [x for v in (vs or DIAL) for x in plug(D, col, v, extra)]


def rd(x, nd=2):
    if isinstance(x, (list, tuple, np.ndarray, pd.Series)):
        return [round(float(v), nd) for v in x]
    return round(float(x), nd)


def pp(x):
    if isinstance(x, (list, tuple, np.ndarray, pd.Series)):
        return [100.0 * float(v) for v in x]
    return 100.0 * float(x)


def parse_filter(s):
    conds = []
    for part in [p.strip() for p in s.split(';') if p.strip()]:
        if ' in ' in part:
            col, vals = part.split(' in ', 1)
            vals = [v.strip() for v in vals.split('|')]
            conds.append((col.strip(), 'in', vals))
        else:
            col, val = part.split('=', 1)
            conds.append((col.strip(), '=', val.strip()))
    return conds


def apply_filter(D, conds):
    df = D
    for col, op, val in conds:
        if op == 'in':
            vals = []
            for v in val:
                try:
                    vals.append(float(v))
                except ValueError:
                    vals.append(v)
            if pd.api.types.is_numeric_dtype(df[col]):
                df = df[df[col].isin([float(v) for v in vals])]
            else:
                df = df[df[col].astype(str).isin([str(v) for v in vals])]
        else:
            if pd.api.types.is_numeric_dtype(df[col]):
                df = df[np.isclose(df[col].astype(float), float(val))]
            else:
                df = df[df[col].astype(str) == val]
    return df


def compare(got, claimed, tol):
    if isinstance(claimed, list):
        if not isinstance(got, (list, tuple)) or len(got) != len(claimed):
            return False
        return all(compare(g, c, tol) for g, c in zip(got, claimed))
    if isinstance(claimed, bool):
        return bool(got) == claimed
    if isinstance(claimed, str):
        return str(got) == claimed
    try:
        return abs(float(got) - float(claimed)) <= tol + 1e-12
    except Exception:
        return False


def main():
    ledger = os.path.join(ROOT, 'docs', 'CLAIMS_LEDGER.csv')
    rows = list(csv.DictReader(open(ledger, encoding='utf-8')))
    out = []
    n_pass = n_fail = n_report = 0
    cache = {}
    for r in rows:
        f = r['file'].strip()
        expr = r['expr'].strip()
        claimed = json.loads(r['claimed']) if r['claimed'].strip() else None
        tol = float(r['tol']) if r['tol'].strip() else 0.0
        status, got = '', ''
        if not expr:
            status = 'report-sourced'
            n_report += 1
        else:
            try:
                path = os.path.join(ROOT, f)
                if f not in cache:
                    if f.endswith('.json'):
                        cache[f] = json.load(open(path))
                    else:
                        cache[f] = pd.read_csv(path)
                src = cache[f]
                env = dict(M=M, DIAL=DIAL, pick=pick, rng=rng, cnt=cnt, rd=rd, pp=pp, plug=plug, plugall=plugall, np=np, pd=pd, math=math)
                if isinstance(src, pd.DataFrame):
                    D = src
                    df = apply_filter(D, parse_filter(r['filter'])) if r['filter'].strip() else D
                    env.update(df=df, D=D)
                else:
                    env.update(J=src)
                val = eval(expr, {**env, '__builtins__': __builtins__})   # helpers as globals so that nested comprehensions see them
                if isinstance(val, (np.floating, np.integer)):
                    val = val.item()
                if isinstance(val, (list, tuple)):
                    val = [v.item() if isinstance(v, (np.floating, np.integer)) else v for v in val]
                got = val
                ok = compare(got, claimed, tol)
                status = 'PASS' if ok else 'FAIL'
                if ok:
                    n_pass += 1
                else:
                    n_fail += 1
            except Exception as e:  # noqa
                status = 'ERROR'
                got = f'{type(e).__name__}: {e}'
                n_fail += 1
        out.append((r, status, got))

    lines = ['# Ledger consistency audit', '',
             f'Rows: {len(rows)} — PASS {n_pass}, FAIL/ERROR {n_fail}, report-sourced (not recomputed) {n_report}.',
             '',
             'A consistency audit compares the manuscript\'s numbers and their stated comparison/denominator/interval type with the',
             'frozen result files; it is not an independent re-computation (that is Appendix C / results/indep_check).', '',
             '| id | §/tier | claim | file | computed | claimed | status |', '|---|---|---|---|---|---|---|']
    for r, status, got in out:
        g = got if not isinstance(got, float) else round(got, 4)
        if isinstance(g, list):
            g = [round(x, 4) if isinstance(x, float) else x for x in g]
        lines.append(f"| {r['id']} | {r['section']} / {r['tier']} | {r['claim'].replace('|', '/')} | {r['file']} | {g} | {r['claimed']} | **{status}** |")
    fails = [(r, s, g) for r, s, g in out if s in ('FAIL', 'ERROR')]
    if fails:
        lines += ['', '## Rows needing attention', '']
        for r, s, g in fails:
            lines.append(f"- **{r['id']}** ({s}): {r['claim']} — computed `{g}`, claimed `{r['claimed']}`. {r['note']}")
    open(os.path.join(ROOT, 'docs', 'LEDGER_CHECK.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'PASS {n_pass}  FAIL/ERROR {n_fail}  report-sourced {n_report}')
    for r, s, g in fails:
        print(f'  {s} {r["id"]}: {r["claim"][:70]} -> {g} vs {r["claimed"]}')
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
