#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
export ADA_NQ=500; export ADA_BS=1; export ADA_MODELS=google/gemma-2-9b
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
bash $P/scripts/run_s8b.sh
cd $P; echo "START $(date)" > $P/logs/s3_gemma_resume.log
$PY -u scripts/s3_score.py >> $P/logs/s3_gemma_resume.log 2>&1; echo "EXIT $? $(date)" >> $P/logs/s3_gemma_resume.log
$PY -u scripts/s4_analyze.py > $P/logs/s4_all.log 2>&1
$PY -u scripts/s5_flips.py > $P/logs/s5_all.log 2>&1
$PY -u scripts/s5b_churn.py > $P/logs/s5b_all.log 2>&1
