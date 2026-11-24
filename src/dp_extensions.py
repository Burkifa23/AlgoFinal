def piece_limited_dp(n, prices, k):
    """
    Find the maximum revenue obtainable from a rod of length n using at most k pieces.

    Inputs:
        n: Length of the original rod.
        prices: List where prices[i-1] is the price of a piece of length i.
        k: Maximum number of pieces allowed.

    Outputs:
        A tuple containing:
        - Maximum revenue
        - List of piece lengths used
    """

    # Invalid inputs
    if n < 0 or k < 0:
        raise ValueError("Rod length and piece limit must be nonnegative.")

    if len(prices) < n:
        raise ValueError("A price must be provided for every length.")

    if any(price < 0 for price in prices[:n]):
        raise ValueError("Prices must be nonnegative.")

    # dp[i][m] = maximum revenue for length i using at most m pieces
    dp = [[float("-inf")] * (k + 1) for _ in range(n + 1)]
    first_piece = [[None] * (k + 1) for _ in range(n + 1)]

    for m in range(k + 1):
        dp[0][m] = 0

    # Build the DP table
    for i in range(1, n + 1):
        for m in range(1, k + 1):
            for j in range(1, i + 1):
                remaining_length = i - j
                remaining_pieces = m - 1
                previous_revenue = dp[remaining_length][remaining_pieces]
                if previous_revenue == float("-inf"):
                    continue
                revenue = prices[j - 1] + previous_revenue
                if revenue > dp[i][m]:
                    dp[i][m] = revenue
                    first_piece[i][m] = j

    # Check whether a valid solution exists
    if dp[n][k] == float("-inf"):
        return None, []

    pieces = []
    remaining_length = n
    remaining_limit = k

    while remaining_length > 0:
        chosen_piece = first_piece[remaining_length][remaining_limit]
        if chosen_piece is None:
            return None, []
        pieces.append(chosen_piece)
        remaining_length -= chosen_piece
        remaining_limit -= 1

    return dp[n][k], pieces
