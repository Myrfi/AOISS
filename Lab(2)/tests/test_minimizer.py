import unittest

from algorithms.minimizer import Minimizer


class MinimizerChecks(unittest.TestCase):
    def setUp(self):
        # vector for !(!a→!b)∨c with two vars a,b -> truth table [0,1,1,1]
        self.m = Minimizer([0, 1, 1, 1], ["a", "b"])

    def test_dnf_output(self):
        out = self.m.calculation_method("DNF")
        self.assertIn("result", out)
        self.assertEqual(out["result"], "a ∨ b")

    def test_knf_output(self):
        out = self.m.calculation_method("KNF")
        self.assertIn("result", out)
        self.assertEqual(out["result"], "(a ∨ b)")

    def test_table_method_has_coverage(self):
        res = self.m.table_method("DNF")
        self.assertIn("coverage_table", res)
        self.assertGreaterEqual(len(res["coverage_table"]), 1)

    def test_karnaugh_method_structure(self):
        res = self.m.karnaugh_method()
        self.assertIn("dnf", res)
        self.assertIn("knf", res)
        self.assertGreaterEqual(len(res["dnf"]["layers"]), 1)

    def test_merging_behavior(self):
        # Verify that the DNF result is consistent (covers all ones)
        dnf = self.m.calculation_method("DNF")["result"]
        self.assertEqual(dnf, "a ∨ b")

    def test_empty_universe_cover(self):
        # Создаём функцию без единиц (все нули) для DNF
        m = Minimizer([0, 0, 0, 0], ["a", "b"])
        result = m.calculation_method("DNF")
        self.assertEqual(result["result"], "0")

    def test_karnaugh_5_vars(self):
        # Для 5 переменных нужна функция
        vec = [0] * 32
        vec[0] = 1  # только один минтерм
        m = Minimizer(vec, ["a", "b", "c", "d", "e"])
        res = m.karnaugh_method()
        self.assertIn("dnf", res)
        self.assertIn("knf", res)

    def test_invalid_vector_size(self):
        with self.assertRaises(ValueError):
            Minimizer([0, 1], ["a", "b"])  # неверный размер вектора

    def test_karnaugh_3_vars(self):
        vec = [0] * 8
        vec[0] = 1
        m = Minimizer(vec, ["a", "b", "c"])
        res = m.karnaugh_method()
        self.assertIn("dnf", res)

    def test_karnaugh_4_vars(self):
        vec = [0] * 16
        vec[0] = 1
        m = Minimizer(vec, ["a", "b", "c", "d"])
        res = m.karnaugh_method()
        self.assertIn("dnf", res)