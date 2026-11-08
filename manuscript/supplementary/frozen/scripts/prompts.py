import os, json, numpy as np, pandas as pd
LET=["A","B","C","D"]
def load_pilot(OUT):
    meta=json.load(open(os.path.join(OUT,"pilot_keys.json")))
    df=pd.read_parquet(os.path.join(OUT,"damm.parquet")); df["choices"]=df["choices"].apply(list)
    MSA,ENG=meta["MSA"],meta["ENG"]
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
    sub=df[df.key.isin(set(meta["pilot"]))].copy()
    sub["lang"]=np.where(sub.dialect==ENG,"en","ar")
    sub["prompt"]=[SHOTS[l]+fmt_q(r,l) for l,r in zip(sub["lang"], sub.to_dict("records"))]
    return sub, meta
def letter_ids(tok):
    ids={}
    for L in LET:
        v=[]
        for s in [" "+L, L]:
            e=tok.encode(s, add_special_tokens=False)
            if len(e)==1: v.append(e[0])
        if not v: v=[tok.encode(" "+L, add_special_tokens=False)[-1]]
        ids[L]=sorted(set(v))
    return ids
