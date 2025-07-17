#!/bin/bash

# Usage: ./stress_test_sweep.sh

# Purpose:
# Runs stress tests for both prime and fibonacci API endpoints, varying the number of concurrent requests (threads) 
# from 2 to 16 for each function. This script does not handle resource monitoring—it only stresses the endpoints and helps evaluate server performance under different loads.

START_THREADS=2
END_THREADS=16
VALUE=500000

for FUNCTION in "prime" "fibonacci"
do
  echo "-----------------------------"
  echo "Function: $FUNCTION"
  echo "-----------------------------"
  for THREADS in $(seq $START_THREADS $END_THREADS)
  do
    echo "Running $THREADS concurrent requests for $FUNCTION (value=$VALUE)..."
    ./stress_test.sh $THREADS $FUNCTION $VALUE
    echo "Sleeping 5 seconds to let system stabilize..."
    sleep 5
  done
done

echo "ALL TESTS COMPLETED"
