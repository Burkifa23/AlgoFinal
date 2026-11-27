# visualize the benchmarks results in figures

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=os.path.dirname(os.path.abspath(__file__))
RESULTS=os.path.join(HERE,"results")
FIGURES=os.path.join(HERE,"..","doc", "figures")

BLUE="#2a78d6"
ORANGE="#eb6834"
GREY="#8a8981"

CUTOFF_S=2.0

plt.rcParams.update({
    "figure.figsize": (4.2,2.9),
    "font.size":9,
    "axes.spines.top":False,
    "axes.spines.right":False,
    "axes.grid": True,
    "grid.color": "#e4e3df",
    "lines.linewidth": 2,
    "lines.markersize": 4.5,
    "legend.frameon": False,
    "savefig.bbox": "tight",
})

def load(name):
    with open(os.path.join(RESULTS, name)) as f:
        return list(csv.DictReader(f))

def save(fig, name):
    fig.savefig(os.path.join(FIGURES, f"{name}.png"),dpi=300)
    plt.close(fig)
    print(f"\tsaved {name}.png")

def plot_exhaustive():
    rows=load("exhaustive.csv")
    measured=[r for r in rows if r["kind"]=="measured"]
    predicted=[r for r in rows if r["kind"]=="predicted"]

    fig, ax = plt.subplots()
    ax.semilogy([int(r["n"]) for r in measured], [float(r["seconds"]) for r in measured], marker="o", color=BLUE, label="measured")

    # dashed lines at the last measured point
    tail =measured[-1:] + predicted
    ax.semilogy([int(r["n"]) for r in tail], [float(r["seconds"]) for r in tail], "--", color=GREY, label=r"predicted, $\propto 2^{n-1}$")
    ax.axhline(CUTOFF_S, color=ORANGE, lw=1,ls=":", label="2 sec cutoff")

    ax.set_xlabel("rod length $n$")
    ax.set_ylabel("time (sec, log scale)")
    ax.set_title("Exhaustive recursion: running time grows as $2^{n}$")
    ax.legend()
    save(fig, "exhaustive_time")

def plot_dp():
    rows=load("dp.csv")
    n=[int(r["n"]) for r in rows]
    bottom_up= [float(r["bottomup_seconds"]) for r in rows]
    memo_rows=[r for r in rows if r["memo_seconds"] != ""]
    memo_n=[int(r["n"]) for r in memo_rows]
    memo= [float(r["memo_seconds"]) for r in memo_rows]


    # running time
    fig, ax = plt.subplots()
    ax.plot(n, bottom_up, marker="o", color=BLUE, label="bottom-up")
    ax.plot(memo_n, memo, marker="s", color=ORANGE, label="memoized")
    ax.set_xlabel("rod length $n$")
    ax.set_ylabel("time (sec)")
    ax.set_title("Bottom-up vs memoized DP: running time")
    ax.legend()
    save(fig, "dp_time")

    #time/n^2-> flat if θ(n^2) holds
    fig, ax=plt.subplots()
    ax.plot(n, [t/x**2*1e9 for t, x in zip(bottom_up, n)], marker="o", color=BLUE,label="bottom-up")
    ax.plot(memo_n, [t/x**2*1e9 for t, x in zip(memo, memo_n)], marker="s", color=ORANGE,label="memoized")
    ax.set_xlabel("rod length $n$")
    ax.set_ylabel(r"time/$n^2$ (ns)")
    ax.set_ylim(bottom=0)
    ax.set_title(r"DP running time divided by $n^2$")
    ax.legend()
    save(fig, "dp_normalized")

def main():
    os.makedirs(FIGURES, exist_ok=True)
    plot_exhaustive()
    plot_dp()

if __name__ == "__main__":
        main()
