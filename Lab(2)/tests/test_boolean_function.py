import unittest

from models.boolean_function import BooleanFunction


class BooleanFunctionCase(unittest.TestCase):
    def setUp(self):
        self.f = BooleanFunction("!(!a→!b)∨c")

    def test_row_count(self):
        self.assertEqual(self.f.size, 8)
        self.assertEqual(len(self.f.table), 8)

    def test_forms_contain_operators(self):
        dnf = self.f.sdnf()
        knf = self.f.sknf()
        self.assertIn("∨", dnf)
        self.assertIn("∧", knf)
        self.assertTrue(dnf)

    def test_numeric_representations_match(self):
        self.assertEqual(self.f.numeric_sdnf(), "Σm(1, 2, 3, 5, 7)")
        self.assertEqual(self.f.numeric_sknf(), "ΠM(0, 4, 6)")

    def test_bitstring_and_decimal(self):
        self.assertEqual(self.f.vector_string(), "01110101")
        self.assertEqual(self.f.index_form(), int("01110101", 2))

    def test_table_includes_header(self):
        t = self.f.truth_table()
        self.assertIn("F", t)
        self.assertIn("a", t)

    def test_assignment_lookup(self):
        self.assertEqual(self.f.assignment_at(5), {"a": 1, "b": 0, "c": 1})

    def test_too_many_variables(self):
        with self.assertRaises(ValueError):
            BooleanFunction("a&b&c&d&e&f")