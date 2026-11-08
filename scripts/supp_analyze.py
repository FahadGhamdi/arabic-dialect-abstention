#!/usr/bin/env python
"""Addendum 10 supplements (frozen before execution). 10.1 risk differences vs MSA and target exceedance with fixed-calibration and
double-resampled intervals; 10.2 selective risk of generated (G1) answers on the set accepted by the original tau.
Usage: ADA_RES=results ADA_DATA=data python scripts/supp_analyze.py  -> results/supp/{S101_risk_diff.csv,S102_gen_selective_risk.csv,SUPP_REPORT.md}"""
import os, re, json, glob, math, numpy as np, pandas as pd
RES=os.environ.get("ADA_RES","results"); DATA=os.environ.get("ADA_DATA","data"); OUT=os.path.join(RES,"supp"); os.makedirs(OUT,exist_ok=True)
MSA="MSA"; ENG="ENG"; RSTAR=0.20; B2=2000; B1=1000; LET="ABCD"; RX1=re.compile(r"^\s*\(?([A-D])(?=[\s.):،]|$)")
def ci(x): x=np.asarray(x,float); return float(np.nanpercentile(x,2.5)), float(np.nanpercentile(x,97.5))
def tau_rule(c,k,r):
    o=np.argsort(-c); cum=np.cumsum(1-k[o])/np.arange(1,len(o)+1); ok=np.where(cum<=r)[0]; return float(c[o][ok.max()]) if len(ok) else 1.01
def risk(C,mask): return (1-C[mask]).mean() if mask.any() else np.nan
splits=json.load(open(os.path.join(DATA,"confirmatory_splits.json"))); CK=set(splits["calibration"]); TK=set(splits["test"]); RK=sorted(json.load(open(os.path.join(DATA,"robust_keys.json")))["keys"])
rep=["# Addendum 10 supplements\n"]; R1=[]; R2=[]
for fn in sorted(glob.glob(os.path.join(RES,"confirm_scores_*.csv"))):
    tag=os.path.basename(fn)[len("confirm_scores_"):-4]; df=pd.read_csv(fn,dtype={"key":str}).drop_duplicates(["dialect","key"])
    D=sorted(df.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); im=D.index(MSA)
    comp=set.intersection(*[set(df[df.dialect==d].key) for d in D]); tk=sorted(TK&comp); ck=sorted(CK&comp)
    def arrs(keys):
        sub=df[df.key.isin(keys)]; piv=lambda c: sub.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
        return dict(C=piv("correct").astype(float),PM=piv("p_max").astype(float),ANS=piv("answer").astype(int))
    T=arrs(tk); Cc=arrs(ck); n=len(tk); nc=len(ck)
    # 10.1 fixed calibration
    tau=tau_rule(Cc["PM"][:,im],Cc["C"][:,im],RSTAR); rng0=np.random.default_rng(0); BS=[rng0.integers(0,n,n) for _ in range(B2)]
    rng1=np.random.default_rng(1); DR={d:[] for d in D}; RR={d:[] for d in D}
    for b in range(B1):
        sc=rng1.integers(0,nc,nc); st=rng1.integers(0,n,n); t=tau_rule(Cc["PM"][sc,im],Cc["C"][sc,im],RSTAR); rm=risk(T["C"][st,im],T["PM"][st,im]>=t)
        for j,d in enumerate(D): rv=risk(T["C"][st,j],T["PM"][st,j]>=t); DR[d].append(rv-rm); RR[d].append(rv)
    rep.append(f"\n## {tag} — 10.1 S4 realised risk at τ_MSA={tau:.3f} (r*=0.20): Δrisk vs MSA and exceedance of 0.20\n\n| variety | risk (point) | Δrisk vs MSA fixed-cal [CI] | Δrisk double-resampled [CI] | risk fixed-cal [CI] | risk double-resampled [CI] | > MSA? (fixed / double) | > 0.20? point / fixed / double |\n|---|---|---|---|---|---|---|---|")
    rm_pt=risk(T["C"][:,im],T["PM"][:,im]>=tau)
    for j,d in enumerate(D):
        a=T["PM"][:,j]>=tau; rp=risk(T["C"][:,j],a); dr=rp-rm_pt
        drb=[risk(T["C"][s,j],T["PM"][s,j]>=tau)-risk(T["C"][s,im],T["PM"][s,im]>=tau) for s in BS]; rb=[risk(T["C"][s,j],T["PM"][s,j]>=tau) for s in BS]
        dlo,dhi=ci(drb); rlo,rhi=ci(rb); d2lo,d2hi=ci(DR[d]); r2lo,r2hi=ci(RR[d])
        gm=("yes" if dlo>0 else "no")+" / "+("yes" if d2lo>0 else "no"); ex=("yes" if rp>0.20 else "no")+" / "+("yes" if rlo>0.20 else "no")+" / "+("yes" if r2lo>0.20 else "no")
        rep.append(f"| {d} | {rp:.3f} | {dr:+.3f} [{dlo:+.3f},{dhi:+.3f}] | {np.nanmean(DR[d]):+.3f} [{d2lo:+.3f},{d2hi:+.3f}] | [{rlo:.3f},{rhi:.3f}] | [{r2lo:.3f},{r2hi:.3f}] | {gm} | {ex} |")
        R1.append(dict(model=tag,variety=d,tau=tau,risk=rp,risk_msa=rm_pt,d_risk=dr,d_risk_lo=dlo,d_risk_hi=dhi,d_risk_rs=np.nanmean(DR[d]),d_risk_rs_lo=d2lo,d_risk_rs_hi=d2hi,risk_lo=rlo,risk_hi=rhi,risk_rs_lo=r2lo,risk_rs_hi=r2hi,higher_than_msa_fixed=dlo>0,higher_than_msa_rs=d2lo>0,exceeds_target_point=rp>0.20,exceeds_target_fixed=rlo>0.20,exceeds_target_rs=r2lo>0.20))
    # 10.2 generated answers on accepted set (subset, k=0)
    rf=os.path.join(RES,f"robust_scores_{tag}.csv"); gf=os.path.join(RES,f"robust_gen_{tag}.csv")
    if os.path.exists(rf) and os.path.exists(gf):
        r=pd.read_csv(rf,dtype={"key":str}); r=r[(r.k==0)&(r.key.isin(RK))]; g=pd.read_csv(gf,dtype={"key":str}); g=g[(g.cond=="G1")&(g.key.isin(RK))]
        keys=sorted(set(RK)&set.intersection(*[set(r[r.dialect==d].key) for d in D])&set.intersection(*[set(g[g.dialect==d].key) for d in D])); ns=len(keys)
        pv=lambda c: r.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
        PM=pv("p_max").astype(float); C=pv("correct").astype(float); ANS=pv("answer_orig").astype(int)
        gi=g.set_index(["dialect","key"]); GEN=np.full((ns,len(D)),-1)
        for j,d in enumerate(D):
            for i,k in enumerate(keys):
                t=gi.loc[(d,k),"gen_text"]; t="" if pd.isna(t) else str(t); m=RX1.match(t); GEN[i,j]=LET.index(m.group(1)) if m else -1
        GC=(GEN==ANS).astype(float); acc=PM>=tau; rng0=np.random.default_rng(0); BSs=[rng0.integers(0,ns,ns) for _ in range(B2)]
        rep.append(f"\n## {tag} — 10.2 generated (G1) vs letter-logit answers on the items accepted by τ_MSA={tau:.3f} (subset {ns} keys)\n\n| variety | accepted fraction | selective risk: logit | selective risk: generated | paired difference (gen − logit) [CI] |\n|---|---|---|---|---|")
        for j,d in enumerate(D):
            a=acc[:,j]; rl=risk(C[:,j],a); rg=risk(GC[:,j],a); dd=[risk(GC[s,j],acc[s,j])-risk(C[s,j],acc[s,j]) for s in BSs]; lo,hi=ci(dd)
            rep.append(f"| {d} | {a.mean():.3f} | {rl:.3f} | {rg:.3f} | {rg-rl:+.3f} [{lo:+.3f},{hi:+.3f}] |")
            R2.append(dict(model=tag,variety=d,accepted=a.mean(),sel_risk_logit=rl,sel_risk_gen=rg,diff=rg-rl,diff_lo=lo,diff_hi=hi))
pd.DataFrame(R1).to_csv(os.path.join(OUT,"S101_risk_diff.csv"),index=False); pd.DataFrame(R2).to_csv(os.path.join(OUT,"S102_gen_selective_risk.csv"),index=False)
open(os.path.join(OUT,"SUPP_REPORT.md"),"w").write("\n".join(rep)+"\n"); print("\n".join(rep))
