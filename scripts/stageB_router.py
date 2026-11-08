#!/usr/bin/env python
"""Stage B — variety-aware conformal calibration with routers, done right.
Grouped 3-way split by question key (all 7 variants of a key in the same split): R (router train) / Cal / Test.
Thresholds are computed on Cal per PREDICTED group (router applied to Cal), then applied on Test by predicted group.
Methods (same Cal budget): msa_only | pooled | oracle (true labels on Cal and Test) | text_router (char n-gram LR, trained on R)
| internal_router (LR on last-token hidden state, trained on R) | plausible_set (internal probe top-mass set, conservative max threshold).
Scores = ORIGINAL scores (results/scores_<model>.csv), never lens. Hidden states from results/internals_<model>/hidden.npy (layer L).
Outputs: results/stageB/B_<model>.csv (per split x method x alpha x true variety), B_router_<model>.csv (router acc, confusion)."""
import os, sys, math, json, zlib, numpy as np, pandas as pd
RES=os.environ.get("ADA_RES","results"); OUT=os.path.join(RES,"stageB"); os.makedirs(OUT,exist_ok=True)
DATA=os.environ.get("ADA_DATA","data"); tag=sys.argv[1]; L=int(sys.argv[2]); s0,s1=[int(x) for x in sys.argv[3].split(":")]
MSA="MSA"; ENG="ENG"; ALPHAS=[0.2,0.3]; NR,NC=150,175  # keys for router-train and calibration; the rest (175) test
def qhat(s,a): n=len(s); k=min(n,math.ceil((n+1)*(1-a))); return np.sort(s)[k-1] if n>0 else 1.0
# ---- data
sc=pd.read_csv(os.path.join(RES,f"scores_{tag}.csv")).drop_duplicates(["dialect","key"])
meta=pd.read_csv(os.path.join(RES,f"internals_{tag}","meta.csv")); H=np.load(os.path.join(RES,f"internals_{tag}","hidden.npy"),mmap_mode="r")
Xh=np.asarray(H[:,L,:],dtype=np.float32)
m=meta.merge(sc,on=["dialect","key"],suffixes=("","_s")); assert len(m)==len(meta)
D=sorted(m.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); y=np.array([D.index(d) for d in m.dialect]); K=len(D)
Lg=m[["lA","lB","lC","lD"]].values; P=np.exp(Lg-np.logaddexp.reduce(Lg,-1,keepdims=True)); ans=m.answer.values.astype(int)
S=1-P[np.arange(len(m)),ans]; SO=1-P
# text for text-router: question+choices from damm.csv
dm=pd.read_csv(os.path.join(DATA,"damm.csv")); dm["key"]=dm["domain"]+"|"+dm["qid"].astype(str); dm["text"]=dm["question"].astype(str)+" "+dm["choices"].astype(str).str.replace("|||"," ")
tmap={(r.dialect,r.key):r.text for r in dm.itertuples()}; texts=[tmap[(d,k)] for d,k in zip(m.dialect,m.key)]
DIM=8192
def featurize(t):
    v=np.zeros(DIM,dtype=np.float32); t=" "+t+" "
    for n in (2,3):
        for i in range(len(t)-n+1): v[zlib.crc32(t[i:i+n].encode())%DIM]+=1
    nrm=np.linalg.norm(v); return v/nrm if nrm>0 else v
Xt=np.stack([featurize(t) for t in texts])
def softmax(z): z=z-z.max(1,keepdims=True); e=np.exp(z); return e/e.sum(1,keepdims=True)
def train_mlr(X,yy,k,l2=10.0,iters=250,lr=0.5):
    W=np.zeros((X.shape[1],k),dtype=np.float32); b=np.zeros(k,dtype=np.float32); Y=np.eye(k,dtype=np.float32)[yy]
    for t in range(iters):
        p=softmax(X@W+b); W-=lr*(X.T@(p-Y)/len(yy)+l2*W/len(yy)); b-=lr*(p-Y).mean(0)
    return W,b
keys=np.array(sorted(m.key.unique())); rows=[]; rrows=[]
for sp in range(s0,s1):
    rng=np.random.default_rng(1000+sp); perm=rng.permutation(len(keys)); R=set(keys[perm[:NR]]); Cc=set(keys[perm[NR:NR+NC]]); T=set(keys[perm[NR+NC:]])
    inR=m.key.isin(R).values; inC=m.key.isin(Cc).values; inT=m.key.isin(T).values
    # routers trained on R only
    mu=Xh[inR].mean(0); sd=Xh[inR].std(0)+1e-6; Xhn=(Xh-mu)/sd
    Wi,bi=train_mlr(Xhn[inR],y[inR],K,l2=50.0); Pi=softmax(Xhn@Wi+bi); yi=Pi.argmax(1)
    Wt,bt=train_mlr(Xt[inR],y[inR],K,l2=1.0,iters=300,lr=1.0); Pt=softmax(Xt@Wt+bt); yt=Pt.argmax(1)
    for name,yh in [("internal",yi),("text",yt)]:
        acc=(yh[inT]==y[inT]).mean(); conf=np.zeros((K,K),dtype=int)
        for a_,b_ in zip(y[inT],yh[inT]): conf[a_,b_]+=1
        rrows.append(dict(split=sp,router=name,acc=acc,confusion=json.dumps(conf.tolist()),varieties=json.dumps(D)))
    for a in ALPHAS:
        # thresholds
        q_msa=qhat(S[inC&(y==D.index(MSA))],a); q_pool=qhat(S[inC],a)
        q_true={g:qhat(S[inC&(y==g)],a) for g in range(K)}
        q_int={g:qhat(S[inC&(yi==g)],a) for g in range(K)}   # per PREDICTED group on Cal
        q_txt={g:qhat(S[inC&(yt==g)],a) for g in range(K)}
        # plausible set: smallest set of varieties with internal-probe mass >= 0.9, conservative threshold = max over set
        def plaus_q(i):
            o=np.argsort(-Pi[i]); cum=np.cumsum(Pi[i][o]); kk=int(np.searchsorted(cum,0.9))+1; return max(q_int[g] for g in o[:kk])
        for g in range(K):
            mt=inT&(y==g); idx=np.where(mt)[0]
            def rep(method,qv):
                cov=(S[idx]<=qv).mean(); sz=(SO[idx]<=np.asarray(qv).reshape(-1,1)).sum(1).mean() if np.ndim(qv) else (SO[idx]<=qv).sum(1).mean()
                rows.append(dict(split=sp,alpha=a,method=method,variety=D[g],coverage=cov,set_size=sz,n=len(idx)))
            rep("msa_only",q_msa); rep("pooled",q_pool); rep("oracle",q_true[g])
            rep("internal_router",np.array([q_int[j] for j in yi[idx]])); rep("text_router",np.array([q_txt[j] for j in yt[idx]]))
            rep("plausible_set",np.array([plaus_q(i) for i in idx]))
    print("split",sp,"done", flush=True)
pd.DataFrame(rows).to_csv(os.path.join(OUT,f"B_{tag}_L{L}_{s0}-{s1}.csv"),index=False); pd.DataFrame(rrows).to_csv(os.path.join(OUT,f"Brouter_{tag}_L{L}_{s0}-{s1}.csv"),index=False)
print("saved")
