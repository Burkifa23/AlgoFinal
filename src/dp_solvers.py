"""Dynamic programming solvers for the rod cutting problem: a memoized
top-down version and a bottom-up table version."""

import sys
from typing import List, Optional

from .exhaustive import CutPlan, check_inputs  # adjust to your package layout


def _rebuild_pieces(chosen_piece: List[int], rod_length: int) -> List[int]:
    """Follow chosen_piece from the full rod down to zero, collecting piece lengths."""
    pieces, length_left = [], rod_length
    while length_left > 0:
        pieces.append(chosen_piece[length_left])
        length_left -= chosen_piece[length_left]
    return pieces
    """Work backwards from the full rod using chosen_piece and collect the
    piece lengths."""


def memoized_cut(
    price_table, rod_length: int, cut_fee: float = 0, metrics: Optional[dict] = None
) -> CutPlan:
    """Top-down recursion with a cache. O(n^2) time, O(n) space."""
    check_inputs(price_table, rod_length, cut_fee)
    # recursion can go rod_length levels deep
    sys.setrecursionlimit(max(sys.getrecursionlimit(), rod_length + 100))

    cache = [None] * (rod_length + 1)
    chosen_piece = [0] * (rod_length + 1)
    cache[0] = 0
    call_total = 0

    def lookup(length_left: int):
        nonlocal call_total
        call_total += 1
        if cache[length_left] is not None:
            return cache[length_left]
        top_revenue, top_piece = price_table[length_left], length_left  # uncut: no fee
        for i in range(1, length_left):
            trial_revenue = (
                price_table[i] - cut_fee + lookup(length_left - i)
            )  # one cut: one fee
            if trial_revenue > top_revenue:
                top_revenue, top_piece = trial_revenue, i
        cache[length_left] = top_revenue
        chosen_piece[length_left] = top_piece
        return top_revenue

    revenue = lookup(rod_length)
    if metrics is not None:
        metrics["calls"] = call_total
    return CutPlan(revenue, _rebuild_pieces(chosen_piece, rod_length))
    """Same problem as exhaustive_cut, but each length is solved once and
    stored in a cache, so repeated subproblems are looked up instead of
    recomputed.

    Inputs and the returned CutPlan are the same as in exhaustive_cut. If
    metrics is a dict, metrics["calls"] gets the number of calls to lookup.

    Runs in O(n^2) time and O(n) space. The recursion can go as deep as
    rod_length, so the recursion limit is raised to fit.
    """


def tabulated_cut(price_table, rod_length: int, cut_fee: float = 0) -> CutPlan:
    """Bottom-up table, shortest lengths first. O(n^2) time, O(n) space."""
    check_inputs(price_table, rod_length, cut_fee)
    best_for_length = [0] * (rod_length + 1)
    chosen_piece = [0] * (rod_length + 1)

    for length_left in range(1, rod_length + 1):
        top_revenue, top_piece = price_table[length_left], length_left  # uncut: no fee
        for i in range(1, length_left):
            trial_revenue = price_table[i] - cut_fee + best_for_length[length_left - i]
            if trial_revenue > top_revenue:
                top_revenue, top_piece = trial_revenue, i
        best_for_length[length_left] = top_revenue
        chosen_piece[length_left] = top_piece

    return CutPlan(
        best_for_length[rod_length], _rebuild_pieces(chosen_piece, rod_length)
    )
    """Bottom-up version: fill in the best revenue for lengths 1, 2, 3, and
    so on up to rod_length, using the smaller answers already in the table.
    chosen_piece remembers the first piece picked for each length so the
    cuts can be recovered at the end.

    Inputs and the returned CutPlan are the same as in exhaustive_cut.

    Runs in O(n^2) time and O(n) space, with no recursion.
    """
