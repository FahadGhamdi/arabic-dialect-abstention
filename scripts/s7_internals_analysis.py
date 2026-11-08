#!/usr/bin/env python
"""Stage 7: analyses on internals: (1) logit-lens 'knows-but-fails' curves, (2) MSA-trained correctness probe transfer,
(3) dialect decodability at the answer position. Writes results/internals_<model>/analysis.md"""
import os, glob, json, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score
RES=os.environ["ADA_RES"]; OUT=os.environ["ADA_DATA"]
meta=json.load(open(os.path.join(OUT,"pilot_keys.json"))); MSA=meta["MSA"]; ENG=meta["ENG"]
for od in sorted(glob.glob(os.path.join(RES,"internals_*"))):
    tag=os.path.basename(od)[10:]; 
    if not os.path.exists(os.path.join(od,"lens.npy")): continue
    H=np.load(os.path.join(od,"hidden.npy")); LENS=np.load(os.path.join(od,"lens.npy")); M=pd.read_csv(os.path.join(od,"meta.csv"))
    n,L1,d=H.shape; lines=[f"# Internals analysis — {tag} (n={n}, layers+1={L1}, d={d})\n"]
    # normalize lens over 4 letters
    P=np.exp(LENS-np.logaddexp.reduce(LENS,axis=-1,keepdims=True))  # n x L1 x 4
    ans=M.answer.values; pc=P[np.arange(n),:,ans]  # n x L1 prob of correct letter
    pred=P.argmax(-1); corr_layer=(pred==ans[:,None])  # n x L1
    final_corr=corr_layer[:,-1]
    M["final_correct"]=final_corr
    dial=sorted(M.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x))
    # (1) logit-lens accuracy curve per variety
    lines.append("## 1. Logit-lens accuracy (argmax over 4 letters) by layer\n")
    layers=list(range(0,L1,max(1,L1//12)))+[L1-1]; layers=sorted(set(layers))
    lines.append("| variety | "+" | ".join(f"L{l}" for l in layers)+" |"); lines.append("|---|"+"---|"*len(layers))
    for dname in dial:
        m=(M.dialect==dname).values; lines.append(f"| {dname} | "+" | ".join(f"{corr_layer[m,l].mean():.2f}" for l in layers)+" |")
    # knows-but-fails: among final-wrong items, fraction where correct letter is argmax at some layer in the last third
    lines.append("\n## 2. 'Knows-but-fails': final-wrong items where the correct letter was argmax at some layer in the last third (and max p_correct over those layers)\n")
    lo=int(L1*2/3)
    lines.append("| variety | n final-wrong | transiently-correct (%) | mean max p_correct (layers last third) | mean final p_correct |"); lines.append("|---|---|---|---|---|")
    for dname in dial:
        m=((M.dialect==dname)&(~M.final_correct)).values
        tc=corr_layer[m,lo:-1].any(1).mean()*100 if m.any() else float('nan')
        lines.append(f"| {dname} | {m.sum()} | {tc:.1f} | {pc[m,lo:-1].max(1).mean():.3f} | {pc[m,-1].mean():.3f} |")
    # paired flips: MSA-correct & D-wrong items: is correct letter transiently argmax in D run? vs MSA-wrong&D-wrong
    piv=M.pivot(index="key",columns="dialect",values="final_correct")
    lines.append("\n## 3. Paired flip items (MSA✓→D✗): transient correctness in the dialect run vs. items wrong in both\n")
    lines.append("| dialect | flips n | transiently-correct % (flips) | both-wrong n | transiently-correct % (both-wrong) |"); lines.append("|---|---|---|---|---|")
    idx={(r.dialect,r.key):i for i,r in enumerate(M.itertuples())}
    for dname in dial:
        if dname in (MSA,): continue
        fl=[k for k in piv.index if piv.loc[k,MSA]==1 and piv.loc[k,dname]==0]; bw=[k for k in piv.index if piv.loc[k,MSA]==0 and piv.loc[k,dname]==0]
        f=lambda ks: np.mean([corr_layer[idx[(dname,k)],lo:-1].any() for k in ks])*100 if ks else float('nan')
        lines.append(f"| {dname} | {len(fl)} | {f(fl):.1f} | {len(bw)} | {f(bw):.1f} |")
    # (4) correctness probe trained on MSA, tested on dialects (5-fold over keys), a few layers
    lines.append("\n## 4. Correctness probe (logistic, L2) trained on MSA last-token states; AUROC on held-out keys per variety\n")
    keys=sorted(M.key.unique()); kf=KFold(5,shuffle=True,random_state=0)
    probe_layers=sorted(set([L1//4, L1//2, (3*L1)//4, L1-2, L1-1]))
    lines.append("| layer | "+" | ".join(dial)+" | (p_max AUROC baseline per variety) |"); lines.append("|---|"+"---|"*(len(dial)+1))
    # baseline from final-layer letter probs
    pmax=P[:,-1,:].max(-1)
    base={dn: roc_auc_score(final_corr[(M.dialect==dn).values], pmax[(M.dialect==dn).values]) for dn in dial}
    for l in probe_layers:
        scores={dn:[] for dn in dial}; ys={dn:[] for dn in dial}
        for tr,te in kf.split(keys):
            trk=set(np.array(keys)[tr]); tek=set(np.array(keys)[te])
            mtr=((M.dialect==MSA)&(M.key.isin(trk))).values
            X=H[mtr,l,:].astype(np.float32); mu=X.mean(0); sd=X.std(0)+1e-6
            clf=LogisticRegression(C=0.05,max_iter=2000).fit((X-mu)/sd, final_corr[mtr])
            for dn in dial:
                mte=((M.dialect==dn)&(M.key.isin(tek))).values
                scores[dn]+=list(clf.decision_function((H[mte,l,:].astype(np.float32)-mu)/sd)); ys[dn]+=list(final_corr[mte])
        lines.append(f"| L{l} | "+" | ".join(f"{roc_auc_score(ys[dn],scores[dn]):.3f}" for dn in dial)+" | "+", ".join(f"{dn}:{base[dn]:.2f}" for dn in dial)+" |")
    # (5) dialect decodability at the answer position: MSA vs each dialect, 5-fold, layers
    lines.append("\n## 5. Dialect-vs-MSA decodability at the answer position (probe accuracy, 5-fold over keys)\n")
    lines.append("| layer | "+" | ".join(dn for dn in dial if dn!=MSA)+" |"); lines.append("|---|"+"---|"*(len(dial)-1))
    for l in probe_layers:
        accs=[]
        for dn in dial:
            if dn==MSA: continue
            m=(M.dialect.isin([MSA,dn])).values; X=H[m,l,:].astype(np.float32); y=(M.dialect[m]==dn).values.astype(int); kk=M.key[m].values
            ok=[]
            for tr,te in kf.split(keys):
                tek=set(np.array(keys)[te]); te_m=np.isin(kk,list(tek)); tr_m=~te_m
                mu=X[tr_m].mean(0); sd=X[tr_m].std(0)+1e-6
                clf=LogisticRegression(C=0.05,max_iter=2000).fit((X[tr_m]-mu)/sd,y[tr_m]); ok.append((clf.predict((X[te_m]-mu)/sd)==y[te_m]).mean())
            accs.append(np.mean(ok))
        lines.append(f"| L{l} | "+" | ".join(f"{a:.3f}" for a in accs)+" |")
    open(os.path.join(od,"analysis.md"),"w").write("\n".join(lines)); print("\n".join(lines)); print()
