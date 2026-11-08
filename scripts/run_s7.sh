#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export ADA_DATA=$P/data; export ADA_RES=$P/results
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P; echo "START $(date)" > $P/logs/s7.log
$PY -c "import pandas as pd; d=pd.read_parquet('$P/data/damm.parquet'); d['choices']=d['choices'].apply(lambda c:'|||'.join(list(c))); d.to_csv('$P/data/damm.csv',index=False); print('csv ok')" >> $P/logs/s7.log 2>&1
$PY -u scripts/s4_analyze.py > $P/logs/s4_all.log 2>&1
$PY -u scripts/s5_flips.py > $P/logs/s5_all.log 2>&1
$PY -u scripts/s5b_churn.py > $P/logs/s5b_all.log 2>&1
$PY -u scripts/s7_internals_analysis.py >> $P/logs/s7.log 2>&1; echo "EXIT $? $(date)" >> $P/logs/s7.log
bash /Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention/scripts/run_s8.sh
