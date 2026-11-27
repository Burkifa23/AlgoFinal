import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from dp_solvers import tabulated_cut

CLRS=[0,1,5,8,9,10,17,17,20,24,30]

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

if __name__ == "__main__":
    unittest.main()
