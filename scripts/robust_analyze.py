#!/usr/bin/env python
"""Measurement-robustness analysis (ANALYSIS_PLAN.md Addendum 8 §8.3; pre-registered — frozen before any robust_scores_*/robust_gen_* file was opened).
Inputs : $ADA_RES/robust_scores_<tag>.csv, $ADA_RES/robust_gen_<tag>.csv (scripts/s12_robustness.py), $ADA_RES/confirm_scores_<tag>.csv
         (τ_MSA from the calibration part under the original ordering; re-run reproducibility), $ADA_DATA/confirmatory_splits.json,
         $ADA_DATA/robust_keys.json, $ADA_DATA/damm.csv (option texts for G2 extraction rule 3).
Outputs: $ADA_RES/robust/{R1_order_sensitivity,R2_gap_stability,R3_s4_by_order,R4_p3_decomposition,R5_generation}.csv + ROBUST_REPORT.md
Rules  : subset = the 500 pre-drawn test keys; paired bootstrap over keys (B=2000, default_rng(0)); thresholds fixed; all quantities
         reported whatever their direction. Reading rule for R2: "order-robust" iff the order-averaged gap's CI excludes 0 and the four
         per-order gaps share its sign.
Usage  : ADA_RES=results ADA_DATA=data ADA_B=2000 python scripts/robust_analyze.py"""
import os, re, json, glob, math, numpy as np, pandas as pd
RES=os.environ.get("ADA_RES","results"); DATA=os.environ.get("ADA_DATA","data"); OUT=os.path.join(RES,"robust"); os.makedirs(OUT,exist_ok=True)
B=int(os.environ.get("ADA_B","2000")); rng=np.random.default_rng(0); MSA="MSA"; ENG="ENG"; RSTAR=0.20; ORD=[0,1,2,3]; LET="ABCD"
def ci(x): x=np.asarray(x,float); return float(np.nanpercentile(x,2.5)), float(np.nanpercentile(x,97.5))
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
# ---------- extraction rules (Addendum 8 §8.2) ----------
RX1=re.compile(r"^\s*\(?([A-D])(?=[\s.):،]|$)")
RX2=[re.compile(r"الإجابة(?: الصحيحة)?(?: هي)?\s*[:：]?\s*\(?([A-D])\b"), re.compile(r"[Aa]nswer(?: is)?\s*[:：]?\s*\(?([A-D])\b")]
norm=lambda s: re.sub(r"\s+"," ",str(s)).strip()
def extract_g1(txt):
    m=RX1.match(txt or ""); return (LET.index(m.group(1)),"rule1") if m else (None,"none")
def extract_g2(txt,opts):
    txt=txt or ""; m=RX1.match(txt)
    if m: return LET.index(m.group(1)),"rule1"
    for r in RX2:
        m=r.search(txt)
        if m: return LET.index(m.group(1)),"rule2"
    t=norm(txt); hits=[i for i,o in enumerate(opts) if norm(o) and norm(o) in t]
    if len(hits)==1: return hits[0],"rule3"
    return None,"none"
splits=json.load(open(os.path.join(DATA,"confirmatory_splits.json"))); CAL=set(splits["calibration"])
RK=json.load(open(os.path.join(DATA,"robust_keys.json"))); KEYS=sorted(RK["keys"]); assert len(KEYS)==500
texts=pd.read_csv(os.path.join(DATA,"damm.csv"),dtype={"key":str}); OPTS={(r.key,r.dialect):str(r.choices).split("|||") for r in texts.itertuples()}
rep=[f"# Measurement robustness (Addendum 8): option order and answer extraction\n\nSubset: {len(KEYS)} confirmatory test keys (seed 20261107); orderings k=0..3 (cyclic shifts); B={B} paired bootstrap resamples over keys; τ_MSA (r*={RSTAR}) from the calibration part under k=0 as in CONFIRM_REPORT.\n"]
R1=[];R2=[];R3=[];R4=[];R5=[]
for fn in sorted(glob.glob(os.path.join(RES,"robust_scores_*.csv"))):
    tag=os.path.basename(fn)[len("robust_scores_"):-4]; df=pd.read_csv(fn,dtype={"key":str}).drop_duplicates(["dialect","key","k"])
    D=sorted(df.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); im=D.index(MSA); dial=[d for d in D if d not in (MSA,ENG)]
    complete=set.intersection(*[set(df[(df.dialect==d)&(df.k==k)].key) for d in D for k in ORD]); keys=[k for k in KEYS if k in complete]; n=len(keys)
    rep.append(f"\n## {tag}: complete keys {n}/{len(KEYS)}\n")
    if n<0.9*len(KEYS): rep.append("SKIPPED: scoring incomplete."); continue
    A={}
    for k in ORD:
        sub=df[(df.k==k)&(df.key.isin(keys))]; piv=lambda c: sub.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
        A[k]=dict(C=piv("correct").astype(float),PM=piv("p_max").astype(float),PR=piv("pred_orig").astype(int),ANS=piv("answer_orig").astype(int))
    BS=[rng.integers(0,n,n) for _ in range(B)]
    # ---------- reproducibility of k=0 against the confirmatory run ----------
    cf=pd.read_csv(os.path.join(RES,f"confirm_scores_{tag}.csv"),dtype={"key":str}).drop_duplicates(["dialect","key"])
    cs=cf[cf.key.isin(keys)]; cPR=cs.pivot(index="key",columns="dialect",values="pred").loc[keys,D].values; cPM=cs.pivot(index="key",columns="dialect",values="p_max").loc[keys,D].values
    rep.append(f"Re-run reproducibility (k=0 vs confirm_scores, {n}×{len(D)} cells): identical prediction {np.mean(A[0]['PR']==cPR):.4f}; mean |Δp_max| {np.mean(np.abs(A[0]['PM']-cPM)):.4f}; max |Δp_max| {np.max(np.abs(A[0]['PM']-cPM)):.4f}\n")
    # ---------- R1 order sensitivity ----------
    PRs=np.stack([A[k]["PR"] for k in ORD],0)                       # 4 × n × |D|
    osr=(PRs!=PRs[0:1]).any(0).astype(float)                         # n × |D|
    MV=np.zeros_like(A[0]["PR"])
    for i in range(n):
        for j in range(len(D)):
            cnt=np.bincount(PRs[:,i,j],minlength=4); top=np.flatnonzero(cnt==cnt.max()); MV[i,j]=top[0] if len(top)==1 else PRs[0,i,j]
    mvacc=(MV==A[0]["ANS"]).astype(float)
    rep.append("### R1 Order-sensitivity rate (prediction by content not identical across the 4 orderings) and majority-vote accuracy\n\n| variety | OSR [CI] | ΔOSR vs MSA [CI] | acc k=0 | majority-vote acc | mean acc over orderings |\n|---|---|---|---|---|---|")
    for j,d in enumerate(D):
        lo,hi=ci([osr[s,j].mean() for s in BS]); dlo,dhi=ci([osr[s,j].mean()-osr[s,im].mean() for s in BS]); macc=np.mean([A[k]["C"][:,j].mean() for k in ORD])
        rep.append(f"| {d} | {osr[:,j].mean():.3f} [{lo:.3f},{hi:.3f}] | {osr[:,j].mean()-osr[:,im].mean():+.3f} [{dlo:+.3f},{dhi:+.3f}] | {A[0]['C'][:,j].mean():.3f} | {mvacc[:,j].mean():.3f} | {macc:.3f} |")
        R1.append(dict(model=tag,variety=d,n=n,osr=osr[:,j].mean(),osr_lo=lo,osr_hi=hi,d_osr=osr[:,j].mean()-osr[:,im].mean(),d_osr_lo=dlo,d_osr_hi=dhi,acc_k0=A[0]['C'][:,j].mean(),mv_acc=mvacc[:,j].mean(),mean_acc_orders=macc))
    # ---------- R2 gap stability: Δacc_k and ΔP1_k per ordering; order-averaged with CI ----------
    rep.append("\n### R2 Gap stability across orderings (variety − MSA)\n\n| variety | Δacc k=0,1,2,3 | Δacc order-avg [CI] | verdict | ΔP1 k=0,1,2,3 | ΔP1 order-avg [CI] | verdict |\n|---|---|---|---|---|---|---|")
    for j,d in enumerate(D):
        if d==MSA: continue
        dacc=[A[k]["C"][:,j].mean()-A[k]["C"][:,im].mean() for k in ORD]; dp1=[p1_gap(A[k]["PM"],A[k]["C"],j,im) for k in ORD]
        ba=[np.mean([A[k]["C"][s,j].mean()-A[k]["C"][s,im].mean() for k in ORD]) for s in BS]
        bp=[np.mean([p1_gap(A[k]["PM"][s],A[k]["C"][s],j,im) for k in ORD]) for s in BS]
        alo,ahi=ci(ba); plo,phi=ci(bp); ma=np.mean(dacc); mp=np.mean(dp1)
        va="order-robust" if ((ahi<0 or alo>0) and all(np.sign(x)==np.sign(ma) for x in dacc)) else "order-sensitive/not resolved"
        vp="order-robust" if ((phi<0 or plo>0) and all(np.sign(x)==np.sign(mp) for x in dp1)) else "order-sensitive/not resolved"
        rep.append(f"| {d} | {' / '.join(f'{x:+.3f}' for x in dacc)} | {ma:+.3f} [{alo:+.3f},{ahi:+.3f}] | {va} | {' / '.join(f'{x:+.3f}' for x in dp1)} | {mp:+.3f} [{plo:+.3f},{phi:+.3f}] | {vp} |")
        R2.append(dict(model=tag,variety=d,**{f"d_acc_k{k}":dacc[k] for k in ORD},d_acc_avg=ma,d_acc_lo=alo,d_acc_hi=ahi,d_acc_verdict=va,**{f"d_p1_k{k}":dp1[k] for k in ORD},d_p1_avg=mp,d_p1_lo=plo,d_p1_hi=phi,d_p1_verdict=vp))
    # ---------- R3 S4 at the original τ_MSA per ordering ----------
    cal=cf[(cf.key.isin(CAL))&(cf.dialect==MSA)]; tau=tau_rule(cal.p_max.values.astype(float),cal.correct.values.astype(float),RSTAR)
    rep.append(f"\n### R3 S4 at the original τ_MSA = {tau:.3f} (r*={RSTAR}, calibration MSA under k=0): Δanswered (variety − MSA) per ordering\n\n| variety | Δanswered k=0,1,2,3 | order-avg [CI] | realised risk k=0 → order-avg |\n|---|---|---|---|")
    for j,d in enumerate(D):
        if d==MSA: continue
        dk=[(A[k]["PM"][:,j]>=tau).mean()-(A[k]["PM"][:,im]>=tau).mean() for k in ORD]
        bb=[np.mean([(A[k]["PM"][s,j]>=tau).mean()-(A[k]["PM"][s,im]>=tau).mean() for k in ORD]) for s in BS]; lo,hi=ci(bb)
        rk_=[(1-A[k]["C"][A[k]["PM"][:,j]>=tau,j]).mean() if (A[k]["PM"][:,j]>=tau).any() else np.nan for k in ORD]
        rep.append(f"| {d} | {' / '.join(f'{x:+.3f}' for x in dk)} | {np.mean(dk):+.3f} [{lo:+.3f},{hi:+.3f}] | {rk_[0]:.3f} → {np.nanmean(rk_):.3f} |")
        R3.append(dict(model=tag,variety=d,tau_msa=tau,**{f"d_ans_k{k}":dk[k] for k in ORD},d_ans_avg=np.mean(dk),d_ans_lo=lo,d_ans_hi=hi,risk_k0=rk_[0],risk_avg=np.nanmean(rk_)))
    # ---------- R4 P3 decomposition ----------
    rep.append("\n### R4 Answer change vs MSA (P3) against the position-noise floor\n\n| variety | P3 answer change k=0 | order-avg | within-variety change k=0 vs k=1 (noise floor) | answer change on majority-vote predictions |\n|---|---|---|---|---|")
    floor_msa=(A[0]["PR"][:,im]!=A[1]["PR"][:,im]).mean()
    for j,d in enumerate(D):
        fl=(A[0]["PR"][:,j]!=A[1]["PR"][:,j]).mean()
        if d==MSA: rep.append(f"| {d} | — | — | {fl:.3f} | — |"); R4.append(dict(model=tag,variety=d,p3_k0=np.nan,p3_avg=np.nan,floor_k0_vs_k1=fl,p3_majority=np.nan)); continue
        p3=[(A[k]["PR"][:,j]!=A[k]["PR"][:,im]).mean() for k in ORD]; p3mv=(MV[:,j]!=MV[:,im]).mean()
        rep.append(f"| {d} | {p3[0]:.3f} | {np.mean(p3):.3f} | {fl:.3f} | {p3mv:.3f} |")
        R4.append(dict(model=tag,variety=d,p3_k0=p3[0],p3_avg=np.mean(p3),floor_k0_vs_k1=fl,p3_majority=p3mv))
    rep.append(f"\n(MSA within-variety change k=0 vs k=1: {floor_msa:.3f}.)")
    # ---------- R5 generation agreement ----------
    gf=os.path.join(RES,f"robust_gen_{tag}.csv")
    if os.path.exists(gf):
        g=pd.read_csv(gf,dtype={"key":str}).drop_duplicates(["dialect","key","cond"]); g=g[g.key.isin(keys)]
        for cond in sorted(g.cond.unique()):
            gc=g[g.cond==cond]; have=set.intersection(*[set(gc[gc.dialect==d].key) for d in D]); kk=[k for k in keys if k in have]; nn=len(kk)
            if nn<0.9*n: rep.append(f"\n### R5 {cond}: incomplete ({nn}/{n} keys) — skipped"); continue
            gc=gc.set_index(["dialect","key"]); idx=[keys.index(k) for k in kk]; BSg=[rng.integers(0,nn,nn) for _ in range(B)]
            ex=np.full((nn,len(D)),-1); rule=np.empty((nn,len(D)),dtype=object)
            for j,d in enumerate(D):
                for i,k in enumerate(kk):
                    txt=gc.loc[(d,k),"gen_text"]; txt="" if pd.isna(txt) else str(txt)
                    e,r=extract_g1(txt) if cond=="G1" else extract_g2(txt,OPTS.get((k,d),["\x00"]*4)); ex[i,j]=-1 if e is None else e; rule[i,j]=r
            PR0=A[0]["PR"][idx]; ANS=A[0]["ANS"][idx]; unex=(ex<0).astype(float); agree=np.where(ex>=0,(ex==PR0).astype(float),np.nan); gacc=(ex==ANS).astype(float)
            rep.append(f"\n### R5 {cond} ({nn} keys): generated answer vs letter-logit prediction (k=0)\n\n| variety | unextractable [CI] | Δunextr vs MSA [CI] | agreement with logit pred (extractable) [CI] | gen acc (unextractable = wrong) | logit acc | rules used |\n|---|---|---|---|---|---|---|")
            for j,d in enumerate(D):
                ulo,uhi=ci([unex[s,j].mean() for s in BSg]); dlo,dhi=ci([unex[s,j].mean()-unex[s,im].mean() for s in BSg]); alo,ahi=ci([np.nanmean(agree[s,j]) for s in BSg])
                rc_=pd.Series(rule[:,j]).value_counts().to_dict()
                rep.append(f"| {d} | {unex[:,j].mean():.3f} [{ulo:.3f},{uhi:.3f}] | {unex[:,j].mean()-unex[:,im].mean():+.3f} [{dlo:+.3f},{dhi:+.3f}] | {np.nanmean(agree[:,j]):.3f} [{alo:.3f},{ahi:.3f}] | {gacc[:,j].mean():.3f} | {A[0]['C'][idx][:,j].mean():.3f} | {rc_} |")
                row=dict(model=tag,cond=cond,variety=d,n=nn,unextractable=unex[:,j].mean(),unex_lo=ulo,unex_hi=uhi,d_unex=unex[:,j].mean()-unex[:,im].mean(),d_unex_lo=dlo,d_unex_hi=dhi,agreement=np.nanmean(agree[:,j]),agr_lo=alo,agr_hi=ahi,gen_acc=gacc[:,j].mean(),logit_acc=A[0]['C'][idx][:,j].mean(),rules=str(rc_))
                if cond=="G2" and "pred_chat" in gc.columns:
                    pc=np.array([gc.loc[(d,k),"pred_chat"] for k in kk],dtype=float); okc=~np.isnan(pc)
                    row.update(chat_logit_acc=float((pc[okc]==ANS[okc,j]).mean()) if okc.any() else np.nan, chat_logit_vs_raw_logit=float((pc[okc]==PR0[okc,j]).mean()) if okc.any() else np.nan,
                               gen_vs_chat_logit=float(np.nanmean(np.where(ex[okc,j]>=0,(ex[okc,j]==pc[okc]).astype(float),np.nan))) if okc.any() else np.nan)
                R5.append(row)
            if cond=="G2":
                rep.append("\nG2 secondary (letter-logit under the chat template, first generated step):\n\n| variety | chat-logit acc | agreement chat-logit vs raw-prompt logit | agreement generated vs chat-logit |\n|---|---|---|---|")
                for r in [x for x in R5 if x["model"]==tag and x["cond"]=="G2"]: rep.append(f"| {r['variety']} | {r.get('chat_logit_acc',np.nan):.3f} | {r.get('chat_logit_vs_raw_logit',np.nan):.3f} | {r.get('gen_vs_chat_logit',np.nan):.3f} |")
    else: rep.append("\n### R5: no generation file yet")
for name,rows in [("R1_order_sensitivity",R1),("R2_gap_stability",R2),("R3_s4_by_order",R3),("R4_p3_decomposition",R4),("R5_generation",R5)]:
    pd.DataFrame(rows).to_csv(os.path.join(OUT,f"{name}.csv"),index=False)
open(os.path.join(OUT,"ROBUST_REPORT.md"),"w").write("\n".join(rep)+"\n"); print("\n".join(rep)); print("written",OUT)
