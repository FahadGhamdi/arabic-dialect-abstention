#!/bin/bash
# second mending pass: larger scales at the decision layers, with reverse control; last-position and all-position variants
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P; echo "START $(date)" > $P/logs/s8b.log
ADA_MEND_POS=last ADA_MEND_DIALS=MAG,SYR ADA_MEND_LAYERS=27,28,29 ADA_MEND_SCALES=4.0,8.0 ADA_MEND_CONDS=mend,reverse,random $PY -u scripts/s8_mend.py >> $P/logs/s8b.log 2>&1
echo "--- POS=all ---" >> $P/logs/s8b.log
ADA_MEND_POS=all ADA_MEND_DIALS=MAG,SYR ADA_MEND_LAYERS=27,28 ADA_MEND_SCALES=1.0,3.0 ADA_MEND_CONDS=mend,random $PY -u scripts/s8_mend.py >> $P/logs/s8b.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/s8b.log
