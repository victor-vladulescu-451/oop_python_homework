#!/bin/bash

# Purpose:
# Orchestrates both resource monitoring and stress testing for a single math function (prime or fibonacci).
# Starts the resource monitor in the background, which logs CPU and memory usage to a CSV file.
# Runs the sweep of stress tests for the specified function (prime or fibonacci), from 2 to 16 concurrent requests.
# Ensures each run is labeled with function name and thread count.
# Stops the monitor and saves all collected resource metrics once the sweep is complete.
# Usage:

# ./run_with_monitoring.sh prime
# # or
# ./run_with_monitoring.sh fibonacci

FUNCTION=$1
VALUE=500000
CONTEXT="outputs/context.txt"

if [[ -z "$FUNCTION" ]]; then
  echo "Usage: $0 <function>"
  exit 1
fi

# Start the monitor in the background, passing FUNCTION as an environment variable
FUNCTION_RAN=$FUNCTION python3 utils/monitoring/resource_monitor.py &
MONITOR_PID=$!

echo "Started resource monitor with PID $MONITOR_PID for function $FUNCTION"

for THREADS in $(seq 2 16)
do
    # Update context file before each test
    echo "{\"function_ran\": \"${FUNCTION}\", \"n_threads_used\": $THREADS}" > $CONTEXT

    echo "Running $THREADS concurrent requests for $FUNCTION (value=$VALUE)..."
    ./stress_test.sh $THREADS $FUNCTION $VALUE
    echo "Sleeping 5 seconds to let system stabilize..."
    sleep 5
done

# When the sweep finishes, stop the monitor
echo "Stopping resource monitor..."
kill $MONITOR_PID
wait $MONITOR_PID

echo "All tests and monitoring for $FUNCTION completed!"
