import os
import sys
import unittest
import random

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from exhaustive import exhaustive_cut
from dp_solvers import tabulated_cut, memoized_cut
from dp_extensions import piece_limited_dp
from greedy import greedy_cut


CLRS=[0,1,5,8,9,10,17,17,20,24,30]
# every exact  solvers
EXACT=[exhaustive_cut, memoized_cut, tabulated_cut]

def enumerate_all(prices, n, fee=0, max_pieces=None):
    # best revenue over all 2^(n-1) ways to cur without using any recurrece
    # return none if no cutting gits within max_pieces

    if n==0:
        return 0
    best=None
    for mask in range(2**(n-1)):
        pieces=[]
        start=0
        for position in range(1,n):
            # check for a cut at this position
            if (mask>>(position-1))&1:
                pieces.append(position-start)
                start=position
        # the last piece
        pieces.append(n-start)

        if max_pieces is not None and len(pieces)>max_pieces:
            continue
        revenue=sum(prices[p] for p in pieces)-fee*(len(pieces)-1)
        if best is None or revenue>best:
            best=revenue
    return best

def plan_value(prices, pieces, fee=0):
    # recompute a plan's revenue from its pieces
    return sum(prices[p] for p in pieces) - fee*max(0,len(pieces)-1)

def random_prices(n, seeded_random, pattern):
    if pattern=="random":
        return [0]+ [seeded_random.randint(0,5*i) for i in range(1, n+1)]
    if pattern=="linear":
        return [0]+ [3*i for i in range(1, n+1)]
    if pattern=="concave":
        return [0]+ [int(10*i**0.5) for i in range(1, n+1)]
    if pattern=="convex":
        return [0]+ [i*i for i in range(1, n+1)]
    raise ValueError(pattern)




class HandVerified(unittest.TestCase):
    # best revenue for n =4 (2+2)
    def test_clrs_n4(self):
        plan = tabulated_cut(CLRS,4)
        self.assertEqual(plan.revenue,10)

    def test_clrs_n5(self):
        # best revenue for n =5 (2+3)
        plan = tabulated_cut(CLRS,5)
        self.assertEqual(plan.revenue,13)
    def test_clrs_n7(self):
        # best revenue for n =7 (1+6) or 2+2+3
        plan = tabulated_cut(CLRS,7)
        self.assertEqual(plan.revenue,18)
    def test_clrs_n8(self):
        # best revenue for n =8 (2+6)
        plan = tabulated_cut(CLRS,8)
        self.assertEqual(plan.revenue,22)
    def test_clrs_n10(self):
        # best revenue for n =10 as there would be no cuts
        plan = tabulated_cut(CLRS,10)
        self.assertEqual(plan.revenue,30)
    def test_uncut_rod_pays_no_fee(self):
        #revenu must be exaxtly p7=17
        plan=tabulated_cut(CLRS,7,cut_fee=10**6)
        self.assertEqual(plan.revenue, 17)
        self.assertEqual(plan.piece_lengths, [7])

    def test_greedy_fails_report_example(self):
        # for n=6, prices 1,3,9,13,14,16
        # greedy takes 4 then 2=16
        # the optimum must be 3+3=18
        prices=[0,1,3,9,13,14,16]
        greedy=greedy_cut(prices,6)
        exact=tabulated_cut(prices,6)
        self.assertEqual(greedy.revenue,16)
        self.assertEqual(sorted(greedy.piece_lengths), [2,4])
        self.assertEqual(exact.revenue, 18)
        self.assertEqual(exact.piece_lengths, [3,3])

class EdgeCases(unittest.TestCase):
    def test_zero_length(self):
        # n=0 whereby nothing to sell returns 0 revenue and no piveces
        for solve in EXACT:
            with self.subTest(solver=solve.__name__):
                plan=solve([0],0)
                self.assertEqual(plan.revenue,0)
                self.assertEqual(plan.piece_lengths,[])

    def test_length_one_with_feet(self):
        #n=1 so no cut is possible meaning no feel will charged
        for solve in EXACT:
            with self.subTest(solver=solve.__name__):
                plan=solve([0,7],1,cut_fee=3)
                self.assertEqual(plan.revenue,7)
                self.assertEqual(plan.piece_lengths,[1])

    def test_invalid_inputs_rejected(self):
        for solve in EXACT + [greedy_cut]:
            with self.subTest(solver=solve.__name__):
                # negative length
                with self.assertRaises(ValueError):
                    solve(CLRS,-1)
                # negative fee
                with self.assertRaises(ValueError):
                    solve(CLRS,4,cut_fee=-1)
                # a really short price table
                with self.assertRaises(ValueError):
                    solve(CLRS,20)

class AgainstBaseline(unittest.TestCase):
    # crosschecking wheter the every exact solver matches the bruteforce on small n

    def test_baseline_matches_clrs(self):
        # check my checker against answers from CLRS
        for n, expected in [(4,10), (5,13), (7,18), (8,22), (10,30)]:
            with self.subTest(n=n):
                self.assertEqual(enumerate_all(CLRS,n), expected)

    def test_exact_solvers(self):
        seeded_random=random.Random(456)
        for pattern in ["random", "linear","concave", "convex"]:
            for n in range(0,13):
                prices=random_prices(n, seeded_random,pattern)
                for fee in [0,1,4]:
                    expected=enumerate_all(prices, n, fee)
                    for solve in EXACT:
                        with self.subTest(pattern=pattern, n=n, fee=fee, solver=solve.__name__):
                            plan=solve(prices,n,cut_fee=fee)
                            self.assertEqual(plan.revenue, expected)
                            self.assertEqual(sum(plan.piece_lengths),n)
                            self.assertEqual(plan_value(prices, plan.piece_lengths,fee),expected)

    def test_piece_limited(self):
        seeded_random= random.Random(7)
        for n in range(1,12):
            prices=random_prices(n,seeded_random,"random")
            for k in range(1, n+2):
                with self.subTest(n=n, k=k):
                    revenue,pieces=piece_limited_dp(n, prices[1:],k)
                    self.assertEqual(revenue,enumerate_all(prices,n,max_pieces=k))
                    self.assertLessEqual(len(pieces),k)
                    self.assertEqual(sum(pieces),n)
                    self.assertEqual(plan_value(prices,pieces),revenue)



if __name__ == "__main__":
    unittest.main()
