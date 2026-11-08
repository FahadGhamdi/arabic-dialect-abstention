import sys, os, json, numpy as np, pandas as pd
od=sys.argv[1]; MSA="MSA"; ENG="ENG"
LENS=np.load(os.path.join(od,"lens.npy")); M=pd.read_csv(os.path.join(od,"meta.csv"))
n,L1,_=LENS.shape
P=np.exp(LENS-np.logaddexp.reduce(LENS,axis=-1,keepdims=True)); ans=M.answer.values
pc=P[np.arange(n),:,ans]; pred=P.argmax(-1); corr=(pred==ans[:,None]); M["fc"]=corr[:,-1]
dial=sorted(M.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x))
layers=sorted(set(list(range(0,L1,4))+[L1-1]))
print(f"# {os.path.basename(od)} n={n} L1={L1}")
print("## lens accuracy by layer"); print("| variety | "+" | ".join(f"L{l}" for l in layers)+" |")
for d in dial:
    m=(M.dialect==d).values; print(f"| {d} | "+" | ".join(f"{corr[m,l].mean():.2f}" for l in layers)+" |")
print("\n## mean p_correct by layer (last 10 layers)")
for d in dial:
    m=(M.dialect==d).values; print(f"| {d} | "+" | ".join(f"{pc[m,l].mean():.3f}" for l in range(L1-10,L1))+" |")
lo=int(L1*2/3)
print(f"\n## final-wrong items: transiently correct at some layer in [{lo},{L1-2}]")
for d in dial:
    m=((M.dialect==d)&(~M.fc)).values
    print(f"- {d}: n_wrong={m.sum()} transient%={corr[m,lo:-1].any(1).mean()*100:.1f} max_pc={pc[m,lo:-1].max(1).mean():.3f} final_pc={pc[m,-1].mean():.3f}")
piv=M.pivot(index="key",columns="dialect",values="fc"); idx={(r.dialect,r.key):i for i,r in enumerate(M.itertuples())}
print("\n## paired: MSA✓→D✗ flips vs both-wrong — transient correctness in the D run; p_correct trajectory of flip items (D run vs MSA run)")
for d in dial:
    if d==MSA: continue
    fl=[k for k in piv.index if piv.loc[k,MSA]==1 and piv.loc[k,d]==0]; bw=[k for k in piv.index if piv.loc[k,MSA]==0 and piv.loc[k,d]==0]
    f=lambda ks: np.mean([corr[idx[(d,k)],lo:-1].any() for k in ks])*100 if ks else float('nan')
    trajD=np.mean([pc[idx[(d,k)],:] for k in fl],0); trajM=np.mean([pc[idx[(MSA,k)],:] for k in fl],0)
    sel=[L1//2, (3*L1)//4, L1-4, L1-2, L1-1]
    print(f"- {d}: flips={len(fl)} transient%={f(fl):.1f} | both-wrong={len(bw)} transient%={f(bw):.1f} | p_c D-run {[round(float(trajD[l]),3) for l in sel]} vs MSA-run {[round(float(trajM[l]),3) for l in sel]} @L{sel}")
# where does the dialect gap in p_correct open up? per-layer mean(pc_MSA - pc_D) over all items
print("\n## layer at which the MSA−dialect gap in p_correct opens (mean paired difference by layer, last 16 layers)")
pm=M.pivot(index="key",columns="dialect",values=None) if False else None
for d in dial:
    if d==MSA: continue
    ks=piv.index; dif=np.array([pc[idx[(MSA,k)],:]-pc[idx[(d,k)],:] for k in ks]).mean(0)
    print(f"- {d}: "+" ".join(f"L{l}:{dif[l]:+.3f}" for l in range(L1-16,L1)))
