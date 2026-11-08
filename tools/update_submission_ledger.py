#!/usr/bin/env python3
"""Derive the v1.0 claim ledger from the preserved historical ledger."""
from pathlib import Path
import argparse,csv,json

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);a=ap.parse_args();r=a.repository
    with (r/'docs/historical/CLAIMS_LEDGER.csv').open() as f:rows=list(csv.DictReader(f))
    edits={
      'AUD-01':('SCREEN_RECOMPUTED.json','',"[J['counts'][x] for x in ['pairs','keys','double_rated']]",[400,80,150]),
      'AUD-02':('rates_recomputed.csv','dialect=all;measure=basic',"rd(df[['rate','lo','hi']].iloc[0].tolist(),2)",[.37,.31,.43]),
      'AUD-03':('SCREEN_RECOMPUTED.json','',"rd([next(r['rate'] for r in J['rates'] if r['dialect']==d and r['measure']==m) for d,m in [('all','q2no'),('MAG','q2no'),('all','q3no')]],2)",[.08,.16,.34]),
      'AUD-04':('agreement_recomputed.csv','',"rd(df.kappa.tolist(),2)",[.86,.36,.90,0]),
      'AUD-05':('association_recomputed.csv','flag=basic;metric=dacc',"rd(pp(df[['unflagged','flagged','difference','lo','hi']].iloc[0].tolist()),1)",[-4.5,-6.2,-1.8,-8.2,5.1]),
      'AUD-06':('sensitivity_recomputed.csv','scen=excl_basic',"rd([100*df.groupby('d').dans.mean().min(),100*df.groupby('d').dans.mean().max()],0)",[-20,-6]),
    }
    for row in rows:
        if row['id']=='D01':row['file']='data/damm_keys.csv'
        if row['id'] in edits:
            file,filt,expr,expected=edits[row['id']]
            row.update(file='results/audit_recomputed/'+file,filter=filt,expr=expr,claimed=json.dumps(expected),tol='0.000000001',note='Recomputed from text-free ratings and stored scores; seed 0, 2,000 key-bootstrap replicates. Original interactive record preserved in docs/historical and results/audit.')
            row['claim']=row['claim'].replace('0.44]; UAE','0.43]; UAE').replace('−8.6, +4.6','−8.2, +5.1').replace('MAG per-model ΔP1 CIs ≈ ±40 pp','MAG per-model ΔP1 interval widths 38–94 pp')
    with (r/'docs/CLAIMS_LEDGER.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Updated',len(rows),'ledger rows; six former report-only screen claims are computable.')

if __name__=='__main__':main()
