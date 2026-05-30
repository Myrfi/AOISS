import unittest

from models.boolean_function import BooleanFunction
from models.post_analyzer import PostAnalyzer
from algorithms.minimizer import Minimizer


class WholeWorkflowTest(unittest.TestCase):
    def test_complete_analysis(self):
        expr = BooleanFunction("!(!a→!b)∨c")
        analyzer = PostAnalyzer(expr.vector, expr.variables)
        minimizer = Minimizer(expr.vector, expr.variables)

        self.assertEqual(expr.variables, ["a", "b", "c"])
        self.assertEqual(expr.vector_string(), "01110101")
        self.assertTrue(analyzer.check_t0())
        self.assertFalse(analyzer.check_l())
        self.assertIn("⊕", analyzer.zhegalkin_polynomial())

        dnf_res = minimizer.calculation_method("DNF")["result"]
        knf_res = minimizer.calculation_method("KNF")["result"]
        self.assertTrue(dnf_res)
        self.assertTrue(knf_res)