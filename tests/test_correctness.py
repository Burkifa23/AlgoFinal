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

if __name__ == "__main__":
    unittest.main()
