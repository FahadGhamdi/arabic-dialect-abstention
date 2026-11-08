#!/usr/bin/env python
"""Stage 2: download MBZUAI/Dialectal-Arabic-MMLU (+ IFM verified variant), dump schema and save parquet."""
import os, json, time
import pandas as pd
from huggingface_hub import hf_hub_download, HfApi
OUT=os.environ["ADA_DATA"]; t0=time.time()
api=HfApi()
for rid in ["MBZUAI/Dialectal-Arabic-MMLU","IFM/Dialectal-Arabic-MMLU_verified"]:
    try:
        info=api.dataset_info(rid)
        files=[s.rfilename for s in info.siblings]
        print("\n=== ",rid," files:",files, flush=True)
        try:
            p=hf_hub_download(rid, "README.md", repo_type="dataset"); print("--- README head ---"); print(open(p,encoding="utf-8").read()[:3000])
        except Exception as e: print("no README", e)
        tag=rid.split("/")[1].lower()
        frames=[]
        for f in files:
            if f.endswith(".parquet") or f.endswith(".jsonl") or f.endswith(".json") or f.endswith(".csv"):
                p=hf_hub_download(rid, f, repo_type="dataset")
                if f.endswith(".parquet"): df=pd.read_parquet(p)
                elif f.endswith(".csv"): df=pd.read_csv(p)
                else: df=pd.read_json(p, lines=f.endswith(".jsonl"))
                df["_file"]=f; frames.append(df); print("loaded",f,df.shape)
        if frames:
            df=pd.concat(frames, ignore_index=True)
            print("columns:", list(df.columns)); print("dtypes:\n", df.dtypes)
            print("shape:", df.shape)
            for c in df.columns:
                if df[c].dtype==object and df[c].nunique()<=40:
                    print("value_counts[%s]:"%c, df[c].value_counts().to_dict())
            print("--- 3 rows ---")
            for i in range(min(3,len(df))): print(json.dumps({k:(str(v)[:300]) for k,v in df.iloc[i].to_dict().items()}, ensure_ascii=False))
            df.to_parquet(os.path.join(OUT, f"{tag}.parquet"), index=False)
            print("saved", f"{tag}.parquet")
    except Exception as e:
        print("FAILED", rid, repr(e))
print("DONE s2 in %.1fs"%(time.time()-t0))
