#!/usr/bin/env python3
"""Replay the stored-score analyses in a new directory, preserving the archive.

No model inference. --text-input points to the private damm.csv produced by
prepare_damm_texts.py. Report-only portability adaptations are recorded.
Optional --plots needs matplotlib; statistics do not. Nothing is installed.
"""
from pathlib import Path
import argparse,subprocess,sys,os,shutil,json,time,difflib,importlib.util
import pandas as pd

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repository',type=Path,required=True)
    ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--text-input',type=Path,required=True)
    ap.add_argument('--plots',action='store_true');a=ap.parse_args()
    src=a.repository.resolve();work=a.work_dir.resolve()
    if work.exists():raise SystemExit('Use a new, non-existent work directory.')
    if a.plots and not importlib.util.find_spec('matplotlib'):
        raise SystemExit('--plots requires an existing matplotlib installation.')
    assert a.text_input.is_file()
    work.mkdir(parents=True)
    for folder in ['scripts','data','audit','results','docs']:
        shutil.copytree(src/folder,work/folder)
    shutil.copy2(a.text_input,work/'data/damm.csv')
    (work/'audit_in').mkdir()
    pd.read_csv(src/'audit/screen_flags_400.csv').set_index(['key','d']).to_pickle(work/'audit_in/flags.pkl')
    patches=[]
    def adapt(name,fn):
        p=work/'scripts'/name;old=p.read_text();new=fn(old);p.write_text(new)
        patches.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='archived/'+name,tofile='replay/'+name))
    adapt('indep_check/recompute.py',lambda s:s.replace('ROOT = "/home/claude/ada"','ROOT = '+repr(str(work))))
    if not importlib.util.find_spec('tabulate'):
        adapt('validity_analyze.py',lambda s:s.replace('.to_markdown()','.to_string()'))
    if not a.plots:
        # Statistics are written before the plotting block. Preserve report output.
        def without_plot(s):
            start=s.index('# ---------- D5 figure:')
            tail=s.index('open(os.path.join(OUT,"DIAG_REPORT.md")',start)
            return s[:start]+s[tail:]
        adapt('diag_analyze.py',without_plot)
    (work/'portability_adapters.diff').write_text(''.join(patches))
    logs=work/'replay_logs';logs.mkdir();records=[]
    jobs=[['confirm_analyze.py'],['validity_analyze.py','all'],['diag_analyze.py'],
          ['robust_analyze.py'],['sens_analyze.py'],['supp_analyze.py'],['indep_check/recompute.py']]
    if a.plots:jobs.append(['make_figures.py'])
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','ADA_RES':str(work/'results'),'ADA_DATA':str(work/'data')}
    for job in jobs:
        start=time.time()
        with (logs/(job[0].replace('/','_')+'.log')).open('w') as out:
            p=subprocess.run([sys.executable,str(work/'scripts'/job[0]),*job[1:]],cwd=work,env=env,stdout=out,stderr=subprocess.STDOUT)
        rec={'script':job[0],'returncode':p.returncode,'seconds':round(time.time()-start,2)}
        records.append(rec);print(rec,flush=True)
        (work/'REPLAY_RUN.json').write_text(json.dumps({'jobs':records,'plots_regenerated':a.plots,'model_inference':False},indent=2)+'\n')
        if p.returncode:raise SystemExit('Replay failed; inspect '+str(logs))
    # New screening reconstruction is separate from the frozen historical scripts.
    ratings=work/'results/audit_recomputed'
    for tool,args in [('audit_screen.py',[]),('audit_sensitivity.py',['--repository',str(work)])]:
        subprocess.run([sys.executable,str(src/'tools'/tool),'--ratings-dir',str(ratings),*args],check=True,env=env)
    print('Finished. Compare results with the archive; do not assume byte identity across environments.')

if __name__=='__main__':main()
