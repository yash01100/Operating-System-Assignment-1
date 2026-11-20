"""
Q4. Classical Synchronization Problems
Name: Yash Raj | Roll No: 2401010008
"""
import threading
import time
import random

random.seed(7)
PRINT = threading.Lock()
def log(msg):
    with PRINT:
        print(msg, flush=True)

# ======================================================================
# 1. PRODUCER-CONSUMER with a finite circular buffer
# ======================================================================
class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buf = [None] * size
        self.head = 0                           # next write position
        self.tail = 0                           # next read position
        self.empty = threading.Semaphore(size)  # counts free slots
        self.full = threading.Semaphore(0)      # counts filled slots
        self.mutex = threading.Lock()           # protects head/tail/buf

    def state(self):
        return "[" + " ".join("-" if x is None else str(x) for x in self.buf) + "]"

    def put(self, item, who):
        self.empty.acquire()                    # wait for a free slot
        with self.mutex:
            self.buf[self.head] = item
            self.head = (self.head + 1) % self.size
            log(f"  {who} produced {item:>2}  buffer={self.state()}")
        self.full.release()                     # signal: one more item

    def get(self, who):
        self.full.acquire()                     # wait for an item
        with self.mutex:
            item = self.buf[self.tail]
            self.buf[self.tail] = None
            self.tail = (self.tail + 1) % self.size
            log(f"  {who} consumed {item:>2}  buffer={self.state()}")
        self.empty.release()                    # signal: one more free slot
        return item

def producer_consumer():
    print("=" * 70)
    print("1. PRODUCER-CONSUMER (circular buffer size 4, 2 producers, 2 consumers)")
    print("=" * 70)
    buf = CircularBuffer(4)
    ITEMS = 5                                   # per producer / consumer (finite)

    def producer(pid):
        for k in range(ITEMS):
            buf.put(pid * 10 + k, f"Producer-{pid}")
            time.sleep(random.uniform(0.01, 0.05))

    def consumer(cid):
        for _ in range(ITEMS):
            buf.get(f"Consumer-{cid}")
            time.sleep(random.uniform(0.03, 0.08))

    ts = [threading.Thread(target=producer, args=(i,)) for i in (1, 2)] + \
         [threading.Thread(target=consumer, args=(i,)) for i in (1, 2)]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"  Final buffer = {buf.state()}  (all 10 items produced and consumed)\n")

# ======================================================================
# 2. READERS-WRITERS (reader count protected, writer exclusive)
# ======================================================================
def readers_writers():
    print("=" * 70)
    print("2. READERS-WRITERS (3 readers, 2 writers, finite iterations)")
    print("=" * 70)
    shared = {"data": 0}
    read_count = 0
    rc_mutex = threading.Lock()                 # protects read_count
    resource = threading.Lock()                 # exclusive access for writers

    def reader(rid):
        nonlocal read_count
        for _ in range(3):
            with rc_mutex:
                read_count += 1
                if read_count == 1:             # first reader locks out writers
                    resource.acquire()
                log(f"  Reader-{rid} ENTER  active_readers={read_count}")
            log(f"  Reader-{rid} READING data={shared['data']}")
            time.sleep(random.uniform(0.02, 0.05))
            with rc_mutex:
                read_count -= 1
                log(f"  Reader-{rid} EXIT   active_readers={read_count}")
                if read_count == 0:             # last reader lets writers in
                    resource.release()
            time.sleep(random.uniform(0.01, 0.04))

    def writer(wid):
        for _ in range(2):
            resource.acquire()
            log(f"  Writer-{wid} WRITING (exclusive access)")
            shared["data"] += 1
            time.sleep(random.uniform(0.03, 0.06))
            log(f"  Writer-{wid} DONE    data={shared['data']}")
            resource.release()
            time.sleep(random.uniform(0.02, 0.05))

    ts = [threading.Thread(target=reader, args=(i,)) for i in (1, 2, 3)] + \
         [threading.Thread(target=writer, args=(i,)) for i in (1, 2)]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"  Final shared data = {shared['data']} (2 writers x 2 writes = 4 expected)\n")

# ======================================================================
# 3. DINING PHILOSOPHERS (resource ordering and waiter)
# ======================================================================
def dining_philosophers(strategy):
    N, MEALS = 5, 3
    forks = [threading.Lock() for _ in range(N)]
    waiter = threading.Semaphore(N - 1)         # at most 4 philosophers may try
    fork_owner = [None] * N

    def fork_state():
        return "forks=" + "".join(str(o) if o is not None else "." for o in fork_owner)

    def philosopher(i):
        left, right = i, (i + 1) % N
        for meal in range(1, MEALS + 1):
            log(f"  P{i} THINKING")
            time.sleep(random.uniform(0.01, 0.04))

            if strategy == "ordering":
                first, second = min(left, right), max(left, right)   # global order
            else:
                first, second = left, right
                waiter.acquire()                                      # ask waiter

            forks[first].acquire();  fork_owner[first] = i
            log(f"  P{i} picked fork {first}   {fork_state()}")
            time.sleep(0.01)                    # widen the deadlock window
            forks[second].acquire(); fork_owner[second] = i
            log(f"  P{i} picked fork {second}  {fork_state()}")

            log(f"  P{i} EATING (meal {meal}/{MEALS})")
            time.sleep(random.uniform(0.01, 0.03))

            fork_owner[second] = None; forks[second].release()
            fork_owner[first] = None;  forks[first].release()
            if strategy == "waiter":
                waiter.release()
            log(f"  P{i} put down forks {first},{second}  {fork_state()}")

    ts = [threading.Thread(target=philosopher, args=(i,)) for i in range(N)]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"  All {N} philosophers finished {MEALS} meals each - no deadlock.\n")

def main():
    producer_consumer()
    readers_writers()
    print("=" * 70)
    print("3a. DINING PHILOSOPHERS - Resource ordering (lower-numbered fork first)")
    print("=" * 70)
    dining_philosophers("ordering")
    print("=" * 70)
    print("3b. DINING PHILOSOPHERS - Waiter mechanism (max 4 may sit at once)")
    print("=" * 70)
    dining_philosophers("waiter")

if __name__ == "__main__":
    main()
