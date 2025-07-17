#!/bin/bash

REQUESTS_AMOUNT=$1
FUNCTION=$2

if [[ "$FUNCTION" == "prime" ]]; then
  for ((i=1; i<=REQUESTS_AMOUNT; i++))
  do
    curl -s "http://127.0.0.1:5000/prime?count=$3" > /dev/null &
  done
elif [[ "$FUNCTION" == "fibonacci" ]]; then
  for ((i=1; i<=REQUESTS_AMOUNT; i++))
  do
    curl -s "http://127.0.0.1:5000/fibonacci?count=$3" > /dev/null &
  done
fi

wait
echo "All requests completed."
