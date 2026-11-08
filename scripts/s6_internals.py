#!/usr/bin/env python
"""Stage 6: last-token hidden states at every layer + logit-lens letter log-probs per layer, same pilot prompts.
Saves results/internals_<model>/{hidden.npy (fp16: n x L+1 x d), lens.npy (n x L+1 x 4), meta.csv}"""
import os, sys, time, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
sys.path.insert(0, os.path.dirname(__file__)); from prompts import load_pilot, letter_ids, LET
OUT=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]; BS=int(os.environ.get("ADA_BS","8")); DO_LENS=os.environ.get("ADA_LENS","1")=="1"
MODELS=os.environ.get("ADA_MODELS","ALLaM-AI/ALLaM-7B-Instruct-preview").split(",")
dev="mps" if torch.backends.mps.is_available() else "cpu"
sub,meta=load_pilot(OUT); rows=sub.to_dict("records"); rows.sort(key=lambda r: len(r["prompt"]))
print("rows",len(rows),"device",dev, flush=True)
@torch.no_grad()
def run(mid):
    tag=mid.split("/")[1]; od=os.path.join(RES,f"internals_{tag}"); os.makedirs(od,exist_ok=True)
    if os.path.exists(os.path.join(od,"hidden.npy")): print(tag,"exists, skip"); return
    tok=AutoTokenizer.from_pretrained(mid); tok.padding_side="left"
    if tok.pad_token is None: tok.pad_token=tok.eos_token
    kw=dict(dtype=torch.bfloat16)
    if "gemma" in mid.lower(): kw["attn_implementation"]="eager"
    model=AutoModelForCausalLM.from_pretrained(mid, **kw).to(dev).eval()
    ids=letter_ids(tok); print(tag,"letter ids",ids, flush=True)
    # final norm + head
    base=model.model if hasattr(model,"model") else model.get_decoder()
    norm=base.norm if hasattr(base,"norm") else base.final_layernorm
    head=model.get_output_embeddings()
    # unembedding rows for letter tokens (all variants)
    W=head.weight  # V x d
    H=None; LENS=None; n=len(rows); t0=time.time()
    for i in range(0,n,BS):
        b=rows[i:i+BS]
        enc=tok([r["prompt"] for r in b], return_tensors="pt", padding=True, truncation=True, max_length=2048).to(dev)
        out=model(**enc, output_hidden_states=True)
        hs=torch.stack([h[:,-1,:] for h in out.hidden_states],1)  # B x (L+1) x d
        if H is None:
            L1,d=hs.shape[1],hs.shape[2]; H=np.zeros((n,L1,d),dtype=np.float16); LENS=np.zeros((n,L1,4),dtype=np.float32); print(tag,"layers+1",L1,"d",d, flush=True)
        if DO_LENS:
            hn=torch.cat([norm(hs[:,:-1,:].float().to(W.dtype)), hs[:,-1:,:].to(W.dtype)],1)  # last hidden state is already normed by the model
            lp=torch.log_softmax((hn@W.T).float(),-1)
            for li,Lt in enumerate(LET):
                LENS[i:i+len(b),:,li]=torch.logsumexp(lp[:,:,ids[Lt]],-1).cpu().numpy()
        H[i:i+len(b)]=hs.float().cpu().numpy().astype(np.float16)
        if (i//BS)%25==0: print(f"{tag} {i+len(b)}/{n} {time.time()-t0:.0f}s", flush=True)
        if (i//BS)%250==0 and i>0: np.save(os.path.join(od,"hidden_partial.npy"),H[:i+len(b)]); torch.mps.empty_cache() if dev=='mps' else None
    np.save(os.path.join(od,"hidden.npy"),H); np.save(os.path.join(od,"lens.npy"),LENS)
    pd.DataFrame([{k:r[k] for k in ["dialect","domain","qid","key","answer"]} for r in rows]).to_csv(os.path.join(od,"meta.csv"),index=False)
    print(tag,"saved", flush=True); del model; torch.mps.empty_cache() if dev=="mps" else None
for m in MODELS:
    try: run(m)
    except Exception as e:
        import traceback; print("FAILED",m,repr(e)); traceback.print_exc()
print("ALL DONE")
