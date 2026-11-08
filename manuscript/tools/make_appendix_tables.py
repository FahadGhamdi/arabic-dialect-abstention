#!/usr/bin/env python3
"""Generate A2--A21 from archived aggregates; no model calls or score reanalysis.
Run from any directory. --check verifies the generated files.
Layout metadata contains captions/headers/widths only, never observations.
"""
from pathlib import Path
import csv, re, json, hashlib, argparse
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'supplementary/frozen'
LAYOUTS = json.loads((ROOT/'tools/table_layouts.json').read_text())
MODELS = {'ALLaM':'ALLaM-7B-Instruct-preview', 'Fanar':'Fanar-1-9B',
          'Qwen3':'Qwen3-8B-Base', 'Gemma':'gemma-2-9b'}
DIALECTS = ['MAG','SYR','EGY','KSA','UAE']
VARIETIES = ['MSA'] + DIALECTS + ['ENG']
FILES = {
'p1':'results/confirm/P1_selective.csv', 'p2':'results/confirm/P2_conformal.csv',
's4':'results/confirm/S4_operational_selective.csv', 's2':'results/confirm/S2_variety_aware.csv',
's1':'results/confirm/S1_calib_efficiency.csv', 's3':'results/confirm/S3_calibration.csv',
'd1':'results/diag/D1_D2_discrimination.csv', 'd4':'results/diag/D4_variety_threshold.csv',
'sens':'results/sens/S91_calibration_sensitivity.csv', 'risk':'results/supp/S101_risk_diff.csv',
'ara':'results/validity/L4_aradice.csv', 'osr':'results/robust/R1_order_sensitivity.csv',
'rot':'results/robust/R2_gap_stability.csv', 'pair':'results/sens/S93_R4_paired.csv',
'gen':'results/robust/R5_generation.csv', 'selgen':'results/supp/S102_gen_selective_risk.csv',
'audit':'../recomputed_screen/SCREEN_RECOMPUTED.md', 'indep':'results/indep_check/INDEP_COMPARISON.md'}
DATA = {}
for key, name in FILES.items():
    if not name.endswith('.csv'): continue
    rows = list(csv.DictReader((BASE/name).open()))
    for row in rows:
        for k,v in row.items():
            try: row[k] = float(v)
            except (ValueError, TypeError): pass
    DATA[key] = rows
def get(key, model, variety, **conditions):
    found = [r for r in DATA[key] if r['model']==MODELS.get(model,model)
             and r['variety']==variety and all(r[k]==v for k,v in conditions.items())]
    if len(found)!=1: raise ValueError((key,model,variety,conditions,len(found)))
    return found[0]
def num(x, digits=3):
    x = 0.0 if abs(x) < .5*10**(-digits) else x
    return f'{x:.{digits}f}'
def n(x): return '$'+num(x)+'$'
def ci(lo,hi): return '$['+num(lo)+',\\,'+num(hi)+']$'
def est(x,lo,hi): return '$'+num(x)+'\\;['+num(lo)+',\\,'+num(hi)+']$'
def pair(x,y): return '$'+num(x)+'\\,/\\,'+num(y)+'$'
def markdown_table(key, first):
    lines = (BASE/FILES[key]).read_text().splitlines()
    start = next(i for i,l in enumerate(lines) if l.startswith('| '+first+' |'))
    result=[]
    for line in lines[start+2:]:
        if not line.startswith('|'): break
        result.append([v.strip() for v in line.strip('|').split('|')])
    return result
def prose(s):
    s=s.replace('**','').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
    for a,b in [('q̂',r'$\hat q$'),('τ',r'$\tau$'),('α',r'$\alpha$'),
                ('Δcov',r'$\Delta C$'),('≤',r'$\leq$'),('×',r'$\times$'),
                ('–','--'),('−',r'$-$')]:
        s=s.replace(a,b)
    return s
TABLES={}
def add(key, rows, sources):TABLES[key] = (rows, sources)
for key in ['p1full','p2coverage','p2size','s4answers','s4risk','d4points','d4gaps','aradice','paired','g1']:
    out=[]
    for m in MODELS:
        vv=VARIETIES if key=='g1' else (['MSA']+DIALECTS if key=='p1full'
            else ['EGY','LEV'] if key=='aradice' else DIALECTS)
        for v in vv:
            cells=[m,v]
            if key=='p1full':
                r=get('p1',m,v)
                cells += [n(r['msa_matched_risk']),n(r['answerable']),
                    'reference' if v=='MSA' else est(r['answerable']-get('p1',m,'MSA')['answerable'],r['d_lo'],r['d_hi'])]
                sources=['p1']
            elif key in ['p2coverage','p2size']:
                r=get('p2',m,v,alpha=.3);b=get('sens',m,v)
                if key=='p2coverage':
                    cells += [n(r['cov_msathr']-get('p2',m,'MSA',alpha=.3)['cov_msathr']),
                      ci(r['d_cov_lo'],r['d_cov_hi']),ci(b['p2_dcov_lo_rs'],b['p2_dcov_hi_rs']),
                      n(r['cov_ownthr']),n(r['size_ratio'])]
                else:
                    cells += [n(r['size_ownthr']),n(r['size_ratio']),
                        ci(r['size_ratio_lo'],r['size_ratio_hi']),ci(b['p2_szr_lo_rs'],b['p2_szr_hi_rs'])]
                sources=['p2','sens']
            elif key=='s4answers':
                r=get('s4',m,v,target_risk=.2);b=get('sens',m,v)
                cells += [n(r['answered']),n(r['answered']-get('s4',m,'MSA',target_risk=.2)['answered']),
                    ci(r['d_lo'],r['d_hi']),ci(b['s4_lo_rs'],b['s4_hi_rs'])]
                sources=['s4','sens']
            elif key=='s4risk':
                r=get('risk',m,v)
                cells += [n(r['risk']),n(r['d_risk']),ci(r['d_risk_lo'],r['d_risk_hi']),
                    ci(r['d_risk_rs_lo'],r['d_risk_rs_hi'])]
                sources=['risk']
            elif key in ['d4points','d4gaps']:
                r=get('d4',m,v,target_risk=.2)
                if key=='d4points':
                    cells += [n(r[k]) for k in ['answered_msa_thr','answered_v_thr','realised_risk_msa_thr','realised_risk_v_thr']]
                    cells += [ci(r['risk_lo'],r['risk_hi'])];sources=['d4']
                else:
                    b=get('sens',m,v)
                    cells += [est(r['recoverable'],r['rec_lo'],r['rec_hi']),n(r['residual_gap']),
                        ci(r['res_lo'],r['res_hi']),ci(b['d4_res_lo_rs'],b['d4_res_hi_rs'])]
                    sources=['d4','sens']
            elif key=='aradice':
                r=get('ara',m,v)
                cells += [est(r[k],r[k+'_lo'],r[k+'_hi']) for k in ['dacc','dp1','dcov']]
                cells += [n(r['size_ratio'])];sources=['ara']
            elif key=='paired':
                r=get('pair',m,v)
                cells += [n(r['p3']),n(r['within_rotation']),est(r['mean_D'],r['D_lo'],r['D_hi']),
                    est(r['mean_Dprime'],r['Dp_lo'],r['Dp_hi'])];sources=['pair']
            elif key=='g1':
                r=get('gen',m,v,cond='G1');b=get('selgen',m,v)
                cells += [est(r['agreement'],r['agr_lo'],r['agr_hi']),n(r['unextractable']),
                    n(b['accepted']),n(b['sel_risk_logit']),n(b['sel_risk_gen'])];sources=['gen','selgen']
            out.append(cells)
    add(key,out,sources)
for key,source,fields in [('accuracyfull','d1',['acc','auroc']),('s3','s3',['ece','brier'])]:
    add(key,[[v]+[pair(*(get(source,m,v)[k] for k in fields)) for m in MODELS] for v in VARIETIES],[source])
out=[]
for label,method in [('MSA-only','msa_only'),('Pooled','pooled'),('Predicted label','text_router'),
                     ('True label','oracle'),('Plausible-set union','plausible_set')]:
    out.append([label]+[pair(get('s2',m,'MAG',alpha=.3,method=method)['coverage'],
                             get('s2',m,'MAG',alpha=.3,method=method)['set_size']) for m in MODELS])
recovery=[]
for m in MODELS:
    a=get('s2',m,'MAG',alpha=.3,method='msa_only')['coverage']
    b=get('s2',m,'MAG',alpha=.3,method='oracle')['coverage']
    q=get('s2',m,'MAG',alpha=.3,method='text_router')['coverage']
    recovery.append('$'+f'{100*(q-a)/(b-a):.1f}'+r'\%$')
out.append(['Recovered coverage gain']+recovery);add('s2full',out,['s2'])
out=[]
for v in VARIETIES:
    row=[v]
    for m in MODELS:
        r=get('osr',m,v)
        row += [n(r['osr']) if v=='MSA' else n(r['osr'])+' / '+n(r['d_osr'])+r'\newline'+ci(r['d_osr_lo'],r['d_osr_hi'])]
    out.append(row)
add('ordersensitivity',out,['osr'])
out=[]
for v in DIALECTS:
    for label,prefix in [('Accuracy','d_acc'),('P1','d_p1')]:
        out.append([v+' / '+label]+[est(get('rot',m,v)[prefix+'_avg'],
             get('rot',m,v)[prefix+'_lo'],get('rot',m,v)[prefix+'_hi']) for m in MODELS])
add('rotationgaps',out,['rot'])
add('g2',[[v]+[n(get('gen','ALLaM',v,cond='G2')[k]) for k in ['agreement','gen_vs_chat_logit','unextractable','gen_acc']]
    for v in ['MSA','EGY','KSA','MAG','SYR','UAE','ENG']],['gen'])
out=[]
for size in sorted(set(r['n_cal'] for r in DATA['s1'])):
    rows=[r for r in DATA['s1'] if r['n_cal']==size and r['variety'] in DIALECTS]
    out.append([str(int(size))]+['$'+num(min(r[k] for r in rows))+r'\text{--}'+num(max(r[k] for r in rows))+'$'
        for k in ['p_within5','cov']])
add('s1',out,['s1'])
for key,first,columns in [('auditflags','dialect',[0,1,2,3,4]),('auditagreement','check',[0,1,3,4])]:
    rows=markdown_table('audit',first);out=[]
    for r in rows:
        cells=[]
        for j in columns:
            val=r[j].replace('**','')
            if j==0: cells.append(prose(val));continue
            if key=='auditagreement' and j in [3,4]:val=val.split(' (')[0]
            cells.append('$'+val+'$')
        out.append(cells)
    add(key,out,['audit'])
add('indep',[[prose(c) for c in r] for r in markdown_table('indep','quantity')],['indep'])
LAYOUTS['indep'].update(weights=[.32,.10,.32,.26],
    head='Quantity & Cells & Maximum absolute difference & Interpretation')
assert set(TABLES)==set(LAYOUTS),(set(TABLES)^set(LAYOUTS))
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
records={}
for key,(rows,sources) in TABLES.items():
    layout=LAYOUTS[key];weights=layout['weights'];nc=len(weights)
    if key in ['aradice','rotationgaps']:
        rows=[[c.replace(r'\;[',r'$\newline$[') for c in row] for row in rows]
    assert all(len(r)==nc for r in rows),(key,nc,[len(r) for r in rows])
    widths=[x/sum(weights) for x in weights]
    cols='@{}'+''.join(r'>{\raggedright\arraybackslash}p{\dimexpr '+f'{w:.7f}'+
       r'\linewidth-'+f'{2*(nc-1)/nc:.7f}'+r'\tabcolsep\relax}' for w in widths)+'@{}'
    text='% Generated by tools/make_appendix_tables.py; do not edit data cells.\n'
    text+=r'\begingroup'+'\n'+r'\setstretch{1}\small\setlength{\tabcolsep}{3pt}'+'\n'
    text+=r'\setlength{\LTleft}{0pt plus 1fill}\setlength{\LTright}{0pt plus 1fill}\setlength{\LTcapwidth}{\linewidth}'+'\n'
    text+=r'\setlength{\LTpre}{8pt}\setlength{\LTpost}{8pt}'+'\n'
    text+=r'\begin{longtable}{'+cols+'}\n'
    text+=r'\caption{'+layout['caption']+r'}\label{'+layout['label']+r'}\\'+'\n'
    header=r'\toprule'+'\n'+layout['head']+r' \\'+'\n'+r'\midrule'+'\n'
    text+=header+r'\endfirsthead'+'\n'
    text+=r'\multicolumn{'+str(nc)+r'}{l}{\small\itshape Table~\thetable\ (continued)}\\'+'\n'
    text+=header+r'\endhead'+'\n'+r'\midrule\endfoot'+'\n'+r'\bottomrule\endlastfoot'+'\n'
    # Keep the first and last two rows together; every observation remains intact.
    for i,row in enumerate(rows):
        end=r' \\*' if i in (0,len(rows)-2) else r' \\'
        text+=' & '.join(row)+end+'\n'
    text+=r'\end{longtable}'+'\n'+r'\endgroup'+'\n'
    target=ROOT/'generated'/f'{key}.tex'
    if args.check:
        if not target.exists() or target.read_text()!=text:raise SystemExit('Mismatch: '+str(target))
    else:target.write_text(text)
    records[key]={'rows':len(rows),'source_files':[FILES[k] for k in sources],
                  'generated_sha256':hashlib.sha256(text.encode()).hexdigest()}
manifest={'tables':records,'source_sha256':{v:hashlib.sha256((BASE/v).read_bytes()).hexdigest() for v in FILES.values()}}
if not args.check:(ROOT/'generated/table_provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(('Verified' if args.check else 'Generated'),len(TABLES),'tables;',sum(len(r) for r,_ in TABLES.values()),'rows.')
order=re.findall(r'\\input\{generated/([^}]+)\.tex\}',(ROOT/'main.tex').read_text())
index=['# Appendix file index — manuscript v1.0','',
'Paths below are relative to this source archive. The historical score archive is identified by commit §8e103a0§. This index maps the additional files supplied with manuscript v1.0.','',
'Tables A2–A21 are generated by §tools/make_appendix_tables.py§ from archived CSVs, the independent-check report and the recomputed screen report. Headers and captions are in §tools/table_layouts.json§. Observed-sample contrasts use the stored absolute values; archived percentile interval endpoints are retained, except for the explicitly reseeded screen intervals described in Appendix E. §generated/table_provenance.json§ records input and output hashes.','',
'| Table | Generated file | Original aggregate/report |','|---|---|---|',
'| A1: chronology | §main.tex§ | §supplementary/frozen/ANALYSIS_PLAN.md§; §supplementary/frozen/FROZEN_SCRIPTS.md§ |']
for no,key in enumerate(order,2):
    sources='; '.join('§supplementary/frozen/'+s+'§' for s in records[key]['source_files'])
    index.append(f'| A{no} | §generated/{key}.tex§ | {sources} |')
index+=['','Figure A3 is regenerated by §tools/make_rotation_figure.py§ from §supplementary/frozen/results/robust/R2_gap_stability.csv§. Its 20 means, intervals and 80 per-rotation points are preserved in §generated/rotation_figure_provenance.json§. Only its presentation changed.',
'','Figure data are unchanged from v0.9; the main-figure citation order and the external-filter bibliography entry are corrected in v1.0. Original full score records and source dataset texts are not included in this selected manuscript archive. The data-availability statement identifies their sources.','']
target=ROOT/'docs/FILE_INDEX.md';text='\n'.join(index).replace('§',chr(96))
if args.check:
    if not target.exists() or target.read_text()!=text:raise SystemExit('File index mismatch')
else:target.write_text(text)
