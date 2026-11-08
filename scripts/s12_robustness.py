#!/usr/bin/env python
"""Measurement robustness scoring (pre-registered, ANALYSIS_PLAN.md Addendum 8): option-order permutations and answer extraction.
Subset: data/robust_keys.json (500 confirmatory TEST keys, seed 20261107) x 7 varieties x 4 cyclic orderings k=0..3
(option at original index i shown at position (i+k) mod 4; gold index shifted; the 3 shots keep their original order).
Prompt template, truncation and letter-logit scoring IDENTICAL to scripts/s9_score_confirm.py.
Stages (env ADA_STAGES, default "score,g1,g2"):
  score : letter-logit scoring of all orderings      -> results/robust_scores_<tag>.csv
  g1    : greedy generation, <=8 new tokens, from the identical k=0 prompt (all models) -> results/robust_gen_<tag>.csv (cond=G1)
  g2    : chat-template generation, <=32 new tokens, k=0 prompt as the single user turn, + first-step letter log-probs under the
          chat template (ALLaM-7B-Instruct-preview only: the only instruction-tuned checkpoint) -> results/robust_gen_<tag>.csv (cond=G2)
Resumable per (dialect,key,k) / (dialect,key,cond). Env: ADA_DATA, ADA_RES, ADA_MODELS, ADA_BS, ADA_GBS (generation batch), HF_HOME."""
import os, json, time, csv, traceback, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
DATA=os.environ["ADA_DATA"]; RES=os.environ["ADA_RES"]; BS=int(os.environ.get("ADA_BS","4")); GBS=int(os.environ.get("ADA_GBS",str(BS)))
MODELS=os.environ.get("ADA_MODELS","ALLaM-AI/ALLaM-7B-Instruct-preview,Qwen/Qwen3-8B-Base,QCRI/Fanar-1-9B,google/gemma-2-9b").split(",")
STAGES=os.environ.get("ADA_STAGES","score,g1,g2").split(","); G2_MODELS={"ALLaM-7B-Instruct-preview"}; G1_TOK=8; G2_TOK=32
dev="mps" if torch.backends.mps.is_available() else "cpu"; print("device",dev,"BS",BS,"GBS",GBS,"stages",STAGES,"models",MODELS,flush=True)
meta=json.load(open(os.path.join(DATA,"pilot_keys.json"))); MSA,ENG=meta["MSA"],meta["ENG"]
rk=json.load(open(os.path.join(DATA,"robust_keys.json"))); KEYS=rk["keys"]; ORD=rk["orderings"]; assert len(KEYS)==500 and ORD==[0,1,2,3]
df=pd.read_parquet(os.path.join(DATA,"damm.parquet")); df["choices"]=df["choices"].apply(list)
LET=["A","B","C","D"]
def fmt_q(question,choices,lang):
    ch="\n".join(f"{LET[i]}. {c}" for i,c in enumerate(choices))
    if lang=="en": return f"Question: {question}\n{ch}\nAnswer:"
    return f"السؤال: {question}\n{ch}\nالإجابة:"
msa_rows={r.key:r for r in df[df.dialect==MSA].itertuples()}; eng_rows={r.key:r for r in df[df.dialect==ENG].itertuples()} if ENG else {}
def shots_text(lang):
    src=eng_rows if (lang=="en" and eng_rows) else msa_rows
    return "\n\n".join(fmt_q(src[k].question,src[k].choices,lang)+" "+LET[src[k].answer] for k in meta["shots"])
HEAD_AR="فيما يلي أسئلة اختيار من متعدد. اختر الإجابة الصحيحة بكتابة حرفها فقط.\n\n"
HEAD_EN="The following are multiple choice questions. Answer with the letter of the correct option only.\n\n"
SHOTS={"ar":HEAD_AR+shots_text("ar")+"\n\n","en":HEAD_EN+shots_text("en")+"\n\n"}
sub=df[df.key.isin(set(KEYS))].copy(); assert sub.key.nunique()==500
ROWS=[]
for r in sub.itertuples():
    lang="en" if r.dialect==ENG else "ar"
    for k in ORD:
        ch=[r.choices[(p-k)%4] for p in range(4)]; ans_pos=(int(r.answer)+k)%4
        ROWS.append(dict(dialect=r.dialect,key=r.key,k=k,lang=lang,answer_orig=int(r.answer),answer_pos=ans_pos,prompt=SHOTS[lang]+fmt_q(r.question,ch,lang),choices=ch))
print("rows",len(ROWS),"per dialect",sub.dialect.value_counts().to_dict(),flush=True); print("example k=1:\n",[x for x in ROWS if x["k"]==1][0]["prompt"][-500:],flush=True)
def letter_ids(tok):
    ids={}
    for L in LET:
        v=[]
        for s in [" "+L,L]:
            e=tok.encode(s,add_special_tokens=False)
            if len(e)==1: v.append(e[0])
        if not v: v=[tok.encode(" "+L,add_special_tokens=False)[-1]]
        ids[L]=sorted(set(v))
    return ids
def letter_lp(lp_row,ids): return [float(np.logaddexp.reduce([lp_row[t] for t in ids[L]])) for L in LET]
@torch.no_grad()
def run_model(mid):
    tag=mid.split("/")[1]; out_s=os.path.join(RES,f"robust_scores_{tag}.csv"); out_g=os.path.join(RES,f"robust_gen_{tag}.csv")
    tok=AutoTokenizer.from_pretrained(mid); tok.padding_side="left"
    if tok.pad_token is None: tok.pad_token=tok.eos_token
    kw=dict(torch_dtype=torch.bfloat16)
    if "gemma" in mid.lower(): kw["attn_implementation"]="eager"
    t0=time.time(); model=AutoModelForCausalLM.from_pretrained(mid,**kw).to(dev).eval(); print(tag,"loaded in %.0fs"%(time.time()-t0),flush=True)
    ids=letter_ids(tok); print(tag,"letter ids",ids,flush=True)
    # ---------------- stage score ----------------
    if "score" in STAGES:
        done=set()
        if os.path.exists(out_s):
            prev=pd.read_csv(out_s,dtype={"key":str}); done=set(zip(prev.dialect,prev.key,prev.k.astype(int))); print(tag,"score resuming, done:",len(done),flush=True)
        rows=[r for r in ROWS if (r["dialect"],r["key"],r["k"]) not in done]; rows.sort(key=lambda r: len(r["prompt"]))
        if rows:
            hdr=not os.path.exists(out_s); f=open(out_s,"a")
            if hdr: f.write("model,dialect,key,k,answer_orig,answer_pos,lA,lB,lC,lD,pred_pos,pred_orig,correct,p_true,p_max,n_tok\n")
            t0=time.time()
            for i in range(0,len(rows),BS):
                b=rows[i:i+BS]; enc=tok([r["prompt"] for r in b],return_tensors="pt",padding=True,truncation=True,max_length=2048).to(dev)
                logits=model(**enc).logits[:,-1,:].float(); lp=(logits-torch.logsumexp(logits,dim=-1,keepdim=True)).cpu().numpy()
                for j,r in enumerate(b):
                    comb=letter_lp(lp[j],ids); z=np.array(comb); p=np.exp(z-np.logaddexp.reduce(z)); pred=int(np.argmax(p)); pred_orig=(pred-r["k"])%4
                    f.write(",".join(map(str,[tag,r["dialect"],r["key"],r["k"],r["answer_orig"],r["answer_pos"],*["%.4f"%x for x in comb],pred,pred_orig,int(pred==r["answer_pos"]),"%.5f"%p[r["answer_pos"]],"%.5f"%p.max(),int(enc["attention_mask"][j].sum())]))+"\n")
                if (i//BS)%50==0:
                    f.flush(); el=time.time()-t0; print(f"{tag} score {i+len(b)}/{len(rows)} {el:.0f}s eta {el/(i+len(b))*(len(rows)-i-len(b)):.0f}s",flush=True)
            f.close(); print(tag,"SCORE DONE in %.0fs"%(time.time()-t0),flush=True)
        else: print(tag,"score already complete",flush=True)
    # ---------------- stages g1 / g2 ----------------
    conds=[c for c in ["g1","g2"] if c in STAGES and (c=="g1" or tag in G2_MODELS)]
    if conds:
        done=set()
        if os.path.exists(out_g):
            prev=pd.read_csv(out_g,dtype={"key":str}); done=set(zip(prev.dialect,prev.key,prev.cond)); print(tag,"gen resuming, done:",len(done),flush=True)
        hdr=not os.path.exists(out_g); f=open(out_g,"a",newline=""); w=csv.writer(f,quoting=csv.QUOTE_ALL)
        if hdr: w.writerow(["model","dialect","key","cond","answer_orig","gen_text","n_new","cA","cB","cC","cD","pred_chat"])
        base=[r for r in ROWS if r["k"]==0]
        for cond in conds:
            C=cond.upper(); rows=[r for r in base if (r["dialect"],r["key"],C) not in done]; rows.sort(key=lambda r: len(r["prompt"]))
            if not rows: print(tag,cond,"already complete",flush=True); continue
            ntok=G1_TOK if cond=="g1" else G2_TOK; t0=time.time()
            for i in range(0,len(rows),GBS):
                b=rows[i:i+GBS]
                if cond=="g1": enc=tok([r["prompt"] for r in b],return_tensors="pt",padding=True,truncation=True,max_length=2048).to(dev)
                else:
                    texts=[tok.apply_chat_template([{"role":"user","content":r["prompt"]}],add_generation_prompt=True,tokenize=False) for r in b]
                    enc=tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=2048,add_special_tokens=False).to(dev)
                gen=model.generate(**enc,max_new_tokens=ntok,do_sample=False,pad_token_id=tok.pad_token_id,return_dict_in_generate=True,output_logits=(cond=="g2"))
                seqs=gen.sequences[:,enc["input_ids"].shape[1]:]
                first=None
                if cond=="g2":
                    L=gen.logits if getattr(gen,"logits",None) is not None else gen.scores
                    l0=L[0].float(); first=(l0-torch.logsumexp(l0,dim=-1,keepdim=True)).cpu().numpy()
                for j,r in enumerate(b):
                    new=seqs[j]; txt=tok.decode(new,skip_special_tokens=True); nn=int((new!=tok.pad_token_id).sum())
                    if first is not None:
                        c=letter_lp(first[j],ids); pc=int(np.argmax(c)); w.writerow([tag,r["dialect"],r["key"],C,r["answer_orig"],txt,nn,*["%.4f"%x for x in c],pc])
                    else: w.writerow([tag,r["dialect"],r["key"],C,r["answer_orig"],txt,nn,"","","","",""])
                if (i//GBS)%50==0:
                    f.flush(); el=time.time()-t0; print(f"{tag} {cond} {i+len(b)}/{len(rows)} {el:.0f}s eta {el/(i+len(b))*(len(rows)-i-len(b)):.0f}s | ex: {txt[:40]!r}",flush=True)
            print(tag,cond.upper(),"DONE in %.0fs"%(time.time()-t0),flush=True)
        f.close()
    print(tag,"ROBUST DONE",flush=True); del model
    if dev=="mps": torch.mps.empty_cache()
for mid in MODELS:
    try: run_model(mid)
    except Exception as e: print("MODEL FAILED",mid,repr(e)); traceback.print_exc()
print("ALL DONE")
