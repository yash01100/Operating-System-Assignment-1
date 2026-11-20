# Operating Systems Assignment: Multithreading, Synchronization and Deadlock

| | |
|---|---|
| **Name** | Yash Raj |
| **Roll No.** | 2401010008 |
| **Section** | D |
| **Course** | B.Tech CSE, K.R. Mangalam University |
| **Subject** | Operating Systems |

Python implementations (standard library only) of deadlock handling, the Banker's Algorithm, threading, race conditions, locks, semaphores and classical synchronization problems.

## Repository Structure

```
os-assignment/
├── README.md
├── q1_deadlock.py      # Deadlock handling and Banker's Algorithm
├── q2_threads.py       # Thread creation, models and benefits
├── q3_race.py          # Race condition, Lock and Semaphore
├── q4_classic.py       # Producer-Consumer, Readers-Writers, Dining Philosophers
├── outputs/            # Captured program output for each question
└── reports/            # Submitted Word reports (code + output + discussion)
```

## Requirements

- Python 3.8 or newer (developed and tested on Python 3.12)
- No external libraries needed

## How to Run

```bash
python q1_deadlock.py
python q1_deadlock.py --interactive   # enter your own Allocation, Maximum and Available data
python q2_threads.py
python q3_race.py
python q4_classic.py
```

## Question Summary

### Q1. Deadlock Handling and Banker's Algorithm
- Controlled circular wait between two threads using locks (a Barrier guarantees both hold their first lock).
- Program never blocks permanently: `acquire(timeout=...)` detects the stall and the victim thread releases its lock.
- Identifies the four Coffman conditions: mutual exclusion, hold and wait, no preemption, circular wait.
- **Prevention:** resource ordering (always lock `R_A` before `R_B`).
- **Banker's Algorithm:** takes Allocation, Maximum and Available data, computes the Need matrix, runs the safety algorithm and prints the safe sequence (`P1 -> P3 -> P4 -> P0 -> P2` for the test data) or reports an unsafe state.
- **Detection and recovery:** detection algorithm on Allocation and Request matrices, then recovery by terminating a victim process and releasing its resources.

### Q2. Thread Creation, Models and Benefits
- Single-threaded baseline versus one worker thread per task, with thread names, identifiers and progress printed.
- Same workload for both versions, timed with `time.perf_counter()`.
- Sample result: I/O-bound workload about **8x** faster with threads, CPU-bound workload about **1.1x** (limited by the Python GIL).
- Report covers user-level vs kernel-level threads and the many-to-one, one-to-one and many-to-many models.

### Q3. Race Condition, Lock and Semaphore
- Shared counter updated by 4 threads without protection, showing lost updates that change from run to run.
- Fixed using `threading.Lock` and a binary `threading.Semaphore(1)`.
- All three versions use the same workload and are timed and compared for correctness and synchronization overhead.
- A `time.sleep(0)` yield inside the read-modify-write step is used in every version to make the timing-dependent bug reliably visible.

### Q4. Classical Synchronization Problems
- **Producer-Consumer:** finite circular buffer using `empty` and `full` semaphores plus a mutex.
- **Readers-Writers:** reader count protected by a mutex, exclusive access for writers.
- **Dining Philosophers:** deadlock prevented in two ways, resource ordering and a waiter (`Semaphore(4)`).
- All loops are finite, so every program terminates normally, and the state of shared resources is printed at each step.

## Notes

- Timing values in the output change slightly on every run; the overall pattern stays the same.
- The programs are written for learning, so they print a lot of trace output.

## Author

**Yash Raj** (Roll No. 2401010008), B.Tech CSE, K.R. Mangalam University
