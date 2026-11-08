#!/usr/bin/env python3
"""Recompute screen/behaviour associations and 80-key sensitivity analyses.

Inputs are released model scores and text-free session-1 ratings. No model calls
or dataset texts. The script was reconstructed during the submission audit;
it is not the missing historical interactive analysis script.
"""
from pathlib import Path
import argparse,json,math
import numpy as np
import pandas as pd
from audit_screen import read,flags

MODELS=['ALLaM-7B-Instruct-preview','Fanar-1-9B','Qwen3-8B-Base','gemma-2-9b']
SHORT=['ALLaM','Fanar','Qwen3','Gemma'];DIAL=['UAE','EGY','KSA','SYR','MAG']
def threshold(c,y):
    order=np.argsort(-c);risk=np.cumsum(1-y[order])/np.arange(1,len(c)+1);ok=np.flatnonzero(risk<=.2)
    return c[order[ok[-1]]] if len(ok) else 1.01
def qhat(s):return np.sort(s)[min(len(s),math.ceil((len(s)+1)*.7))-1]
def p1(c,y,t):
    order=np.argsort(-c);risk=np.cumsum(1-y[order])/np.arange(1,len(c)+1);ok=np.flatnonzero(risk<=t)
    return (ok[-1]+1)/len(c) if len(ok) else 0.
def metrics(m,x,q,t):
    o=np.argsort(-m[:,2]);r=(1-m[o[:math.ceil(len(m)*.5)],0]).mean()
    return np.array([(x[:,0]-m[:,0]).mean(),(x[:,3]!=m[:,3]).mean(),
        ((1-x[:,1]<=q).astype(float)-(1-m[:,1]<=q)).mean(),
        ((x[:,2]>=t).astype(float)-(m[:,2]>=t)).mean(),
        p1(x[:,2],x[:,0],r)-p1(m[:,2],m[:,0],r)])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);ap.add_argument('--ratings-dir',type=Path,required=True)
    ap.add_argument('--replicates',type=int,default=2000);ap.add_argument('--seed',type=int,default=0);a=ap.parse_args()
    ratings=read(a.ratings_dir/'ratings_session1_400.csv');keys=sorted({r['key'] for r in ratings});by={(r['key'],r['dialect']):flags(r) for r in ratings}
    cf=json.loads((a.repository/'data/confirmatory_splits.json').read_text());cal=sorted(cf['calibration']);sensitivity=[];obs=[]
    for model,short in zip(MODELS,SHORT):
        confirm=pd.read_csv(a.repository/f'results/confirm_scores_{model}.csv')
        pilot=pd.read_csv(a.repository/f'results/scores_{model}.csv')
        data=pd.concat([pilot,confirm],ignore_index=True)
        assert not data.duplicated(['key','dialect']).any()
        data=data.set_index(['key','dialect'])[['correct','p_true','p_max','pred']]
        cm=data.loc[[(k,'MSA') for k in cal]].to_numpy(float);q=qhat(1-cm[:,1]);t=threshold(cm[:,2],cm[:,0])
        m=data.loc[[(k,'MSA') for k in keys]].to_numpy(float)
        for d in DIAL:
            x=data.loc[[(k,d) for k in keys]].to_numpy(float)
            for i,k in enumerate(keys):obs.append({'model':short,'key':k,'dialect':d,**by[k,d], 'dacc':x[i,0]-m[i,0],'change':float(x[i,3]!=m[i,3])})
            for scen in ['original','excl_basic','cf_basic','cf_strict']:
                keep=np.ones(len(keys),bool);xx=x.copy()
                if scen.startswith('excl_'):keep=np.array([not by[k,d][scen[5:]] for k in keys])
                elif scen.startswith('cf_'):
                    mask=np.array([by[k,d][scen[3:]] for k in keys]);xx[mask]=m[mask]
                mm=m[keep];xx=xx[keep];point=metrics(mm,xx,q,t)
                row={'model':short,'scen':scen,'d':d,'n':len(mm)}
                for name,val in zip(['dacc','chg','dcov','dans','dp1'],point):row[name]=float(val)
                if a.replicates:
                    rng=np.random.default_rng(a.seed);boot=np.array([metrics(mm[ix],xx[ix],q,t) for ix in rng.integers(0,len(mm),(a.replicates,len(mm)))])
                    for j,name in enumerate(['dacc','chg','dcov','dans','dp1']):row[name+'_lo'],row[name+'_hi']=np.quantile(boot[:,j],[.025,.975])
                sensitivity.append(row)
        print('recomputed',short,flush=True)
    pd.DataFrame(sensitivity).to_csv(a.ratings_dir/'sensitivity_recomputed.csv',index=False)
    df=pd.DataFrame(obs);associations=[]
    for flag in ['basic','strict','q2no']:
        part=df.groupby(['key',flag])[['dacc','change']].agg(['sum','count'])
        # Vectorise cluster bootstrap: each key carries all dialect/model records.
        sums=np.zeros((len(keys),2,2));counts=np.zeros((len(keys),2))
        for i,k in enumerate(keys):
            for f in [False,True]:
                subset=df[(df.key==k)&(df[flag]==f)];counts[i,int(f)]=len(subset)
                sums[i,int(f)]=subset[['dacc','change']].sum().to_numpy()
        pts=sums.sum(0)/counts.sum(0)[:,None]
        draws=np.random.default_rng(a.seed).integers(0,len(keys),(a.replicates,len(keys))) if a.replicates else None
        bs=sums[draws].sum(1)/counts[draws].sum(1)[...,None] if a.replicates else None
        for j,metric in enumerate(['dacc','change']):
            row={'flag':flag,'metric':metric,'unflagged_n':int(counts[:,0].sum()),'flagged_n':int(counts[:,1].sum()),'unflagged':pts[0,j],'flagged':pts[1,j],'difference':pts[1,j]-pts[0,j]}
            if a.replicates:row['lo'],row['hi']=np.quantile(bs[:,1,j]-bs[:,0,j],[.025,.975])
            associations.append(row)
    pd.DataFrame(associations).to_csv(a.ratings_dir/'association_recomputed.csv',index=False)
    (a.ratings_dir/'SENSITIVITY_METHOD.json').write_text(json.dumps({'seed':a.seed,'replicates':a.replicates,'source':'pilot scores for development keys; confirmatory scores for test keys','calibration':'808 confirmatory MSA calibration keys; fixed across bootstrap replicates','key_order':'lexicographic','sensitivity_resampling':'paired keys within each scenario','association_resampling':'80 question clusters retaining all dialects and models','p1_ties':'NumPy default argsort, matching archived metric definition'},indent=2)+'\n')
    print(pd.DataFrame(associations).to_string(index=False))
if __name__=='__main__':main()
