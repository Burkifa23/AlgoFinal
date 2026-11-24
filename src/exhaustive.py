from typing import List, NamedTuple, Optional


class CutPlan(NamedTuple):
    revenue: float
    piece_lengths: List[int]


def check_inputs(price_table, rod_length, cut_fee):
    if not isinstance(rod_length, int) or rod_length < 0:
        raise ValueError("rod_length must be a nonnegative integer")
    if cut_fee < 0:
        raise ValueError("cut_fee must be nonnegative")
    if len(price_table) < rod_length + 1:
        raise ValueError("price_table needs entries for lengths 0..rod_length (index 0 unused)")


def exhaustive_cut(price_table, rod_length: int, cut_fee: float = 0,
                   metrics: Optional[dict] = None) -> CutPlan:
    """Try every possible first piece, then recurse on what is left.
    O(2^n) calls, O(n) stack depth. price_table[i] is the price of length i."""
    check_inputs(price_table, rod_length, cut_fee)
    call_total = 0

    def best_cut(length_left: int):
        nonlocal call_total
        call_total += 1
        if length_left == 0:
            return 0, []
        # selling the whole piece uncut costs nothing extra
        top_revenue, top_pieces = price_table[length_left], [length_left]
        # otherwise cut off a piece of length i: one cut, so one fee
        for i in range(1, length_left):
            leftover_revenue, leftover_pieces = best_cut(length_left - i)
            trial_revenue = price_table[i] - cut_fee + leftover_revenue
            if trial_revenue > top_revenue:
                top_revenue, top_pieces = trial_revenue, [i] + leftover_pieces
        return top_revenue, top_pieces

    revenue, piece_lengths = best_cut(rod_length)
    if metrics is not None:
        metrics["calls"] = call_total
    return CutPlan(revenue, piece_lengths)