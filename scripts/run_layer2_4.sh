#!/bin/bash
# Automatic validity layers: (2) embedding fidelity covariate for all DAMM pairs; (4) AraDiCE cross-resource replication (pre-registered).
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P; LOG=$P/logs/layer24.log
echo "START layers 2+4 $(date)" >> $LOG
echo "== fidelity $(date)" >> $LOG
$PY -u scripts/s10_fidelity.py >> $LOG 2>&1; echo "== fidelity exit $? $(date)" >> $LOG
run_model () { M=$1; shift
  for B in "$@"; do
    echo "== aradice $M BS=$B $(date)" >> $LOG
    ADA_BS=$B ADA_MODELS=$M $PY -u scripts/s11_aradice_score.py >> $LOG 2>&1; echo "== aradice $M BS=$B exit $? $(date)" >> $LOG
    if grep -q "^${M#*/} DONE in\|^${M#*/} already complete" $LOG; then break; fi
  done; }
run_model ALLaM-AI/ALLaM-7B-Instruct-preview 8 4 2 1
run_model Qwen/Qwen3-8B-Base 8 4 2 1
run_model QCRI/Fanar-1-9B 4 2 1
run_model google/gemma-2-9b 4 2 1
echo "ALL LAYERS FINISHED $(date)" >> $LOG
