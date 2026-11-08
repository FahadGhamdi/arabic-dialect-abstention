#!/usr/bin/env python
"""Pre-registered confirmatory analysis (ANALYSIS_PLAN.md). v2 (adds S4 operational selective prediction; P1 kept as the descriptive\ncomparison). Frozen before any confirm_scores_*.csv was opened for analysis (see ANALYSIS_PLAN.md freeze log).
Inputs : $ADA_RES/confirm_scores_<tag>.csv  (same columns as pilot scores), $ADA_SPLITS (default data/confirmatory_splits.json),
         $ADA_DATA/damm.csv (texts, for the char n-gram variety router).
Outputs: $ADA_RES/confirm/{P1_selective,P2_conformal,P3_churn,S1_calib_efficiency,S2_variety_aware,S3_calibration,S4_operational_selective}.csv + CONFIRM_REPORT.md
Rules  : primary endpoints on TEST keys only; thresholds from CALIBRATION keys; router trained on ROUTER_TRAIN keys.
         Uncertainty = paired bootstrap over TEST keys (B resamples); thresholds held fixed (calibration is treated as given).
Usage  : ADA_RES=results ADA_DATA=data ADA_B=2000 python scripts/confirm_analyze.py"""
import os, sys, json, glob, math, zlib, numpy as np, pandas as pd
from scipy import stats
RES=os.environ.get("ADA_RES","results"); DATA=os.environ.get("ADA_DATA","data")
SPL=os.environ.get("ADA_SPLITS",os.path.join(DATA,"confirmatory_splits.json")); OUT=os.path.join(RES,"confirm"); os.makedirs(OUT,exist_ok=True)
B=int(os.environ.get("ADA_B","2000")); rng=np.random.default_rng(0)
MSA="MSA"; ENG="ENG"; ALPHAS=[0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40]; PRIMARY_A=[0.20,0.30]; LET=["A","B","C","D"]
def qhat(s,a): n=len(s); k=min(n,math.ceil((n+1)*(1-a))); return np.sort(s)[k-1]
def ci(x): x=np.asarray(x,float); return np.nanpercentile(x,2.5), np.nanpercentile(x,97.5)
def ece(p,c,nb=15):
    b=np.minimum((p*nb).astype(int),nb-1); return sum(((b==i).mean()*abs(p[b==i].mean()-c[b==i].mean())) for i in range(nb) if (b==i).any())
splits=json.load(open(SPL)); R_KEYS=set(splits["router_train"]); C_KEYS=set(splits["calibration"]); T_KEYS=set(splits["test"])
assert not (R_KEYS&C_KEYS) and not (R_KEYS&T_KEYS) and not (C_KEYS&T_KEYS)
texts=pd.read_csv(os.path.join(DATA,"damm.csv")); texts["text"]=texts["question"].astype(str)+" "+texts["choices"].astype(str).str.replace("|||"," ")
TXT={(r.key,r.dialect):r.text for r in texts.itertuples()}
# ---------- char n-gram hashed features + multinomial LR (numpy), as in the pilot ----------
HD=8192
def feats(strs):
    X=np.zeros((len(strs),HD),np.float32)
    for i,s in enumerate(strs):
        s=" "+str(s)+" "
        for n in (2,3):
            for j in range(len(s)-n+1): X[i,zlib.crc32(s[j:j+n].encode())%HD]+=1
        nr=np.linalg.norm(X[i]); X[i]/= nr if nr>0 else 1
    return X
def train_lr(X,y,K,l2=1.0,it=300,lr=0.5):
    W=np.zeros((X.shape[1],K),np.float32); b=np.zeros(K,np.float32); Y=np.eye(K,dtype=np.float32)[y]; n=len(y)
    for _ in range(it):
        Z=X@W+b; Z-=Z.max(1,keepdims=True); P=np.exp(Z); P/=P.sum(1,keepdims=True); G=(P-Y)/n
        W-=lr*(X.T@G+l2*W/n); b-=lr*G.sum(0)
    return W,b
def predict_proba(W,b,X): Z=X@W+b; Z-=Z.max(1,keepdims=True); P=np.exp(Z); return P/P.sum(1,keepdims=True)
report=[f"# Confirmatory analysis (pre-registered; ANALYSIS_PLAN.md)\n\nSplits: router_train={len(R_KEYS)}, calibration={len(C_KEYS)}, test={len(T_KEYS)} keys. B={B} bootstrap resamples over test keys. Thresholds fixed from calibration.\n"]
P1=[];P2=[];P3=[];S1=[];S2=[];S3=[];S4=[]
for fn in sorted(glob.glob(os.path.join(RES,"confirm_scores_*.csv"))):
    tag=os.path.basename(fn)[len("confirm_scores_"):-4]; df=pd.read_csv(fn).drop_duplicates(["dialect","key"])
    D=sorted(df.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); dial=[d for d in D if d not in (MSA,ENG)]; im=D.index(MSA)
    complete=set.intersection(*[set(df[df.dialect==d].key) for d in D])
    parts={"R":sorted(R_KEYS&complete),"C":sorted(C_KEYS&complete),"T":sorted(T_KEYS&complete)}
    miss=len(T_KEYS)-len(parts["T"]); report.append(f"\n## {tag}: test keys complete {len(parts['T'])}/{len(T_KEYS)} (missing {miss}), calibration {len(parts['C'])}/{len(C_KEYS)}, router_train {len(parts['R'])}/{len(R_KEYS)}\n")
    if len(parts["T"])<0.9*len(T_KEYS): report.append("SKIPPED: scoring incomplete."); continue
    def arrs(keys):
        sub=df[df.key.isin(keys)]; piv=lambda c: sub.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
        L=np.stack([piv(c) for c in ["lA","lB","lC","lD"]],-1); P=np.exp(L-np.logaddexp.reduce(L,-1,keepdims=True))
        return dict(C=piv("correct").astype(float),PT=piv("p_true"),PM=piv("p_max"),PR=piv("pred"),ANS=piv("answer").astype(int),P=P,S=1-piv("p_true"),SO=1-P,keys=keys)
    T=arrs(parts["T"]); Cc=arrs(parts["C"]); n=len(parts["T"])
    # ---------- P1 selective prediction ----------
    grid=np.linspace(0.05,1.0,20)
    def rc(conf,corr):
        o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1); return np.array([cum[int(math.ceil(c*len(e)))-1] for c in grid])
    def ans_at(conf,corr,t):
        o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1); ok=np.where(cum<=t)[0]; return (ok.max()+1)/len(e) if len(ok) else 0.0
    t50=rc(T["PM"][:,im],T["C"][:,im])[np.argmin(abs(grid-0.5))]
    report.append(f"### P1 Answerable fraction at the risk MSA attains at 50% coverage (= {t50:.3f}); AURC\n\n| variety | acc | answerable | Δ vs MSA [95% CI] | AURC | ΔAURC [CI] |\n|---|---|---|---|---|---|")
    BS=[rng.integers(0,n,n) for _ in range(B)]
    for j,d in enumerate(D):
        a0=ans_at(T["PM"][:,j],T["C"][:,j],t50); au=rc(T["PM"][:,j],T["C"][:,j]).mean(); da=[];dau=[]
        for s in BS:
            t=rc(T["PM"][s,im],T["C"][s,im])[np.argmin(abs(grid-0.5))]
            da.append(ans_at(T["PM"][s,j],T["C"][s,j],t)-ans_at(T["PM"][s,im],T["C"][s,im],t)); dau.append(rc(T["PM"][s,j],T["C"][s,j]).mean()-rc(T["PM"][s,im],T["C"][s,im]).mean())
        lo,hi=ci(da); lo2,hi2=ci(dau)
        report.append(f"| {d} | {T['C'][:,j].mean():.3f} | {a0:.3f} | {np.mean(da):+.3f} [{lo:+.3f},{hi:+.3f}] | {au:.3f} | {np.mean(dau):+.3f} [{lo2:+.3f},{hi2:+.3f}] |")
        P1.append(dict(model=tag,variety=d,acc=T['C'][:,j].mean(),msa_matched_risk=t50,answerable=a0,d_answerable=np.mean(da),d_lo=lo,d_hi=hi,aurc=au,d_aurc=np.mean(dau),d_aurc_lo=lo2,d_aurc_hi=hi2))
    # ---------- S4 (added in v2, pre-unblinding): OPERATIONAL selective prediction. A confidence threshold tau is chosen on the
    # CALIBRATION part (MSA items) to reach a target selective risk r*; it is then applied unchanged to every variety on TEST.
    # Reports the answered fraction and the realised risk per variety -> what a deployed MSA-tuned abstention rule would do to dialect users.
    report.append("\n### S4 Operational selective prediction: confidence threshold chosen on calibration MSA for target risk r*, applied to test\n\n| r* | τ | variety | answered fraction [CI] | realised risk [CI] | Δ answered vs MSA [CI] |\n|---|---|---|---|---|---|")
    for rstar in [0.15,0.20,0.25,0.30]:
        cm=Cc["PM"][:,im]; cc_=Cc["C"][:,im]; o=np.argsort(-cm); cum=np.cumsum(1-cc_[o])/np.arange(1,len(o)+1); ok=np.where(cum<=rstar)[0]
        tau=cm[o][ok.max()] if len(ok) else 1.01   # lowest confidence still meeting the target risk on calibration MSA
        ansm=(T["PM"][:,im]>=tau)
        for j,d in enumerate(D):
            ans=(T["PM"][:,j]>=tau); frac=ans.mean(); risk=(1-T["C"][ans,j]).mean() if ans.any() else float("nan")
            fb=[ans[s].mean() for s in BS]; rb=[(1-T["C"][s,j][ans[s]]).mean() if ans[s].any() else np.nan for s in BS]; db=[ans[s].mean()-ansm[s].mean() for s in BS]
            lo,hi=ci(fb); rlo,rhi=ci(rb); dlo,dhi=ci(db)
            report.append(f"| {rstar:.2f} | {tau:.3f} | {d} | {frac:.3f} [{lo:.3f},{hi:.3f}] | {risk:.3f} [{rlo:.3f},{rhi:.3f}] | {np.mean(db):+.3f} [{dlo:+.3f},{dhi:+.3f}] |")
            S4.append(dict(model=tag,target_risk=rstar,tau=tau,variety=d,answered=frac,ans_lo=lo,ans_hi=hi,realised_risk=risk,risk_lo=rlo,risk_hi=rhi,d_answered=np.mean(db),d_lo=dlo,d_hi=dhi))
    # ---------- P2 conformal: thresholds from calibration, evaluated on test ----------
    report.append("\n### P2 Conformal (thresholds from calibration): coverage under the MSA threshold; size & coverage under own-variety threshold\n\n| α | variety | cov@MSA-thr | Δcov [CI] | size@MSA-thr | cov@own | size@own | size ratio own/MSA-own [CI] |\n|---|---|---|---|---|---|---|---|")
    for a in ALPHAS:
        qm=qhat(Cc["S"][:,im],a); qo=[qhat(Cc["S"][:,j],a) for j in range(len(D))]
        covm=(T["S"]<=qm); szm=(T["SO"]<=qm).sum(-1); covo=np.stack([T["S"][:,j]<=qo[j] for j in range(len(D))],1); szo=np.stack([(T["SO"][:,j,:]<=qo[j]).sum(-1) for j in range(len(D))],1)
        for j,d in enumerate(D):
            dc=[covm[s,j].mean()-covm[s,im].mean() for s in BS]; r=[szo[s,j].mean()/szo[s,im].mean() for s in BS]; lo,hi=ci(dc); rlo,rhi=ci(r)
            report.append(f"| {a:.2f} | {d} | {covm[:,j].mean():.3f} | {np.mean(dc):+.3f} [{lo:+.3f},{hi:+.3f}] | {szm[:,j].mean():.2f} | {covo[:,j].mean():.3f} | {szo[:,j].mean():.2f} | {szo[:,j].mean()/szo[:,im].mean():.3f} [{rlo:.3f},{rhi:.3f}] |")
            P2.append(dict(model=tag,alpha=a,variety=d,cov_msathr=covm[:,j].mean(),d_cov=np.mean(dc),d_cov_lo=lo,d_cov_hi=hi,size_msathr=szm[:,j].mean(),cov_ownthr=covo[:,j].mean(),size_ownthr=szo[:,j].mean(),size_ratio=szo[:,j].mean()/szo[:,im].mean(),size_ratio_lo=rlo,size_ratio_hi=rhi))
    # ---------- P3 instability ----------
    report.append("\n### P3 Item-level instability vs MSA (test)\n\n| variety | answer changed [CI] | correctness changed [CI] | ✓→✗ | ✗→✓ | ✗→other✗ |\n|---|---|---|---|---|---|")
    for j,d in enumerate(D):
        if d==MSA: continue
        ch=(T["PR"][:,j]!=T["PR"][:,im]); cc=(T["C"][:,j]!=T["C"][:,im]); a_=int(((T["C"][:,im]==1)&(T["C"][:,j]==0)).sum()); b_=int(((T["C"][:,im]==0)&(T["C"][:,j]==1)).sum()); ww=int((ch&(T["C"][:,j]==0)&(T["C"][:,im]==0)).sum())
        l1,h1=ci([ch[s].mean() for s in BS]); l2,h2=ci([cc[s].mean() for s in BS])
        report.append(f"| {d} | {ch.mean():.3f} [{l1:.3f},{h1:.3f}] | {cc.mean():.3f} [{l2:.3f},{h2:.3f}] | {a_} | {b_} | {ww} |")
        P3.append(dict(model=tag,variety=d,answer_change=ch.mean(),ac_lo=l1,ac_hi=h1,correct_change=cc.mean(),cc_lo=l2,cc_hi=h2,ok_to_bad=a_,bad_to_ok=b_,bad_to_otherbad=ww))
    dj=[D.index(d) for d in dial]; anyc=T["C"][:,dj].max(1).mean(); strict=T["C"][:,dj].min(1).mean()
    report.append(f"\nA_any = {anyc:.3f}; A_strict = {strict:.3f}; MSA acc = {T['C'][:,im].mean():.3f}; mean dialect acc = {T['C'][:,dj].mean():.3f}")
    P3.append(dict(model=tag,variety="ALL5",a_any=anyc,a_strict=strict,msa_acc=T['C'][:,im].mean(),mean_dialect_acc=T['C'][:,dj].mean()))
    # ---------- S1 calibration efficiency: n items from calibration part -> coverage on test ----------
    a=0.30; tgt=1-a; NS=[25,50,100,150,200,250,400]; NSPL=500; nc=len(parts["C"])
    report.append(f"\n### S1 Calibration efficiency (α={a:.2f}; n own-variety calibration items from the calibration part; evaluated on all test items; {NSPL} draws)\n\nCell: mean cov [2.5,97.5 pct] · P(|cov−{tgt:.2f}|≤0.05) · mean size\n\n| variety | "+" | ".join(f"n={k}" for k in NS)+" |\n|---|"+"---|"*len(NS))
    for j,d in enumerate(D):
        cells=[]
        for k in NS:
            if k>nc: cells.append("—"); continue
            covs=[];szs=[]
            for _ in range(NSPL):
                idx=rng.choice(nc,k,replace=False); q=qhat(Cc["S"][idx,j],a); covs.append((T["S"][:,j]<=q).mean()); szs.append((T["SO"][:,j,:]<=q).sum(-1).mean())
            covs=np.array(covs); lo,hi=ci(covs); pin=(abs(covs-tgt)<=0.05).mean(); l=math.floor((k+1)*a); blo,bhi=stats.beta.ppf([0.025,0.975],k+1-l,l)
            cells.append(f"{covs.mean():.3f} [{lo:.3f},{hi:.3f}] · {pin:.2f} · {np.mean(szs):.2f}")
            S1.append(dict(model=tag,variety=d,n_cal=k,cov=covs.mean(),sd=covs.std(),lo=lo,hi=hi,p_within5=pin,p_ge_minus5=(covs>=tgt-0.05).mean(),set_size=np.mean(szs),beta_lo=blo,beta_hi=bhi))
        report.append(f"| {d} | "+" | ".join(cells)+" |")
    # ---------- S2 variety-aware calibration with predicted groups (text router) ----------
    Rk=parts["R"]; K=len(D)
    Xr=feats([TXT[(k,d)] for k in Rk for d in D]); yr=np.array([j for k in Rk for j in range(K)]); W,bb=train_lr(Xr,yr,K)
    def route(keys): X=feats([TXT[(k,d)] for k in keys for d in D]); return predict_proba(W,bb,X).reshape(len(keys),K,K)   # keys x true x prob(pred)
    PRc=route(parts["C"]); PRt=route(parts["T"]); predc=PRc.argmax(-1); predt=PRt.argmax(-1)
    racc=(predt==np.arange(K)[None,:]).mean(); report.append(f"\n### S2 Variety-aware calibration, predicted groups (text router acc on test = {racc:.3f}); per TRUE variety on test\n")
    S_all=Cc["S"].ravel()
    for a in PRIMARY_A:
        qm=qhat(Cc["S"][:,im],a); qp=qhat(S_all,a); qo=np.array([qhat(Cc["S"][:,j],a) for j in range(K)])
        qg=np.array([qhat(Cc["S"][predc==g],a) if (predc==g).sum()>=20 else qp for g in range(K)])   # threshold per PREDICTED group on calibration
        # plausible set: groups covering 0.9 of router mass -> max threshold (conservative)
        def plaus_q(pr):
            o=np.argsort(-pr); cum=np.cumsum(pr[o]); m=int(np.searchsorted(cum,0.9))+1; return qg[o[:m]].max()
        qpl=np.vectorize(lambda i,j: plaus_q(PRt[i,j]))(*np.indices(predt.shape))
        meth={"msa_only":np.full(predt.shape,qm),"pooled":np.full(predt.shape,qp),"oracle":np.tile(qo,(n,1)),"text_router":qg[predt],"plausible_set":qpl}
        report.append(f"α={a:.2f} (target {1-a:.2f})\n\n| method | "+" | ".join(D)+" | worst dialect [CI] | mean size (dialects) | size MAG |\n|---|"+"---|"*(K+3))
        for mname,Q in meth.items():
            cov=(T["S"]<=Q); sz=(T["SO"]<=Q[...,None]).sum(-1)
            worst=[min(cov[s][:,j].mean() for j in dj) for s in BS]; wlo,whi=ci(worst)
            report.append(f"| {mname} | "+" | ".join(f"{cov[:,j].mean():.3f}" for j in range(K))+f" | {min(cov[:,j].mean() for j in dj):.3f} [{wlo:.3f},{whi:.3f}] | {sz[:,dj].mean():.2f} | {sz[:,D.index('MAG')].mean() if 'MAG' in D else float('nan'):.2f} |")
            for j,d in enumerate(D): S2.append(dict(model=tag,alpha=a,method=mname,variety=d,coverage=cov[:,j].mean(),set_size=sz[:,j].mean(),router_acc=racc))
        # paired differences vs msa_only on MAG and worst dialect
        if "MAG" in D:
            jm=D.index("MAG"); base=(T["S"]<=meth["msa_only"]); lines=[]
            for mname in ["pooled","oracle","text_router","plausible_set"]:
                cv=(T["S"]<=meth[mname]); dm=[cv[s][:,jm].mean()-base[s][:,jm].mean() for s in BS]; dw=[min(cv[s][:,j].mean() for j in dj)-min(base[s][:,j].mean() for j in dj) for s in BS]
                lo,hi=ci(dm); lo2,hi2=ci(dw); lines.append(f"{mname}: ΔMAG {np.mean(dm):+.3f} [{lo:+.3f},{hi:+.3f}], Δworst {np.mean(dw):+.3f} [{lo2:+.3f},{hi2:+.3f}]")
            report.append("\nPaired differences vs msa_only (bootstrap over test keys): "+"; ".join(lines)+"\n")
    # ---------- S3 calibration ----------
    Y=np.zeros_like(T["P"]);
    for j in range(K): Y[np.arange(n),j,T["ANS"][:,j]]=1
    brier=((T["P"]-Y)**2).sum(-1)
    report.append("\n### S3 Calibration (test)\n\n| variety | acc | mean conf | ECE | multiclass Brier [CI] |\n|---|---|---|---|---|")
    for j,d in enumerate(D):
        lo,hi=ci([brier[s,j].mean() for s in BS]); report.append(f"| {d} | {T['C'][:,j].mean():.3f} | {T['PM'][:,j].mean():.3f} | {ece(T['PM'][:,j],T['C'][:,j]):.3f} | {brier[:,j].mean():.3f} [{lo:.3f},{hi:.3f}] |")
        S3.append(dict(model=tag,variety=d,acc=T['C'][:,j].mean(),conf=T['PM'][:,j].mean(),ece=ece(T['PM'][:,j],T['C'][:,j]),brier=brier[:,j].mean(),brier_lo=lo,brier_hi=hi))
for name,rows in [("P1_selective",P1),("P2_conformal",P2),("P3_churn",P3),("S1_calib_efficiency",S1),("S2_variety_aware",S2),("S3_calibration",S3),("S4_operational_selective",S4)]:
    pd.DataFrame(rows).to_csv(os.path.join(OUT,name+".csv"),index=False)
open(os.path.join(OUT,"CONFIRM_REPORT.md"),"w").write("\n".join(report)); print("\n".join(report))
