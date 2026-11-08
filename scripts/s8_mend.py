#!/usr/bin/env python
"""Stage 8: training-free mending. Difference vector v_l = mean(h_l^MSA - h_l^D) at the answer position, computed on fold-A keys
from internals; added at layer l output (last position, or all positions) during the dialect forward pass on fold-B keys.
Controls: random vector (same norm), reverse direction (-v). Metrics: accuracy, agreement with MSA prediction, flip recovery."""
import os, sys, json, time, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
sys.path.insert(0, os.path.dirname(__file__)); from prompts import load_pilot, letter_ids, LET
OUT=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]; BS=int(os.environ.get("ADA_BS","8"))
MID=os.environ.get("ADA_MEND_MODEL","ALLaM-AI/ALLaM-7B-Instruct-preview"); tag=MID.split("/")[1]
DIALS=os.environ.get("ADA_MEND_DIALS","MAG,SYR,KSA").split(","); SCALES=[float(x) for x in os.environ.get("ADA_MEND_SCALES","1.0").split(",")]
POS=os.environ.get("ADA_MEND_POS","last")  # last | all
dev="mps" if torch.backends.mps.is_available() else "cpu"
sub,meta=load_pilot(OUT); MSA=meta["MSA"]
od=os.path.join(RES,f"internals_{tag}"); H=np.load(os.path.join(od,"hidden.npy")); M=pd.read_csv(os.path.join(od,"meta.csv"))
n,L1,d=H.shape; rng=np.random.default_rng(0); keys=sorted(M.key.unique()); perm=rng.permutation(len(keys)); A=set(np.array(keys)[perm[:len(keys)//2]]); B=set(np.array(keys)[perm[len(keys)//2:]])
LAYERS=[int(x) for x in os.environ.get("ADA_MEND_LAYERS", ",".join(str(x) for x in sorted(set([L1//4, L1//3, L1//2, (2*L1)//3, (3*L1)//4])))).split(",")]
print("model",tag,"layers",LAYERS,"dials",DIALS,"scales",SCALES,"pos",POS,"foldA",len(A),"foldB",len(B), flush=True)
# vectors on fold A (paired by key)
def mean_state(dn, l, ks):
    m=(M.dialect==dn)&(M.key.isin(ks)); sel=M[m].sort_values("key"); return H[sel.index.values, l, :].astype(np.float32), sel.key.values
vecs={}
for dn in DIALS:
    for l in LAYERS:
        hm,km=mean_state(MSA,l,A); hd,kd=mean_state(dn,l,A); assert (km==kd).all()
        v=(hm-hd).mean(0); vecs[(dn,l)]=v
        print(f"v[{dn},L{l}] norm={np.linalg.norm(v):.2f}  mean ||h||={np.linalg.norm(hd,axis=1).mean():.2f}", flush=True)
tok=AutoTokenizer.from_pretrained(MID); tok.padding_side="left"
if tok.pad_token is None: tok.pad_token=tok.eos_token
kw=dict(dtype=torch.bfloat16)
if "gemma" in MID.lower(): kw["attn_implementation"]="eager"
model=AutoModelForCausalLM.from_pretrained(MID, **kw).to(dev).eval(); ids=letter_ids(tok)
layers=model.model.layers if hasattr(model,"model") else model.get_decoder().layers
# hook state
STATE={"v":None,"l":None}
def make_hook(li):
    def hook(mod, inp, out):
        if STATE["v"] is None or STATE["l"]!=li: return out
        hs=out[0] if isinstance(out,tuple) else out
        v=STATE["v"].to(hs.dtype)
        if POS=="last": hs[:,-1,:]+=v
        else: hs+=v
        return (hs,)+tuple(out[1:]) if isinstance(out,tuple) else hs
    return hook
hooks=[layers[i].register_forward_hook(make_hook(i)) for i in range(len(layers))]
# NOTE: hidden_states index l corresponds to output of layer l-1 (index 0 = embeddings). Adding v_l at layer (l-1) output.
rows=sub[sub.key.isin(B)].to_dict("records")
@torch.no_grad()
def score(rs):
    rs=sorted(rs,key=lambda r: len(r["prompt"])); preds={}; pts={}
    for i in range(0,len(rs),BS):
        b=rs[i:i+BS]; enc=tok([r["prompt"] for r in b],return_tensors="pt",padding=True,truncation=True,max_length=2048).to(dev)
        lp=torch.log_softmax(model(**enc).logits[:,-1,:].float(),-1).cpu().numpy()
        for j,r in enumerate(b):
            z=np.array([np.logaddexp.reduce([lp[j,t] for t in ids[L]]) for L in LET]); p=np.exp(z-np.logaddexp.reduce(z))
            preds[r["key"]]=int(p.argmax()); pts[r["key"]]=float(p[r["answer"]])
    return preds,pts
ans={r["key"]:r["answer"] for r in rows}
STATE["v"]=None; msa_pred,_=score([r for r in rows if r["dialect"]==MSA]); print("MSA acc foldB: %.3f"%np.mean([msa_pred[k]==ans[k] for k in msa_pred]), flush=True)
out=[]
for dn in DIALS:
    drows=[r for r in rows if r["dialect"]==dn]; STATE["v"]=None; base_pred,base_pt=score(drows)
    acc0=np.mean([base_pred[k]==ans[k] for k in base_pred]); agr0=np.mean([base_pred[k]==msa_pred[k] for k in base_pred])
    flips=[k for k in base_pred if msa_pred[k]==ans[k] and base_pred[k]!=ans[k]]
    print(f"\n{dn}: baseline acc={acc0:.3f} agree-with-MSA={agr0:.3f} flips(MSA✓D✗)={len(flips)}", flush=True)
    out.append(dict(model=tag,dialect=dn,cond="baseline",layer=-1,scale=0,acc=acc0,agree_msa=agr0,flip_recovered=0,n=len(base_pred),mean_ptrue=np.mean(list(base_pt.values()))))
    for l in LAYERS:
        v=torch.tensor(vecs[(dn,l)]).to(dev); rv=torch.randn_like(v); rv=rv/rv.norm()*v.norm()
        for cond,vv in [c for c in [("mend",v),("reverse",-v),("random",rv)] if c[0] in os.environ.get("ADA_MEND_CONDS","mend,random").split(",")]:
            for s in SCALES:
                STATE["v"]=vv*s; STATE["l"]=l-1  # hidden_states[l] == output of layers[l-1]
                pr,pt=score(drows); acc=np.mean([pr[k]==ans[k] for k in pr]); agr=np.mean([pr[k]==msa_pred[k] for k in pr]); rec=np.mean([pr[k]==ans[k] for k in flips]) if flips else float('nan')
                print(f"  L{l} {cond:7s} s={s}: acc={acc:.3f} (Δ{acc-acc0:+.3f}) agree-MSA={agr:.3f} flip-recovered={rec:.2f} mean p_true={np.mean(list(pt.values())):.3f}", flush=True)
                out.append(dict(model=tag,dialect=dn,cond=cond,layer=l,scale=s,acc=acc,agree_msa=agr,flip_recovered=rec,n=len(pr),mean_ptrue=np.mean(list(pt.values()))))
        pd.DataFrame(out).to_csv(os.path.join(RES,f"mend_{tag}_{POS}.csv"),index=False)
STATE["v"]=None
print("DONE")
