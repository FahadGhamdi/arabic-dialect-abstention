#!/usr/bin/env python
"""Churn analysis: pairwise answer-change matrix across varieties; flip rate vs MSA decision margin;
flip vs per-item lexical distance (token Jaccard between dialect and MSA question+choices)."""
import os, glob, json, re, numpy as np, pandas as pd
RES=os.environ["ADA_RES"]; OUT=os.environ["ADA_DATA"]
meta=json.load(open(os.path.join(OUT,"pilot_keys.json"))); MSA=meta["MSA"]; ENG=meta["ENG"]
dm=None
if os.path.exists(os.path.join(OUT,"damm.csv")):
    dm=pd.read_csv(os.path.join(OUT,"damm.csv")); dm["choices"]=dm["choices"].astype(str).str.split(r"\|\|\|")
elif os.path.exists(os.path.join(OUT,"damm.parquet")):
    try: dm=pd.read_parquet(os.path.join(OUT,"damm.parquet"))
    except Exception as e: print("parquet unreadable:",e)
def toks(s): return set(re.findall(r"\w+", str(s)))
lex={}
if dm is not None:
    dm["key"]=dm["domain"]+"|"+dm["qid"].astype(str); dm["text"]=dm["question"]+" "+dm["choices"].apply(lambda c:" ".join(list(c)))
    T=dm.pivot(index="key",columns="dialect",values="text")
    for d in T.columns:
        if d==MSA: continue
        lex[d]={k:1-len(toks(T.loc[k,d])&toks(T.loc[k,MSA]))/max(1,len(toks(T.loc[k,d])|toks(T.loc[k,MSA]))) for k in T.index}
for fn in sorted(glob.glob(os.path.join(RES,"scores_*.csv"))):
    df=pd.read_csv(fn).drop_duplicates(["dialect","key"]); tag=os.path.basename(fn)[7:-4]
    keys=sorted(set.intersection(*[set(df[df.dialect==d].key) for d in df.dialect.unique()]))
    if len(keys)<100: continue
    df=df[df.key.isin(keys)]
    PR=df.pivot(index="key",columns="dialect",values="pred"); C=df.pivot(index="key",columns="dialect",values="correct")
    L=np.stack([df.pivot(index="key",columns="dialect",values=c).loc[PR.index].values for c in ["lA","lB","lC","lD"]],-1)
    P=np.exp(L-np.logaddexp.reduce(L,-1,keepdims=True)); srt=np.sort(P,-1); margin=srt[...,-1]-srt[...,-2]  # keys x dial
    D=list(PR.columns); order=sorted(D,key=lambda x:(x!=MSA,x==ENG,x))
    print(f"\n## {tag}: pairwise answer-change rate (% of items whose predicted letter differs), n={len(PR)}")
    print("| | "+" | ".join(order)+" |"); print("|---|"+"---|"*len(order))
    for a in order: print(f"| {a} | "+" | ".join(f"{(PR[a]!=PR[b]).mean()*100:.0f}" if a!=b else "–" for b in order)+" |")
    print(f"\n{tag}: answer-change rate vs MSA by MSA decision-margin quartile (low margin = near tie)")
    mi=D.index(MSA); q=pd.qcut(margin[:,mi],4,labels=["Q1 low","Q2","Q3","Q4 high"])
    rows=[]
    for d in order:
        if d==MSA: continue
        ch=(PR[d]!=PR[MSA]).values; rows.append([d]+[f"{ch[(q==qq).values].mean()*100:.0f}" for qq in ["Q1 low","Q2","Q3","Q4 high"]]+[f"{np.mean([margin[:,mi].mean()]):.2f}"])
    print("| dialect | Q1 low | Q2 | Q3 | Q4 high |"); print("|---|---|---|---|---|")
    for r in rows: print("| "+" | ".join(r[:5])+" |")
    if lex:
        print(f"\n{tag}: answer change vs per-item lexical distance to MSA (token Jaccard distance), by distance tercile; plus point-biserial corr")
        print("| dialect | mean lex dist | change% T1 (close) | T2 | T3 (far) | corr(change, lexdist) | corr(change, 1-margin) |"); print("|---|---|---|---|---|---|---|")
        for d in order:
            if d in (MSA,ENG): continue
            ld=np.array([lex[d][k] for k in PR.index]); ch=(PR[d]!=PR[MSA]).values.astype(float)
            t=pd.qcut(ld,3,labels=False,duplicates="drop")
            print(f"| {d} | {ld.mean():.2f} | "+" | ".join(f"{ch[t==i].mean()*100:.0f}" for i in range(3))+f" | {np.corrcoef(ch,ld)[0,1]:+.3f} | {np.corrcoef(ch,1-margin[:,mi])[0,1]:+.3f} |")
