#!/usr/bin/env python3
"""Consolidate Stage B outputs (results/stageB/B_<tag>_L<L>_<s0>-<s1>.csv, Brouter_*.csv)
into results/stageB/STAGE_B_REPORT.md. Standard library only (runs anywhere)."""
import csv, glob, os, re, sys, json, statistics as st
from collections import defaultdict
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "results", "stageB")
D = os.path.abspath(D)
ORDER = ["msa_only","pooled","oracle","text_router","internal_router","plausible_set"]
VARS = ["MSA","UAE","EGY","KSA","SYR","MAG","ENG"]
DIAL = ["UAE","EGY","KSA","SYR","MAG"]
def mean(x): return sum(x)/len(x) if x else float("nan")
def sd(x): return st.pstdev(x) if len(x) > 1 else 0.0
tags = {}
for f in sorted(glob.glob(os.path.join(D, "B_*.csv"))):
    m = re.match(r"B_(.+)_L(\d+)_(\d+)-(\d+)\.csv$", os.path.basename(f))
    if not m: continue
    tags.setdefault((m.group(1), int(m.group(2))), []).append(f)
out = ["# Stage B — variety-aware conformal calibration under the correct protocol (all models)", "",
       "Grouped 3-way split per seed (router-train / calibration / test, 150/175/175 question keys); routers trained on router-train only; thresholds per PREDICTED group on calibration; evaluated per TRUE variety on test. Original scoring-run scores. Same calibration budget for every method.", ""]
summary_rows = []
for (tag, L), files in tags.items():
    # per (split, alpha, method, variety) -> coverage, size
    cov = defaultdict(dict); size = defaultdict(dict); splits = set(); alphas = set()
    for f in files:
        for r in csv.DictReader(open(f)):
            k = (float(r["alpha"]), r["method"], r["variety"]); s = int(r["split"])
            cov[k][s] = float(r["coverage"]); size[k][s] = float(r["set_size"]); splits.add(s); alphas.add(float(r["alpha"]))
    racc = defaultdict(list); conf = defaultdict(lambda: None)
    for f in glob.glob(os.path.join(D, f"Brouter_{tag}_L{L}_*.csv")):
        for r in csv.DictReader(open(f)):
            racc[r["router"]].append(float(r["acc"]))
            C = json.loads(r["confusion"]); V = json.loads(r["varieties"])
            if conf[r["router"]] is None: conf[r["router"]] = [[0]*len(V) for _ in V]
            for i in range(len(V)):
                for j in range(len(V)): conf[r["router"]][i][j] += C[i][j]
            conf[(r["router"], "V")] = V
    out += [f"## {tag} (layer {L}; {len(splits)} splits)", ""]
    out += ["Router accuracy on test (7-way): " + "; ".join(f"{k} {mean(v):.3f} ± {sd(v):.3f}" for k, v in sorted(racc.items())), ""]
    for rt in sorted(racc):
        V = conf[(rt, "V")]; C = conf[rt]
        # top confusions (off-diagonal, as fraction of true row)
        pairs = []
        for i in range(len(V)):
            tot = sum(C[i]) or 1
            for j in range(len(V)):
                if i != j and C[i][j]/tot >= 0.15: pairs.append(f"{V[i]}→{V[j]} {C[i][j]/tot:.2f}")
        out.append(f"- {rt} router: per-variety recall " + ", ".join(f"{V[i]} {C[i][i]/(sum(C[i]) or 1):.2f}" for i in range(len(V))) + (f"; main confusions: " + ", ".join(pairs) if pairs else ""))
    out.append("")
    for a in sorted(alphas):
        tgt = 1 - a
        out += [f"### α={a:g} (target coverage {tgt:.2f}); mean over splits (split SD in brackets)", "",
                "| method | " + " | ".join(VARS) + " | worst dialect | mean size (dialects) | size MAG |", "|---|" + "---|"*(len(VARS)+3)]
        for mth in ORDER:
            cells = []; worst = []; sizes = []
            for v in VARS:
                vals = [cov[(a, mth, v)][s] for s in sorted(splits) if s in cov[(a, mth, v)]]
                if not vals: cells.append("—"); continue
                cells.append(f"{mean(vals):.3f} [{sd(vals):.3f}]")
            for s in sorted(splits):
                ws = [cov[(a, mth, v)].get(s) for v in DIAL]
                if all(w is not None for w in ws): worst.append(min(ws))
            for v in DIAL:
                sizes += [size[(a, mth, v)][s] for s in sorted(splits) if s in size[(a, mth, v)]]
            mag = [size[(a, mth, "MAG")][s] for s in sorted(splits) if s in size[(a, mth, "MAG")]]
            out.append(f"| {mth} | " + " | ".join(cells) + f" | {mean(worst):.3f} | {mean(sizes):.2f} | {mean(mag):.2f} |")
            summary_rows.append((tag, a, mth, mean(worst), mean(sizes), mean([cov[(a,mth,'MAG')][s] for s in splits if s in cov[(a,mth,'MAG')]] or [float('nan')])))
        # paired differences vs msa_only on MAG and worst-dialect, over splits
        out.append("")
        diffs = []
        for mth in ORDER[1:]:
            d_mag = []; d_w = []
            for s in sorted(splits):
                if s in cov[(a, mth, "MAG")] and s in cov[(a, "msa_only", "MAG")]:
                    d_mag.append(cov[(a, mth, "MAG")][s] - cov[(a, "msa_only", "MAG")][s])
                    w1 = [cov[(a, mth, v)].get(s) for v in DIAL]; w0 = [cov[(a, "msa_only", v)].get(s) for v in DIAL]
                    if all(x is not None for x in w1 + w0): d_w.append(min(w1) - min(w0))
            if d_mag:
                se = sd(d_mag)/max(1, len(d_mag))**0.5; sew = sd(d_w)/max(1, len(d_w))**0.5
                diffs.append(f"{mth}: ΔMAG {mean(d_mag):+.3f} (±{1.96*se:.3f}), Δworst {mean(d_w):+.3f} (±{1.96*sew:.3f})")
        out += ["Paired differences vs msa_only over splits (mean, ±1.96·SE): " + "; ".join(diffs), ""]
    out.append("")
out += ["## Reading", "",
        "A method is useful only if it raises worst-dialect / MAG coverage toward target by more than the split noise, at equal calibration budget, without inflating set size, and the internal router must beat the text router (which costs no model access). Oracle Mondrian uses true labels and is a reference, not a guaranteed ceiling.", ""]
open(os.path.join(D, "STAGE_B_REPORT.md"), "w").write("\n".join(out))
print("\n".join(out))
