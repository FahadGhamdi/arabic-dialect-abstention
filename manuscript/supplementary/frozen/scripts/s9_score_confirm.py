#!/usr/bin/env python
"""Confirmatory scoring (pre-registered): the 2,632 held-out keys (data/confirm_keys.json) x 7 varieties,
IDENTICAL protocol to the pilot (scripts/s3_score.py): same 3 MSA shots (data/pilot_keys.json['shots']),
same prompt template, same option-letter logit scoring, bf16 on MPS. Resumable.
Output: results/confirm_scores_<model>.csv  (same columns as scores_<model>.csv)
Env: ADA_DATA, ADA_RES, ADA_MODELS (comma list of HF ids), ADA_BS (batch size), HF_HOME."""
import os, sys, json, time, traceback
import numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]; BS=int(os.environ.get("ADA_BS","4"))
MODELS=os.environ.get("ADA_MODELS","ALLaM-AI/ALLaM-7B-Instruct-preview,Qwen/Qwen3-8B-Base,QCRI/Fanar-1-9B,google/gemma-2-9b").split(",")
dev="mps" if torch.backends.mps.is_available() else "cpu"
print("device",dev,"BS",BS,"models",MODELS, flush=True)

meta=json.load(open(os.path.join(OUT,"pilot_keys.json"))); MSA,ENG=meta["MSA"],meta["ENG"]
keys=json.load(open(os.path.join(OUT,"confirm_keys.json")))["confirm_keys"]
assert not (set(keys)&set(meta["pilot"])) and not (set(keys)&set(meta["shots"])), "confirm keys overlap pilot/shots"
df=pd.read_parquet(os.path.join(OUT,"damm.parquet")); df["choices"]=df["choices"].apply(list)
LET=["A","B","C","D"]
def fmt_q(row, lang="ar"):
    ch="\n".join(f"{LET[i]}. {c}" for i,c in enumerate(row["choices"]))
    if lang=="en": return f"Question: {row['question']}\n{ch}\nAnswer:"
    return f"السؤال: {row['question']}\n{ch}\nالإجابة:"
msa_rows={r.key:r for r in df[df.dialect==MSA].itertuples()}
eng_rows={r.key:r for r in df[df.dialect==ENG].itertuples()} if ENG else {}
def shots_text(lang):
    src=eng_rows if (lang=="en" and eng_rows) else msa_rows
    return "\n\n".join(fmt_q(src[k]._asdict(), lang)+" "+LET[src[k].answer] for k in meta["shots"])
HEAD_AR="فيما يلي أسئلة اختيار من متعدد. اختر الإجابة الصحيحة بكتابة حرفها فقط.\n\n"
HEAD_EN="The following are multiple choice questions. Answer with the letter of the correct option only.\n\n"
SHOTS={"ar":HEAD_AR+shots_text("ar")+"\n\n","en":HEAD_EN+shots_text("en")+"\n\n"}
sub=df[df.key.isin(set(keys))].copy()
sub["lang"]=np.where(sub.dialect==ENG,"en","ar")
sub["prompt"]=[SHOTS[l]+fmt_q(r,l) for l,r in zip(sub["lang"], sub.to_dict("records"))]
print("confirm rows:",len(sub),"keys:",sub.key.nunique(),"per dialect:",sub.dialect.value_counts().to_dict(), flush=True)

@torch.no_grad()
def run_model(mid):
    tag=mid.split("/")[1]; out=os.path.join(RES,f"confirm_scores_{tag}.csv")
    done=set()
    if os.path.exists(out):
        prev=pd.read_csv(out); done=set(zip(prev.dialect,prev.key)); print(tag,"resuming, done:",len(done), flush=True)
    rows=[r for r in sub.to_dict("records") if (r["dialect"],r["key"]) not in done]
    if not rows: print(tag,"already complete"); return
    tok=AutoTokenizer.from_pretrained(mid); tok.padding_side="left"
    if tok.pad_token is None: tok.pad_token=tok.eos_token
    kw=dict(torch_dtype=torch.bfloat16)
    if "gemma" in mid.lower(): kw["attn_implementation"]="eager"
    t0=time.time(); model=AutoModelForCausalLM.from_pretrained(mid, **kw).to(dev).eval(); print(tag,"loaded in %.0fs"%(time.time()-t0), flush=True)
    ids={}
    for L in LET:
        v=[]
        for s in [" "+L, L]:
            e=tok.encode(s, add_special_tokens=False)
            if len(e)==1: v.append(e[0])
        if not v: e=tok.encode(" "+L, add_special_tokens=False); v=[e[-1]]
        ids[L]=sorted(set(v))
    print(tag,"letter ids",ids, flush=True)
    rows.sort(key=lambda r: len(r["prompt"]))
    hdr=not os.path.exists(out); f=open(out,"a")
    if hdr: f.write("model,dialect,domain,qid,key,answer,lA,lB,lC,lD,lA_sp,lB_sp,lC_sp,lD_sp,pred,correct,p_true,p_max,n_tok\n")
    t0=time.time()
    for i in range(0,len(rows),BS):
        b=rows[i:i+BS]
        enc=tok([r["prompt"] for r in b], return_tensors="pt", padding=True, truncation=True, max_length=2048).to(dev)
        logits=model(**enc).logits[:,-1,:].float()
        lp=(logits-torch.logsumexp(logits,dim=-1,keepdim=True)).cpu().numpy()
        for j,r in enumerate(b):
            comb=[float(np.logaddexp.reduce([lp[j,t] for t in ids[L]])) for L in LET]
            sp=[float(lp[j,ids[L][0]]) for L in LET]
            z=np.array(comb); p=np.exp(z-np.logaddexp.reduce(z)); pred=int(np.argmax(p)); ans=int(r["answer"])
            f.write(",".join(map(str,[tag, r["dialect"], r["domain"], r["qid"], r["key"], ans, *["%.4f"%x for x in comb], *["%.4f"%x for x in sp],
                                      pred, int(pred==ans), "%.5f"%p[ans], "%.5f"%p.max(), int(enc["attention_mask"][j].sum())]))+"\n")
        if (i//BS)%50==0:
            f.flush(); el=time.time()-t0; print(f"{tag} {i+len(b)}/{len(rows)} {el:.0f}s eta {el/(i+len(b))*(len(rows)-i-len(b)):.0f}s", flush=True)
    f.close(); print(tag,"DONE in %.0fs"%(time.time()-t0), flush=True)
    del model
    if dev=="mps": torch.mps.empty_cache()

for mid in MODELS:
    try: run_model(mid)
    except Exception as e:
        print("MODEL FAILED",mid,repr(e)); traceback.print_exc()
print("ALL DONE")
