#!/usr/bin/env python
"""Stage 5: item-level flip analysis + cross-model agreement + selective prediction under MSA-set thresholds."""
import os, glob, json, math, itertools
import numpy as np, pandas as pd
RES=os.environ["ADA_RES"]; OUT=os.environ["ADA_DATA"]
meta=json.load(open(os.path.join(OUT,"pilot_keys.json"))); MSA=meta["MSA"]; ENG=meta["ENG"]
mods={}
for fn in sorted(glob.glob(os.path.join(RES,"scores_*.csv"))):
    df=pd.read_csv(fn).drop_duplicates(["dialect","key"]); tag=os.path.basename(fn)[7:-4]
    keys=sorted(set.intersection(*[set(df[df.dialect==d].key) for d in df.dialect.unique()]))
    if len(keys)<100: continue
    df=df[df.key.isin(keys)]; mods[tag]=df
print("models:", {m:len(d)//7 for m,d in mods.items()})
dial=[d for d in next(iter(mods.values())).dialect.unique() if d not in (MSA,ENG)]
out=[]
for tag,df in mods.items():
    C=df.pivot(index="key",columns="dialect",values="correct"); P=df.pivot(index="key",columns="dialect",values="p_max")
    print(f"\n## {tag}: item-level flips relative to MSA (n={len(C)})")
    print("| dialect | MSA✓→D✗ | MSA✗→D✓ | net | both✓ | both✗ | McNemar p |")
    from math import comb
    for d in dial:
        a=int(((C[MSA]==1)&(C[d]==0)).sum()); b=int(((C[MSA]==0)&(C[d]==1)).sum())
        bb=int(((C[MSA]==1)&(C[d]==1)).sum()); ww=int(((C[MSA]==0)&(C[d]==0)).sum())
        n=a+b; p=sum(comb(n,k) for k in range(0,min(a,b)+1))/2**n*2 if n>0 else 1.0; p=min(1,p)
        print(f"| {d} | {a} | {b} | {b-a:+d} | {bb} | {ww} | {p:.3f} |")
        out.append(dict(model=tag,dialect=d,msa_ok_d_bad=a,msa_bad_d_ok=b,both_ok=bb,both_bad=ww,mcnemar_p=p))
    # selective prediction: threshold chosen on MSA for 50% coverage; apply to dialects
    print("Selective prediction (threshold set on MSA at 50% coverage):")
    thr=np.quantile(P[MSA],0.5)
    for d in [MSA]+dial:
        m=P[d]>=thr; print(f"- {d}: coverage={m.mean():.3f} selective_acc={C[d][m].mean():.3f} (full acc {C[d].mean():.3f})")
    # alpha=0.05 conformal quick check (single split, seeded)
    pt=df.pivot(index="key",columns="dialect",values="p_true"); rng=np.random.default_rng(1); idx=rng.permutation(len(pt)); cal,tst=idx[:len(idx)//2],idx[len(idx)//2:]
    for alpha in [0.05,0.10,0.20]:
        s=1-pt[MSA].values[cal]; n=len(s); k=min(n,math.ceil((n+1)*(1-alpha))); q=np.sort(s)[k-1]
        cov={d:float(((1-pt[d].values[tst])<=q).mean()) for d in [MSA]+dial}
        print(f"alpha={alpha}: cov", {k:round(v,3) for k,v in cov.items()})
# cross-model agreement of dialect-induced flips
if len(mods)>=2:
    print("\n## Cross-model agreement on MSA✓→D✗ flips (Jaccard / expected under independence)")
    for d in dial:
        sets={}
        for tag,df in mods.items():
            C=df.pivot(index="key",columns="dialect",values="correct"); sets[tag]=set(C.index[(C[MSA]==1)&(C[d]==0)]); N=len(C)
        for a,b in itertools.combinations(sets,2):
            inter=len(sets[a]&sets[b]); exp=len(sets[a])*len(sets[b])/N
            print(f"- {d}: {a} ∩ {b} = {inter} (expected {exp:.1f}, ratio {inter/max(exp,1e-9):.2f}); sizes {len(sets[a])},{len(sets[b])}")
pd.DataFrame(out).to_csv(os.path.join(RES,"flips.csv"),index=False)
