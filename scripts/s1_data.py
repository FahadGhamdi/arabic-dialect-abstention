#!/usr/bin/env python
"""Stage 1: environment check + locate/download parallel dialect MCQ data + schema dump.
Writes logs/s1.log via stdout redirection. Produces data/*.jsonl if alignment succeeds."""
import os, sys, json, time, traceback, random
t0=time.time()
print("=== ENV ===", flush=True)
print("python", sys.version.split()[0], "exe", sys.executable)
try:
    import torch; print("torch", torch.__version__, "mps", torch.backends.mps.is_available())
except Exception as e: print("torch import failed:", e)
try:
    import transformers; print("transformers", transformers.__version__)
except Exception as e: print("transformers import failed:", e)
import platform, subprocess
print("machine", platform.machine(), platform.mac_ver()[0])
try:
    mem=subprocess.check_output(["sysctl","-n","hw.memsize"]).decode().strip(); print("RAM_GB", int(mem)/1e9)
except Exception as e: print("mem?", e)
print("HF_HOME", os.environ.get("HF_HOME"))

from huggingface_hub import HfApi
api=HfApi()
print("\n=== SEARCH HF for DialectalArabicMMLU ===", flush=True)
cands=[]
try:
    for q in ["DialectalArabicMMLU","Dialectal Arabic MMLU","DialectalMMLU","Dialectal-Arabic-MMLU"]:
        for d in api.list_datasets(search=q, limit=20):
            cands.append(d.id)
    cands=sorted(set(cands)); print("candidates:", cands)
except Exception as e: print("search failed:", e)
for rid in ["MBZUAI/DialectalArabicMMLU","MBZUAI/Dialectal-Arabic-MMLU","ibm-research/DialectalArabicMMLU","malikaltakrori/DialectalArabicMMLU","CAMeL-Lab/DialectalArabicMMLU"]:
    try:
        info=api.dataset_info(rid); print("FOUND", rid, [s.rfilename for s in info.siblings][:30]); cands.append(rid)
    except Exception as e: print("no", rid, type(e).__name__)
json.dump(sorted(set(cands)), open(os.path.join(OUT:=os.environ["ADA_DATA"],"damm_candidates.json"),"w"))

print("\n=== LOAD AraDiCE (egy, lev) + MBZUAI/ArabicMMLU (MSA) ===", flush=True)
from datasets import load_dataset, get_dataset_config_names
rows={}
for var,rid in [("egy","QCRI/AraDICE-ArabicMMLU-egy"),("lev","QCRI/AraDICE-ArabicMMLU-lev")]:
    try:
        cfgs=get_dataset_config_names(rid); print(var, "configs:", len(cfgs), cfgs[:8], "...")
        rows[var]=[]
        for c in cfgs:
            ds=load_dataset(rid, c, split="test")
            if c==cfgs[0]: print(var, "columns:", ds.column_names); print(var, "example:", json.dumps(ds[0], ensure_ascii=False)[:1200])
            for r in ds:
                r=dict(r); r["_config"]=c; rows[var].append(r)
        print(var, "total rows:", len(rows[var]))
    except Exception as e:
        print(var, "FAILED:", e); traceback.print_exc()
try:
    msa=load_dataset("MBZUAI/ArabicMMLU","All",split="test")
    print("msa columns:", msa.column_names); print("msa example:", json.dumps(msa[0], ensure_ascii=False)[:1200]); print("msa rows:", len(msa))
    rows["msa"]=[dict(r) for r in msa]
except Exception as e:
    print("MSA FAILED:", e); traceback.print_exc()
for k,v in rows.items():
    with open(os.path.join(OUT,f"raw_{k}.jsonl"),"w") as f:
        for r in v: f.write(json.dumps(r, ensure_ascii=False)+"\n")
print("\n=== KEY OVERLAP DIAGNOSTICS ===")
def ids(rs):
    for key in ["ID","id","Id","qid","question_id"]:
        if rs and key in rs[0]: return key,[str(r[key]) for r in rs]
    return None,[]
for k,v in rows.items():
    key,i=ids(v); print(k,"id key:",key,"n_unique:",len(set(i)), "sample:", i[:3])
if "msa" in rows and "egy" in rows:
    km,im=ids(rows["msa"]); ke,ie=ids(rows["egy"]); kl,il=ids(rows.get("lev",[]))
    print("overlap msa∩egy:", len(set(im)&set(ie)), "msa∩lev:", len(set(im)&set(il)), "egy∩lev:", len(set(ie)&set(il)))
print("DONE s1 in %.1fs"%(time.time()-t0))
