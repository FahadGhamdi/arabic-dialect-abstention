#!/usr/bin/env python
"""Automatic validity layers (ANALYSIS_PLAN Addendum 4). Frozen before any L2/L4 output was read.
 L1  IFM external filter: confirmatory P1/P2/P3/S4 on test after dropping, per dialect, keys whose dialect row is in data/ifm_excluded.json.
 L2  Fidelity covariate: results/fidelity.csv -> terciles of sim_all per dialect on test keys; endpoints per tercile; Spearman with per-key degradation;
     model-assisted-screen flag rate per tercile (audit_in/flags.pkl if present).
 L4  AraDiCE replication: results/aradice_scores_<model>.csv with data/aradice_splits.json -> P1/P2/P3/S4 for EGY/LEV vs MSA.
Usage: ADA_RES=results ADA_DATA=data ADA_B=2000 python scripts/validity_analyze.py [L1|L2|L4|all]"""
import os, sys, json, glob, math, numpy as np, pandas as pd
from scipy import stats
RES=os.environ.get("ADA_RES","results"); DATA=os.environ.get("ADA_DATA","data"); B=int(os.environ.get("ADA_B","2000")); OUT=os.path.join(RES,"validity"); os.makedirs(OUT,exist_ok=True)
WHICH=sys.argv[1] if len(sys.argv)>1 else "all"; rng=np.random.default_rng(0)
MODELS=["ALLaM-7B-Instruct-preview","Fanar-1-9B","Qwen3-8B-Base","gemma-2-9b"]
def qhat(s,a): n=len(s); k=min(n,math.ceil((n+1)*(1-a))); return np.sort(s)[k-1]
def ci(x): x=np.asarray(x,float); return np.nanpercentile(x,2.5),np.nanpercentile(x,97.5)
def rc50(conf,corr):
    o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1); return cum[int(math.ceil(0.5*len(e)))-1]
def ans_at(conf,corr,t):
    o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1); ok=np.where(cum<=t)[0]; return (ok.max()+1)/len(e) if len(ok) else 0.0
def tau_for(cm,cc,r):
    o=np.argsort(-cm); cum=np.cumsum(1-cc[o])/np.arange(1,len(o)+1); ok=np.where(cum<=r)[0]; return cm[o][ok.max()] if len(ok) else 1.01
def endpoints(M,X,qm,tau):
    """M, X: arrays [n,4] = correct,p_true,p_max,pred for MSA and dialect on the SAME keys. Returns dict of paired endpoints."""
    t=rc50(M[:,2],M[:,0])
    return dict(dacc=X[:,0].mean()-M[:,0].mean(), chg=(X[:,3]!=M[:,3]).mean(), dp1=ans_at(X[:,2],X[:,0],t)-ans_at(M[:,2],M[:,0],t),
                dcov=((1-X[:,1])<=qm).mean()-((1-M[:,1])<=qm).mean(), dans=(X[:,2]>=tau).mean()-(M[:,2]>=tau).mean())
def boot(M,X,qm,tau,Bn=B):
    base=endpoints(M,X,qm,tau); n=len(M); bs=[endpoints(M[s],X[s],qm,tau) for s in (rng.integers(0,n,n) for _ in range(Bn))]
    out={}
    for k in base: lo,hi=ci([b[k] for b in bs]); out[k]=base[k]; out[k+"_lo"]=lo; out[k+"_hi"]=hi
    return out
def load_conf(tag,prefix="confirm_scores_"):
    df=pd.read_csv(os.path.join(RES,f"{prefix}{tag}.csv"),dtype={"key":str}); return df.set_index(["key","dialect"])[["correct","p_true","p_max","pred"]]
report=[]
# ---------------------------------------------------------------- L1
if WHICH in ("L1","all"):
    spl=json.load(open(os.path.join(DATA,"confirmatory_splits.json"))); C=sorted(spl["calibration"]); T=sorted(spl["test"])
    excl=json.load(open(os.path.join(DATA,"ifm_excluded.json")))["excluded"]; EX={}
    for d,k in excl: EX.setdefault(d,set()).add(k)
    report.append("# L1 — IFM external filter (935 dialect rows unanimously flagged by 3 LLM judges; confirmatory test, thresholds from calibration)\n")
    report.append("| model | dialect | n keys (orig→kept) | Δacc orig→kept | answer change orig→kept | ΔP1 orig→kept | Δcov@MSA-thr(.30) orig→kept | Δanswered@τ(.20) orig→kept |\n|---|---|---|---|---|---|---|---|")
    rows=[]
    for tag in MODELS:
        sc=load_conf(tag); cal_msa=sc.loc[[(k,"MSA") for k in C]].values; qm=qhat(1-cal_msa[:,1],0.30); tau=tau_for(cal_msa[:,2],cal_msa[:,0],0.20)
        M_all=sc.loc[[(k,"MSA") for k in T]].values
        for d in ["UAE","EGY","KSA","SYR","MAG"]:
            X_all=sc.loc[[(k,d) for k in T]].values; keep=np.array([k not in EX.get(d,set()) for k in T])
            o=boot(M_all,X_all,qm,tau,Bn=400); k_=boot(M_all[keep],X_all[keep],qm,tau,Bn=400)
            f=lambda a,b: f"{100*a:+.1f} → {100*b:+.1f}"
            report.append(f"| {tag} | {d} | {len(T)}→{int(keep.sum())} | {f(o['dacc'],k_['dacc'])} | {100*o['chg']:.1f} → {100*k_['chg']:.1f} | {f(o['dp1'],k_['dp1'])} [{100*k_['dp1_lo']:+.0f},{100*k_['dp1_hi']:+.0f}] | {f(o['dcov'],k_['dcov'])} | {f(o['dans'],k_['dans'])} |")
            rows.append(dict(model=tag,dialect=d,n_orig=len(T),n_kept=int(keep.sum()),**{k:v for k,v in o.items()},**{"kept_"+k:v for k,v in k_.items()}))
    pd.DataFrame(rows).to_csv(os.path.join(OUT,"L1_ifm_filter.csv"),index=False)
    report.append("\nNote: the IFM filter screened only items that strong baselines answered wrongly, so it removes a slightly error-enriched set; a small shrinkage is expected even if defects are unrelated to the dialect cost.\n")
# ---------------------------------------------------------------- L2
if WHICH in ("L2","all") and os.path.exists(os.path.join(RES,"fidelity.csv")):
    fid=pd.read_csv(os.path.join(RES,"fidelity.csv")); spl=json.load(open(os.path.join(DATA,"confirmatory_splits.json"))); C=sorted(spl["calibration"]); T=sorted(spl["test"])
    flags=None
    fp=os.path.join("audit_in","flags.pkl")
    if os.path.exists(fp): flags=pd.read_pickle(fp)
    report.append("\n# L2 — Embedding fidelity covariate (multilingual-e5-large cosine, question+options) on the confirmatory test\n")
    desc=fid.groupby("dialect").sim_all.describe()[["mean","25%","50%","75%"]].round(3); report.append("Fidelity by variety (all 3,135 keys):\n\n"+desc.to_markdown()+"\n")
    if flags is not None:
        fl=flags.reset_index().merge(fid,left_on=["key","d"],right_on=["key","dialect"]); fl["terc"]=fl.groupby("d").sim_all.transform(lambda s: pd.qcut(s.rank(method="first"),3,labels=["low","mid","high"]))
        report.append("Model-assisted-screen flag rate by fidelity tercile (400 screened pairs): "+fl.groupby("terc").basic.mean().round(2).to_dict().__repr__()+"; Spearman(sim_all, flagged) = %.3f (p=%.3g)\n"%stats.spearmanr(fl.sim_all,fl.basic.astype(float)))
    report.append("| model | dialect | tercile | n | Δacc | answer change | ΔP1 [CI] | Δcov@MSA-thr | Δanswered@τ | Spearman(sim, answer-changed) |\n|---|---|---|---|---|---|---|---|---|---|")
    rows=[]
    for tag in MODELS:
        sc=load_conf(tag); cal_msa=sc.loc[[(k,"MSA") for k in C]].values; qm=qhat(1-cal_msa[:,1],0.30); tau=tau_for(cal_msa[:,2],cal_msa[:,0],0.20)
        M_all=sc.loc[[(k,"MSA") for k in T]].values
        for d in ["UAE","EGY","KSA","SYR","MAG"]:
            X_all=sc.loc[[(k,d) for k in T]].values; s=fid[fid.dialect==d].set_index("key").loc[T].sim_all.values
            terc=pd.qcut(pd.Series(s).rank(method="first"),3,labels=["low","mid","high"]).values
            chg=(X_all[:,3]!=M_all[:,3]).astype(float); rho,p=stats.spearmanr(s,chg); rho2,p2=stats.spearmanr(s,X_all[:,1]-M_all[:,1])
            for tname in ["low","mid","high","all"]:
                idx=np.ones(len(T),bool) if tname=="all" else (terc==tname); e=boot(M_all[idx],X_all[idx],qm,tau,Bn=400)
                report.append(f"| {tag} | {d} | {tname} | {int(idx.sum())} | {100*e['dacc']:+.1f} | {100*e['chg']:.1f} | {100*e['dp1']:+.1f} [{100*e['dp1_lo']:+.0f},{100*e['dp1_hi']:+.0f}] | {100*e['dcov']:+.1f} | {100*e['dans']:+.1f} | "+(f"{rho:+.3f} (p={p:.2g}); Δp_true {rho2:+.3f}" if tname=="all" else "")+" |")
                rows.append(dict(model=tag,dialect=d,tercile=tname,n=int(idx.sum()),sim_mean=float(s[idx].mean()),rho_chg=rho,rho_dp=rho2,**e))
    pd.DataFrame(rows).to_csv(os.path.join(OUT,"L2_fidelity.csv"),index=False)
    report.append("\nPre-declared reading rule: top-tercile effect ≥ 2/3 of the full-sample effect → fidelity does not account for it; < 1/3 → it does.\n")
# ---------------------------------------------------------------- L4
if WHICH in ("L4","all"):
    files=sorted(glob.glob(os.path.join(RES,"aradice_scores_*.csv")))
    if files:
        spl=json.load(open(os.path.join(DATA,"aradice_splits.json"))); C=spl["calibration"]; T=spl["test"]
        report.append("\n# L4 — Cross-resource replication: AraDiCE (EGY, LEV; QCRI translations of ArabicMMLU) vs ArabicMMLU MSA; 600 calibration / 1,400 test\n")
        report.append("| model | variety | n test | acc MSA→var | Δacc [CI] | answer change [CI] | ΔP1 [CI] | Δcov@MSA-thr(.30) [CI] | size ratio own-thr | Δanswered@τ(.20) [CI] |\n|---|---|---|---|---|---|---|---|---|---|")
        rows=[]
        for f in files:
            tag=os.path.basename(f)[len("aradice_scores_"):-4]; sc=pd.read_csv(f,dtype={"key":str}).drop_duplicates(["dialect","key"]).set_index(["key","dialect"])
            have=set(k for k,_ in sc.index); Tk=[k for k in T if all((k,v) in sc.index for v in ["MSA","EGY","LEV"])]; Ck=[k for k in C if all((k,v) in sc.index for v in ["MSA","EGY","LEV"])]
            if len(Tk)<0.9*len(T): report.append(f"| {tag} | — | {len(Tk)}/{len(T)} scored: SKIPPED | | | | | | | |"); continue
            cal=sc.loc[[(k,"MSA") for k in Ck]][["correct","p_true","p_max","pred"]].values; qm=qhat(1-cal[:,1],0.30); tau=tau_for(cal[:,2],cal[:,0],0.20)
            M=sc.loc[[(k,"MSA") for k in Tk]][["correct","p_true","p_max","pred"]].values
            for v in ["EGY","LEV"]:
                X=sc.loc[[(k,v) for k in Tk]][["correct","p_true","p_max","pred"]].values; e=boot(M,X,qm,tau)
                # own-threshold size ratio at alpha .30 (P2 cost)
                qo=qhat(1-sc.loc[[(k,v) for k in Ck]].p_true.values,0.30)
                def size(P_rows,q):
                    L=np.stack([P_rows[c].values for c in ["lA","lB","lC","lD"]],1); P=np.exp(L-np.logaddexp.reduce(L,1,keepdims=True)); return ((1-P)<=q).sum(1).mean()
                Xr=sc.loc[[(k,v) for k in Tk]]; Mr=sc.loc[[(k,"MSA") for k in Tk]]
                Xr=pd.read_csv(f,dtype={"key":str}).drop_duplicates(["dialect","key"]).set_index(["key","dialect"]).loc[[(k,v) for k in Tk]]; Mr=pd.read_csv(f,dtype={"key":str}).drop_duplicates(["dialect","key"]).set_index(["key","dialect"]).loc[[(k,"MSA") for k in Tk]]
                ratio=size(Xr,qo)/size(Mr,qm)
                report.append(f"| {tag} | {v} | {len(Tk)} | {M[:,0].mean():.3f}→{X[:,0].mean():.3f} | {100*e['dacc']:+.1f} [{100*e['dacc_lo']:+.1f},{100*e['dacc_hi']:+.1f}] | {100*e['chg']:.1f} [{100*e['chg_lo']:.1f},{100*e['chg_hi']:.1f}] | {100*e['dp1']:+.1f} [{100*e['dp1_lo']:+.0f},{100*e['dp1_hi']:+.0f}] | {100*e['dcov']:+.1f} [{100*e['dcov_lo']:+.1f},{100*e['dcov_hi']:+.1f}] | ×{ratio:.2f} | {100*e['dans']:+.1f} [{100*e['dans_lo']:+.1f},{100*e['dans_hi']:+.1f}] |")
                rows.append(dict(model=tag,variety=v,n=len(Tk),acc_msa=M[:,0].mean(),acc_var=X[:,0].mean(),size_ratio=ratio,**e))
        pd.DataFrame(rows).to_csv(os.path.join(OUT,"L4_aradice.csv"),index=False)
    else: report.append("\n# L4 — AraDiCE: no score files yet.\n")
open(os.path.join(OUT,f"VALIDITY_{WHICH}.md"),"w").write("\n".join(report)); print("\n".join(report))
