#!/usr/bin/env python3
"""Check the per-key agreement counts quoted by the independent-check report."""
from pathlib import Path
import argparse,json,math
import pandas as pd
import numpy as np

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=a.repository
    split=json.loads((r/'data/confirmatory_splits.json').read_text())
    s4=pd.read_csv(r/'results/confirm/S4_operational_selective.csv')
    total=accepted=covered=0
    for p in sorted((r/'results/indep_check').glob('perkey_*.csv')):
        model=p.stem.removeprefix('perkey_')
        raw=pd.read_csv(r/f'results/confirm_scores_{model}.csv')
        independent=pd.read_csv(p)
        merged=independent.merge(raw,left_on=['key','variety'],right_on=['key','dialect'],validate='one_to_one')
        assert len(merged)==1420*7
        tau=s4[(s4.model==model)&(s4.target_risk==.2)&(s4.variety=='MSA')].tau.item()
        cal=1-raw[(raw.dialect=='MSA')&raw.key.isin(split['calibration'])].p_true.to_numpy()
        q=np.sort(cal)[min(len(cal),math.ceil((len(cal)+1)*.7))-1]
        accepted+=int(((merged.p_max>=tau)==merged.answered_at_tau_r020.astype(bool)).sum())
        covered+=int(((1-merged.p_true<=q)==merged.covered_at_qmsa_a030.astype(bool)).sum())
        total+=len(merged)
    result={'cells':total,'accepted_matches':accepted,'covered_matches':covered}
    assert result=={'cells':39760,'accepted_matches':39759,'covered_matches':39755},result
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(result)

if __name__=='__main__':main()
