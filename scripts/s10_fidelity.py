#!/usr/bin/env python
"""Automatic translation-fidelity covariate for every (key, variety) pair of DialectalArabicMMLU.
Cosine similarity between the MSA text and each variety's text under a multilingual embedding model
(intfloat/multilingual-e5-large, mean pooling, L2-normalised), computed separately for question, options and question+options.
Also a cross-variety baseline: similarity between MSA and ENG (translation across languages) for scale.
Output: results/fidelity.csv with columns key,dialect,sim_q,sim_opts,sim_all,len_ratio_q
Env: ADA_DATA, ADA_RES, HF_HOME. Runs on MPS if available."""
import os, json, time, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModel
DATA=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]; MID=os.environ.get("ADA_EMB","intfloat/multilingual-e5-large")
dev="mps" if torch.backends.mps.is_available() else "cpu"
df=pd.read_parquet(os.path.join(DATA,"damm.parquet")); df["choices"]=df["choices"].apply(list); df["key"]=df["domain"]+"|"+df["qid"].astype(str)
tok=AutoTokenizer.from_pretrained(MID); model=AutoModel.from_pretrained(MID).to(dev).eval(); print("loaded",MID,dev,flush=True)
@torch.no_grad()
def embed(texts,bs=32):
    out=[]
    for i in range(0,len(texts),bs):
        enc=tok(["query: "+t for t in texts[i:i+bs]],padding=True,truncation=True,max_length=512,return_tensors="pt").to(dev)
        h=model(**enc).last_hidden_state; m=enc["attention_mask"].unsqueeze(-1).float(); e=(h*m).sum(1)/m.sum(1)
        out.append(torch.nn.functional.normalize(e,dim=-1).float().cpu().numpy())
        if (i//bs)%50==0: print(f"{i}/{len(texts)}",flush=True)
    return np.concatenate(out)
df["q_text"]=df["question"].astype(str); df["o_text"]=df["choices"].apply(lambda c: " | ".join(map(str,c))); df["a_text"]=df["q_text"]+" "+df["o_text"]
t0=time.time(); Eq=embed(df.q_text.tolist()); Eo=embed(df.o_text.tolist()); Ea=embed(df.a_text.tolist()); print("embedded in %.0fs"%(time.time()-t0),flush=True)
idx={(k,d):i for i,(k,d) in enumerate(zip(df.key,df.dialect))}
rows=[]
for (k,d),i in idx.items():
    j=idx.get((k,"MSA"))
    if j is None: continue
    rows.append(dict(key=k,dialect=d,sim_q=float(Eq[i]@Eq[j]),sim_opts=float(Eo[i]@Eo[j]),sim_all=float(Ea[i]@Ea[j]),len_ratio_q=len(df.q_text.iloc[i])/max(1,len(df.q_text.iloc[j]))))
pd.DataFrame(rows).to_csv(os.path.join(RES,"fidelity.csv"),index=False); print("saved",len(rows),"rows; model",MID)
