#!/usr/bin/env python
"""Cross-resource replication (pre-registered, ANALYSIS_PLAN Addendum 4): AraDiCE (ArabicMMLU translated to Egyptian and Levantine by
QCRI) with the MBZUAI ArabicMMLU MSA originals. 2,000 parallel 4-option items (data/aradice_splits.json: 600 calibration / 1,400 test;
3 fixed MSA shots), varieties MSA/EGY/LEV, same prompt template and letter-logit scoring as the main study. Resumable.
Output: results/aradice_scores_<model>.csv  (columns as scores_*.csv; key = AraDiCE ID; domain = Group|Subject)
Env: ADA_DATA, ADA_RES, ADA_MODELS, ADA_BS, HF_HOME."""
import os, json, time, traceback, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
DATA=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]; BS=int(os.environ.get("ADA_BS","4"))
MODELS=os.environ.get("ADA_MODELS","ALLaM-AI/ALLaM-7B-Instruct-preview,Qwen/Qwen3-8B-Base,QCRI/Fanar-1-9B,google/gemma-2-9b").split(",")
dev="mps" if torch.backends.mps.is_available() else "cpu"
spl=json.load(open(os.path.join(DATA,"aradice_splits.json"))); items=json.load(open(os.path.join(DATA,"aradice_items.json")))
keys=spl["calibration"]+spl["test"]; shots=spl["shots_msa"]; V=["MSA","EGY","LEV"]; LET=["A","B","C","D"]
assert not set(keys)&set(shots)
def fmt_q(q,opts): return f"السؤال: {q}\n"+"\n".join(f"{LET[i]}. {c}" for i,c in enumerate(opts))+"\nالإجابة:"
HEAD="فيما يلي أسئلة اختيار من متعدد. اختر الإجابة الصحيحة بكتابة حرفها فقط.\n\n"
SHOTS=HEAD+"\n\n".join(fmt_q(items[s]["q"]["MSA"],items[s]["o"]["MSA"])+" "+LET[items[s]["ans"]] for s in shots)+"\n\n"
rows_all=[dict(key=k,dialect=v,domain=f"{items[k]['group']}|{items[k]['subject']}",answer=items[k]["ans"],prompt=SHOTS+fmt_q(items[k]["q"][v],items[k]["o"][v])) for k in keys for v in V]
print("rows",len(rows_all),"keys",len(keys),"device",dev,"BS",BS,flush=True); print("example:\n",rows_all[0]["prompt"][-600:],flush=True)
@torch.no_grad()
def run_model(mid):
    tag=mid.split("/")[1]; out=os.path.join(RES,f"aradice_scores_{tag}.csv"); done=set()
    if os.path.exists(out):
        prev=pd.read_csv(out,dtype={"key":str}); done=set(zip(prev.dialect,prev.key)); print(tag,"resuming, done:",len(done),flush=True)
    rows=[r for r in rows_all if (r["dialect"],r["key"]) not in done]
    if not rows: print(tag,"already complete"); return
    tok=AutoTokenizer.from_pretrained(mid); tok.padding_side="left"
    if tok.pad_token is None: tok.pad_token=tok.eos_token
    kw=dict(torch_dtype=torch.bfloat16)
    if "gemma" in mid.lower(): kw["attn_implementation"]="eager"
    t0=time.time(); model=AutoModelForCausalLM.from_pretrained(mid,**kw).to(dev).eval(); print(tag,"loaded in %.0fs"%(time.time()-t0),flush=True)
    ids={}
    for L in LET:
        v=[]
        for s in [" "+L,L]:
            e=tok.encode(s,add_special_tokens=False)
            if len(e)==1: v.append(e[0])
        if not v: v=[tok.encode(" "+L,add_special_tokens=False)[-1]]
        ids[L]=sorted(set(v))
    rows.sort(key=lambda r: len(r["prompt"])); hdr=not os.path.exists(out); f=open(out,"a")
    if hdr: f.write("model,dialect,domain,qid,key,answer,lA,lB,lC,lD,lA_sp,lB_sp,lC_sp,lD_sp,pred,correct,p_true,p_max,n_tok\n")
    t0=time.time()
    for i in range(0,len(rows),BS):
        b=rows[i:i+BS]; enc=tok([r["prompt"] for r in b],return_tensors="pt",padding=True,truncation=True,max_length=2048).to(dev)
        logits=model(**enc).logits[:,-1,:].float(); lp=(logits-torch.logsumexp(logits,dim=-1,keepdim=True)).cpu().numpy()
        for j,r in enumerate(b):
            comb=[float(np.logaddexp.reduce([lp[j,t] for t in ids[L]])) for L in LET]; sp=[float(lp[j,ids[L][0]]) for L in LET]
            z=np.array(comb); p=np.exp(z-np.logaddexp.reduce(z)); pred=int(np.argmax(p)); ans=int(r["answer"])
            f.write(",".join(map(str,[tag,r["dialect"],r["domain"].replace(",",";"),r["key"],r["key"],ans,*["%.4f"%x for x in comb],*["%.4f"%x for x in sp],pred,int(pred==ans),"%.5f"%p[ans],"%.5f"%p.max(),int(enc["attention_mask"][j].sum())]))+"\n")
        if (i//BS)%50==0:
            f.flush(); el=time.time()-t0; print(f"{tag} {i+len(b)}/{len(rows)} {el:.0f}s eta {el/(i+len(b))*(len(rows)-i-len(b)):.0f}s",flush=True)
    f.close(); print(tag,"DONE in %.0fs"%(time.time()-t0),flush=True); del model
    if dev=="mps": torch.mps.empty_cache()
for mid in MODELS:
    try: run_model(mid)
    except Exception as e: print("MODEL FAILED",mid,repr(e)); traceback.print_exc()
print("ALL DONE")
