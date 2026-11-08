#!/usr/bin/env python
"""Stage 3: option-letter logit scoring on DialectalArabicMMLU pilot subset, several models, MPS.
Output: results/scores_<model>.csv (incremental), data/pilot_keys.json, data/damm.parquet"""
import os, sys, json, time, math, random, traceback
import numpy as np, pandas as pd, torch
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]
N_Q=int(os.environ.get("ADA_NQ","500")); SEED=0; BS=int(os.environ.get("ADA_BS","8"))
MODELS=os.environ.get("ADA_MODELS","ALLaM-AI/ALLaM-7B-Instruct-preview,QCRI/Fanar-1-9B,Qwen/Qwen3-8B-Base,google/gemma-2-9b").split(",")
dev="mps" if torch.backends.mps.is_available() else "cpu"
print("device",dev,"N_Q",N_Q,"BS",BS,"models",MODELS, flush=True)

# ---------- data ----------
pq=hf_hub_download("MBZUAI/Dialectal-Arabic-MMLU","data/test-00000-of-00001.parquet",repo_type="dataset")
df=pd.read_parquet(pq); df["choices"]=df["choices"].apply(lambda x: list(x))
df["key"]=df["domain"]+"|"+df["qid"].astype(str)
print("dialects:", df["dialect"].value_counts().to_dict(), flush=True)
print("n domains", df["domain"].nunique(), "n keys", df["key"].nunique())
dialects=sorted(df["dialect"].unique())
def find(lbls, needles):
    for l in lbls:
        if any(n in l.lower() for n in needles): return l
    return None
MSA=find(dialects,["msa","standard"]); ENG=find(dialects,["eng"])
print("MSA label:",MSA,"ENG label:",ENG)
assert MSA is not None
# keys present in all dialects with 4 choices everywhere
ok=df.groupby("key").agg(n=("dialect","nunique"), c=("choices", lambda s: all(len(x)==4 for x in s)))
full=sorted(ok[(ok.n==len(dialects))&(ok.c)].index.tolist()); print("complete keys:",len(full))
rng=random.Random(SEED)
# stratified by domain: proportional sample of N_Q
bydom={}
for k in full: bydom.setdefault(k.split("|")[0],[]).append(k)
pilot=[]
for d,ks in sorted(bydom.items()):
    ks=sorted(ks); rng.shuffle(ks); m=max(1, round(N_Q*len(ks)/len(full))); pilot+=ks[:m]
rng.shuffle(pilot); pilot=pilot[:N_Q]
pilot_set=set(pilot)
# 3 fixed MSA demonstrations from the complement
comp=[k for k in full if k not in pilot_set]; rng.shuffle(comp); shots_keys=comp[:3]
json.dump({"pilot":pilot,"shots":shots_keys,"dialects":dialects,"MSA":MSA,"ENG":ENG}, open(os.path.join(OUT,"pilot_keys.json"),"w"), ensure_ascii=False, indent=1)
df.to_parquet(os.path.join(OUT,"damm.parquet"), index=False)
LET=["A","B","C","D"]
def fmt_q(row, lang="ar"):
    ch="\n".join(f"{LET[i]}. {c}" for i,c in enumerate(row["choices"]))
    if lang=="en": return f"Question: {row['question']}\n{ch}\nAnswer:"
    return f"السؤال: {row['question']}\n{ch}\nالإجابة:"
msa_rows={r.key:r for r in df[df.dialect==MSA].itertuples()}
eng_rows={r.key:r for r in df[df.dialect==ENG].itertuples()} if ENG else {}
def shots_text(lang):
    src=eng_rows if (lang=="en" and eng_rows) else msa_rows
    parts=[]
    for k in shots_keys:
        r=src[k]; parts.append(fmt_q(r._asdict(), lang)+" "+LET[r.answer])
    return "\n\n".join(parts)
HEAD_AR="فيما يلي أسئلة اختيار من متعدد. اختر الإجابة الصحيحة بكتابة حرفها فقط.\n\n"
HEAD_EN="The following are multiple choice questions. Answer with the letter of the correct option only.\n\n"
SHOTS={"ar":HEAD_AR+shots_text("ar")+"\n\n","en":HEAD_EN+shots_text("en")+"\n\n"}
sub=df[df.key.isin(pilot_set)].copy()
sub["lang"]=np.where(sub.dialect==ENG,"en","ar")
sub["prompt"]=[SHOTS[l]+fmt_q(r, l) for l,r in zip(sub["lang"], sub.to_dict("records"))]
print("pilot rows:",len(sub), "per dialect:", sub.dialect.value_counts().to_dict(), flush=True)
print("example prompt (MSA):\n", sub[sub.dialect==MSA].iloc[0]["prompt"][-700:], flush=True)

# ---------- scoring ----------
@torch.no_grad()
def run_model(mid):
    tag=mid.split("/")[1]; out=os.path.join(RES,f"scores_{tag}.csv")
    done=set()
    if os.path.exists(out):
        prev=pd.read_csv(out); done=set(zip(prev.dialect,prev.key)); print(tag,"resuming, done:",len(done))
    tok=AutoTokenizer.from_pretrained(mid); tok.padding_side="left"
    if tok.pad_token is None: tok.pad_token=tok.eos_token
    kw=dict(torch_dtype=torch.bfloat16)
    if "gemma" in mid.lower(): kw["attn_implementation"]="eager"
    t0=time.time(); model=AutoModelForCausalLM.from_pretrained(mid, **kw).to(dev).eval(); print(tag,"loaded in %.0fs"%(time.time()-t0), flush=True)
    # letter token ids: variants with and without leading space
    ids={}
    for L in LET:
        v=[]
        for s in [" "+L, L]:
            e=tok.encode(s, add_special_tokens=False)
            if len(e)==1: v.append(e[0])
        if not v: e=tok.encode(" "+L, add_special_tokens=False); v=[e[-1]]
        ids[L]=sorted(set(v))
    print(tag,"letter ids",ids, flush=True)
    rows=[r for r in sub.to_dict("records") if (r["dialect"],r["key"]) not in done]
    rows.sort(key=lambda r: len(r["prompt"]))
    hdr=not os.path.exists(out); f=open(out,"a"); 
    if hdr: f.write("model,dialect,domain,qid,key,answer,lA,lB,lC,lD,lA_sp,lB_sp,lC_sp,lD_sp,pred,correct,p_true,p_max,n_tok\n")
    t0=time.time()
    for i in range(0,len(rows),BS):
        b=rows[i:i+BS]
        enc=tok([r["prompt"] for r in b], return_tensors="pt", padding=True, truncation=True, max_length=2048).to(dev)
        logits=model(**enc).logits[:,-1,:].float()
        lse=torch.logsumexp(logits,dim=-1,keepdim=True)
        lp=(logits-lse).cpu().numpy()
        for j,r in enumerate(b):
            # combined letter log-prob = logsumexp over variants; also record space-variant alone
            comb=[float(np.logaddexp.reduce([lp[j,t] for t in ids[L]])) for L in LET]
            sp=[float(lp[j,ids[L][0]]) for L in LET]
            z=np.array(comb); p=np.exp(z-np.logaddexp.reduce(z))
            pred=int(np.argmax(p)); ans=int(r["answer"])
            f.write(",".join(map(str,[r["model"] if "model" in r else tag, r["dialect"], r["domain"], r["qid"], r["key"], ans,
                *["%.4f"%x for x in comb], *["%.4f"%x for x in sp], pred, int(pred==ans), "%.5f"%p[ans], "%.5f"%p.max(), int(enc["attention_mask"][j].sum())]))+"\n")
        if (i//BS)%25==0:
            f.flush(); el=time.time()-t0; print(f"{tag} {i+len(b)}/{len(rows)} {el:.0f}s eta {el/(i+len(b))*(len(rows)-i-len(b)):.0f}s", flush=True)
    f.close(); print(tag,"DONE in %.0fs"%(time.time()-t0), flush=True)
    del model; 
    if dev=="mps": torch.mps.empty_cache()

for mid in MODELS:
    try: run_model(mid)
    except Exception as e:
        print("MODEL FAILED",mid,repr(e)); traceback.print_exc()
print("ALL DONE")
