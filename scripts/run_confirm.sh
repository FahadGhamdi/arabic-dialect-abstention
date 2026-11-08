#!/bin/bash
# Confirmatory scoring chain: each model is retried with a smaller batch size if the process is killed (MPS memory, exit 137).
# Output is resumable, so a retry continues where the previous attempt stopped.
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P
LOG=$P/logs/confirm.log
echo "START confirmatory scoring $(date)" >> $LOG
run_model () {  # $1 = HF id, $2.. = batch sizes to try in order
  M=$1; shift
  for B in "$@"; do
    echo "== $M BS=$B $(date)" >> $LOG
    ADA_BS=$B ADA_MODELS=$M $PY -u scripts/s9_score_confirm.py >> $LOG 2>&1
    RC=$?; echo "== $M BS=$B exit $RC $(date)" >> $LOG
    if grep -q "^${M#*/} DONE in\|^${M#*/} already complete" $LOG; then break; fi
  done
}
run_model ALLaM-AI/ALLaM-7B-Instruct-preview 8 4 2 1
run_model Qwen/Qwen3-8B-Base 8 4 2 1
run_model QCRI/Fanar-1-9B 4 2 1
run_model google/gemma-2-9b 4 2 1
echo "ALL MODELS FINISHED $(date)" >> $LOG
echo "EXIT $(date)" >> $LOG
