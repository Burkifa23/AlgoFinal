# AlgoFinal: Maximising Revenue from Cutting Material (Rod Cutting)

Group 14, CS456 Algorithm Design & Analysis, Ashesi University.

We solve the rod-cutting problem with exhaustive recursion, memoized and bottom-up
dynamic programming, a fixed cost per cut, a limit on the number of pieces, and a
greedy heuristic. The code, the tests, and the experiments behind the report are all
in this repository.

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) (recommended), or `pip`
- `matplotlib` (used only to draw the plots; the solvers use the standard library only)

## Setup

With uv (from the project root):

```
uv sync
```

Without uv:

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

If you are not using uv, drop the `uv run` prefix from every command below.

## Project layout

| Path | Contents |
|---|---|
| `src/exhaustive.py` | `exhaustive_cut`, plus the shared `CutPlan` result type and input checks |
| `src/dp_solvers.py` | `memoized_cut` and `tabulated_cut` (bottom-up), both with an optional cut fee |
| `src/dp_extensions.py` | `piece_limited_dp`: at most `k` pieces |
| `src/greedy.py` | `greedy_cut`: best price per unit length (not always optimal) |
| `tests/test_correctness.py` | 13 unit tests |
| `benchmarks/run_experiments.py` | runs every experiment and writes CSV files |
| `benchmarks/plot_results.py` | draws the figures from those CSV files |
| `benchmarks/results/` | the results used in the report |
| `doc/figures/` | the figures used in the report (PNG) |

## 1. Run the tests

```
uv run python -m unittest discover -s tests -v
```

Expected result: `Ran 13 tests ... OK` in under a second. The tests check:
- hand-verified textbook answers;
- edge cases (`n = 0`, `n = 1`, invalid inputs);
- about 550 comparisons of every exact solver against an independent brute force
  that lists all 2^(n-1) cuttings for `n <= 12`.

## 2. Reproduce the experiments

```
uv run python benchmarks/run_experiments.py
```

This takes a few minutes. It writes these files to `benchmarks/results/`:

| File | Experiment |
|---|---|
| `machine.txt` | Python version, OS, processor and date of the run |
| `exhaustive.csv` | exhaustive time and call count for n = 1, 2, ... until one run exceeds 2 s; larger n are predicted, not run |
| `dp.csv` | bottom-up and memoized DP times for n = 100 to 5000 (memoized only up to n = 2000) |
| `memo_limit.csv` | largest n memoized DP survives before a stack overflow (each size runs in a separate process) |
| `greedy.csv`, `greedy_worst.txt` | greedy revenue divided by the optimum, 200 random price lists per n, plus the worst case |
| `limits.csv` | largest n each method solves within 2 seconds |
| `cut_fee.csv` | effect of the cut fee on revenue, number of pieces and time (n = 1000) |
| `piece_limit.csv` | effect of the piece limit k on revenue (n = 200) |

All inputs come from seeded random generators, so every run uses the same price
lists. Running times depend on the machine and on its load, so your times will
differ, and the largest n values may shift. The growth rates (2^n for exhaustive,
n^2 for DP) should stay the same. The results in the report come from the run
recorded in `benchmarks/results/machine.txt`. **Re-running overwrites those files.**

## 3. Draw the plots

```
uv run python benchmarks/plot_results.py
```

This reads `benchmarks/results/` and saves three PNG files to `doc/figures/`:
- `exhaustive_time.png`: exhaustive time on a log scale, with the 2 s cutoff
- `dp_time.png`: bottom-up and memoized running time
- `dp_normalized.png`: DP time divided by n^2 (a flat line supports Θ(n^2))

## 4. Use the solvers in your own code

Run from the project root. The modules import each other by name, so add `src` to the path:

```python
import sys
sys.path.insert(0, "src")

from exhaustive import exhaustive_cut
from dp_solvers import memoized_cut, tabulated_cut
from dp_extensions import piece_limited_dp
from greedy import greedy_cut

prices = [0, 1, 5, 8, 9]        # prices[i] = price of length i; index 0 is unused

print(tabulated_cut(prices, 4))              # CutPlan(revenue=10, piece_lengths=[2, 2])
print(tabulated_cut(prices, 4, cut_fee=2))   # a fee per cut; an uncut rod pays nothing
print(greedy_cut(prices, 4))                 # CutPlan(revenue=9, piece_lengths=[3, 1]): not optimal
print(piece_limited_dp(4, prices[1:], 1))    # (9, [4]): note the argument order and prices[1:]
```

## Core solvers (`src/exhaustive.py`, `src/dp_solvers.py`)

### Inputs
- `price_table[i]` is the price of a piece of length `i`. Put 0 at index 0 so the indexing lines up. The table needs at least `rod_length + 1` entries.
- `rod_length` is the length of the rod, an integer that is 0 or more.
- `cut_fee` is the fixed cost of each cut and must be 0 or more. A rod sold in k pieces has k - 1 cuts, and a rod sold whole pays nothing.

### Functions
Each function returns `CutPlan(revenue, piece_lengths)`. The revenue is the total after cut fees.

| Function | File | Time | Space |
|---|---|---|---|
| `exhaustive_cut(price_table, rod_length, cut_fee=0, metrics=None)` | `exhaustive.py` | about 2^(n-1) calls | O(n) |
| `memoized_cut(price_table, rod_length, cut_fee=0, metrics=None)` | `dp_solvers.py` | O(n^2) | O(n) |
| `tabulated_cut(price_table, rod_length, cut_fee=0)` | `dp_solvers.py` | O(n^2) | O(n) |

### Notes
- If `metrics` is a dict, the number of recursive calls is stored in `metrics["calls"]`.
- When two choices give the same revenue, the solvers prefer selling the rod whole, then the smaller first piece. This makes all three return the same pieces.
- A `rod_length` of 0 returns revenue 0 and an empty list of pieces.
- A short `price_table`, a negative `rod_length` or a negative `cut_fee` raises `ValueError`.
- `exhaustive_cut` is only practical for small rods. Use the DP versions for large ones.
- `memoized_cut` recurses `n` levels deep. On our machine it crashed (stack overflow) above about n = 2100, so use `tabulated_cut` for large rods.

## Extensions (`src/dp_extensions.py`, `src/greedy.py`)

| Function | Returns | Time | Space |
|---|---|---|---|
| `piece_limited_dp(n, prices, k)` | `(revenue, pieces)`, or `(None, [])` if no plan fits | O(k·n^2) | O(k·n) |
| `greedy_cut(price_table, rod_length, cut_fee=0)` | `CutPlan` | O(n^2) | O(n) |

- `piece_limited_dp` takes **`n` first**, and its `prices` list starts at length 1 (`prices[i-1]` is the price of length `i`). Pass `price_table[1:]`.
- `greedy_cut` picks the piece with the highest price per unit length; ties keep the shorter piece. It is fast but **not always optimal**.
