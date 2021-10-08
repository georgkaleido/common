#!/bin/bash
export DANNI_USER=$(cat ~/Documents/danni_auth_user.txt)
export DANNI_TOKEN=$(cat ~/Documents/danni_auth_token.txt)

BATCH=Carl
DATE=2021-08-16

python ../bin/danni_count_batch.py --batch=${BATCH} --date=${DATE}
