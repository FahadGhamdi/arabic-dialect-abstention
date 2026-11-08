#!/bin/bash
P=/Users/fahad/Documents/Research-Projects/Arabic-Dialect-Abstention
echo "JOB START $(date) pid $$ : measurement robustness (Addendum 8: 500 keys x 7 x 4 orderings x 4 models + G1/G2 generation), under caffeinate" >> $P/logs/runner.log
/usr/bin/caffeinate -i -s /bin/bash $P/scripts/run_robust.sh
echo "JOB END $(date)" >> $P/logs/runner.log
