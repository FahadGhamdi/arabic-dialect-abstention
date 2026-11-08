#!/usr/bin/env python
"""Stage 4: paired analysis per model. Accuracy, ECE, Brier, AUROC, split-conformal coverage
(MSA-calibrated, alpha=0.10, cross-fitted over 2 folds) vs Mondrian (same-dialect) calibration.
Bootstrap over question keys (paired across dialects). Writes results/pilot_summary.md + CSVs."""
import os, sys, json, glob, math
import numpy as np, pandas as pd
RES=os.environ["ADA_RES"]; OUT=os.environ["ADA_DATA"]
meta=json.load(open(os.path.join(OUT,"pilot_keys.json"))); MSA=meta["MSA"]; ENG=meta["ENG"]
ALPHA=0.10; B=2000; rng=np.random.default_rng(0)
def ece(p,c,nb=15):
    bins=np.minimum((p*nb).astype(int),nb-1); e=0
    for b in range(nb):
        m=bins==b
        if m.any(): e+=m.mean()*abs(p[m].mean()-c[m].mean())
    return e
def rankdata(a):
    a=np.asarray(a); order=np.argsort(a,kind='mergesort'); r=np.empty(len(a)); r[order]=np.arange(1,len(a)+1)
    # average ties
    sa=a[order]; i=0
    while i<len(a):
        j=i
        while j+1<len(a) and sa[j+1]==sa[i]: j+=1
        if j>i: r[order[i:j+1]]=(i+j+2)/2
        i=j+1
    return r
def auroc(s,y):
    if y.sum()==0 or y.sum()==len(y): return np.nan
    r=rankdata(s); n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def qhat(scores):
    n=len(scores); k=math.ceil((n+1)*(1-ALPHA)); k=min(k,n)
    return np.sort(scores)[k-1]
lines=["# Pilot summary — DialectalArabicMMLU, paired by question key\n",
       f"alpha={ALPHA}; conformal score = 1 - p(true option); 2-fold cross-fitting over keys; {B} bootstrap resamples over keys.\n"]
allsum=[]
for fn in sorted(glob.glob(os.path.join(RES,"scores_*.csv"))):
    df=pd.read_csv(fn); tag=os.path.basename(fn)[7:-4]
    df=df.drop_duplicates(["dialect","key"])
    keys=sorted(set.intersection(*[set(df[df.dialect==d].key) for d in df.dialect.unique()]))
    df=df[df.key.isin(keys)]
    dial=[d for d in df.dialect.unique()]
    piv={}
    for col in ["correct","p_true","p_max","pred","answer","lA","lB","lC","lD"]:
        piv[col]=df.pivot(index="key",columns="dialect",values=col).loc[keys]
    # option probabilities for set sizes
    L=np.stack([piv[c].values for c in ["lA","lB","lC","lD"]],-1)  # keys x dial x 4
    P=np.exp(L-np.logaddexp.reduce(L,axis=-1,keepdims=True))
    S=1-P  # nonconformity for every option
    strue=1-piv["p_true"].values  # keys x dial
    corr=piv["correct"].values.astype(float); pmax=piv["p_max"].values; ptrue=piv["p_true"].values
    D={d:i for i,d in enumerate(piv["correct"].columns)}; im=D[MSA]
    n=len(keys); idx=np.arange(n); half=n//2
    def conf_metrics(sel):  # sel: array of key indices (resample); returns per-dialect coverage/size for MSA-cal and Mondrian
        covM=np.zeros(len(D)); szM=np.zeros(len(D)); covO=np.zeros(len(D)); szO=np.zeros(len(D))
        perm=sel  # fold split by position within the (re)sample
        folds=[perm[:len(perm)//2], perm[len(perm)//2:]]
        for a,b in [(0,1),(1,0)]:
            cal,tst=folds[a],folds[b]
            q=qhat(strue[cal,im])
            for d,i in D.items():
                covM[i]+=(strue[tst,i]<=q).mean()/2; szM[i]+=(S[tst,i,:]<=q).sum(-1).mean()/2
                qo=qhat(strue[cal,i]); covO[i]+=(strue[tst,i]<=qo).mean()/2; szO[i]+=(S[tst,i,:]<=qo).sum(-1).mean()/2
        return covM,szM,covO,szO
    # point estimates with fixed seeded split
    base=rng.permutation(n); cM,sM,cO,sO=conf_metrics(base)
    # bootstrap
    boots={k:[] for k in ["acc","ece","auroc","brier","covM","szM","covO","mconf"]}
    for _ in range(B):
        sel=rng.integers(0,n,n)
        boots["acc"].append(corr[sel].mean(0)); boots["mconf"].append(pmax[sel].mean(0))
        boots["ece"].append([ece(pmax[sel,i],corr[sel,i]) for i in range(len(D))])
        boots["auroc"].append([auroc(pmax[sel,i],corr[sel,i]) for i in range(len(D))])
        boots["brier"].append(((1-ptrue[sel])**2).mean(0))
        a,b_,c,_=conf_metrics(rng.permutation(sel)); boots["covM"].append(a); boots["szM"].append(b_); boots["covO"].append(c)
    boots={k:np.array(v) for k,v in boots.items()}
    def ci(arr,i): lo,hi=np.percentile(arr[:,i],[2.5,97.5]); return lo,hi
    def dci(arr,i): d=arr[:,i]-arr[:,im]; lo,hi=np.percentile(d,[2.5,97.5]); return d.mean(),lo,hi
    lines.append(f"\n## {tag}  (n_keys={n}, dialects={len(D)})\n")
    lines.append("| variety | acc | Δacc vs MSA [95% CI] | mean conf | ECE | AUROC | Brier | cov@MSA-cal | Δcov vs MSA [CI] | set size | cov@own-cal (Mondrian) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    order=sorted(D, key=lambda d: (d!=MSA, d==ENG, d))
    for d in order:
        i=D[d]; acc=corr[:,i].mean(); da,dlo,dhi=dci(boots["acc"],i)
        e=ece(pmax[:,i],corr[:,i]); au=auroc(pmax[:,i],corr[:,i]); br=((1-ptrue[:,i])**2).mean()
        dc,clo,chi=dci(boots["covM"],i)
        lines.append(f"| {d} | {acc:.3f} | {da:+.3f} [{dlo:+.3f},{dhi:+.3f}] | {pmax[:,i].mean():.3f} | {e:.3f} | {au:.3f} | {br:.3f} | {cM[i]:.3f} | {dc:+.3f} [{clo:+.3f},{chi:+.3f}] | {sM[i]:.2f} | {cO[i]:.3f} |")
        allsum.append(dict(model=tag,variety=d,n=n,acc=acc,d_acc=da,d_acc_lo=dlo,d_acc_hi=dhi,mean_conf=pmax[:,i].mean(),ece=e,auroc=au,brier=br,cov_msacal=cM[i],d_cov=dc,d_cov_lo=clo,d_cov_hi=chi,setsize_msacal=sM[i],cov_owncal=cO[i],setsize_owncal=sO[i]))
    # confidence-vs-accuracy gap: does confidence fall as much as accuracy?
    lines.append("\nConfidence–accuracy decoupling (dialect − MSA): Δacc vs Δmean-confidence")
    for d in order:
        if d==MSA: continue
        i=D[d]; lines.append(f"- {d}: Δacc={corr[:,i].mean()-corr[:,im].mean():+.3f}, Δconf={pmax[:,i].mean()-pmax[:,im].mean():+.3f}, Δ(conf−acc)={ (pmax[:,i].mean()-corr[:,i].mean())-(pmax[:,im].mean()-corr[:,im].mean()):+.3f}")
pd.DataFrame(allsum).to_csv(os.path.join(RES,"pilot_summary.csv"),index=False)
open(os.path.join(RES,"pilot_summary.md"),"w").write("\n".join(lines))
print("\n".join(lines))
