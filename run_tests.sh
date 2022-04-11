#!/bin/bash
set -e

#pylint treasure_island
#coverage run -m pytest --disable-warnings

cov_result=$(coverage report -m)
cov_result=${cov_result##* }
cov_result=$(echo $cov_result | sed 's/.$//')
if (( $cov_result < 95 )); then
  echo 'Coverage fail.'
  exit 1
fi
