#!/usr/bin/env python3
"""Render existing R2 aggregates with PGFPlots. Requires an existing TeX installation."""
from pathlib import Path
import csv,json,hashlib,subprocess,shutil,tempfile
ROOT=Path(__file__).resolve().parents[1]
data=ROOT/'supplementary/frozen/results/robust/R2_gap_stability.csv'
rows=list(csv.DictReader(data.open()))
models=[('ALLaM','ALLaM-7B-Instruct-preview'),('Fanar','Fanar-1-9B'),
        ('Qwen3','Qwen3-8B-Base'),('Gemma','gemma-2-9b')]
dialects=['MAG','SYR','EGY','KSA','UAE']
colors=['F24A46','FD743C','2878D7','258B24','6B52CE']
tex=[r'\documentclass[border=3pt]{standalone}',r'\usepackage{pgfplots}',
     r'\usepgfplotslibrary{groupplots}',r'\usetikzlibrary{calc}',r'\pgfplotsset{compat=1.18}',
     r'\begin{document}',r'\begin{tikzpicture}']
for k,c in enumerate(colors):tex.append(r'\definecolor{dial'+str(k)+'}{HTML}{'+c+'}')
tex += [r'\begin{groupplot}[group style={group size=2 by 2,horizontal sep=1.05cm,vertical sep=1.65cm},',
        r'width=6.35cm,height=4.7cm,scale only axis=false,',
        r'xmin=-.345,xmax=.02,ymin=-.4,ymax=4.5,xtick={-.3,-.2,-.1,0},',
        r'ytick={0,1,2,3,4},yticklabels={UAE,KSA,EGY,SYR,MAG},',
        r'axis lines=left,axis line style={gray},tick style={gray},grid=major,grid style={gray!20},',
        r'tick label style={font=\sffamily\small},title style={font=\sffamily\bfseries},',
        r'xticklabel style={/pgf/number format/fixed,/pgf/number format/precision=1}]']
shown=[]
for short,model in models:
    tex += [r'\nextgroupplot[title={'+short+'}]',
            r'\addplot[gray,dashed,forget plot] coordinates {(0,-.4) (0,4.5)};']
    for k,(y,var) in enumerate(zip(range(4,-1,-1),dialects)):
        r=next(r for r in rows if r['model']==model and r['variety']==var)
        mean,lo,hi=[float(r[k]) for k in ['d_p1_avg','d_p1_lo','d_p1_hi']]
        orders=[float(r[f'd_p1_k{i}']) for i in range(4)]
        tex.append(r'\addplot[dial'+str(k)+',line width=.8pt] coordinates {'+f'({lo:.12f},{y}) ({hi:.12f},{y})'+'};')
        tex.append(r'\addplot[only marks,mark=o,mark size=2.1pt,line width=.8pt,mark options={fill=white},dial'+str(k)+
                   '] coordinates {'+f'({mean:.12f},{y})'+'};')
        for x in orders:
            tex.append(r'\addplot[dial'+str(k)+',line width=.8pt] coordinates {'+f'({x:.12f},{y+.10}) ({x:.12f},{y+.28})'+'};')
        shown.append({'model':model,'variety':var,'mean':mean,'lo':lo,'hi':hi,'rotations':orders})
tex += [r'\end{groupplot}',
        r'\node[font=\sffamily\small,anchor=north,yshift=-22pt] at ($(group c1r2.south)!0.5!(group c2r2.south)$) {$\Delta$P1 (dialect $-$ MSA), 500 keys};',
        r'\node[font=\sffamily\footnotesize,anchor=north,yshift=-42pt] at ($(group c1r2.south)!0.5!(group c2r2.south)$) {$|$\quad Each of the four option rotations};',
        r'\node[font=\sffamily\footnotesize,anchor=north,yshift=-57pt] at ($(group c1r2.south)!0.5!(group c2r2.south)$) {$-\!\circ\!-$\quad Order-averaged difference with 95\% key-bootstrap interval};',
        r'\end{tikzpicture}',r'\end{document}']
path=ROOT/'figures/figB_rotations.tex';path.write_text('\n'.join(tex)+'\n')
compiler=shutil.which('pdflatex') or '/Library/TeX/texbin/pdflatex'
with tempfile.TemporaryDirectory(prefix='rotation_',dir=ROOT/'generated') as td:
    result=subprocess.run([compiler,'-interaction=nonstopmode','-halt-on-error','-output-directory='+td,str(path)],
                          cwd=ROOT,capture_output=True,text=True)
    if result.returncode:raise SystemExit(result.stdout[-3000:])
    shutil.copy2(Path(td)/'figB_rotations.pdf',ROOT/'figures/figB_rotations.pdf')
(ROOT/'generated/rotation_figure_provenance.json').write_text(json.dumps({
 'source':str(data.relative_to(ROOT)),'source_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),
 'figure_sha256':hashlib.sha256((ROOT/'figures/figB_rotations.pdf').read_bytes()).hexdigest(),
 'displayed_values':shown},indent=2)+'\n')
print('Rendered 20 existing estimates and 80 rotation ticks in four separated panels.')
