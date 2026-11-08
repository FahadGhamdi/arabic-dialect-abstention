#!/usr/bin/env python
"""Final verification package (ANALYSIS_PLAN.md Addendum 9, §9.1–9.4; specified before computation; frozen by sha256 before execution).
9.1 Calibration sensitivity: double resampling (calibration keys AND test keys, independently, pairing across varieties preserved) with
    re-selection of τ (S4 rule), τ_v (D4) and the conformal q̂ in every iteration; intervals shown next to the original fixed-calibration ones.
9.2 Re-run reproducibility diagnostic (robustness k=0 vs confirmatory scores): disagreement share, top-2 margin at disagreements, gap estimates.
9.3 R4 paired comparison: dialect-vs-MSA answer change minus within-variety change under one rotation, per key, with key-bootstrap CI.
9.4 D4 distance-to-target table (post hoc descriptive) with answered fractions.
Inputs : $ADA_RES/confirm_scores_<tag>.csv, $ADA_RES/robust_scores_<tag>.csv, $ADA_RES/confirm/{S4_operational_selective,P2_conformal}.csv,
         $ADA_RES/diag/D4_variety_threshold.csv, $ADA_RES/robust_interim_4models_scoring/R3_s4_by_order.csv, $ADA_DATA/confirmatory_splits.json,
         $ADA_DATA/robust_keys.json.
Outputs: $ADA_RES/sens/{S91_calibration_sensitivity.csv, S91_rotation_sensitivity.csv, S92_reproducibility.csv, S93_R4_paired.csv,
         S94_D4_distance.csv, SENS_REPORT.md}
Usage  : ADA_RES=results ADA_DATA=data ADA_B1=1000 ADA_B2=2000 python scripts/sens_analyze.py"""
import os, json, glob, math, numpy as np, pandas as pd
RES=os.environ.get("ADA_RES","results"); DATA=os.environ.get("ADA_DATA","data"); OUT=os.path.join(RES,"sens"); os.makedirs(OUT,exist_ok=True)
B1=int(os.environ.get("ADA_B1","1000")); B2=int(os.environ.get("ADA_B2","2000")); MSA="MSA"; ENG="ENG"; RSTAR=0.20; ALPHA=0.30; LET=["A","B","C","D"]
def ci(x): x=np.asarray(x,float); return float(np.nanpercentile(x,2.5)), float(np.nanpercentile(x,97.5))
def qhat(s,a): n=len(s); k=min(n,math.ceil((n+1)*(1-a))); return np.sort(s)[k-1]
def tau_rule(conf_cal,corr_cal,rstar):
    o=np.argsort(-conf_cal); cum=np.cumsum(1-corr_cal[o])/np.arange(1,len(o)+1); ok=np.where(cum<=rstar)[0]
    return float(conf_cal[o][ok.max()]) if len(ok) else 1.01
grid=np.linspace(0.05,1.0,20)
def rc(conf,corr):
    o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1); return np.array([cum[int(math.ceil(c*len(e)))-1] for c in grid])
def ans_at(conf,corr,t):
    o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1); ok=np.where(cum<=t)[0]; return (ok.max()+1)/len(e) if len(ok) else 0.0
def p1_gap(PM,C,j,im):
    t=rc(PM[:,im],C[:,im])[np.argmin(abs(grid-0.5))]; return ans_at(PM[:,j],C[:,j],t)-ans_at(PM[:,im],C[:,im],t)
def wfmt(x,lo,hi): return f"{x:+.3f} [{lo:+.3f},{hi:+.3f}]"
splits=json.load(open(os.path.join(DATA,"confirmatory_splits.json"))); C_KEYS=set(splits["calibration"]); T_KEYS=set(splits["test"])
RK=sorted(json.load(open(os.path.join(DATA,"robust_keys.json")))["keys"])
S4o=pd.read_csv(os.path.join(RES,"confirm","S4_operational_selective.csv")); P2o=pd.read_csv(os.path.join(RES,"confirm","P2_conformal.csv"))
D4o=pd.read_csv(os.path.join(RES,"diag","D4_variety_threshold.csv")); R3o=pd.read_csv(os.path.join(RES,"robust_interim_4models_scoring","R3_s4_by_order.csv"))
rep=[f"# Final verification package (Addendum 9)\n\nDouble resampling B1={B1} (default_rng(1)); key bootstrap B2={B2} (default_rng(0)). Every new interval is shown NEXT TO the original fixed-calibration interval; nothing replaces a pre-registered estimate.\n"]
S91=[];S91r=[];S92=[];S93=[];S94=[]
for fn in sorted(glob.glob(os.path.join(RES,"confirm_scores_*.csv"))):
    tag=os.path.basename(fn)[len("confirm_scores_"):-4]; df=pd.read_csv(fn,dtype={"key":str}).drop_duplicates(["dialect","key"])
    D=sorted(df.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); im=D.index(MSA); dial=[d for d in D if d not in (MSA,ENG)]
    complete=set.intersection(*[set(df[df.dialect==d].key) for d in D]); tk=sorted(T_KEYS&complete); ck=sorted(C_KEYS&complete)
    def arrs(keys):
        sub=df[df.key.isin(keys)]; piv=lambda c: sub.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
        L=np.stack([piv(c) for c in ["lA","lB","lC","lD"]],-1); P=np.exp(L-np.logaddexp.reduce(L,-1,keepdims=True))
        return dict(C=piv("correct").astype(float),PM=piv("p_max").astype(float),PR=piv("pred").astype(int),S=1-piv("p_true").astype(float),SO=1-P,L=L)
    T=arrs(tk); Cc=arrs(ck); n=len(tk); nc=len(ck); rng1=np.random.default_rng(1)
    rep.append(f"\n## {tag}: test {n}, calibration {nc}\n")
    # ---------------- 9.1 double resampling ----------------
    acc={d:dict(ans=[],dans=[],risk=[],ansv=[],riskv=[],rec=[],res=[],cov=[],dcov=[],szr=[],tau=[],tauv=[],qm=[]) for d in D}
    for b in range(B1):
        sc=rng1.integers(0,nc,nc); st=rng1.integers(0,n,n)
        cm=Cc["PM"][sc,im]; cc_=Cc["C"][sc,im]; tau=tau_rule(cm,cc_,RSTAR); ansm=(T["PM"][st,im]>=tau)
        qm=qhat(Cc["S"][sc,im],ALPHA); covm=(T["S"][st][:,im]<=qm); szm=(T["SO"][st][:,im,:]<=qhat(Cc["S"][sc,im],ALPHA)).sum(-1).mean()
        for j,d in enumerate(D):
            a=(T["PM"][st,j]>=tau); frac=a.mean(); risk=(1-T["C"][st,j][a]).mean() if a.any() else np.nan
            tv=tau_rule(Cc["PM"][sc,j],Cc["C"][sc,j],RSTAR); av=(T["PM"][st,j]>=tv); fv=av.mean(); rv=(1-T["C"][st,j][av]).mean() if av.any() else np.nan
            qo=qhat(Cc["S"][sc,j],ALPHA); cov=(T["S"][st][:,j]<=qm).mean(); szo=(T["SO"][st][:,j,:]<=qo).sum(-1).mean()
            A=acc[d]; A["ans"].append(frac); A["dans"].append(frac-ansm.mean()); A["risk"].append(risk); A["ansv"].append(fv); A["riskv"].append(rv); A["rec"].append(fv-frac); A["res"].append(fv-ansm.mean())
            A["cov"].append(cov); A["dcov"].append(cov-covm.mean()); A["szr"].append(szo/szm); A["tau"].append(tau); A["tauv"].append(tv); A["qm"].append(qm)
    rep.append(f"### 9.1 Calibration sensitivity (r*={RSTAR}, α={ALPHA}); τ_MSA across resamples: median {np.median(acc[MSA]['tau']):.3f} [{ci(acc[MSA]['tau'])[0]:.3f},{ci(acc[MSA]['tau'])[1]:.3f}]; q̂_MSA median {np.median(acc[MSA]['qm']):.3f} [{ci(acc[MSA]['qm'])[0]:.3f},{ci(acc[MSA]['qm'])[1]:.3f}]\n")
    rep.append("| variety | S4 Δanswered: original [CI] → double-resampled [CI] (width ratio) | realised risk @τ: orig → resampled [CI] | D4 residual gap: orig [CI] → resampled [CI] | D4 realised risk @τ_v resampled [CI] | P2 Δcov: orig [CI] → resampled [CI] | P2 size ratio: orig [CI] → resampled [CI] | verdict |\n|---|---|---|---|---|---|---|---|")
    for j,d in enumerate(D):
        if d==MSA: continue
        A=acc[d]; o4=S4o[(S4o.model==tag)&(S4o.variety==d)&(S4o.target_risk==RSTAR)].iloc[0]; o2=P2o[(P2o.model==tag)&(P2o.variety==d)&(P2o.alpha==ALPHA)].iloc[0]; od=D4o[(D4o.model==tag)&(D4o.variety==d)&(D4o.target_risk==RSTAR)].iloc[0]
        dlo,dhi=ci(A["dans"]); rlo,rhi=ci(A["risk"]); reslo,reshi=ci(A["res"]); rvlo,rvhi=ci(A["riskv"]); clo,chi=ci(A["dcov"]); slo,shi=ci(A["szr"])
        wr=(dhi-dlo)/max(1e-9,(o4.d_hi-o4.d_lo)); wr2=(chi-clo)/max(1e-9,(o2.d_cov_hi-o2.d_cov_lo)); wr3=(shi-slo)/max(1e-9,(o2.size_ratio_hi-o2.size_ratio_lo))
        v=[]; v.append("S4 "+("robust" if (dhi<0 or dlo>0) else "sensitive")); v.append("D4 "+("robust" if (reshi<0 or reslo>0) else "sensitive")); v.append("Δcov "+("robust" if (chi<0 or clo>0) else "sensitive")); v.append("size "+("robust" if (slo>1 or shi<1) else "sensitive"))
        rep.append(f"| {d} | {wfmt(o4.d_answered,o4.d_lo,o4.d_hi)} → {wfmt(np.mean(A['dans']),dlo,dhi)} (×{wr:.2f}) | {o4.realised_risk:.3f} → {np.nanmean(A['risk']):.3f} [{rlo:.3f},{rhi:.3f}] | {wfmt(od.residual_gap,od.res_lo,od.res_hi)} → {wfmt(np.mean(A['res']),reslo,reshi)} | {np.nanmean(A['riskv']):.3f} [{rvlo:.3f},{rvhi:.3f}] | {wfmt(o2.d_cov,o2.d_cov_lo,o2.d_cov_hi)} → {wfmt(np.mean(A['dcov']),clo,chi)} (×{wr2:.2f}) | {o2.size_ratio:.3f} [{o2.size_ratio_lo:.3f},{o2.size_ratio_hi:.3f}] → {np.mean(A['szr']):.3f} [{slo:.3f},{shi:.3f}] (×{wr3:.2f}) | {'; '.join(v)} |")
        S91.append(dict(model=tag,variety=d,s4_d_ans_orig=o4.d_answered,s4_lo_orig=o4.d_lo,s4_hi_orig=o4.d_hi,s4_d_ans_rs=np.mean(A["dans"]),s4_lo_rs=dlo,s4_hi_rs=dhi,s4_width_ratio=wr,risk_orig=o4.realised_risk,risk_rs=np.nanmean(A["risk"]),risk_lo_rs=rlo,risk_hi_rs=rhi,
                        d4_res_orig=od.residual_gap,d4_res_lo_orig=od.res_lo,d4_res_hi_orig=od.res_hi,d4_res_rs=np.mean(A["res"]),d4_res_lo_rs=reslo,d4_res_hi_rs=reshi,d4_riskv_rs=np.nanmean(A["riskv"]),d4_riskv_lo_rs=rvlo,d4_riskv_hi_rs=rvhi,d4_rec_rs=np.mean(A["rec"]),d4_rec_lo_rs=ci(A["rec"])[0],d4_rec_hi_rs=ci(A["rec"])[1],
                        p2_dcov_orig=o2.d_cov,p2_dcov_lo_orig=o2.d_cov_lo,p2_dcov_hi_orig=o2.d_cov_hi,p2_dcov_rs=np.mean(A["dcov"]),p2_dcov_lo_rs=clo,p2_dcov_hi_rs=chi,p2_dcov_width_ratio=wr2,p2_szr_orig=o2.size_ratio,p2_szr_lo_orig=o2.size_ratio_lo,p2_szr_hi_orig=o2.size_ratio_hi,p2_szr_rs=np.mean(A["szr"]),p2_szr_lo_rs=slo,p2_szr_hi_rs=shi,p2_szr_width_ratio=wr3,
                        tau_msa_median=np.median(acc[MSA]["tau"]),tau_v_median=np.median(A["tauv"]),verdict="; ".join(v)))
    # ---------------- 9.1 rotation subset (R3) double resampling + 9.2 + 9.3 ----------------
    rf=os.path.join(RES,f"robust_scores_{tag}.csv")
    if os.path.exists(rf):
        rdf=pd.read_csv(rf,dtype={"key":str}).drop_duplicates(["dialect","key","k"]); ORD=[0,1,2,3]
        keys=sorted(set(RK)&set.intersection(*[set(rdf[(rdf.dialect==d)&(rdf.k==kk)].key) for d in D for kk in ORD]))
        ns=len(keys); Rk={}
        for kk in ORD:
            sub=rdf[(rdf.k==kk)&(rdf.key.isin(keys))]; piv=lambda c: sub.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
            Rk[kk]=dict(C=piv("correct").astype(float),PM=piv("p_max").astype(float),PR=piv("pred_orig").astype(int))
        rng1b=np.random.default_rng(11); accR={d:[] for d in D}
        for b in range(B1):
            sc=rng1b.integers(0,nc,nc); ss=rng1b.integers(0,ns,ns); tau=tau_rule(Cc["PM"][sc,im],Cc["C"][sc,im],RSTAR)
            for j,d in enumerate(D):
                if d==MSA: continue
                accR[d].append(np.mean([(Rk[kk]["PM"][ss,j]>=tau).mean()-(Rk[kk]["PM"][ss,im]>=tau).mean() for kk in ORD]))
        rep.append(f"\n### 9.1b Rotation subset ({ns} keys): S4 Δanswered order-averaged — original (τ fixed) [CI] → double-resampled [CI]\n\n| variety | original | double-resampled | verdict |\n|---|---|---|---|")
        for d in dial+([ENG] if ENG in D else []):
            o=R3o[(R3o.model==tag)&(R3o.variety==d)]; lo,hi=ci(accR[d]); m=np.mean(accR[d])
            if len(o): o=o.iloc[0]; rep.append(f"| {d} | {wfmt(o.d_ans_avg,o.d_ans_lo,o.d_ans_hi)} | {wfmt(m,lo,hi)} | {'robust' if (hi<0 or lo>0) else 'sensitive'} |"); S91r.append(dict(model=tag,variety=d,d_ans_avg_orig=o.d_ans_avg,lo_orig=o.d_ans_lo,hi_orig=o.d_ans_hi,d_ans_avg_rs=m,lo_rs=lo,hi_rs=hi))
        # 9.2 reproducibility
        idx=[tk.index(k) for k in keys]; cPR=T["PR"][idx]; cPM=T["PM"][idx]; cC=T["C"][idx]; L=T["L"][idx]; Ls=np.sort(L,-1); margin=Ls[...,-1]-Ls[...,-2]
        dis=(Rk[0]["PR"]!=cPR); share=dis.mean(); med_all=np.median(margin); med_dis=np.median(margin[dis]) if dis.any() else np.nan; lt_all=(margin<0.05).mean(); lt_dis=(margin[dis]<0.05).mean() if dis.any() else np.nan
        tau0=tau_rule(Cc["PM"][:,im],Cc["C"][:,im],RSTAR); rows=[]
        for j,d in enumerate(D):
            if d==MSA: continue
            dacc_c=cC[:,j].mean()-cC[:,im].mean(); dacc_r=Rk[0]["C"][:,j].mean()-Rk[0]["C"][:,im].mean(); dp1_c=p1_gap(cPM,cC,j,im); dp1_r=p1_gap(Rk[0]["PM"],Rk[0]["C"],j,im)
            s4c=(cPM[:,j]>=tau0).mean()-(cPM[:,im]>=tau0).mean(); s4r=(Rk[0]["PM"][:,j]>=tau0).mean()-(Rk[0]["PM"][:,im]>=tau0).mean()
            rows.append(dict(model=tag,variety=d,share_disagree=share,margin_median_all=med_all,margin_median_disagree=med_dis,share_margin_lt005_all=lt_all,share_margin_lt005_disagree=lt_dis,d_acc_confirm=dacc_c,d_acc_rerun=dacc_r,d_p1_confirm=dp1_c,d_p1_rerun=dp1_r,s4_d_ans_confirm=s4c,s4_d_ans_rerun=s4r))
        S92+=rows; mx=max(max(abs(r["d_acc_confirm"]-r["d_acc_rerun"]),abs(r["d_p1_confirm"]-r["d_p1_rerun"]),abs(r["s4_d_ans_confirm"]-r["s4_d_ans_rerun"])) for r in rows)
        rep.append(f"\n### 9.2 Re-run reproducibility (subset {ns}×{len(D)} cells): different prediction in {share:.3%}; top-2 margin median all {med_all:.3f} nats vs disagreeing {med_dis:.3f}; share margin<0.05: all {lt_all:.3f} vs disagreeing {lt_dis:.3f}; max |Δ(gap estimate)| across Δacc/ΔP1/S4 and dialects = {mx:.3f}\n\n| variety | Δacc confirm → rerun | ΔP1 confirm → rerun | S4 Δanswered confirm → rerun |\n|---|---|---|---|")
        for r in rows: rep.append(f"| {r['variety']} | {r['d_acc_confirm']:+.3f} → {r['d_acc_rerun']:+.3f} | {r['d_p1_confirm']:+.3f} → {r['d_p1_rerun']:+.3f} | {r['s4_d_ans_confirm']:+.3f} → {r['s4_d_ans_rerun']:+.3f} |")
        # 9.3 R4 paired
        rng0=np.random.default_rng(0); BS=[rng0.integers(0,ns,ns) for _ in range(B2)]
        rep.append("\n### 9.3 R4 paired comparison: D = [dialect≠MSA at k=0] − [same variety k=0≠k=1]; D′ uses MSA's own rotation change\n\n| variety | P3 (dialect vs MSA) | within-variety rotation change | mean D [CI] | mean D′ [CI] | reading |\n|---|---|---|---|---|---|")
        for j,d in enumerate(D):
            if d==MSA: continue
            I1=(Rk[0]["PR"][:,j]!=Rk[0]["PR"][:,im]).astype(float); I2=(Rk[0]["PR"][:,j]!=Rk[1]["PR"][:,j]).astype(float); I2m=(Rk[0]["PR"][:,im]!=Rk[1]["PR"][:,im]).astype(float)
            Dd=I1-I2; Dm=I1-I2m; lo,hi=ci([Dd[s].mean() for s in BS]); lo2,hi2=ci([Dm[s].mean() for s in BS])
            read="larger than one-rotation change" if lo>0 else "not larger than one-rotation change"
            rep.append(f"| {d} | {I1.mean():.3f} | {I2.mean():.3f} | {wfmt(Dd.mean(),lo,hi)} | {wfmt(Dm.mean(),lo2,hi2)} | {read} |")
            S93.append(dict(model=tag,variety=d,p3=I1.mean(),within_rotation=I2.mean(),mean_D=Dd.mean(),D_lo=lo,D_hi=hi,mean_Dprime=Dm.mean(),Dp_lo=lo2,Dp_hi=hi2,reading=read))
    # ---------------- 9.4 D4 distance table ----------------
    q=D4o[(D4o.model==tag)&(D4o.target_risk==RSTAR)&(~D4o.variety.isin([MSA,ENG]))].copy()
    q["dist_msa_thr"]=(q.realised_risk_msa_thr-RSTAR).abs(); q["dist_v_thr"]=(q.realised_risk_v_thr-RSTAR).abs(); q["closer"]=q.dist_v_thr<q.dist_msa_thr
    rep.append(f"\n### 9.4 D4 distance to target (post hoc): closer in {int(q.closer.sum())}/{len(q)} cells; cells with risk>0.24 under τ_MSA {int((q.realised_risk_msa_thr>0.24).sum())} → under τ_v {int((q.realised_risk_v_thr>0.24).sum())}; mean distance {q.dist_msa_thr.mean():.3f} → {q.dist_v_thr.mean():.3f}\n\n| variety | risk @τ_MSA → @τ_v | distance → | closer | answered @τ_MSA → @τ_v |\n|---|---|---|---|---|")
    for r in q.itertuples(): rep.append(f"| {r.variety} | {r.realised_risk_msa_thr:.3f} → {r.realised_risk_v_thr:.3f} | {r.dist_msa_thr:.3f} → {r.dist_v_thr:.3f} | {'yes' if r.closer else 'no'} | {r.answered_msa_thr:.3f} → {r.answered_v_thr:.3f} |"); S94.append(dict(model=tag,variety=r.variety,risk_msa_thr=r.realised_risk_msa_thr,risk_v_thr=r.realised_risk_v_thr,dist_msa_thr=r.dist_msa_thr,dist_v_thr=r.dist_v_thr,closer=bool(r.closer),answered_msa_thr=r.answered_msa_thr,answered_v_thr=r.answered_v_thr))
for name,rows in [("S91_calibration_sensitivity",S91),("S91_rotation_sensitivity",S91r),("S92_reproducibility",S92),("S93_R4_paired",S93),("S94_D4_distance",S94)]:
    pd.DataFrame(rows).to_csv(os.path.join(OUT,f"{name}.csv"),index=False)
open(os.path.join(OUT,"SENS_REPORT.md"),"w").write("\n".join(rep)+"\n"); print("\n".join(rep)); print("written",OUT)
