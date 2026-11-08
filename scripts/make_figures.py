#!/usr/bin/env python3
"""Figures for the manuscript, drawn from the frozen result files only (no new estimates).

Main figures
  fig1_s4_transfer      S4 operating points at the MSA-calibrated threshold (r* = 0.20): answered fraction vs realised risk,
                        one point per variety with fixed-calibration 95% intervals; 0.20 ceiling. One panel per model.
  fig2_d4_adaptation    D4: for each dialect, the move from the transferred threshold (tau_MSA) to the re-selected one (tau_v).
  fig3_p2_conformal     P2 at alpha = 0.30: coverage loss under the MSA quantile and own-quantile set-size ratio, with the
                        fixed-calibration (thick) and double-resampled (thin) intervals.
  figP1_matched_risk    P1: answerable-fraction difference at the MSA-matched risk (descriptive), with intervals.
Appendix figures
  figA_risk_coverage    risk–coverage curves per variety (from the stored per-item scores; descriptive) with the S4 and P1
                        operating points marked.
  figB_rotations        R2: order-averaged ΔP1 with per-rotation values.
  figC_interval_widths  ratio of double-resampled to fixed-calibration interval widths, per quantity.

Inputs: results/confirm/*.csv, results/diag/D4_variety_threshold.csv, results/sens/S91_calibration_sensitivity.csv,
results/robust/R2_gap_stability.csv, results/confirm_scores_<tag>.csv (curves only).  Output: figures/*.png (600 dpi) and *.pdf.
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'figures')
os.makedirs(OUT, exist_ok=True)

M = ['ALLaM-7B-Instruct-preview', 'Fanar-1-9B', 'Qwen3-8B-Base', 'gemma-2-9b']
MNAME = {'ALLaM-7B-Instruct-preview': 'ALLaM-7B-Instruct-preview', 'Fanar-1-9B': 'Fanar-1-9B', 'Qwen3-8B-Base': 'Qwen3-8B-Base', 'gemma-2-9b': 'gemma-2-9b'}
VAR = ['MSA', 'EGY', 'SYR', 'KSA', 'UAE', 'MAG', 'ENG']
DIAL = ['MAG', 'SYR', 'EGY', 'KSA', 'UAE']          # display order (largest cost first)
# fixed identity -> colour/marker (validated categorical palette; identity also carried by direct labels / markers)
COL = {'MSA': '#0b0b0b', 'EGY': '#2a78d6', 'SYR': '#eb6834', 'KSA': '#008300', 'UAE': '#6250d6', 'MAG': '#e34948', 'ENG': '#8a8984'}
MK = {'MSA': 's', 'EGY': 'o', 'SYR': 'D', 'KSA': '^', 'UAE': 'v', 'MAG': 'P', 'ENG': 'x'}
TXT = '#0b0b0b'; TXT2 = '#52514e'; GRID = '#e3e2de'

plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9, 'axes.labelsize': 8, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
                     'legend.fontsize': 7, 'axes.edgecolor': '#9a9994', 'axes.linewidth': 0.6, 'xtick.color': TXT2,
                     'ytick.color': TXT2, 'axes.labelcolor': TXT, 'text.color': TXT, 'figure.dpi': 110,
                     'savefig.dpi': 600, 'pdf.fonttype': 42, 'font.family': 'DejaVu Sans'})


def style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(True, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), bbox_inches='tight', facecolor='white')
    fig.savefig(os.path.join(OUT, name + '.pdf'), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('wrote', name)


def rd(path):
    return pd.read_csv(os.path.join(ROOT, path))


def place_labels(ax, pts, fontsize=6.5):
    """Greedy collision-avoiding direct labels. pts: list of (x, y, text, color). Tries 8 offsets (points)."""
    fig = ax.figure; fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    placed = []
    # marker boxes (approximate 8pt squares around each point) count as obstacles
    for x, y, t, c in pts:
        px, py = ax.transData.transform((x, y))
        placed.append((px - 5, py - 5, px + 5, py + 5))
    cands = [(6, 4), (6, -9), (-6, 4), (-6, -9), (0, 8), (0, -11), (9, -2), (-9, -2), (12, 6), (-12, 6), (12, -12), (-12, -12)]
    for x, y, t, c in pts:
        best = None
        for dx, dy in cands:
            ha = 'left' if dx > 0 else ('right' if dx < 0 else 'center')
            va = 'bottom' if dy >= 0 else 'top'
            txt = ax.annotate(t, (x, y), xytext=(dx, dy), textcoords='offset points', fontsize=fontsize, color=TXT, ha=ha, va=va, zorder=5)
            bb = txt.get_window_extent(renderer); box = (bb.x0, bb.y0, bb.x1, bb.y1)
            ov = sum(max(0, min(box[2], b[2]) - max(box[0], b[0])) * max(0, min(box[3], b[3]) - max(box[1], b[1])) for b in placed)
            axbb = ax.get_window_extent(renderer)
            if box[0] < axbb.x0 or box[2] > axbb.x1 or box[1] < axbb.y0 or box[3] > axbb.y1:
                ov += 1e6
            if best is None or ov < best[0]:
                best = (ov, dx, dy, box)
            txt.remove()
            if ov == 0:
                break
        ov, dx, dy, box = best
        ha = 'left' if dx > 0 else ('right' if dx < 0 else 'center'); va = 'bottom' if dy >= 0 else 'top'
        ax.annotate(t, (x, y), xytext=(dx, dy), textcoords='offset points', fontsize=fontsize, color=TXT, ha=ha, va=va, zorder=5)
        placed.append(box)


# ------------------------------------------------------------------ Figure 1: S4 transfer
def fig1():
    s4 = rd('results/confirm/S4_operational_selective.csv')
    s4 = s4[np.isclose(s4.target_risk, 0.20)]
    fig, axes = plt.subplots(2, 2, figsize=(6.9, 5.4), sharex=True, sharey=True)
    for ax, m in zip(axes.ravel(), M):
        d = s4[s4.model == m].set_index('variety')
        style(ax)
        ax.axhline(0.20, color='#52514e', lw=0.8, ls='--', zorder=1)
        ax.text(0.845, 0.203, 'target risk 0.20', ha='right', va='bottom', fontsize=6.5, color=TXT2)
        pts = []
        for v in VAR:
            r = d.loc[v]
            ax.errorbar(r.answered, r.realised_risk, xerr=[[r.answered - r.ans_lo], [r.ans_hi - r.answered]],
                        yerr=[[r.realised_risk - r.risk_lo], [r.risk_hi - r.realised_risk]], fmt='none', ecolor=COL[v], elinewidth=0.8, capsize=0, alpha=0.9, zorder=2)
            face = 'white' if v == 'MSA' else COL[v]
            ax.plot(r.answered, r.realised_risk, marker=MK[v], ms=5.5 if v != 'ENG' else 6, mfc=face, mec=COL[v], mew=1.2, ls='none', zorder=3)
            pts.append((r.answered, r.realised_risk, v, COL[v]))
        ax.set_title(f'{MNAME[m]}   τ_MSA = {s4[s4.model == m].tau.iloc[0]:.3f}', loc='left')
        ax.set_xlim(0.2, 0.85); ax.set_ylim(0.08, 0.36)
        place_labels(ax, pts)
    for ax in axes[1]:
        ax.set_xlabel('answered fraction at the MSA-calibrated threshold')
    for ax in axes[:, 0]:
        ax.set_ylabel('realised risk among answered questions')
    fig.tight_layout()
    save(fig, 'fig1_s4_transfer')


# ------------------------------------------------------------------ Figure 2: D4 adaptation
def fig2():
    d4 = rd('results/diag/D4_variety_threshold.csv')
    d4 = d4[np.isclose(d4.target_risk, 0.20)]
    fig, axes = plt.subplots(2, 2, figsize=(6.9, 5.6), sharex=True, sharey=True)
    for ax, m in zip(axes.ravel(), M):
        d = d4[d4.model == m].set_index('variety')
        style(ax)
        ax.axhline(0.20, color='#52514e', lw=0.8, ls='--', zorder=1)
        msa = d.loc['MSA']
        ax.plot(msa.answered_msa_at_msa_thr, msa.realised_risk_msa_thr, marker='s', ms=6, mfc='white', mec=COL['MSA'], mew=1.2, ls='none', zorder=3)
        pts = [(msa.answered_msa_at_msa_thr, msa.realised_risk_msa_thr, 'MSA', COL['MSA'])]
        for v in DIAL:
            r = d.loc[v]
            x0, y0 = r.answered_msa_thr, r.realised_risk_msa_thr
            x1, y1 = r.answered_v_thr, r.realised_risk_v_thr
            ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='-|>', color=COL[v], lw=1.0, shrinkA=3, shrinkB=3), zorder=2)
            ax.plot(x0, y0, marker=MK[v], ms=5, mfc='white', mec=COL[v], mew=1.1, ls='none', zorder=3)
            ax.plot(x1, y1, marker=MK[v], ms=5, mfc=COL[v], mec=COL[v], mew=1.1, ls='none', zorder=3)
            ax.errorbar(x1, y1, yerr=[[y1 - r.risk_lo], [r.risk_hi - y1]], fmt='none', ecolor=COL[v], elinewidth=0.6, alpha=0.6, zorder=2)
            pts.append((x0, y0, v, COL[v]))
        ax.set_title(MNAME[m], loc='left')
        ax.set_xlim(0.15, 0.7); ax.set_ylim(0.1, 0.36)
        place_labels(ax, pts)
    for ax in axes[1]:
        ax.set_xlabel('answered fraction')
    for ax in axes[:, 0]:
        ax.set_ylabel('realised risk among answered')
    handles = [Line2D([], [], marker='o', mfc='white', mec=TXT2, ls='none', label='under the transferred threshold τ_MSA'),
               Line2D([], [], marker='o', mfc=TXT2, mec=TXT2, ls='none', label='under the re-selected threshold τ_v (same rule, target 0.20, dialect calibration items)'),
               Line2D([], [], color='#52514e', lw=0.8, ls='--', label='target risk 0.20 (ceiling)')]
    fig.legend(handles=handles, loc='lower center', ncol=1, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, 'fig2_d4_adaptation')


# ------------------------------------------------------------------ Figure 3: P2 conformal
def fig3():
    p2 = rd('results/confirm/P2_conformal.csv'); p2 = p2[np.isclose(p2.alpha, 0.30)]
    s91 = rd('results/sens/S91_calibration_sensitivity.csv')
    fig, axes = plt.subplots(2, 4, figsize=(6.9, 4.2), sharey=True)
    y = np.arange(len(DIAL))[::-1]
    for j, m in enumerate(M):
        a = p2[p2.model == m].set_index('variety'); b = s91[s91.model == m].set_index('variety')
        for i, (key, lo, hi, rlo, rhi, ref, lab) in enumerate([('d_cov', 'd_cov_lo', 'd_cov_hi', 'p2_dcov_lo_rs', 'p2_dcov_hi_rs', 0.0, 'coverage − MSA coverage under the MSA quantile (points)'),
                                                            ('size_ratio', 'size_ratio_lo', 'size_ratio_hi', 'p2_szr_lo_rs', 'p2_szr_hi_rs', 1.0, 'mean set size under the own quantile ÷ MSA')]):
            ax = axes[i, j]; style(ax)
            ax.axvline(ref, color='#52514e', lw=0.8, ls='--', zorder=1)
            for yy, v in zip(y, DIAL):
                # point estimate: plug-in difference (the released d_cov column is a bootstrap mean; 2026-11-08)
                val = (a.loc[v, 'cov_msathr'] - a.loc['MSA', 'cov_msathr']) if key == 'd_cov' else a.loc[v, key]; scale = 100 if key == 'd_cov' else 1
                ax.plot([b.loc[v, rlo] * scale, b.loc[v, rhi] * scale], [yy, yy], color=COL[v], lw=0.9, alpha=0.9, zorder=2)
                ax.plot([a.loc[v, lo] * scale, a.loc[v, hi] * scale], [yy, yy], color=COL[v], lw=3.2, solid_capstyle='butt', zorder=3)
                ax.plot(val * scale, yy, marker='o', ms=3.2, mfc='white', mec=COL[v], mew=0.9, ls='none', zorder=4)
            ax.set_yticks(y); ax.set_yticklabels(DIAL)
            if i == 0:
                ax.set_title(MNAME[m].replace('ALLaM-7B-Instruct-preview', 'ALLaM-7B-\nInstruct-preview'), loc='left', fontsize=7.5)
                ax.set_xlim(-16, 1); ax.set_xlabel('Δ coverage (pp)' if j == 0 else '')
            else:
                ax.set_xlim(0.98, 1.42); ax.set_xlabel('set-size ratio' if j == 0 else '')
            if j == 0:
                ax.set_ylabel(['coverage loss under\nthe MSA quantile', 'set size under the\nown quantile ÷ MSA'][i])
    handles = [Line2D([], [], color=TXT2, lw=3.2, label='95% interval, calibration sample fixed (B = 2000)'),
               Line2D([], [], color=TXT2, lw=0.9, label='95% interval, calibration and test resampled with q̂ re-selected (B = 1000)')]
    fig.legend(handles=handles, loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, 'fig3_p2_conformal')


# ------------------------------------------------------------------ P1 panel
def figp1():
    p1 = rd('results/confirm/P1_selective.csv')
    fig, ax = plt.subplots(figsize=(3.4, 3.0)); style(ax)
    ax.axvline(0, color='#52514e', lw=0.8, ls='--')
    y = np.arange(len(DIAL))[::-1]
    off = np.linspace(0.27, -0.27, 4)
    mm = {'ALLaM-7B-Instruct-preview': 'o', 'Fanar-1-9B': 's', 'Qwen3-8B-Base': 'D', 'gemma-2-9b': '^'}
    for k, m in enumerate(M):
        d = p1[p1.model == m].set_index('variety')
        for yy, v in zip(y, DIAL):
            r = d.loc[v]
            ax.plot([r.d_lo, r.d_hi], [yy + off[k]] * 2, color=COL[v], lw=1.0, alpha=0.9)
            ax.plot(r.answerable - d.loc['MSA', 'answerable'], yy + off[k], marker=mm[m], ms=3.6, mfc='white', mec=COL[v], mew=0.9, ls='none')   # plug-in difference
    ax.set_yticks(y); ax.set_yticklabels(DIAL)
    ax.set_xlabel('answerable fraction at the MSA-matched risk: dialect − MSA (MSA ≈ 0.50)')
    handles = [Line2D([], [], marker=mm[m], mfc='white', mec=TXT2, ls='none', label=MNAME[m]) for m in M]
    ax.legend(handles=handles, frameon=False, loc='upper center', ncol=2, handletextpad=0.3, bbox_to_anchor=(0.5, -0.28), columnspacing=1.0)
    fig.tight_layout()
    save(fig, 'figP1_matched_risk')


# ------------------------------------------------------------------ Appendix A: risk–coverage curves
def figA():
    import json
    splits = json.load(open(os.path.join(ROOT, 'data/confirmatory_splits.json')))
    test = set(splits['test'])
    s4 = rd('results/confirm/S4_operational_selective.csv'); s4 = s4[np.isclose(s4.target_risk, 0.20)]
    p1 = rd('results/confirm/P1_selective.csv')
    fig, axes = plt.subplots(2, 2, figsize=(6.9, 5.6), sharex=True, sharey=True)
    for ax, m in zip(axes.ravel(), M):
        sc = pd.read_csv(os.path.join(ROOT, f'results/confirm_scores_{m}.csv'))
        sc = sc[sc.key.isin(test)].drop_duplicates(['dialect', 'key'])
        style(ax)
        tau = s4[s4.model == m].tau.iloc[0]
        t50 = p1[(p1.model == m) & (p1.variety == 'MSA')].msa_matched_risk.iloc[0]
        ax.axhline(t50, color='#9a9994', lw=0.7, ls=':', zorder=1)
        ax.axhline(0.20, color='#52514e', lw=0.8, ls='--', zorder=1)
        for v in VAR:
            d = sc[sc.dialect == v].sort_values('p_max', ascending=False)
            err = (1 - d.correct.values).astype(float)
            cov = np.arange(1, len(d) + 1) / len(d)
            risk = np.cumsum(err) / np.arange(1, len(d) + 1)
            keep = cov >= 0.1
            ax.plot(cov[keep], risk[keep], color=COL[v], lw=1.1 if v in ('MSA', 'MAG', 'SYR') else 0.8, alpha=0.95 if v != 'ENG' else 0.7, label=v, zorder=2)
            ans = float((d.p_max >= tau).mean())
            rr = float(risk[int(round(ans * len(d))) - 1]) if ans > 0 else np.nan
            ax.plot(ans, rr, marker=MK[v], ms=4.5, mfc='white' if v == 'MSA' else COL[v], mec=COL[v], mew=1.0, ls='none', zorder=3)
        ax.set_title(f'{MNAME[m]}\nτ_MSA = {tau:.3f};  MSA risk at 50% coverage = {t50:.3f}', loc='left', fontsize=7.5)
    for ax in axes[1]:
        ax.set_xlabel('coverage (fraction answered, most confident first)')
    for ax in axes[:, 0]:
        ax.set_ylabel('cumulative risk')
    axes[0, 0].set_xlim(0.1, 1.0); axes[0, 0].set_ylim(0.0, 0.5)
    handles = [Line2D([], [], color=COL[v], lw=1.2, marker=MK[v], mfc='white' if v == 'MSA' else COL[v], mec=COL[v], ms=4, label=v) for v in VAR]
    handles += [Line2D([], [], color='#52514e', lw=0.8, ls='--', label='target risk 0.20'), Line2D([], [], color='#9a9994', lw=0.7, ls=':', label='MSA risk at 50% coverage (P1 reference)')]
    fig.legend(handles=handles, loc='lower center', ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, 'figA_risk_coverage')


# ------------------------------------------------------------------ Appendix B: rotations
def figB():
    r2 = rd('results/robust/R2_gap_stability.csv')
    fig, axes = plt.subplots(1, 4, figsize=(6.9, 2.6), sharey=True, sharex=True)
    y = np.arange(len(DIAL))[::-1]
    for ax, m in zip(axes, M):
        d = r2[r2.model == m].set_index('variety'); style(ax)
        ax.axvline(0, color='#52514e', lw=0.8, ls='--')
        for yy, v in zip(y, DIAL):
            r = d.loc[v]
            ax.plot([r.d_p1_lo, r.d_p1_hi], [yy, yy], color=COL[v], lw=1.0)
            ax.plot([r.d_p1_k0, r.d_p1_k1, r.d_p1_k2, r.d_p1_k3], [yy + 0.18] * 4, marker='|', ms=5, color=COL[v], ls='none', alpha=0.8)
            ax.plot(r.d_p1_avg, yy, marker='o', ms=3.6, mfc='white', mec=COL[v], mew=0.9, ls='none')
        ax.set_yticks(y); ax.set_yticklabels(DIAL); ax.set_title(MNAME[m], loc='left')
    axes[0].set_xlabel('ΔP1 (dialect − MSA), 500 keys');
    handles = [Line2D([], [], marker='|', ms=6, color=TXT2, ls='none', label='each of the four option rotations'),
               Line2D([], [], marker='o', mfc='white', mec=TXT2, ls='-', color=TXT2, label='order-averaged ΔP1 with 95% key-bootstrap interval')]
    fig.legend(handles=handles, loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, 'figB_rotations')


# ------------------------------------------------------------------ Appendix C: interval widths
def figC():
    s = rd('results/sens/S91_calibration_sensitivity.csv'); s = s[s.variety.isin(DIAL)]
    q = {'S4 Δanswered': s.s4_width_ratio, 'P2 Δcoverage': s.p2_dcov_width_ratio, 'P2 set-size ratio': s.p2_szr_width_ratio,
         'D4 residual gap': (s.d4_res_hi_rs - s.d4_res_lo_rs) / (s.d4_res_hi_orig - s.d4_res_lo_orig)}
    fig, ax = plt.subplots(figsize=(4.6, 2.6)); style(ax)
    ax.axhline(1, color='#52514e', lw=0.8, ls='--')
    rng = np.random.default_rng(0)
    for i, (k, vals) in enumerate(q.items()):
        x = i + rng.uniform(-0.18, 0.18, len(vals))
        for xx, vv, v in zip(x, vals, s.variety):
            ax.plot(xx, vv, marker=MK[v], ms=4, mfc=COL[v], mec=COL[v], ls='none', alpha=0.85)
    ax.set_xticks(range(len(q))); ax.set_xticklabels(list(q.keys()))
    ax.set_ylabel('interval width: double-resampled ÷ fixed-calibration')
    handles = [Line2D([], [], marker=MK[v], mfc=COL[v], mec=COL[v], ls='none', label=v) for v in DIAL]
    ax.legend(handles=handles, frameon=False, ncol=5, loc='upper left', handletextpad=0.2, columnspacing=0.8)
    ax.set_ylim(0.5, 5)
    fig.tight_layout()
    save(fig, 'figC_interval_widths')


if __name__ == '__main__':
    fig1(); fig2(); fig3(); figp1(); figA(); figB(); figC()
