#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data
export TOKENIZERS_PARALLELISM=false
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P
echo "START $(date)" > $P/logs/s1.log
$PY -u scripts/s1_data.py >> $P/logs/s1.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/s1.log
