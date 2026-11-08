#!/usr/bin/env python3
"""Recompute screening rates and agreement from text-free ratings.

Optional --workbook exports only identifiers, categorical ratings and numeric
confidence values. Question text, options, explanations and notes are excluded.
The XLSX is read directly as OOXML; formulas/cached statistics are not inputs.
No new model judgments are created. The original workbook is never modified.
"""
from pathlib import Path
import argparse,csv,hashlib,json,re,zipfile,xml.etree.ElementTree as ET
import numpy as np

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DIALECT={'المصرية':'EGY','السورية':'SYR','السعودية':'KSA','الإماراتية':'UAE','المغربية':'MAG'}
CATEGORY={'نعم':'yes','لا':'no','غير متأكد':'unsure'}
ORDER=['UAE','EGY','KSA','SYR','MAG']
def rows_from_xlsx(path):
    out={}
    with zipfile.ZipFile(path) as z:
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
        rels={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS):
            target=rels[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            data=[]
            for row in ET.fromstring(z.read(target)).findall('s:sheetData/s:row',NS)[1:]:
                d={}
                for c in row.findall('s:c',NS):
                    v=c.find('s:v',NS);inline=c.find('s:is',NS)
                    s=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
                    if c.attrib.get('t')=='s':s=strings[int(s)]
                    d[re.sub(r'\d','',c.attrib['r'])]=(s or '').strip()
                data.append(d)
            out[sh.attrib['name']]=data
    return out
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def export_ratings(workbook,out):
    sheets=rows_from_xlsx(workbook);sessions=[]
    for no in [1,2]:
        result=[]
        for r in sheets['المقيّم '+str(no)]:
            if not r.get('A'):continue
            d={'pair_id':r['A'],'key':r['C'],'dialect':DIALECT[r['I']],
               'source':'development' if r['B']=='تجريبي' else 'test'}
            for j,c in enumerate('LMNO',1):
                assert r[c] in CATEGORY,(r['A'],j,r[c]);d['Q'+str(j)]=CATEGORY[r[c]]
            # Numeric confidence only. Never export free text in the confidence column.
            conf=re.findall(r'(?:س|Q)\s*([1-4])\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%',r.get('Q',''))
            for j in range(1,5):d['confidence_Q'+str(j)]=dict(conf).get(str(j),'')
            result.append(d)
        assert len(result)==(400 if no==1 else 150)
        write_csv(out/f'ratings_session{no}_{len(result)}.csv',result);sessions.append(result)
    index={r['pair_id']:r for r in sessions[0]};adjud=[]
    for r in sheets['الخلافات']:
        if not r.get('A'):continue
        original=index[r['A']]
        answers=re.findall(r'غير متأكد|نعم|لا',r['L'])
        assert len(answers)==4,(r['A'],'four categorical adjudications required')
        d={k:original[k] for k in ['pair_id','key','dialect','source']}
        d.update({'Q'+str(j):CATEGORY[v] for j,v in enumerate(answers,1)})
        adjud.append(d)
    assert len(adjud)==150
    write_csv(out/'adjudication_150.csv',adjud)
    (out/'WORKBOOK_PROVENANCE.json').write_text(json.dumps({'sha256':hashlib.sha256(workbook.read_bytes()).hexdigest(),'exported_fields':'identifiers, categorical ratings, numeric confidence only','question_text_exported':False,'formula_cache_used':False},indent=2)+'\n')
def read(path):
    with path.open() as f:return list(csv.DictReader(f))
def flags(r):
    return {'basic':r['Q1']=='no' or r['Q2']=='no','q2no':r['Q2']=='no','q3no':r['Q3']=='no',
            'strict':any(r['Q'+str(i)]!='yes' for i in [1,2,3])}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workbook',type=Path);ap.add_argument('--ratings-dir',type=Path,required=True)
    ap.add_argument('--seed',type=int,default=0);ap.add_argument('--replicates',type=int,default=2000);a=ap.parse_args()
    out=a.ratings_dir;out.mkdir(parents=True,exist_ok=True)
    if a.workbook:export_ratings(a.workbook,out)
    r1=read(out/'ratings_session1_400.csv');r2=read(out/'ratings_session2_150.csv');r3=read(out/'adjudication_150.csv')
    idx={r['pair_id']:r for r in r1};keys=sorted({r['key'] for r in r1});assert len(keys)==80
    assert len(idx)==400 and len({r['pair_id'] for r in r2})==150
    for r in r2+r3:
        assert r['pair_id'] in idx and all(r[k]==idx[r['pair_id']][k] for k in ['key','dialect','source'])
    agreement=[]
    for q in ['Q1','Q2','Q3','Q4']:
        x=np.array([idx[r['pair_id']][q] for r in r2]);y=np.array([r[q] for r in r2])
        po=float((x==y).mean());pe=float(sum((x==c).mean()*(y==c).mean() for c in CATEGORY.values()))
        agreement.append({'check':q,'n':len(x),'observed':po,'expected':pe,'kappa':(po-pe)/(1-pe) if pe<1 else None,'disagreements':int((x!=y).sum())})
    rng=np.random.default_rng(a.seed);draws=rng.integers(0,len(keys),(a.replicates,len(keys)))
    by_pair={(r['key'],r['dialect']):flags(r) for r in r1};rate_rows=[]
    for dialect in ORDER+['all']:
        ds=ORDER if dialect=='all' else [dialect]
        for field in ['basic','q2no','q3no','strict']:
            v=np.array([np.mean([by_pair[k,d][field] for d in ds]) for k in keys]);lo,hi=np.quantile(v[draws].mean(1),[.025,.975])
            rate_rows.append({'dialect':dialect,'measure':field,'rate':float(v.mean()),'lo':float(lo),'hi':float(hi)})
    source_rates=[]
    for source in ['development','test']:
        kk=sorted({r['key'] for r in r1 if r['source']==source});v=np.array([np.mean([by_pair[k,d]['basic'] for d in ORDER]) for k in kk])
        bs=np.random.default_rng(a.seed).integers(0,len(kk),(a.replicates,len(kk)));lo,hi=np.quantile(v[bs].mean(1),[.025,.975])
        source_rates.append({'source':source,'keys':len(kk),'rate':float(v.mean()),'lo':float(lo),'hi':float(hi)})
    f1=np.array([flags(idx[r['pair_id']])['basic'] for r in r2]);f2=np.array([flags(r)['basic'] for r in r2]);f3=np.array([flags(r)['basic'] for r in r3])
    meta={'counts':{'pairs':len(r1),'keys':len(keys),'double_rated':len(r2)},'seed':a.seed,'replicates':a.replicates,'cluster':'question key; all five dialects retained together','key_order':'lexicographically sorted','quantile':'NumPy linear percentile',
          'q2_unsure':float(np.mean([r['Q2']=='unsure' for r in r1])),
          'double_rated_basic':{'session1':float(f1.mean()),'session2':float(f2.mean()),'both':float((f1&f2).mean()),'either':float((f1|f2).mean()),'adjudicated':float(f3.mean())},
          'agreement':agreement,'rates':rate_rows,'source_rates':source_rates}
    write_csv(out/'agreement_recomputed.csv',agreement);write_csv(out/'rates_recomputed.csv',rate_rows);write_csv(out/'source_rates_recomputed.csv',source_rates)
    (out/'SCREEN_RECOMPUTED.json').write_text(json.dumps(meta,indent=2)+'\n')
    lines=['# Recomputed model-assisted screen','',f'Computed from text-free categorical ratings. Seed {a.seed}; {a.replicates} bootstrap replicates, clustered by question key. Original interactive-run confidence intervals are retained in the frozen historical report; the intervals below use an explicit seed.','',
    '| dialect | basic defect (Q1 or Q2 = no) | Q2 = no | Q3 = no | strict |','|---|---|---|---|---|']
    for d in ORDER+['all']:
        rr={r['measure']:r for r in rate_rows if r['dialect']==d}
        def fmt(f):r=rr[f];return f"{r['rate']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}]"
        lines.append('| '+d+' | '+' | '.join(fmt(f) for f in ['basic','q2no','q3no','strict'])+' |')
    lines+=['','| check | observed agreement | expected | kappa | disagreements |','|---|---|---|---|---|']
    for r,label in zip(agreement,['Q1 meaning','Q2 answer/options','Q3 clarity','Q4 dialect membership']):
        lines.append(f"| {label} | {r['observed']:.3f} | {r['expected']:.3f} | {r['kappa']:.2f} | {r['disagreements']} |")
    lines+=['','The four values of kappa measure consistency between sessions of one model, not agreement between human annotators. Q4 has kappa zero because one session uses a single category on all double-rated pairs.','']
    (out/'SCREEN_RECOMPUTED.md').write_text('\n'.join(lines))
    print(json.dumps({'agreement':agreement,'source_rates':source_rates,'basic_all':next(r for r in rate_rows if r['dialect']=='all' and r['measure']=='basic'),'q2_unsure':meta['q2_unsure'],'double':meta['double_rated_basic']},indent=2))
if __name__=='__main__':main()
