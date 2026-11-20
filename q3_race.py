"""
Q3. Race Condition, Lock and Semaphore
Name: Yash Raj | Roll No: 2401010008
"""
import sys
import threading
import time

NUM_THREADS = 4
INCREMENTS  = 20_000
EXPECTED    = NUM_THREADS * INCREMENTS

# Force frequent thread switches so the timing-dependent bug is visible
sys.setswitchinterval(1e-6)

def yield_cpu():
    """Gives other threads a chance to run in the middle of read-modify-write.
    Used in ALL three versions so the workload stays identical."""
    time.sleep(0)

def run(worker_factory):
    """Run the same workload with a given worker; return (final_value, seconds)."""
    state = {"counter": 0}                      # shared data (Task 1)
    worker = worker_factory(state)
    threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
    start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    return state["counter"], time.perf_counter() - start

# ---- Version 1: UNPROTECTED (Task 2) --------------------------------
def unprotected(state):
    def work():
        for _ in range(INCREMENTS):
            temp = state["counter"]             # READ
            temp = temp + 1                     # MODIFY
            yield_cpu()
            state["counter"] = temp             # WRITE  (not atomic as a whole)
    return work

# ---- Version 2: LOCK (Task 5) ----------------------------------------
def with_lock(state):
    lock = threading.Lock()
    def work():
        for _ in range(INCREMENTS):
            with lock:                          # mutual exclusion
                temp = state["counter"]
                temp = temp + 1
                yield_cpu()
                state["counter"] = temp
    return work

# ---- Version 3: SEMAPHORE (Task 6) -----------------------------------
def with_semaphore(state):
    sem = threading.Semaphore(1)                # binary semaphore
    def work():
        for _ in range(INCREMENTS):
            sem.acquire()                       # wait / P
            temp = state["counter"]
            temp = temp + 1
            yield_cpu()
            state["counter"] = temp
            sem.release()                       # signal / V
    return work

def main():
    print(f"Threads = {NUM_THREADS}, increments per thread = {INCREMENTS}")
    print(f"Expected final value = {EXPECTED}\n")

    # Tasks 2, 3, 4: repeat unprotected runs
    print("=" * 66)
    print("UNPROTECTED VERSION - repeated 5 times (timing-dependent result)")
    print("=" * 66)
    print(f"{'Run':<6}{'Expected':>10}{'Actual':>10}{'Lost updates':>16}   Status")
    unprot_times = []
    for r in range(1, 6):
        val, secs = run(unprotected)
        unprot_times.append(secs)
        status = "CORRECT (lucky)" if val == EXPECTED else "RACE CONDITION"
        print(f"{r:<6}{EXPECTED:>10}{val:>10}{EXPECTED - val:>16}   {status}")

    print("\n" + "=" * 66)
    print("LOCK-BASED and SEMAPHORE-BASED VERSIONS - 5 runs each")
    print("=" * 66)
    lock_times, sem_times = [], []
    print(f"{'Run':<6}{'Lock result':>14}{'Semaphore result':>20}")
    for r in range(1, 6):
        lv, ls = run(with_lock)
        sv, ss = run(with_semaphore)
        lock_times.append(ls); sem_times.append(ss)
        ok = lambda v: f"{v} OK" if v == EXPECTED else f"{v} WRONG"
        print(f"{r:<6}{ok(lv):>14}{ok(sv):>20}")

    avg = lambda L: sum(L) / len(L)
    print("\n" + "=" * 66)
    print("COMPARISON (same workload, average of 5 runs)")
    print("=" * 66)
    print(f"{'Version':<16}{'Avg time (s)':>14}{'Correct?':>12}")
    print(f"{'Unprotected':<16}{avg(unprot_times):>14.3f}{'No':>12}")
    print(f"{'Lock':<16}{avg(lock_times):>14.3f}{'Yes':>12}")
    print(f"{'Semaphore':<16}{avg(sem_times):>14.3f}{'Yes':>12}")
    print(f"\nLock overhead vs unprotected      : {avg(lock_times) / avg(unprot_times):.2f}x")
    print(f"Semaphore overhead vs unprotected : {avg(sem_times) / avg(unprot_times):.2f}x")

if __name__ == "__main__":
    main()
