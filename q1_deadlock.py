"""
Q1. Deadlock Handling and Banker's Algorithm
Name: Yash Raj | Roll No: 2401010008
"""
import threading
import time
import sys

PRINT = threading.Lock()
def log(msg):
    with PRINT:
        print(msg, flush=True)

# ----------------------------------------------------------------------
# PART A : Controlled circular wait (Tasks 1, 2, 3)
# ----------------------------------------------------------------------
def circular_wait_demo():
    print("\n" + "=" * 70)
    print("PART A: CONTROLLED CIRCULAR-WAIT SCENARIO (with timeout + recovery)")
    print("=" * 70)
    lock_a, lock_b = threading.Lock(), threading.Lock()
    both_hold_first = threading.Barrier(2)

    def worker(name, first, second, fname, sname, timeout):
        first.acquire()
        log(f"[{name}] acquired {fname}")
        both_hold_first.wait()          # guarantees the circular wait
        log(f"[{name}] holds {fname}, now requesting {sname} (timeout={timeout}s)")
        got = second.acquire(timeout=timeout)
        if got:
            log(f"[{name}] acquired {sname} -> work done")
            second.release()
        else:
            log(f"[{name}] TIMEOUT on {sname}: deadlock suspected -> "
                f"releasing {fname} (recovery by resource release)")
        first.release()
        log(f"[{name}] finished")

    # T1 uses a shorter timeout, so it becomes the 'victim'
    t1 = threading.Thread(target=worker, args=("T1", lock_a, lock_b, "R_A", "R_B", 1))
    t2 = threading.Thread(target=worker, args=("T2", lock_b, lock_a, "R_B", "R_A", 3))
    t1.start(); t2.start()
    t1.join(); t2.join()
    print("Program did NOT remain blocked: both threads finished.\n")

    print("Four necessary (Coffman) conditions in this scenario:")
    print(" 1. Mutual exclusion : R_A and R_B are Locks; only one thread can own each.")
    print(" 2. Hold and wait    : T1 holds R_A while waiting for R_B; T2 holds R_B while waiting for R_A.")
    print(" 3. No preemption    : A Lock cannot be forcibly taken from its owner.")
    print(" 4. Circular wait    : T1 -> R_B (held by T2) -> R_A (held by T1)  => cycle.")

# ----------------------------------------------------------------------
# PART B : Deadlock prevention using resource ordering (Task 4)
# ----------------------------------------------------------------------
def prevention_demo():
    print("\n" + "=" * 70)
    print("PART B: DEADLOCK PREVENTION USING RESOURCE ORDERING")
    print("=" * 70)
    print("Rule: every thread must acquire R_A (rank 1) before R_B (rank 2).")
    print("This breaks the CIRCULAR WAIT condition.\n")
    lock_a, lock_b = threading.Lock(), threading.Lock()

    def worker(name):
        with lock_a:
            log(f"[{name}] acquired R_A")
            time.sleep(0.2)
            with lock_b:
                log(f"[{name}] acquired R_B -> critical work")
                time.sleep(0.2)
            log(f"[{name}] released R_B")
        log(f"[{name}] released R_A")

    ts = [threading.Thread(target=worker, args=(f"T{i}",)) for i in (1, 2)]
    for t in ts: t.start()
    for t in ts: t.join()
    print("Both threads completed without deadlock.")

# ----------------------------------------------------------------------
# PART C : Banker's Algorithm (Tasks 5, 6, 7, 8)
# ----------------------------------------------------------------------
def read_matrix(prompt, rows, cols):
    print(prompt)
    return [list(map(int, input(f"  row {i}: ").split())) for i in range(rows)]

def show(title, M, names, res):
    print(f"\n{title}")
    print("      " + "  ".join(f"{r:>3}" for r in res))
    for n, row in zip(names, M):
        print(f"{n:>4}  " + "  ".join(f"{v:>3}" for v in row))

def bankers(alloc, maxm, avail, label=""):
    n, m = len(alloc), len(avail)
    names = [f"P{i}" for i in range(n)]
    res = [chr(65 + j) for j in range(m)]

    need = [[maxm[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]   # Task 6
    print("\n" + "-" * 70)
    print(f"BANKER'S ALGORITHM {label}")
    print("-" * 70)
    show("Allocation", alloc, names, res)
    show("Maximum", maxm, names, res)
    show("Need = Max - Allocation", need, names, res)
    print("\nAvailable:", dict(zip(res, avail)))

    work = avail[:]                      # Task 7: safety algorithm
    finish = [False] * n
    seq = []
    print("\nSafety algorithm trace:")
    while len(seq) < n:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                print(f"  {names[i]}: Need {need[i]} <= Work {work}  -> can finish; "
                      f"Work becomes ", end="")
                work = [work[j] + alloc[i][j] for j in range(m)]
                print(work)
                finish[i] = True
                seq.append(names[i])
                found = True
        if not found:
            break
    if len(seq) == n:                    # Task 8
        print("\nRESULT: SAFE STATE. Safe sequence: " + " -> ".join(seq))
    else:
        stuck = [names[i] for i in range(n) if not finish[i]]
        print("\nRESULT: UNSAFE STATE. Processes that cannot finish:", stuck)
    return len(seq) == n

# ----------------------------------------------------------------------
# PART D : Deadlock detection + recovery (Tasks 9, 10)
# ----------------------------------------------------------------------
def detect(alloc, request, avail):
    n, m = len(alloc), len(avail)
    work = avail[:]
    finish = [all(a == 0 for a in alloc[i]) for i in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if not finish[i] and all(request[i][j] <= work[j] for j in range(m)):
                work = [work[j] + alloc[i][j] for j in range(m)]
                finish[i] = True
                changed = True
    return [i for i in range(n) if not finish[i]]

def detection_and_recovery():
    print("\n" + "=" * 70)
    print("PART D: DEADLOCK DETECTION AND CONTROLLED RECOVERY")
    print("=" * 70)
    alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 3], [2, 1, 1], [0, 0, 2]]
    request = [[0, 0, 0], [2, 0, 2], [0, 0, 1], [1, 0, 0], [0, 0, 2]]
    avail = [0, 0, 0]
    names = [f"P{i}" for i in range(5)]
    res = ["A", "B", "C"]
    show("Allocation", alloc, names, res)
    show("Request (outstanding)", request, names, res)
    print("\nAvailable:", dict(zip(res, avail)))

    round_no = 1
    while True:
        dead = detect(alloc, request, avail)
        if not dead:
            print(f"\n[Round {round_no}] No deadlock. All remaining processes can finish.")
            break
        print(f"\n[Round {round_no}] DEADLOCK DETECTED among: {[names[i] for i in dead]}")
        victim = max(dead, key=lambda i: sum(alloc[i]))     # victim = holds most resources
        print(f"  Recovery: terminating victim {names[victim]} "
              f"(holds {alloc[victim]}), releasing its resources")
        avail = [avail[j] + alloc[victim][j] for j in range(3)]
        alloc[victim] = [0, 0, 0]
        request[victim] = [0, 0, 0]
        print(f"  Available after release: {dict(zip(res, avail))}")
        round_no += 1
    print("System recovered through process termination.")

# ----------------------------------------------------------------------
def main():
    circular_wait_demo()
    prevention_demo()

    print("\n" + "=" * 70)
    print("PART C: BANKER'S ALGORITHM")
    print("=" * 70)
    if "--interactive" in sys.argv:           # Task 5: accept input
        n = int(input("Number of processes: "))
        m = int(input("Number of resource types: "))
        alloc = read_matrix("Enter Allocation matrix:", n, m)
        maxm = read_matrix("Enter Maximum matrix:", n, m)
        avail = list(map(int, input("Enter Available vector: ").split()))
        bankers(alloc, maxm, avail, "(user input)")
    else:
        alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
        maxm = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
        bankers(alloc, maxm, [3, 3, 2], "- Test 1 (safe state)")
        alloc2 = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
        maxm2 = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
        bankers(alloc2, maxm2, [0, 0, 0], "- Test 2 (unsafe state, Available = 0 0 0)")

    detection_and_recovery()

if __name__ == "__main__":
    main()
