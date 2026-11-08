#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
export HF_HOME=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.cache/huggingface
export ADA_DATA=$P/data; export ADA_RES=$P/results
export TOKENIZERS_PARALLELISM=false; export PYTORCH_ENABLE_MPS_FALLBACK=1
PY=/Users/fahad/Documents/Research-Projects/CS-MDPI-Paper/.venv/bin/python
cd $P
echo "START stageA full $(date)" > $P/logs/stageA.log
ADA_B=1000 $PY -u scripts/stageA_measure.py >> $P/logs/stageA.log 2>&1; echo "EXIT $? $(date)" >> $P/logs/stageA.log
echo "START s6 fanar/qwen $(date)" > $P/logs/s6b.log
ADA_LENS=0 ADA_BS=2 ADA_MODELS=QCRI/Fanar-1-9B,Qwen/Qwen3-8B-Base $PY -u scripts/s6_internals.py >> $P/logs/s6b.log 2>&1; echo "EXIT $? $(date)" >> $P/logs/s6b.log
echo "START stageB $(date)" > $P/logs/stageB.log
for M in Fanar-1-9B Qwen3-8B-Base; do
  L=$( [ "$M" = "Fanar-1-9B" ] && echo 40 || echo 34 )
  $PY -u scripts/stageB_router.py $M $L 0:10 >> $P/logs/stageB.log 2>&1
done
$PY -u scripts/stageB_router.py ALLaM-7B-Instruct-preview 31 10:30 >> $P/logs/stageB.log 2>&1
echo "EXIT $? $(date)" >> $P/logs/stageB.log
