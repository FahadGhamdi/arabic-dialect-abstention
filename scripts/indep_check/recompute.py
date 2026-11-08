#!/usr/bin/env python3
"""
Independent recomputation of the P1 / S4 / P2 metrics (Addendum 9 §9.5).

Implemented from scratch using ONLY
  - docs/METRIC_DEFINITIONS.md          (the specification)
  - data/confirmatory_splits.json       (calibration / test key lists)
  - results/confirm_scores_<tag>.csv    (raw per-item scores)

No other analysis script or report was consulted.

Outputs (results/indep_check/):
  P1_indep.csv, S4_indep.csv, P2_indep.csv, perkey_<tag>.csv,
  P1_msa_curve_indep.csv (extra: the 20-point MSA risk-coverage curve), INDEP_NOTES.md

Point values only; no bootstrap.
"""
import json
import math
import os
from fractions import Fraction

import numpy as np
import pandas as pd

ROOT = "/home/claude/ada"
TAGS = ["ALLaM-7B-Instruct-preview", "Fanar-1-9B", "Qwen3-8B-Base", "gemma-2-9b"]
VARIETIES = ["MSA", "EGY", "SYR", "KSA", "UAE", "MAG", "ENG"]
R_STARS = ["0.15", "0.20", "0.25", "0.30"]  # strings -> exact Fractions
ALPHAS = ["0.20", "0.30"]
GRID = [Fraction(j, 20) for j in range(1, 21)]  # c = 0.05 .. 1.00
OUT = os.path.join(ROOT, "results", "indep_check")
NO_THRESHOLD = 1.01


# ----------------------------------------------------------------------------
# loading / preprocessing
# ----------------------------------------------------------------------------
def softmax_rows(L):
    L = L - L.max(axis=1, keepdims=True)
    P = np.exp(L)
    return P / P.sum(axis=1, keepdims=True)


def load_model(tag, splits):
    """Return (df, diag). df has one row per (dialect, key) restricted to complete keys."""
    path = os.path.join(ROOT, "results", f"confirm_scores_{tag}.csv")
    raw = pd.read_csv(path)
    diag = {"tag": tag, "n_raw_rows": int(len(raw))}

    # --- duplicate (dialect, key) rows: keep the first -------------------
    dup_mask = raw.duplicated(subset=["dialect", "key"], keep="first")
    diag["n_dup_dialect_key_dropped"] = int(dup_mask.sum())
    diag["n_dup_full_row"] = int(raw.duplicated(keep="first").sum())
    df = raw.loc[~dup_mask].copy().reset_index(drop=True)

    # --- option probabilities recomputed from lA..lD ----------------------
    L = df[["lA", "lB", "lC", "lD"]].to_numpy(dtype=float)
    P = softmax_rows(L)
    answer = df["answer"].to_numpy(dtype=int)
    pred_rc = L.argmax(axis=1)
    # argmax ties in the raw log-probs (two or more options sharing the max)
    n_argmax_ties = int((np.sum(L == L.max(axis=1, keepdims=True), axis=1) > 1).sum())
    p_true_rc = P[np.arange(len(df)), answer]
    p_max_rc = P.max(axis=1)
    correct_rc = (pred_rc == answer).astype(int)

    diag["n_argmax_ties_in_logprobs"] = n_argmax_ties
    diag["n_pred_mismatch"] = int((pred_rc != df["pred"].to_numpy()).sum())
    diag["n_correct_mismatch"] = int((correct_rc != df["correct"].to_numpy()).sum())
    diag["max_abs_diff_p_true"] = float(np.abs(p_true_rc - df["p_true"].to_numpy()).max())
    diag["max_abs_diff_p_max"] = float(np.abs(p_max_rc - df["p_max"].to_numpy()).max())

    # Are all pred mismatches explained by argmax ties in the 4-decimal log-probs, with the file's pred
    # being one of the tied maxima?  (If so, the file's pred was computed at higher precision.)
    tie_rows = np.sum(L == L.max(axis=1, keepdims=True), axis=1) > 1
    mism = pred_rc != df["pred"].to_numpy()
    diag["n_pred_mismatch_off_tie_rows"] = int(np.sum(mism & ~tie_rows))
    diag["n_file_pred_not_a_tied_max"] = int(np.sum(L[np.arange(len(df)), df["pred"].to_numpy()] != L.max(axis=1)))

    for o in range(4):
        df[f"p{o}"] = P[:, o]
    df["p_true_rc"] = p_true_rc
    df["p_max_rc"] = p_max_rc
    df["correct_rc"] = correct_rc          # recomputed with first-index tie-breaking (sensitivity only)
    df["correct_file"] = df["correct"].astype(int)
    df["err"] = 1 - df["correct_file"]     # PRIMARY: errors from the file's correct column
    df["err_rc"] = 1 - df["correct_rc"]

    # --- complete keys ----------------------------------------------------
    present = df.groupby("key")["dialect"].apply(lambda s: set(s))
    complete = sorted(k for k, s in present.items() if set(VARIETIES) <= s)
    diag["n_keys_in_file"] = int(len(present))
    diag["n_complete_keys"] = int(len(complete))
    diag["dialects_in_file"] = sorted(df["dialect"].unique().tolist())
    complete_set = set(complete)
    df = df[df["key"].isin(complete_set)].copy()

    cal = [k for k in splits["calibration"] if k in complete_set]
    test = [k for k in splits["test"] if k in complete_set]
    diag["n_cal_listed"] = len(splits["calibration"])
    diag["n_test_listed"] = len(splits["test"])
    diag["n_cal_used"] = len(cal)
    diag["n_test_used"] = len(test)
    diag["n_cal_test_overlap"] = len(set(cal) & set(test))
    diag["n_complete_keys_in_no_split"] = int(
        len(complete_set - set(splits["calibration"]) - set(splits["test"]) - set(splits["router_train"]))
    )
    df["split"] = np.where(df["key"].isin(set(cal)), "cal", np.where(df["key"].isin(set(test)), "test", "other"))
    return df, diag


# ----------------------------------------------------------------------------
# generic helpers
# ----------------------------------------------------------------------------
def order_by_conf(sub, scol, tie_order):
    """Sort descending by confidence with a fixed, deterministic tie order."""
    if tie_order == "key":
        return sub.sort_values([scol, "key"], ascending=[False, True], kind="mergesort")
    if tie_order == "pessimistic":  # errors first among ties
        return sub.sort_values([scol, "err", "key"], ascending=[False, False, True], kind="mergesort")
    if tie_order == "optimistic":  # correct first among ties
        return sub.sort_values([scol, "err", "key"], ascending=[False, True, True], kind="mergesort")
    raise ValueError(tie_order)


def cum_errors(sub_sorted):
    return np.cumsum(sub_sorted["err"].to_numpy(dtype=np.int64))


def largest_k_meeting(E, target):
    """largest k (1-based) with E_k / k <= target (Fraction), exact integer arithmetic; 0 if none."""
    k = np.arange(1, len(E) + 1, dtype=np.int64)
    ok = E * target.denominator <= target.numerator * k
    idx = np.flatnonzero(ok)
    return int(idx[-1] + 1) if len(idx) else 0


def n_ties(values):
    """number of items involved in a tie (value shared with at least one other item)."""
    v, c = np.unique(values, return_counts=True)
    return int(c[c > 1].sum()), int((c > 1).sum())


def ceil_frac(x: Fraction) -> int:
    return math.ceil(x)


# ----------------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------------
def compute(df, tag, scol="p_max_rc", ptcol="p_true_rc", errcol="err", tie_order="key"):
    """Return dict of result tables for one model."""
    res = {"notes": {}}
    df = df.copy()
    df["err"] = df[errcol].to_numpy()
    test = df[df["split"] == "test"]
    cal = df[df["split"] == "cal"]

    # ---------------- P1 -------------------------------------------------
    msa_t = order_by_conf(test[test["dialect"] == "MSA"], scol, tie_order)
    n = len(msa_t)
    E = cum_errors(msa_t)
    curve = []
    for c in GRID:
        k = ceil_frac(c * n)
        curve.append({"model": tag, "coverage": float(c), "k": k, "risk": E[k - 1] / k})
    k50 = ceil_frac(Fraction(1, 2) * n)
    t50 = Fraction(int(E[k50 - 1]), k50)
    res["notes"]["P1_n_test_msa"] = n
    res["notes"]["P1_k50"] = k50
    res["notes"]["P1_msa_ties_items"], res["notes"]["P1_msa_ties_groups"] = n_ties(msa_t[scol].to_numpy())
    # does a tie straddle the k50 boundary?
    sv = msa_t[scol].to_numpy()
    res["notes"]["P1_tie_at_k50_boundary"] = bool(k50 < n and sv[k50 - 1] == sv[k50])

    p1_rows = []
    ans = {}
    for v in VARIETIES:
        sub = order_by_conf(test[test["dialect"] == v], scol, tie_order)
        Ev = cum_errors(sub)
        K = largest_k_meeting(Ev, t50)
        ans[v] = K / len(sub)
    for v in VARIETIES:
        p1_rows.append({"model": tag, "variety": v, "t50": float(t50), "answerable": ans[v],
                        "d_answerable": ans[v] - ans["MSA"]})
    res["P1"] = pd.DataFrame(p1_rows)
    res["P1_curve"] = pd.DataFrame(curve)

    # ---------------- S4 -------------------------------------------------
    msa_c = order_by_conf(cal[cal["dialect"] == "MSA"], scol, tie_order)
    Ec = cum_errors(msa_c)
    sc = msa_c[scol].to_numpy()
    res["notes"]["S4_n_cal_msa"] = len(msa_c)
    res["notes"]["S4_cal_ties_items"], res["notes"]["S4_cal_ties_groups"] = n_ties(sc)
    s4_rows = []
    taus = {}
    tie_at_K = {}
    for rs in R_STARS:
        target = Fraction(rs)
        K = largest_k_meeting(Ec, target)
        if K == 0:
            tau = NO_THRESHOLD
            tie_at_K[rs] = False
        else:
            tau = float(sc[K - 1])
            tie_at_K[rs] = bool(K < len(sc) and sc[K - 1] == sc[K])
        taus[rs] = (tau, K)
        answered = {}
        risk = {}
        for v in VARIETIES:
            sub = test[test["dialect"] == v]
            a = sub[scol].to_numpy() >= tau
            answered[v] = float(a.mean())
            risk[v] = float(sub["err"].to_numpy()[a].mean()) if a.sum() > 0 else float("nan")
        for v in VARIETIES:
            s4_rows.append({"model": tag, "target_risk": float(target), "tau": tau, "variety": v,
                            "answered": answered[v], "realised_risk": risk[v],
                            "d_answered": answered[v] - answered["MSA"]})
    res["S4"] = pd.DataFrame(s4_rows)
    res["notes"]["S4_K"] = {rs: taus[rs][1] for rs in R_STARS}
    res["notes"]["S4_tau"] = {rs: taus[rs][0] for rs in R_STARS}
    res["notes"]["S4_tie_at_K_boundary"] = tie_at_K

    # ---------------- P2 -------------------------------------------------
    p2_rows = []
    qhat = {}
    qidx = {}
    for al in ALPHAS:
        alpha = Fraction(al)
        for v in VARIETIES:
            nc = np.sort(1.0 - cal.loc[cal["dialect"] == v, ptcol].to_numpy())
            ncal = len(nc)
            m = ceil_frac((ncal + 1) * (1 - alpha))
            m_capped = min(m, ncal)
            qhat[(al, v)] = float(nc[m_capped - 1])
            qidx[(al, v)] = (ncal, m, m_capped)
    res["notes"]["P2_qidx"] = qidx
    size_own = {}
    for al in ALPHAS:
        qm = qhat[(al, "MSA")]
        per_v = {}
        for v in VARIETIES:
            sub = test[test["dialect"] == v]
            nc_true = 1.0 - sub[ptcol].to_numpy()
            NC = 1.0 - sub[["p0", "p1", "p2", "p3"]].to_numpy()
            qv = qhat[(al, v)]
            cov_m = float((nc_true <= qm).mean())
            size_m = float((NC <= qm).sum(axis=1).mean())
            cov_o = float((nc_true <= qv).mean())
            size_o = float((NC <= qv).sum(axis=1).mean())
            per_v[v] = (cov_m, size_m, cov_o, size_o)
        for v in VARIETIES:
            cov_m, size_m, cov_o, size_o = per_v[v]
            p2_rows.append({"model": tag, "alpha": float(Fraction(al)), "variety": v,
                            "qhat_v": qhat[(al, v)], "qhat_msa": qm,
                            "cov_msathr": cov_m, "d_cov": cov_m - per_v["MSA"][0],
                            "size_msathr": size_m, "cov_ownthr": cov_o, "size_ownthr": size_o,
                            "size_ratio": size_o / per_v["MSA"][3]})
    res["P2"] = pd.DataFrame(p2_rows)

    # ---------------- per-key indicators (test keys) ----------------------
    tau020 = taus["0.20"][0]
    qm030 = qhat[("0.30", "MSA")]
    pk = []
    for v in VARIETIES:
        sub = test[test["dialect"] == v].sort_values("key")
        qv = qhat[("0.30", v)]
        s = sub[scol].to_numpy()
        NC = 1.0 - sub[["p0", "p1", "p2", "p3"]].to_numpy()
        pk.append(pd.DataFrame({
            "key": sub["key"].to_numpy(),
            "variety": v,
            "s": s,
            "correct": (1 - sub["err"]).to_numpy().astype(int),
            "answered_at_tau_r020": (s >= tau020).astype(int),
            "covered_at_qmsa_a030": ((1.0 - sub[ptcol].to_numpy()) <= qm030).astype(int),
            "setsize_own_a030": (NC <= qv).sum(axis=1).astype(int),
        }))
    res["perkey"] = pd.concat(pk, ignore_index=True)
    return res


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def fmt(x, nd=4):
    if isinstance(x, float) and math.isnan(x):
        return "NaN"
    return f"{x:.{nd}f}"


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(ROOT, "data", "confirmatory_splits.json")) as fh:
        splits = json.load(fh)

    P1, S4, P2, CURVE = [], [], [], []
    diags, notes, sens, alt_t50 = {}, {}, {}, {}
    for tag in TAGS:
        df, diag = load_model(tag, splits)
        diags[tag] = diag
        primary = compute(df, tag)  # recomputed probabilities, key-order ties
        notes[tag] = primary["notes"]
        P1.append(primary["P1"]); S4.append(primary["S4"]); P2.append(primary["P2"]); CURVE.append(primary["P1_curve"])
        primary["perkey"].to_csv(os.path.join(OUT, f"perkey_{tag}.csv"), index=False)

        # sensitivity: (a) p_true/p_max columns instead of recomputing; (b) tie order;
        #              (c) `correct` recomputed as first-index argmax of the rounded lA..lD
        alt = {}
        alt["columns"] = compute(df, tag, scol="p_max", ptcol="p_true")
        alt["pessimistic"] = compute(df, tag, tie_order="pessimistic")
        alt["optimistic"] = compute(df, tag, tie_order="optimistic")
        alt["argmax_first"] = compute(df, tag, errcol="err_rc")
        sens[tag] = {}
        alt_t50[tag] = {name: r["P1"]["t50"].iloc[0] for name, r in alt.items()}
        for name, r in alt.items():
            d = {}
            for tab in ["P1", "S4", "P2"]:
                a = primary[tab].select_dtypes("number")
                b = r[tab].select_dtypes("number")
                diff = (a - b).abs()
                # NaN realised risks compare equal if both NaN
                diff = diff.where(~(a.isna() & b.isna()), 0.0)
                mx = float(np.nanmax(diff.to_numpy())) if diff.size else 0.0
                where = ""
                if mx > 0:
                    i, j = np.unravel_index(np.nanargmax(diff.to_numpy()), diff.shape)
                    row = primary[tab].iloc[i]
                    lvl = f", r*={row['target_risk']}" if "target_risk" in row else (f", α={row['alpha']}" if "alpha" in row else "")
                    where = f" ({diff.columns[j]}, {row['variety']}{lvl}: {a.iloc[i, j]:.4f} vs {b.iloc[i, j]:.4f})"
                d[tab] = (mx, where)
            d["S4_tau"] = r["notes"]["S4_tau"]
            d["S4_K"] = r["notes"]["S4_K"]
            sens[tag][name] = d

    P1 = pd.concat(P1, ignore_index=True); S4 = pd.concat(S4, ignore_index=True)
    P2 = pd.concat(P2, ignore_index=True); CURVE = pd.concat(CURVE, ignore_index=True)
    P1.to_csv(os.path.join(OUT, "P1_indep.csv"), index=False)
    S4.to_csv(os.path.join(OUT, "S4_indep.csv"), index=False)
    P2.to_csv(os.path.join(OUT, "P2_indep.csv"), index=False)
    CURVE.to_csv(os.path.join(OUT, "P1_msa_curve_indep.csv"), index=False)

    # ------------------------------------------------------------------ notes
    L = []
    L.append("# Independent computational check — notes (Addendum 9 §9.5)\n")
    L.append("Implementation: `scripts/indep_check/recompute.py`, written from `docs/METRIC_DEFINITIONS.md`, "
             "`data/confirmatory_splits.json` and the four `results/confirm_scores_<tag>.csv` files only. "
             "No existing analysis script, plan or report was opened. Point values only (no bootstrap).\n")

    def sline(tag, name, tabs=("P1", "S4", "P2")):
        return "; ".join(f"{t} {sens[tag][name][t][0]:.2e}{sens[tag][name][t][1]}" for t in tabs)

    L.append("## (a) Ambiguities / interpretation choices\n")
    L.append("1. **`correct` cannot be reproduced from the rounded `lA..lD`; the file column is used.** The definitions say "
             "`pred = argmax(lA..lD)`, but the CSV carries the log-probs to 4 decimals and many rows have two or more options tied "
             "at that maximum. Recomputing the argmax (first index on ties) reproduces the file's `pred` for ALLaM and gemma but "
             "not for Fanar and Qwen3; every mismatch is on a tie row and the file's `pred` is always one of the tied options (for "
             "Qwen3 it coincides in 1121/1132 tie rows with the option whose with-space variant `l*_sp` is larger, i.e. the file's "
             "argmax was taken at full precision where the tie is broken below the 4th decimal). Primary results therefore take "
             "errors from the file's `correct` column; p_max/p_true/p_o do not depend on which tied option is the prediction, so "
             "this mixes nothing else. Per model:\n")
    for tag in TAGS:
        d = diags[tag]
        L.append(f"   - {tag}: argmax ties in lA..lD = {d['n_argmax_ties_in_logprobs']} rows; recomputed-vs-file pred mismatches = "
                 f"{d['n_pred_mismatch']} (off tie rows: {d['n_pred_mismatch_off_tie_rows']}; file pred not a tied max: "
                 f"{d['n_file_pred_not_a_tied_max']}); `correct` flips = {d['n_correct_mismatch']}")
    L.append("   Sensitivity (if one *did* recompute `correct` with first-index tie-breaking), max abs change per table: "
             + " | ".join(f"{tag}: {sline(tag, 'argmax_first')}" for tag in TAGS) + ".\n")
    L.append("2. **Probabilities recomputed from lA..lD (primary) vs. the `p_max`/`p_true` columns.** Primary results use "
             "p_o = softmax(lA..lD) recomputed from the four log-probability columns (s = recomputed p_max; nonconformity "
             "1 − recomputed p_true; set sizes from the recomputed p_o), which is the literal definition and keeps P2 internally "
             "consistent (the true option is in the own-threshold set iff the coverage indicator is 1). "
             "Max |recomputed − column|: "
             + "; ".join(f"{tag}: p_true {diags[tag]['max_abs_diff_p_true']:.1e}, p_max {diags[tag]['max_abs_diff_p_max']:.1e}" for tag in TAGS)
             + " (all within the 1e-4 stated in the definitions). Re-running the pipeline with the file columns for s and p_true "
             "(set sizes still from the recomputed p_o) changes the output tables by at most (cell where the max occurs in parentheses):\n")
    for tag in TAGS:
        L.append(f"   - {tag}: {sline(tag, 'columns')}")
    L.append("   These are boundary effects: items sitting exactly on τ or q̂ (each worth 1/1420 = 7.0e-4), or near-tied "
             "calibration items being re-ordered so that K moves. The notable case is Fanar at r*=0.30, where the calibration "
             "cumulative risk hovers at the target: K/τ = "
             + ", ".join(f"{tag} {notes[tag]['S4_K']['0.30']}/{notes[tag]['S4_tau']['0.30']:.5f} (recomputed) vs "
                         f"{sens[tag]['columns']['S4_K']['0.30']}/{sens[tag]['columns']['S4_tau']['0.30']:.5f} (columns)" for tag in TAGS)
             + ". So agreement of the probabilities to 1e-4 does not guarantee agreement of τ(0.30) to better than ~3e-3 or of the "
             "answered fractions to better than ~1e-2 for Fanar; a comparison against the primary analysis should allow for this.\n")
    L.append("3. **Ties in s.** The definitions allow 'any fixed order'. I sort by s descending with `key` ascending as the "
             "deterministic tie-breaker (stable mergesort). Tie counts (items sharing an s value with another item / tie groups) "
             "and whether a tie straddles the decisive boundary:\n")
    for tag in TAGS:
        nt = notes[tag]
        L.append(f"   - {tag}: MSA test (P1): {nt['P1_msa_ties_items']} items in {nt['P1_msa_ties_groups']} groups, "
                 f"tie at the k50={nt['P1_k50']} boundary: {nt['P1_tie_at_k50_boundary']}; "
                 f"MSA calibration (S4): {nt['S4_cal_ties_items']} items in {nt['S4_cal_ties_groups']} groups, "
                 f"tie at the K-th item boundary per r*: {nt['S4_tie_at_K_boundary']}")
    L.append("   Sensitivity: re-running with errors-first ('pessimistic') or correct-first ('optimistic') tie order changes the "
             "P1/S4 tables by at most:\n")
    for tag in TAGS:
        L.append(f"   - {tag}: pessimistic {sline(tag, 'pessimistic', ('P1', 'S4'))}; optimistic {sline(tag, 'optimistic', ('P1', 'S4'))}")
    changed = []
    for tag in TAGS:
        t50_primary = P1[(P1.model == tag) & (P1.variety == "MSA")]["t50"].iloc[0]
        for name in ("pessimistic", "optimistic"):
            if alt_t50[tag][name] != t50_primary:
                changed.append(f"{tag} t50 {t50_primary:.5f} -> {alt_t50[tag][name]:.5f} ({name})")
            for rs in R_STARS:
                if sens[tag][name]["S4_tau"][rs] != notes[tag]["S4_tau"][rs]:
                    changed.append(f"{tag} τ({rs}) {notes[tag]['S4_tau'][rs]:.6f} [K={notes[tag]['S4_K'][rs]}] -> "
                                   f"{sens[tag][name]['S4_tau'][rs]:.6f} [K={sens[tag][name]['S4_K'][rs]}] ({name})")
    L.append("   Thresholds that depend on the tie order: " + ("none (t50 and every τ are identical under all three orders)."
             if not changed else "; ".join(changed) + ". (The 'tie at boundary' flags above only test whether the K-th item is tied "
             "with the next one; a tie group that *starts* right after K with mixed outcomes can also let K extend into it under a "
             "different order, which is what happens here.)") + "\n")
    L.append("4. **Ceilings and ratio comparisons done exactly.** ⌈c·n⌉, ⌈n/2⌉ and ⌈(n_cal+1)(1−α)⌉ are computed with exact "
             "rational arithmetic (`fractions.Fraction`), not floating point, so e.g. 0.05·1420 cannot round to 71.0000…1 and be "
             "ceiled to 72. Likewise the conditions r_k ≤ r*, r_k ≤ t50 are evaluated as exact integer inequalities "
             "(E_k·den ≤ num·k), so a cumulative risk exactly equal to the target counts as meeting it.\n")
    L.append("5. **t50 and τ are the k-th order statistic, not an interpolated quantile.** t50 = r_{⌈n/2⌉}; τ = s of the K-th item "
             "in the calibration MSA ordering (the lowest confidence still meeting the target); 1.01 when no k qualifies. "
             "'s ≥ τ' is applied inclusively on test.\n")
    L.append("6. **Duplicate rule.** 'Exact duplicate (dialect, key) rows' was read as rows sharing the same (dialect, key) pair; "
             "the first occurrence is kept. Counts dropped per model are in (b) (also shown: how many of them were fully identical rows).\n")
    L.append("7. **Complete keys.** A key is complete if, after duplicate dropping, it appears for all seven varieties "
             "{MSA, EGY, SYR, KSA, UAE, MAG, ENG}. Calibration and test lists were intersected with the complete keys; "
             "`router_train` keys are ignored.\n")
    L.append("8. **q̂ cap.** If ⌈(n_cal+1)(1−α)⌉ > n_cal the largest calibration nonconformity is used; the index actually used "
             "is listed in (b). (With n_cal = 808: α=0.20 → 648, α=0.30 → 567; no capping needed.)\n")
    L.append("9. **Per-key files** contain test keys only (the only split on which the three indicators are evaluated), all seven "
             "varieties, columns exactly as specified; `s` is the recomputed p_max and `correct` is the file column (see 1–2).\n")
    L.append("10. **Extra file.** `P1_msa_curve_indep.csv` holds the 20-point MSA risk–coverage curve (k = ⌈c·n⌉ and risk), "
             "which the definitions ask to compute but the specified output CSVs do not carry.\n")
    L.append("11. **Realised risk with nothing answered** is NaN (written as an empty cell in the CSV).\n")

    L.append("## (b) Sizes\n")
    L.append("| model | raw rows | dup (dialect,key) dropped | keys in file | complete keys | calibration used (listed) | test used (listed) | n_cal MSA | n_test MSA | q̂ index α=0.20 / 0.30 (of n_cal) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for tag in TAGS:
        d = diags[tag]; nt = notes[tag]
        q20 = nt["P2_qidx"][("0.20", "MSA")]; q30 = nt["P2_qidx"][("0.30", "MSA")]
        L.append(f"| {tag} | {d['n_raw_rows']} | {d['n_dup_dialect_key_dropped']} (fully identical: {d['n_dup_full_row']}) | "
                 f"{d['n_keys_in_file']} | {d['n_complete_keys']} | {d['n_cal_used']} ({d['n_cal_listed']}) | "
                 f"{d['n_test_used']} ({d['n_test_listed']}) | {nt['S4_n_cal_msa']} | {nt['P1_n_test_msa']} | "
                 f"{q20[2]} / {q30[2]} (of {q20[0]}) |")
    L.append("")
    L.append("Dialects present in every file: " + ", ".join(diags[TAGS[0]]["dialects_in_file"]) +
             ". Calibration/test overlap: " + ", ".join(str(diags[t]["n_cal_test_overlap"]) for t in TAGS) +
             ". Complete keys in no split (router_train excluded): " + ", ".join(str(diags[t]["n_complete_keys_in_no_split"]) for t in TAGS) + ".\n")

    L.append("## (c) Key numbers\n")
    L.append("### t50, S4 τ per r* (K = number of calibration-MSA items answered), q̂_MSA per α\n")
    L.append("| model | t50 | τ(0.15) [K] | τ(0.20) [K] | τ(0.25) [K] | τ(0.30) [K] | q̂_MSA(0.20) | q̂_MSA(0.30) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for tag in TAGS:
        t50 = P1[(P1.model == tag) & (P1.variety == "MSA")]["t50"].iloc[0]
        cells = []
        for rs in R_STARS:
            tau = S4[(S4.model == tag) & (S4.target_risk == float(Fraction(rs))) & (S4.variety == "MSA")]["tau"].iloc[0]
            cells.append(f"{tau:.5f} [{notes[tag]['S4_K'][rs]}]")
        q = [P2[(P2.model == tag) & (P2.alpha == float(Fraction(al))) & (P2.variety == "MSA")]["qhat_msa"].iloc[0] for al in ALPHAS]
        L.append(f"| {tag} | {t50:.5f} | " + " | ".join(cells) + f" | {q[0]:.5f} | {q[1]:.5f} |")
    L.append("")
    L.append("### MAG and SYR: P1 answerable, S4 at r*=0.20, P2 at α=0.30\n")
    L.append("| model | variety | P1 answerable (Δ vs MSA) | S4 answered (Δ) | S4 realised risk | P2 cov@q̂_MSA (Δcov) | P2 size own | size ratio |")
    L.append("|---|---|---|---|---|---|---|---|")
    for tag in TAGS:
        for v in ["MSA", "MAG", "SYR"]:
            p1 = P1[(P1.model == tag) & (P1.variety == v)].iloc[0]
            s4 = S4[(S4.model == tag) & (S4.target_risk == 0.20) & (S4.variety == v)].iloc[0]
            p2 = P2[(P2.model == tag) & (P2.alpha == 0.30) & (P2.variety == v)].iloc[0]
            L.append(f"| {tag} | {v} | {p1.answerable:.4f} ({p1.d_answerable:+.4f}) | {s4.answered:.4f} ({s4.d_answered:+.4f}) | "
                     f"{fmt(s4.realised_risk)} | {p2.cov_msathr:.4f} ({p2.d_cov:+.4f}) | {p2.size_ownthr:.4f} | {p2.size_ratio:.4f} |")
    L.append("")
    L.append("### Full P1 answerable fraction, all varieties\n")
    L.append("| model | " + " | ".join(VARIETIES) + " |")
    L.append("|---|" + "---|" * len(VARIETIES))
    for tag in TAGS:
        L.append(f"| {tag} | " + " | ".join(f"{P1[(P1.model == tag) & (P1.variety == v)]['answerable'].iloc[0]:.4f}" for v in VARIETIES) + " |")
    L.append("")
    L.append("### S4 answered fraction / realised risk at r*=0.20, all varieties\n")
    L.append("| model | " + " | ".join(VARIETIES) + " |")
    L.append("|---|" + "---|" * len(VARIETIES))
    for tag in TAGS:
        cells = []
        for v in VARIETIES:
            r = S4[(S4.model == tag) & (S4.target_risk == 0.20) & (S4.variety == v)].iloc[0]
            cells.append(f"{r.answered:.4f} / {fmt(r.realised_risk)}")
        L.append(f"| {tag} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("### P2 coverage under q̂_MSA / mean set size under own q̂ at α=0.30, all varieties\n")
    L.append("| model | " + " | ".join(VARIETIES) + " |")
    L.append("|---|" + "---|" * len(VARIETIES))
    for tag in TAGS:
        cells = []
        for v in VARIETIES:
            r = P2[(P2.model == tag) & (P2.alpha == 0.30) & (P2.variety == v)].iloc[0]
            cells.append(f"{r.cov_msathr:.4f} / {r.size_ownthr:.3f}")
        L.append(f"| {tag} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("### MSA risk–coverage curve on test (P1 step 1), risk at c = 0.05 … 1.00\n")
    L.append("| model | " + " | ".join(f"{float(c):.2f}" for c in GRID) + " |")
    L.append("|---|" + "---|" * len(GRID))
    for tag in TAGS:
        L.append(f"| {tag} | " + " | ".join(f"{r:.3f}" for r in CURVE[CURVE.model == tag]["risk"]) + " |")
    L.append("")

    with open(os.path.join(OUT, "INDEP_NOTES.md"), "w") as fh:
        fh.write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
