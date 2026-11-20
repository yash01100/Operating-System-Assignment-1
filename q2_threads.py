"""
Q2. Thread Creation, Models and Benefits
Name: Yash Raj | Roll No: 2401010008
"""
import threading
import time

PRINT = threading.Lock()
def log(msg):
    with PRINT:
        print(msg, flush=True)

NUM_TASKS = 8          # independent tasks (Task 2)
CPU_N     = 1_500_000  # loop size for the CPU part of each task
IO_DELAY  = 0.25       # seconds, simulates disk / network wait

def task(task_id, mode, verbose=True):
    """One independent unit of work."""
    if verbose:
        t = threading.current_thread()
        log(f"  Task {task_id} START  | thread={t.name:<9} ident={t.ident}")
    if mode in ("cpu", "mixed"):
        total = 0
        for i in range(CPU_N):
            total += i * i % 7
    if mode in ("io", "mixed"):
        time.sleep(IO_DELAY)
    if verbose:
        log(f"  Task {task_id} FINISH | thread={t.name}")

# ---- Task 1: single-threaded baseline -------------------------------
def run_single(mode):
    start = time.perf_counter()
    for i in range(1, NUM_TASKS + 1):
        task(i, mode)
    return time.perf_counter() - start

# ---- Task 3, 4, 5: multiple worker threads --------------------------
def run_multi(mode, workers=NUM_TASKS):
    threads = [threading.Thread(target=task, args=(i, mode), name=f"Worker-{i}")
               for i in range(1, NUM_TASKS + 1)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:          # wait for all workers to complete
        t.join()
    return time.perf_counter() - start

def experiment(title, mode):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(f"Workload: {NUM_TASKS} identical tasks, mode='{mode}'")
    print("\n--- Single-threaded (main thread only) ---")
    t_single = run_single(mode)
    print(f"Single-threaded time : {t_single:.3f} s")
    print("\n--- Multithreaded (one worker thread per task) ---")
    t_multi = run_multi(mode)
    print(f"Multithreaded time   : {t_multi:.3f} s")
    return t_single, t_multi

def main():
    print(f"Main thread: {threading.current_thread().name}, "
          f"active threads at start: {threading.active_count()}")
    results = {}
    results["I/O-bound"]  = experiment("EXPERIMENT 1: I/O-BOUND WORKLOAD (sleep simulates waiting)", "io")
    results["CPU-bound"]  = experiment("EXPERIMENT 2: CPU-BOUND WORKLOAD (pure Python loops)", "cpu")

    print("\n" + "=" * 70)
    print("COMPARISON (same workload for both versions)")
    print("=" * 70)
    print(f"{'Workload':<12}{'Single (s)':>12}{'Multi (s)':>12}{'Speed-up':>12}")
    for k, (s, m) in results.items():
        print(f"{k:<12}{s:>12.3f}{m:>12.3f}{s / m:>11.2f}x")

if __name__ == "__main__":
    main()
