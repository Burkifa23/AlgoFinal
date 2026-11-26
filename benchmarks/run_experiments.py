import csv
import os
import platform
import random
import statistics
import sys
import time



HERE =os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from exhaustive import exhaustive_cut
from dp_solvers import memoized_cut, tabulated_cut
from greedy import greedy_cut

OUT = os.path.join(HERE, "results")
REPEATS=5

EXHAUSTIVE_CUTOFF_S=2.0
EXHAUSTIVE_MAX_N=30


def prices_for(n,pattern, seed=0):
    # price table for lengths 0 till n
    seeded_random= random.Random(f"{pattern}-{n}-{seed}")
    if pattern=="random":
        return [0] + [seeded_random.randint(1,5*i) for i in range(1, n+1)]

    # p_i=3i: Each way of  cutting earns the same total
    if pattern=="linear":
        return [0] + [3*i for i in range(1, n+1)]

    # long pieces earn less per unit resulting into more cuts
    if pattern=="concave":
        return [0]+ [round(10*i**0.5) for i in range(1, n+1)]

    # long pieces earn more per unit resulting into no cuts
    if pattern=="convex":
        return [0]+[i*i for i in range(1, n+1)]
    raise ValueError(f"unknown pattern {pattern}")

def machine_info():
    info=[
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"processor: {platform.processor()}",
        f"date: {time.strftime('%Y-%m-%d %H:%M')}"
    ]
    with open(os.path.join(OUT, "machine.txt"), "w") as f:
        f.write("\n".join(info)+"\n")
    print("\n".join(info))

def timed(function, *args, **kwargs):
    runs=[]
    for _ in range(REPEATS):
        start=time.perf_counter()
        function(*args, **kwargs)
        runs.append(time.perf_counter()-start)
    return statistics.median(runs)

def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), "w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"\tsaved {name} ({len(rows)} rows)")


def exhaustive_experiment():
    # item 1,2,3,5 exhuastive time and call count vs n, with a cutoff.
    rows=[]
    for n in range(1, EXHAUSTIVE_MAX_N+1):
        prices=prices_for(n,"random")

        # one run to count calls and check how slow this n is going to be
        counter={}
        start=time.perf_counter()
        exhaustive_cut(prices,n,metrics=counter)
        first_run=time.perf_counter()-start

        # fast runs are noisy
        # slow runs are stable
        #
        seconds=timed(exhaustive_cut,prices,n) if first_run<0.1 else first_run

        rows.append([n,seconds, counter["calls"], "measured"])
        print(f"\texhaustive n={n:2d} {seconds:9.5f} sec calls={counter['calls']}")

        if seconds>EXHAUSTIVE_CUTOFF_S:
            print(f"\tcutoff reached at n={n}")
            break

    last_n = rows[-1][0]
    last_seconds=rows[-1][1]
    last_calls =rows[-1][2]

    # predict time per call
    seconds_per_call=last_seconds/last_calls
    for n in range(last_n+1, EXHAUSTIVE_MAX_N+1):
        calls=2**(n-1)
        rows.append([n,seconds_per_call*calls,calls,"predicted"])

    write_csv("exhaustive.csv", ["n","seconds","calls","kind"], rows)

def main():
    os.makedirs(OUT, exist_ok=True)
    machine_info()
    exhaustive_experiment()


if __name__=="__main__":
    main()
