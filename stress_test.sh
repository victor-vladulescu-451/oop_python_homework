#!/bin/bash
# Before using the script, get the JWT token from the login endpoint
# then in the terminal, run:
# export TOKEN=<your_jwt>

REQUESTS_AMOUNT=$1
FUNCTION=$2

if [[ "$FUNCTION" == "prime" ]]; then
  for ((i=1; i<=REQUESTS_AMOUNT; i++))
  do
    curl -s --header "Authorization: Bearer $TOKEN" "http://127.0.0.1:5000/prime?count=$3" > /dev/null &
  done
elif [[ "$FUNCTION" == "fibonacci" ]]; then
  for ((i=1; i<=REQUESTS_AMOUNT; i++))
  do
    curl -s --header "Authorization: Bearer $TOKEN" "http://127.0.0.1:5000/fibonacci?count=$3" > /dev/null &
  done
fi

wait
echo "All requests completed."
