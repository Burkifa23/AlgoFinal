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

def main():
    os.makedirs(OUT, exist_ok=True)
    machine_info()

    #test
    p=prices_for(10,"random")
    print("prices: ",p)
    print("bottom-up n=10 takes", timed(tabulated_cut,p,10),"s")

if __name__=="__main__":
    main()
