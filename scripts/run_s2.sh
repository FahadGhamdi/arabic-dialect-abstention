#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P
echo "START $(date)" > $P/logs/s2.log
$PY -u scripts/s2_damm.py >> $P/logs/s2.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/s2.log
