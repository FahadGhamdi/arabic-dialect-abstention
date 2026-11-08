#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
echo "CHAIN START $(date) pid $$" >> $P/logs/runner.log
bash $P/scripts/run_s6.sh
bash $P/scripts/run_s7.sh
bash $P/scripts/run_gemma_resume.sh
echo "CHAIN END $(date)" >> $P/logs/runner.log
