#!/usr/bin/env python
"""Stage A — corrected measurement from ORIGINAL scores only (results/scores_*.csv). No lens-based numbers.
Outputs results/stageA/*.csv and results/stageA/STAGE_A_REPORT.md
 A1 risk–coverage (selective prediction) per variety; answerable fraction at the MSA-matched risk; AURC
 A2 conformal: coverage at MSA-calibrated thresholds AND set size at matched (Mondrian) coverage, alpha 0.05..0.40
 A3 calibration-efficiency curve: n_cal dialect items -> coverage on held-out dialect items (repeated splits, CI)
 A4 churn: answer change vs correctness change (incl. wrong->other-wrong), A_any / A_strict across dialects
 A5 multiclass Brier, ECE, mean confidence
All uncertainty: paired bootstrap over question keys (B resamples)."""
import os, sys, glob, json, math, numpy as np, pandas as pd
RES=os.environ.get("ADA_RES","results"); OUT=os.path.join(RES,"stageA"); os.makedirs(OUT,exist_ok=True)
MSA="MSA"; ENG="ENG"; B=int(os.environ.get("ADA_B","1000")); rng=np.random.default_rng(0)
ALPHAS=[0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40]
def qhat(s,a): n=len(s); k=min(n,math.ceil((n+1)*(1-a))); return np.sort(s)[k-1]
def ece(p,c,nb=15):
    b=np.minimum((p*nb).astype(int),nb-1); return sum(((b==i).mean()*abs(p[b==i].mean()-c[b==i].mean())) for i in range(nb) if (b==i).any())
def ci(x): x=np.asarray(x); return np.nanpercentile(x,2.5), np.nanpercentile(x,97.5)
report=["# Stage A — corrected measurement (original scores only; v2: A2 cross-fit by key, A3 distributional)\n",
        f"Paired by question key; {B} bootstrap resamples over keys; alphas {ALPHAS}. Generated automatically.\n"]
rowsA1=[];rowsA2=[];rowsA3=[];rowsA4=[];rowsA5=[]
for fn in sorted(glob.glob(os.path.join(RES,"scores_*.csv"))):
    tag=os.path.basename(fn)[7:-4]; df=pd.read_csv(fn).drop_duplicates(["dialect","key"])
    keys=sorted(set.intersection(*[set(df[df.dialect==d].key) for d in df.dialect.unique()])); df=df[df.key.isin(keys)]
    D=sorted(df.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); n=len(keys)
    piv=lambda c: df.pivot(index="key",columns="dialect",values=c).loc[keys,D].values
    C=piv("correct").astype(float); PT=piv("p_true"); PM=piv("p_max"); PR=piv("pred"); ANS=piv("answer")
    L=np.stack([piv(c) for c in ["lA","lB","lC","lD"]],-1); P=np.exp(L-np.logaddexp.reduce(L,-1,keepdims=True))  # keys x D x 4
    im=D.index(MSA); dial=[d for d in D if d not in (MSA,ENG)]
    report.append(f"\n## {tag} (n_keys={n})\n")
    # ---------- A5: calibration (multiclass Brier) ----------
    Y=np.zeros_like(P); 
    for j in range(len(D)): Y[np.arange(n),j,ANS[:,j].astype(int)]=1
    brier=((P-Y)**2).sum(-1)  # keys x D
    report.append("### A5 Calibration (per variety)\n\n| variety | acc | mean conf | ECE | multiclass Brier (mean, 95% CI) |\n|---|---|---|---|---|")
    for j,d in enumerate(D):
        bs=[brier[rng.integers(0,n,n),j].mean() for _ in range(B)]; lo,hi=ci(bs)
        report.append(f"| {d} | {C[:,j].mean():.3f} | {PM[:,j].mean():.3f} | {ece(PM[:,j],C[:,j]):.3f} | {brier[:,j].mean():.3f} [{lo:.3f},{hi:.3f}] |")
        rowsA5.append(dict(model=tag,variety=d,acc=C[:,j].mean(),conf=PM[:,j].mean(),ece=ece(PM[:,j],C[:,j]),brier=brier[:,j].mean(),brier_lo=lo,brier_hi=hi))
    # ---------- A1: risk–coverage / equal-risk answerable fraction ----------
    # selective risk at coverage c: sort by confidence desc, risk = error rate among top c fraction. AURC = mean risk over coverage grid.
    grid=np.linspace(0.05,1.0,20)
    def rc_curve(conf,corr):
        o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1)
        return np.array([cum[int(math.ceil(c*len(e)))-1] for c in grid])
    def answerable_at_risk(conf,corr,target):
        # largest coverage whose selective risk <= target (monotone envelope); 0 if none
        o=np.argsort(-conf); e=1-corr[o]; cum=np.cumsum(e)/np.arange(1,len(e)+1)
        ok=np.where(cum<=target)[0]; return (ok.max()+1)/len(e) if len(ok) else 0.0
    report.append("\n### A1 Selective prediction: answerable fraction at the risk MSA attains at 50% coverage (and at fixed risk levels), AURC\n")
    tgt_msa=rc_curve(PM[:,im],C[:,im])[np.argmin(abs(grid-0.5))]
    report.append(f"MSA selective risk at 50% coverage = {tgt_msa:.3f}\n")
    report.append("| variety | answerable @ MSA-matched risk | Δ vs MSA [95% CI] | answerable @ risk 0.20 | @ risk 0.30 | AURC | ΔAURC [CI] |\n|---|---|---|---|---|---|---|")
    for j,d in enumerate(D):
        a0=answerable_at_risk(PM[:,j],C[:,j],tgt_msa); au=rc_curve(PM[:,j],C[:,j]).mean()
        da=[];dau=[]
        for _ in range(B):
            s=rng.integers(0,n,n); t=rc_curve(PM[s,im],C[s,im])[np.argmin(abs(grid-0.5))]
            da.append(answerable_at_risk(PM[s,j],C[s,j],t)-answerable_at_risk(PM[s,im],C[s,im],t)); dau.append(rc_curve(PM[s,j],C[s,j]).mean()-rc_curve(PM[s,im],C[s,im]).mean())
        lo,hi=ci(da); lo2,hi2=ci(dau)
        report.append(f"| {d} | {a0:.3f} | {np.mean(da):+.3f} [{lo:+.3f},{hi:+.3f}] | {answerable_at_risk(PM[:,j],C[:,j],0.20):.3f} | {answerable_at_risk(PM[:,j],C[:,j],0.30):.3f} | {au:.3f} | {np.mean(dau):+.3f} [{lo2:+.3f},{hi2:+.3f}] |")
        rowsA1.append(dict(model=tag,variety=d,msa_matched_risk=tgt_msa,answerable=a0,d_answerable=np.mean(da),d_lo=lo,d_hi=hi,ans_r20=answerable_at_risk(PM[:,j],C[:,j],0.20),ans_r30=answerable_at_risk(PM[:,j],C[:,j],0.30),aurc=au,d_aurc=np.mean(dau),d_aurc_lo=lo2,d_aurc_hi=hi2))
    # ---------- A2: conformal across alphas: MSA-calibrated coverage; set size (and achieved coverage) at own-variety threshold ----------
    # Cross-fitting by QUESTION KEY: for each replicate, keys are first assigned to 2 folds, then bootstrapped WITHIN fold,
    # so no key (nor any of its 7 variants) is ever in both calibration and evaluation of the same replicate.
    S=1-PT; SO=1-P
    report.append("\n### A2 Conformal across α (2-fold cross-fit by key, bootstrap within fold; B replicates)\n\nCoverage with the MSA threshold (Δ vs MSA) | set size AND achieved coverage with the own-variety threshold (= cost of matched coverage), size ratio vs MSA\n")
    report.append("| α | variety | cov@MSA-thr | Δcov [CI] | size@MSA-thr | cov@own-thr | size@own-thr | size ratio own/MSA-own [CI] |\n|---|---|---|---|---|---|---|---|")
    for a in ALPHAS:
        acc_cov={d:[] for d in D}; acc_sz={d:[] for d in D}; acc_own={d:[] for d in D}; acc_owncov={d:[] for d in D}
        for b in range(B):
            perm=rng.permutation(n); folds=[perm[:n//2],perm[n//2:]]
            fb=[fo[rng.integers(0,len(fo),len(fo))] for fo in folds]   # bootstrap within fold (keys stay in their fold)
            cov=np.zeros(len(D)); sz=np.zeros(len(D)); own=np.zeros(len(D)); owncov=np.zeros(len(D))
            for x,y in [(0,1),(1,0)]:
                q=qhat(S[fb[x],im],a)
                for j in range(len(D)):
                    cov[j]+=(S[fb[y],j]<=q).mean()/2; sz[j]+=(SO[fb[y],j,:]<=q).sum(-1).mean()/2
                    qo=qhat(S[fb[x],j],a); own[j]+=(SO[fb[y],j,:]<=qo).sum(-1).mean()/2; owncov[j]+=(S[fb[y],j]<=qo).mean()/2
            for j,d in enumerate(D): acc_cov[d].append(cov[j]); acc_sz[d].append(sz[j]); acc_own[d].append(own[j]); acc_owncov[d].append(owncov[j])
        for j,d in enumerate(D):
            dc=np.array(acc_cov[d])-np.array(acc_cov[MSA]); r=np.array(acc_own[d])/np.array(acc_own[MSA]); lo,hi=ci(dc); rlo,rhi=ci(r)
            report.append(f"| {a:.2f} | {d} | {np.mean(acc_cov[d]):.3f} | {np.mean(dc):+.3f} [{lo:+.3f},{hi:+.3f}] | {np.mean(acc_sz[d]):.2f} | {np.mean(acc_owncov[d]):.3f} | {np.mean(acc_own[d]):.2f} | {np.mean(r):.3f} [{rlo:.3f},{rhi:.3f}] |")
            rowsA2.append(dict(model=tag,alpha=a,variety=d,cov_msathr=np.mean(acc_cov[d]),d_cov=np.mean(dc),d_cov_lo=lo,d_cov_hi=hi,size_msathr=np.mean(acc_sz[d]),cov_ownthr=np.mean(acc_owncov[d]),size_ownthr=np.mean(acc_own[d]),size_ratio=np.mean(r),size_ratio_lo=rlo,size_ratio_hi=rhi))
    # ---------- A3: calibration-efficiency: n_cal own-variety items -> coverage on disjoint held-out items; DISTRIBUTION across splits, not just the mean ----------
    # Reference: for split conformal with n calibration points, coverage of a fresh point ~ Beta(n+1-l, l), l=floor((n+1)α) (Vovk 2012); the
    # realised coverage on a finite test set adds binomial noise. We report mean, SD, 2.5/97.5 pct, P(|cov-target|<=0.05), P(cov>=target-0.05), set size.
    from scipy import stats
    a=0.30; NS=[25,50,100,150,200,250]; NSPL=500; tgt=1-a
    report.append(f"\n### A3 Calibration efficiency at α={a:.2f} (target {tgt:.2f}): calibrate on n own-variety items, evaluate on 250 disjoint items; {NSPL} random splits\n")
    report.append("Each cell: mean coverage [2.5, 97.5 pct] · P(|cov−target| ≤ 0.05) · mean set size. Last column: MSA threshold with 250 MSA items (no dialect data).\n")
    report.append("| variety | "+" | ".join(f"n={k}" for k in NS)+" | MSA-thr (n=250 MSA) |\n|---|"+"---|"*(len(NS)+1))
    for j,d in enumerate(D):
        cells=[]
        for k in NS:
            covs=[]; szs=[]
            for _ in range(NSPL):
                perm=rng.permutation(n); cal=perm[:k]; tst=perm[250:]
                q=qhat(S[cal,j],a); covs.append((S[tst,j]<=q).mean()); szs.append((SO[tst,j,:]<=q).sum(-1).mean())
            covs=np.array(covs); lo,hi=ci(covs); pin=(abs(covs-tgt)<=0.05).mean(); pge=(covs>=tgt-0.05).mean()
            l=math.floor((k+1)*a); beta_lo,beta_hi=stats.beta.ppf([0.025,0.975],k+1-l,l) if l>0 else (np.nan,np.nan)
            cells.append(f"{covs.mean():.3f} [{lo:.3f},{hi:.3f}] · {pin:.2f} · {np.mean(szs):.2f}")
            rowsA3.append(dict(model=tag,variety=d,n_cal=k,cov=covs.mean(),sd=covs.std(),lo=lo,hi=hi,p_within5=pin,p_ge_minus5=pge,set_size=np.mean(szs),beta_lo=beta_lo,beta_hi=beta_hi))
        base=[]; bsz=[]
        for _ in range(NSPL):
            perm=rng.permutation(n); cal=perm[:250]; tst=perm[250:]; q=qhat(S[cal,im],a); base.append((S[tst,j]<=q).mean()); bsz.append((SO[tst,j,:]<=q).sum(-1).mean())
        base=np.array(base); lo,hi=ci(base)
        report.append(f"| {d} | "+" | ".join(cells)+f" | {base.mean():.3f} [{lo:.3f},{hi:.3f}] · {(abs(base-tgt)<=0.05).mean():.2f} · {np.mean(bsz):.2f} |")
        rowsA3.append(dict(model=tag,variety=d,n_cal=0,cov=base.mean(),sd=base.std(),lo=lo,hi=hi,p_within5=(abs(base-tgt)<=0.05).mean(),p_ge_minus5=(base>=tgt-0.05).mean(),set_size=np.mean(bsz),beta_lo=np.nan,beta_hi=np.nan))
    l=math.floor(51*a); blo,bhi=stats.beta.ppf([0.025,0.975],51-l,l)
    report.append(f"\nTheory check: split conformal with n=50, α={a:.2f} has coverage ~ Beta({51-l},{l}) for a fresh point: 95% range [{blo:.3f},{bhi:.3f}] before test-set noise — the wide ranges above are the expected finite-n behaviour, not an artefact.")
    # ---------- A4: churn, two definitions; A_any / A_strict ----------
    report.append("\n### A4 Item-level instability vs MSA (two definitions) and reliability bounds across the 5 dialects\n")
    report.append("| variety | answer changed (%) [CI] | correctness changed (%) | ✓→✗ | ✗→✓ | ✗→other ✗ | agreement with MSA answer (%) |\n|---|---|---|---|---|---|---|")
    for j,d in enumerate(D):
        if d==MSA: continue
        ch=(PR[:,j]!=PR[:,im]); cc=(C[:,j]!=C[:,im]); a=int(((C[:,im]==1)&(C[:,j]==0)).sum()); b_=int(((C[:,im]==0)&(C[:,j]==1)).sum()); ww=int((ch&(C[:,j]==0)&(C[:,im]==0)).sum())
        bs=[ch[rng.integers(0,n,n)].mean() for _ in range(B)]; lo,hi=ci(bs)
        report.append(f"| {d} | {ch.mean()*100:.1f} [{lo*100:.1f},{hi*100:.1f}] | {cc.mean()*100:.1f} | {a} | {b_} | {ww} | {(1-ch.mean())*100:.1f} |")
        rowsA4.append(dict(model=tag,variety=d,answer_change=ch.mean(),ac_lo=lo,ac_hi=hi,correct_change=cc.mean(),ok_to_bad=a,bad_to_ok=b_,bad_to_otherbad=ww))
    dj=[D.index(d) for d in dial]; anyc=(C[:,dj].max(1)); strict=(C[:,dj].min(1)); msa_c=C[:,im]
    report.append(f"\nAcross the 5 dialects: A_any (correct in ≥1 dialect) = {anyc.mean():.3f}; A_strict (correct in all 5) = {strict.mean():.3f}; MSA accuracy = {msa_c.mean():.3f}; mean dialect accuracy = {C[:,dj].mean():.3f}. Reliability gap A_any−A_strict = {anyc.mean()-strict.mean():.3f}.")
    rowsA4.append(dict(model=tag,variety="ALL5",a_any=anyc.mean(),a_strict=strict.mean(),msa_acc=msa_c.mean(),mean_dialect_acc=C[:,dj].mean()))
pd.DataFrame(rowsA1).to_csv(os.path.join(OUT,"A1_selective.csv"),index=False); pd.DataFrame(rowsA2).to_csv(os.path.join(OUT,"A2_conformal.csv"),index=False)
pd.DataFrame(rowsA3).to_csv(os.path.join(OUT,"A3_calib_efficiency.csv"),index=False); pd.DataFrame(rowsA4).to_csv(os.path.join(OUT,"A4_churn.csv"),index=False); pd.DataFrame(rowsA5).to_csv(os.path.join(OUT,"A5_calibration.csv"),index=False)
open(os.path.join(OUT,"STAGE_A_REPORT.md"),"w").write("\n".join(report)); print("\n".join(report))
