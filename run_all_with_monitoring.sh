#!/bin/bash

# Purpose:
# Main orchestrator that runs full monitoring-and-sweep cycles for both math functions sequentially.
# Calls run_with_monitoring.sh prime first, then waits 5 seconds.
# Calls run_with_monitoring.sh fibonacci next.
# Ensures that resource monitoring and stress testing are run for each function in isolation, generating separate CSV logs for each.

echo "=== Running PRIME sweep with monitoring ==="
./run_with_monitoring.sh prime

echo "Waiting 5 seconds before starting FIBONACCI sweep..."
sleep 5

echo "=== Running FIBONACCI sweep with monitoring ==="
./run_with_monitoring.sh fibonacci

echo "All stress tests and monitoring completed!"
