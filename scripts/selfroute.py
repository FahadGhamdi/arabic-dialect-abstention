"""Self-routed conformal calibration pilot: route each test item to a variety-specific threshold using a probe on the
model's own hidden state (no dialect label at test time). Compare MSA-only, pooled, oracle-Mondrian, self-routed. alpha in {0.2,0.3}."""
import sys, os, math, numpy as np, pandas as pd
od=sys.argv[1]; src=sys.argv[2]; L=int(sys.argv[3]); MSA="MSA"; ENG="ENG"
H=np.load(os.path.join(src,"hidden.npy"), mmap_mode="r"); M=pd.read_csv(os.path.join(od,"meta.csv"))
LENS=np.load(os.path.join(od,"lens.npy")); P=np.exp(LENS[:,-1,:]-np.logaddexp.reduce(LENS[:,-1,:],-1,keepdims=True)); ans=M.answer.values
ptrue=P[np.arange(len(M)),ans]; S=1-ptrue; SO=1-P
dial=sorted(M.dialect.unique(), key=lambda x:(x!=MSA,x==ENG,x)); D={d:i for i,d in enumerate(dial)}; y=np.array([D[d] for d in M.dialect])
keys=np.array(sorted(M.key.unique())); rng=np.random.default_rng(0)
X=np.asarray(H[:,L,:],dtype=np.float32)
def softmax(z): z=z-z.max(1,keepdims=True); e=np.exp(z); return e/e.sum(1,keepdims=True)
def train_mlr(X,y,k,l2=20.0,iters=400,lr=0.5):
    W=np.zeros((X.shape[1],k)); b=np.zeros(k); Y=np.eye(k)[y]
    for t in range(iters):
        p=softmax(X@W+b); g=X.T@(p-Y)/len(y)+l2*W/len(y); W-=lr*g; b-=lr*(p-Y).mean(0)
    return W,b
def qhat(s,a): n=len(s); k=min(n,math.ceil((n+1)*(1-a))); return np.sort(s)[k-1]
res=[]
for rep in range(4):
    perm=rng.permutation(len(keys)); A=set(keys[perm[:len(keys)//2]]); inA=M.key.isin(A).values; inB=~inA
    mu=X[inA].mean(0); sd=X[inA].std(0)+1e-6; Xn=(X-mu)/sd
    W,b=train_mlr(Xn[inA],y[inA],len(dial)); yhat=softmax(Xn@W+b).argmax(1)
    acc_route=(yhat[inB]==y[inB]).mean()
    for a in [0.2,0.3]:
        q_msa=qhat(S[inA&(y==D[MSA])],a); q_pool=qhat(S[inA],a); q_d={i:qhat(S[inA&(y==i)],a) for i in range(len(dial))}
        for d in dial:
            i=D[d]; m=inB&(y==i)
            cov_msa=(S[m]<=q_msa).mean(); cov_pool=(S[m]<=q_pool).mean(); cov_or=(S[m]<=q_d[i]).mean()
            qr=np.array([q_d[j] for j in yhat[m]]); cov_sr=(S[m]<=qr).mean(); sz_sr=(SO[m]<=qr[:,None]).sum(1).mean(); sz_or=(SO[m]<=q_d[i]).sum(1).mean(); sz_msa=(SO[m]<=q_msa).sum(1).mean()
            res.append(dict(rep=rep,alpha=a,variety=d,route_acc=acc_route,cov_msa=cov_msa,cov_pool=cov_pool,cov_oracle=cov_or,cov_selfroute=cov_sr,sz_msa=sz_msa,sz_oracle=sz_or,sz_selfroute=sz_sr))
R=pd.DataFrame(res); g=R.groupby(["alpha","variety"]).mean(numeric_only=True).drop(columns="rep")
print(f"# self-routed conformal, ALLaM layer {L}; 7-way routing accuracy = {R.route_acc.mean():.3f}; 4 random splits")
print(g.round(3).to_string())
