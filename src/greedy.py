from exhaustive import CutPlan, check_inputs


def greedy_cut(price_table, rod_length, cut_fee=0):
    """
    Greedy algorithm for the rod-cutting problem.

    Repeatedly selects the available piece with the highest price per unit length until the
    entire rod is used.

    Inputs:
        price_table: Selling prices for lengths 0 to n.
        rod_length: Total length of the rod.
        cut_fee: Cost charged for each physical cut.

    output:
        CutPlan: Contains the total revenue and selected piece lengths.
    """
    check_inputs(price_table, rod_length, cut_fee)

    pieces = []
    total_revenue = 0
    remaining_length = rod_length

    while remaining_length > 0:
        best_length = 1
        best_ratio = price_table[1]

        for length in range(1, remaining_length + 1):
            ratio = price_table[length] / length

            if ratio > best_ratio:
                best_ratio = ratio
                best_length = length

        pieces.append(best_length)
        total_revenue += price_table[best_length]
        remaining_length -= best_length

    total_cuts = max(0, len(pieces) - 1)
    total_revenue -= total_cuts * cut_fee

    return CutPlan(total_revenue, pieces)
