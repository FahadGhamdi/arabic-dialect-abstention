#!/usr/bin/env python
"""Exploratory diagnostic of the sources of the reliability cost (ANALYSIS_PLAN.md Addendum 7; specified after the confirmatory
results were seen and BEFORE this script was run). Frozen before execution (sha256 in the Addendum 7 freeze line / PILOT_NOTES). v1.1 (after the run): figure title shortened and a common AUROC y-range; no number changed — frozen v1 kept as diag_analyze_v1_frozen.py.
D1 AUROC(p_max -> correct), D2 AUGRC (Traub et al. 2024), D3 paired differences vs MSA, D4 S4 extension with a variety-specific
threshold tau_v chosen on the calibration items of that variety, D5 three-panel figure.
Inputs : $ADA_RES/confirm_scores_<tag>.csv, $ADA_DATA/confirmatory_splits.json.
Outputs: $ADA_RES/diag/{D1_D2_discrimination.csv, D4_variety_threshold.csv, DIAG_REPORT.md, diag_figure.png, diag_figure.pdf}
Rules  : test keys only for estimates; thresholds from calibration keys; paired bootstrap over test keys (B=2000, default_rng(0)),
         thresholds held fixed. No reading rule beyond Addendum 7 §7.4 is applied here.
Usage  : ADA_RES=results ADA_DATA=data ADA_B=2000 python scripts/diag_analyze.py"""
import os, json, glob, math, numpy as np, pandas as pd
from scipy.stats import rankdata
RES=os.environ.get("ADA_RES","results"); DATA=os.environ.get("ADA_DATA","data")
SPL=os.environ.get("ADA_SPLITS",os.path.join(DATA,"confirmatory_splits.json")); OUT=os.path.join(RES,"diag"); os.makedirs(OUT,exist_ok=True)
B=int(os.environ.get("ADA_B","2000")); rng=np.random.default_rng(0)
MSA="MSA"; ENG="ENG"; RSTARS=[0.15,0.20,0.25,0.30]; R_PRIMARY=0.20; FIG_ORDER=["MSA","EGY","SYR","KSA","UAE","MAG"]
def ci(x): x=np.asarray(x,float); return float(np.nanpercentile(x,2.5)), float(np.nanpercentile(x,97.5))
def auroc(conf,corr):
    """P(conf_correct > conf_incorrect) with ties counted 1/2 (Mann-Whitney)."""
    pos=corr==1; n1=pos.sum(); n0=len(corr)-n1
    if n1==0 or n0==0: return float("nan")
    r=rankdata(conf); return float((r[pos].sum()-n1*(n1+1)/2)/(n1*n0))
def augrc(conf,corr):
    """Area under the generalized risk-coverage curve: GR(c)=#errors among the c*n most confident / n, mean over the n steps."""
    o=np.argsort(-conf,kind="stable"); e=1-corr[o]; n=len(e); gr=np.cumsum(e)/n; return float(gr.mean())
def tau_rule(conf_cal,corr_cal,rstar):
    """S4 rule: lowest confidence whose cumulative calibration risk (items at or above it) is <= r*; 1.01 if none."""
    o=np.argsort(-conf_cal); cum=np.cumsum(1-corr_cal[o])/np.arange(1,len(o)+1); ok=np.where(cum<=rstar)[0]
    return float(conf_cal[o][ok.max()]) if len(ok) else 1.01
splits=json.load(open(SPL)); C_KEYS=set(splits["calibration"]); T_KEYS=set(splits["test"]); assert not (C_KEYS&T_KEYS)
rep=[f"# Exploratory diagnostic of the sources of the reliability cost (Addendum 7)\n\nTest keys {len(T_KEYS)}, calibration keys {len(C_KEYS)}; B={B} paired bootstrap resamples over test keys; thresholds fixed from calibration. Confidence = p_max. Exploratory: specified after the confirmatory results were seen and before computation.\n"]
D12=[]; D4=[]; FIG={}
for fn in sorted(glob.glob(os.path.join(RES,"confirm_scores_*.csv"))):
    tag=os.path.basename(fn)[len("confirm_scores_"):-4]; df=pd.read_csv(fn).drop_duplicates(["dialect","key"])
    D=sorted(df.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); im=D.index(MSA)
    complete=set.intersection(*[set(df[df.dialect==d].key) for d in D]); tk=sorted(T_KEYS&complete); ck=sorted(C_KEYS&complete)
    def arrs(keys):
        sub=df[df.key.isin(keys)]; piv=lambda c: sub.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
        return dict(C=piv("correct").astype(float),PM=piv("p_max").astype(float))
    T=arrs(tk); Cc=arrs(ck); n=len(tk); BS=[rng.integers(0,n,n) for _ in range(B)]
    rep.append(f"\n## {tag}: test keys {n}/{len(T_KEYS)}, calibration {len(ck)}/{len(C_KEYS)}\n")
    # ---------- D1-D3 discrimination ----------
    rep.append("### D1-D3 Discrimination of p_max (test)\n\n| variety | acc | AUROC [CI] | ΔAUROC vs MSA [CI] | AUGRC [CI] | ΔAUGRC vs MSA [CI] |\n|---|---|---|---|---|---|")
    au_m=[auroc(T["PM"][s,im],T["C"][s,im]) for s in BS]; ag_m=[augrc(T["PM"][s,im],T["C"][s,im]) for s in BS]
    for j,d in enumerate(D):
        a=auroc(T["PM"][:,j],T["C"][:,j]); g=augrc(T["PM"][:,j],T["C"][:,j])
        ab=[auroc(T["PM"][s,j],T["C"][s,j]) for s in BS]; gb=[augrc(T["PM"][s,j],T["C"][s,j]) for s in BS]
        da=np.array(ab)-np.array(au_m); dg=np.array(gb)-np.array(ag_m)
        alo,ahi=ci(ab); glo,ghi=ci(gb); dalo,dahi=ci(da); dglo,dghi=ci(dg)
        acc=T["C"][:,j].mean(); dA=a-auroc(T["PM"][:,im],T["C"][:,im]); dG=g-augrc(T["PM"][:,im],T["C"][:,im])
        rep.append(f"| {d} | {acc:.3f} | {a:.3f} [{alo:.3f},{ahi:.3f}] | {dA:+.3f} [{dalo:+.3f},{dahi:+.3f}] | {g:.3f} [{glo:.3f},{ghi:.3f}] | {dG:+.3f} [{dglo:+.3f},{dghi:+.3f}] |")
        D12.append(dict(model=tag,variety=d,n_test=n,acc=acc,auroc=a,auroc_lo=alo,auroc_hi=ahi,d_auroc=dA,d_auroc_lo=dalo,d_auroc_hi=dahi,augrc=g,augrc_lo=glo,augrc_hi=ghi,d_augrc=dG,d_augrc_lo=dglo,d_augrc_hi=dghi))
    # ---------- D4 variety-specific threshold (S4 extension) ----------
    rep.append("\n### D4 S4 extension: τ_v chosen on calibration items of variety v (same rule, same r*), applied to test items of v\n\n| r* | variety | τ_MSA | τ_v | answered@τ_MSA | answered@τ_v [CI] | realised risk@τ_v [CI] | recoverable = ans_v(τ_v) − ans_v(τ_MSA) [CI] | residual gap = ans_v(τ_v) − ans_MSA(τ_MSA) [CI] |\n|---|---|---|---|---|---|---|---|---|")
    for rstar in RSTARS:
        tm=tau_rule(Cc["PM"][:,im],Cc["C"][:,im],rstar); ansm=T["PM"][:,im]>=tm
        for j,d in enumerate(D):
            tv=tau_rule(Cc["PM"][:,j],Cc["C"][:,j],rstar); av=T["PM"][:,j]>=tv; am=T["PM"][:,j]>=tm
            frac=av.mean(); risk=(1-T["C"][av,j]).mean() if av.any() else float("nan")
            fb=[av[s].mean() for s in BS]; rb=[(1-T["C"][s,j][av[s]]).mean() if av[s].any() else np.nan for s in BS]
            rec=[av[s].mean()-am[s].mean() for s in BS]; res=[av[s].mean()-ansm[s].mean() for s in BS]
            flo,fhi=ci(fb); rlo,rhi=ci(rb); reclo,rechi=ci(rec); reslo,reshi=ci(res)
            recp=frac-am.mean(); resp=frac-ansm.mean()
            rep.append(f"| {rstar:.2f} | {d} | {tm:.3f} | {tv:.3f} | {am.mean():.3f} | {frac:.3f} [{flo:.3f},{fhi:.3f}] | {risk:.3f} [{rlo:.3f},{rhi:.3f}] | {recp:+.3f} [{reclo:+.3f},{rechi:+.3f}] | {resp:+.3f} [{reslo:+.3f},{reshi:+.3f}] |")
            D4.append(dict(model=tag,target_risk=rstar,variety=d,tau_msa=tm,tau_v=tv,answered_msa_thr=am.mean(),answered_v_thr=frac,ans_lo=flo,ans_hi=fhi,realised_risk_v_thr=risk,risk_lo=rlo,risk_hi=rhi,
                           recoverable=recp,rec_lo=reclo,rec_hi=rechi,residual_gap=resp,res_lo=reslo,res_hi=reshi,answered_msa_at_msa_thr=ansm.mean(),
                           realised_risk_msa_thr=((1-T["C"][am,j]).mean() if am.any() else float("nan"))))
    FIG[tag]=dict(D=D)
pd.DataFrame(D12).to_csv(os.path.join(OUT,"D1_D2_discrimination.csv"),index=False); pd.DataFrame(D4).to_csv(os.path.join(OUT,"D4_variety_threshold.csv"),index=False)
# ---------- D5 figure: one row per model; accuracy | AUROC with CI | answered@r*=0.20 under τ_MSA vs τ_v (realised risk annotated) ----------
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d12=pd.DataFrame(D12); d4=pd.DataFrame(D4); models=sorted(d12.model.unique()); C1,C2,INK,MUTED="#2a78d6","#eb6834","#0b0b0b","#52514e"
plt.rcParams.update({"font.size":8.5,"axes.edgecolor":"#9a9892","axes.linewidth":0.6,"xtick.color":INK,"ytick.color":INK,"axes.labelcolor":INK,"text.color":INK})
fig,axes=plt.subplots(len(models),3,figsize=(10.5,2.3*len(models)),squeeze=False)
for r,m in enumerate(models):
    a=d12[d12.model==m].set_index("variety").reindex(FIG_ORDER); b=d4[(d4.model==m)&(d4.target_risk==R_PRIMARY)].set_index("variety").reindex(FIG_ORDER); x=np.arange(len(FIG_ORDER))
    ax=axes[r,0]; ax.bar(x,a.acc,color=C1,width=0.6); ax.set_ylim(0,1); ax.set_ylabel(m.replace("-Instruct-preview",""),fontweight="bold")
    for i,v in enumerate(a.acc): ax.text(i,v+0.02,f"{v:.2f}",ha="center",va="bottom",fontsize=7,color=MUTED)
    if r==0: ax.set_title("Accuracy (test, 1,420 keys)",fontsize=9)
    ax=axes[r,1]; ax.errorbar(x,a.auroc,yerr=[a.auroc-a.auroc_lo,a.auroc_hi-a.auroc],fmt="o",color=C1,ms=5,capsize=2,lw=1)
    ax.axhline(a.loc["MSA","auroc"],color=MUTED,lw=0.8,ls=":"); ax.set_ylim(0.65,0.87)
    if r==0: ax.set_title("AUROC of p_max for correctness [95% CI]",fontsize=9)
    ax=axes[r,2]; w=0.38; ax.bar(x-w/2,b.answered_msa_thr,width=w,color=C2,label="τ chosen on MSA (S4)"); ax.bar(x+w/2,b.answered_v_thr,width=w,color=C1,label="τ chosen on the variety")
    for i,(v1,v2,k1,k2) in enumerate(zip(b.answered_msa_thr,b.answered_v_thr,b.realised_risk_msa_thr,b.realised_risk_v_thr)):
        ax.text(i-w/2,v1+0.01,f"r={k1:.2f}",ha="center",va="bottom",fontsize=6,color=MUTED,rotation=90); ax.text(i+w/2,v2+0.01,f"r={k2:.2f}",ha="center",va="bottom",fontsize=6,color=MUTED,rotation=90)
    ax.set_ylim(0,1)
    if r==0: ax.set_title(f"Answered fraction at target risk r*={R_PRIMARY:.2f} (r = realised risk)",fontsize=9); ax.legend(frameon=False,fontsize=7,loc="upper right")
    for c in range(3):
        axes[r,c].set_xticks(x); axes[r,c].set_xticklabels(FIG_ORDER); axes[r,c].spines[["top","right"]].set_visible(False); axes[r,c].grid(axis="y",color="#e6e5e0",lw=0.6); axes[r,c].set_axisbelow(True)
fig.suptitle("Diagnostic views of the reliability cost (exploratory; specified after the confirmatory results, before computation)",fontsize=9.5,y=0.995)
fig.tight_layout(rect=(0,0,1,0.98)); fig.savefig(os.path.join(OUT,"diag_figure.png"),dpi=200); fig.savefig(os.path.join(OUT,"diag_figure.pdf"))
open(os.path.join(OUT,"DIAG_REPORT.md"),"w").write("\n".join(rep)+"\n"); print("\n".join(rep)); print("written",OUT)
