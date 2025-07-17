import psutil
import time
import csv
from datetime import datetime, timezone
import signal
import sys
import os
import json

stop_flag = False

def handle_sigterm(signum, frame):
    global stop_flag
    stop_flag = True

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def read_context(context_file):
    try:
        with open(context_file, 'r') as f:
            data = json.load(f)
        return data.get("function_ran", ""), data.get("n_threads_used", 0)
    except Exception:
        return "", 0

def monitor_system_metrics(filename, context_file, interval=1):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fieldnames = ['timestamp', 'function_ran', 'n_threads_used', 'cpu_percent', 'memory_percent']
    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        while not stop_flag:
            now = datetime.now(timezone.utc).isoformat()
            cpu = int(round(psutil.cpu_percent()))
            mem = psutil.virtual_memory().percent
            function_ran, n_threads_used = read_context(context_file)
            writer.writerow({
                'timestamp': now,
                'function_ran': function_ran,
                'n_threads_used': n_threads_used,
                'cpu_percent': cpu,
                'memory_percent': mem
            })
            csvfile.flush()
            print(f"[{now}] Func: {function_ran}, Threads: {n_threads_used}, CPU: {cpu}%, MEM: {mem}%")
            time.sleep(interval)
    print("Monitoring stopped. Data saved.")

if __name__ == "__main__":
    # Get function name from the environment variable FUNCTION_RAN, or default to 'function'
    function_name = os.environ.get('FUNCTION_RAN', 'function')
    monitor_system_metrics(
        filename=f"outputs/{function_name}.csv",
        context_file="outputs/context.txt",
        interval=1
    )
