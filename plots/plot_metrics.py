import pandas as pd
import matplotlib.pyplot as plt

def plot_resource_usage(csv_file, function_name):
    # Load CSV data
    df = pd.read_csv(csv_file, parse_dates=['timestamp'])

    # Group by n_threads_used, and calculate mean and max usage per group
    summary = df.groupby('n_threads_used')[['cpu_percent', 'memory_percent']].agg(['mean', 'max'])

    # Plot CPU
    plt.figure(figsize=(10, 5))
    plt.plot(summary.index, summary['cpu_percent']['mean'], marker='o', label='CPU Mean %')
    plt.plot(summary.index, summary['cpu_percent']['max'], marker='x', label='CPU Max %')
    plt.xlabel('Number of Threads')
    plt.ylabel('CPU Usage (%)')
    plt.title(f'CPU Usage vs Threads for {function_name}')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f'outputs/{function_name}_cpu_vs_threads.png')
    plt.close()

    # Plot Memory
    plt.figure(figsize=(10, 5))
    plt.plot(summary.index, summary['memory_percent']['mean'], marker='o', color='orange', label='Memory Mean %')
    plt.plot(summary.index, summary['memory_percent']['max'], marker='x', color='red', label='Memory Max %')
    plt.xlabel('Number of Threads')
    plt.ylabel('Memory Usage (%)')
    plt.title(f'Memory Usage vs Threads for {function_name}')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f'outputs/{function_name}_mem_vs_threads.png')
    plt.close()

    print(f"Plots saved as outputs/{function_name}_cpu_vs_threads.png and outputs/{function_name}_mem_vs_threads.png")

if __name__ == "__main__":
    # Plot for prime
    plot_resource_usage('outputs/prime.csv', 'prime')
    # Plot for fibonacci
    plot_resource_usage('outputs/fibonacci.csv', 'fibonacci')
