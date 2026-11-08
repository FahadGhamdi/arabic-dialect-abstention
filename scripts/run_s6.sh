#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
export ADA_MODELS=${ADA_MODELS:-ALLaM-AI/ALLaM-7B-Instruct-preview,QCRI/Fanar-1-9B}
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P
echo "START $(date)" > $P/logs/s6.log
$PY -u scripts/s6_internals.py >> $P/logs/s6.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/s6.log
