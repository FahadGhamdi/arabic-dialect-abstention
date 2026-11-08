import sys, os, numpy as np, pandas as pd
od=sys.argv[1]; src=sys.argv[2]; MSA="MSA"; ENG="ENG"
H=np.load(os.path.join(src,"hidden.npy"), mmap_mode="r"); M=pd.read_csv(os.path.join(od,"meta.csv"))
LENS=np.load(os.path.join(od,"lens.npy")); P=np.exp(LENS-np.logaddexp.reduce(LENS,-1,keepdims=True)); ans=M.answer.values
fc=(P[:,-1,:].argmax(-1)==ans).astype(float); pmax=P[:,-1,:].max(-1)
n,L1,d=H.shape; keys=np.array(sorted(M.key.unique())); rng=np.random.default_rng(0); perm=rng.permutation(len(keys)); folds=np.array_split(perm,5)
dial=sorted(M.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x))
def rank(a):
    o=np.argsort(a,kind="mergesort"); r=np.empty(len(a)); r[o]=np.arange(1,len(a)+1); return r
def auroc(s,y):
    r=rank(s); n1=y.sum(); n0=len(y)-n1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def train_lr(X,y,l2=1.0,iters=300,lr=0.5):
    w=np.zeros(X.shape[1]); b=0.0
    for t in range(iters):
        z=X@w+b; p=1/(1+np.exp(-z)); g=X.T@(p-y)/len(y)+l2*w/len(y); gb=(p-y).mean(); w-=lr*g; b-=lr*gb
    return w,b
layers=[int(x) for x in sys.argv[3].split(",")]
print("baseline p_max AUROC:", {dn: round(auroc(pmax[(M.dialect==dn).values], fc[(M.dialect==dn).values]),3) for dn in dial})
print("| layer | "+" | ".join(dial)+" |")
for l in layers:
    X=np.asarray(H[:,l,:],dtype=np.float32)
    sc={dn:[] for dn in dial}; ys={dn:[] for dn in dial}
    for f in range(5):
        tek=set(keys[folds[f]]); te=M.key.isin(tek).values; tr_msa=((M.dialect==MSA).values)&(~te)
        mu=X[tr_msa].mean(0); sd=X[tr_msa].std(0)+1e-6; Xn=(X-mu)/sd
        w,b=train_lr(Xn[tr_msa],fc[tr_msa],l2=50.0)
        for dn in dial:
            m=((M.dialect==dn).values)&te; sc[dn]+=list(Xn[m]@w+b); ys[dn]+=list(fc[m])
    print(f"| L{l} | "+" | ".join(f"{auroc(np.array(sc[dn]),np.array(ys[dn])):.3f}" for dn in dial)+" |")
