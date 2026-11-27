import csv
import os
import platform
import random
import statistics
import sys
import time
import subprocess



HERE =os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from exhaustive import exhaustive_cut
from dp_solvers import memoized_cut, tabulated_cut
from greedy import greedy_cut
from dp_extensions import piece_limited_dp


OUT = os.path.join(HERE, "results")

REPEATS=5

EXHAUSTIVE_CUTOFF_S=2.0
EXHAUSTIVE_MAX_N=30

DP_SIZES=[100,250,500,1000,2000,2500,4000,5000]
MEMO_SAFE_N =2000

GREEDY_SIZES=[5,10,20,50,100,200]
GREEDY_SEEDS=200
PATTERNS=["random","linear","concave","convex"]

TIME_LIMIT_S=2.0

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


def dp_experiment():
    # bottom-up time vs n memoized only where it is safe
    rows=[]
    for n in DP_SIZES:
        prices=prices_for(n, "random")
        bottom_up=timed(tabulated_cut, prices, n)
        memo=timed(memoized_cut,prices, n) if n <= MEMO_SAFE_N else ""
        rows.append([n,bottom_up,memo])
        memo_text=f"{memo:8.4f} sec" if memo != "" else "unsafe"
        print(f"\tdp n={n:5d} bottom-up={bottom_up:8.4f} sec memoized={memo_text}")
    write_csv("dp.csv",["n","bottomup_seconds","memo_seconds"],rows)

def memo_survives(n):
    # run memoized DP at size n in a subprocess

    code=("import sys;"
        "sys.path.insert(0,'src');"
        "from dp_solvers import memoized_cut;"
        f"memoized_cut([0]+[1]*{n}, {n})")
    result=subprocess.run([sys.executable, "-c", code],cwd=os.path.join(HERE,".."),capture_output=True)
    return result.returncode==0, result.returncode

def memo_limit_experiment():
    # largest n memoized DP survives by by binary search
    low=1000
    high=20000
    rows=[]
    while high-low>100:
        mid=(low+high)//2
        survived, exit_code=memo_survives(mid)
        rows.append([mid, survived, hex(exit_code)])
        print(f"\tmemoized n={mid:5d} survived={survived} exit={hex(exit_code)}")
        if survived:
            low=mid
        else:
            high=mid
    print(f"\tmemoized survives n={low}, crashes by n={high}")
    write_csv("memo_limit.csv", ["n", "survived", "exit_code"], rows)
    return low

def greedy_counterexample():
    # hand-checked case p=(1,5,8,9), n=4
    prices=[0,1,5,8,9]
    greedy=greedy_cut(prices,4)
    exact=tabulated_cut(prices,4)
    print(f"\tcounterexample: greedy{greedy.piece_lengths} = {greedy.revenue}, exact {exact.piece_lengths} = {exact.revenue}")

def greedy_experiment():
    # greedy revenue vs exact optimum, per price pattern
    summary= []
    worst =None

    for pattern in PATTERNS:
        # one instance is enough because fixed patterns give the same prices for every seed is enough
        seeds=range(GREEDY_SEEDS) if pattern == "random" else [0]

        for n in GREEDY_SIZES:
            ratios=[]
            failures=0
            for seed in seeds:
                prices =prices_for(n,pattern,seed)
                greedy=greedy_cut(prices,n)
                exact=tabulated_cut(prices,n)

                ratios.append(greedy.revenue/ exact.revenue)
                gap=exact.revenue-greedy.revenue
                if gap>0:
                    failures+=1
                if worst is None or gap> worst[0]:
                    worst=(gap,pattern,n,seed,greedy,exact)
            row=[pattern,n,len(ratios),statistics.mean(ratios), min(ratios), failures/len(ratios)]
            summary.append(row)
            print(f"\tgreedy {pattern:8s} n={n:3d} mean={row[3]:.4f} worst={row[4]:.4f} fail rate={row[5]:.0%}")
    write_csv("greedy.csv", ["pattern","n", "instances", "mean_ratio","worst_ratio", "fail_rate"], summary)

    gap,pattern,n,seed,greedy,exact= worst
    with open(os.path.join(OUT, "greedy_worst.txt"),"w")as f:
        f.write(f"largest gap: {gap} (pattern={pattern}, n={n} seed={seed})\n")
        f.write(f"greedy revenue {greedy.revenue}: {sorted(greedy.piece_lengths)}\n")
        f.write(f"exact revenue {exact.revenue}: {sorted(exact.piece_lengths)}\n")
    print(f"\tlargest gap {gap} at pattern={pattern}, n={n}, seed={seed}")


def one_run(function, *args, **kwargs):
    start=time.perf_counter()
    function(*args, **kwargs)
    return time.perf_counter()-start

def largest_n_within_limit(run, start_n, grow):
    # let n grow until one run exceeds 2 seconds.
    # then retyrn the largest finished in time
    n, last_ok =start_n, None
    while True:
        seconds=run(n)
        if seconds>TIME_LIMIT_S:
            return last_ok
        last_ok=(n, seconds)
        n=grow(n)

def limits_experiment(memo_limit):
    # largest n each method finishes within the 2 sec time limit
    def p(n):
        return prices_for(n,"random")

    # exhaustive n grows by 1
    by_one=lambda n:n+1
    # the rest grow by 25%
    by_25pct=lambda n:int(n*1.25)+1

    cases = [
        ("exhaustive", lambda n:one_run(exhaustive_cut, p(n), n), 10, by_one),
        ("bottom-up", lambda n:one_run(tabulated_cut,p(n), n), 1000, by_25pct),
        ("cut-cost c=1", lambda n:one_run(tabulated_cut,p(n),n, cut_fee=1), 1000, by_25pct),
        ("greedy", lambda n:one_run(greedy_cut,p(n), n), 1000, by_25pct),
        ("piece-limits k=1", lambda n:one_run(piece_limited_dp,n,p(n)[1:],1), 100, by_25pct),
        ("piece-limits k=5", lambda n:one_run(piece_limited_dp, n, p(n)[1:],5), 100, by_25pct),
        ("piece-limits k=20", lambda n:one_run(piece_limited_dp,n, p(n)[1:],20), 100, by_25pct),
        ("piece-limits k=n", lambda n:one_run(piece_limited_dp,n, p(n)[1:],n), 20, by_25pct)
    ]

    rows=[]
    for name, run, start_n, grow in cases:
        n, seconds=largest_n_within_limit(run, start_n,grow)
        rows.append([name,n,f"{seconds:.3f}", "time"])
        print(f"\t{name:18s} largest n ={n:5d} ({seconds:.3f} sec)")

    rows.append(["memoized", memo_limit, "", "stack overflow, not time"])
    print(f"\t{'memoized':18s} largest n ={memo_limit:5d} (stack limit)")
    write_csv("limits.csv", ["method", "largest_n", "seconds", "limited_by"],rows)

def main():
    os.makedirs(OUT, exist_ok=True)
    machine_info()
    exhaustive_experiment()
    dp_experiment()
    memo_limit=memo_limit_experiment()
    greedy_counterexample()
    greedy_experiment()
    limits_experiment(memo_limit)


if __name__=="__main__":
    main()
