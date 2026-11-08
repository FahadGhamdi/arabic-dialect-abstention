#!/bin/bash
# Measurement robustness (ANALYSIS_PLAN Addendum 8): 500 test keys x 7 varieties x 4 option orderings, letter-logit scoring; G1 greedy
# generation (all models); G2 chat-template generation (ALLaM). Each model is retried with a smaller batch size if killed (exit 137);
# output is resumable so a retry continues where the previous attempt stopped.
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P; LOG=$P/logs/robust.log
echo "START robustness scoring $(date)" >> $LOG
run_model () { M=$1; shift
  for B in "$@"; do
    echo "== $M BS=$B $(date)" >> $LOG
    ADA_BS=$B ADA_GBS=$B ADA_MODELS=$M $PY -u scripts/s12_robustness.py >> $LOG 2>&1; echo "== $M BS=$B exit $? $(date)" >> $LOG
    if grep -q "^${M#*/} ROBUST DONE" $LOG; then break; fi
  done; }
run_model ALLaM-AI/ALLaM-7B-Instruct-preview 8 4 2 1
run_model Qwen/Qwen3-8B-Base 8 4 2 1
run_model QCRI/Fanar-1-9B 4 2 1
run_model google/gemma-2-9b 4 2 1
echo "ALL ROBUSTNESS FINISHED $(date)" >> $LOG
