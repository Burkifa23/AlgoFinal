# AlgoFinal

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

### Usage
Run from the project root:

```python
from src.exhaustive import exhaustive_cut
from src.dp_solvers import memoized_cut, tabulated_cut

plan = tabulated_cut([0, 1, 5, 8, 9], 4, 0)
print(plan.revenue, plan.piece_lengths)   # 10 [2, 2]
```