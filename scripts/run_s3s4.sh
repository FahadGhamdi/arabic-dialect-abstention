#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
export ADA_NQ=${ADA_NQ:-500}; export ADA_BS=${ADA_BS:-8}
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P
echo "START $(date)" > $P/logs/s3.log
$PY -u scripts/s3_score.py >> $P/logs/s3.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/s3.log
echo "START $(date)" > $P/logs/s4.log
$PY -u scripts/s4_analyze.py >> $P/logs/s4.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/s4.log
