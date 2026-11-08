#!/usr/bin/env python3
"""Check released stored-score identities and bookkeeping, without inference.

This detects internal inconsistencies; it does not authenticate historical
model execution. Rounded log probabilities need not reconstruct p exactly.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();root=a.repository
    splits=json.loads((root/'data/confirmatory_splits.json').read_text())
    sets=[set(splits[k]) for k in ['router_train','calibration','test']]
    assert [len(x) for x in sets]==[404,808,1420]
    assert all(not sets[i]&sets[j] for i in range(3) for j in range(i))
    pilot=json.loads((root/'data/pilot_keys.json').read_text())
    assert not set.union(*sets)&(set(pilot['pilot'])|set(pilot['shots']))
    rows=[]
    files=sorted({p for pat in ['confirm_scores_*.csv','scores_*.csv','robust_scores_*.csv','aradice_scores_*.csv'] for p in (root/'results').glob(pat)})
    for p in files:
        df=pd.read_csv(p);identity=['key','dialect']+(['k'] if 'k' in df else [])
        assert not df.duplicated(identity).any(),p.name
        pr='pred_orig' if 'pred_orig' in df else 'pred'
        an='answer_orig' if 'answer_orig' in df else 'answer'
        assert np.array_equal(df.correct.astype(int),(df[pr]==df[an]).astype(int)),p.name
        assert df.correct.isin([0,1]).all()
        assert df[an].isin(range(4)).all() and df[pr].isin(range(4)).all()
        assert np.isfinite(df[['p_max','p_true','lA','lB','lC','lD']]).all().all()
        assert ((df[['p_max','p_true']]>=0)&(df[['p_max','p_true']]<=1)).all().all()
        logs=df[['lA','lB','lC','lD']].to_numpy()
        probs=np.exp(logs-np.logaddexp.reduce(logs,axis=1,keepdims=True))
        answer=df['answer_pos' if 'answer_pos' in df else 'answer'].to_numpy(int)
        err=max(float(np.max(abs(probs.max(1)-df.p_max))),float(np.max(abs(probs[np.arange(len(df)),answer]-df.p_true))))
        assert err<0.0001,(p.name,err)
        predpos=df['pred_pos' if 'pred_pos' in df else 'pred'].to_numpy(int)
        max_loss=float(np.max(probs.max(1)-probs[np.arange(len(df)),predpos]))
        assert max_loss<0.0001,(p.name,max_loss)
        if p.name.startswith('confirm_scores_'):
            assert len(df)==2632*7 and set(df.key)==set.union(*sets)
            assert df.groupby('key').dialect.nunique().eq(7).all()
        if p.name.startswith('robust_scores_'):
            rk=set(json.loads((root/'data/robust_keys.json').read_text())['keys'])
            assert len(df)==500*7*4 and set(df.key)==rk and rk<=sets[2]
        rows.append({'file':str(p.relative_to(root)),'rows':len(df),'unique_records':True,
                     'correctness_identity':True,'max_probability_reconstruction_error':err,
                     'max_argmax_probability_loss':max_loss,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    out={'scope':'Internal checks on stored scores, not verification of historical inference',
         'split_sizes':[404,808,1420],'split_and_development_disjoint':True,
         'files':rows,'total_records':sum(r['rows'] for r in rows)}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'score_files':len(rows),'records':out['total_records'],'status':'PASS'},indent=2))

if __name__=='__main__':main()
