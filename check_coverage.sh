#!/bin/bash
set -e

cov_result=$(coverage report -m)
cov_result=${cov_result##* }
cov_result=$(echo "$cov_result" | sed 's/.$//')
if (( "$cov_result" < 95 )); then
  echo 'Coverage fail with current value of' "$cov_result"%
  exit 1
else
  echo 'Coverage check OK with value of' "$cov_result"%
fi