import unittest

from models.post_analyzer import PostAnalyzer


class PostPropertiesTest(unittest.TestCase):
    def test_all_zero_function(self):
        vec = [0, 0, 0, 0]
        pa = PostAnalyzer(vec, ["a", "b"])
        self.assertTrue(pa.check_t0())
        self.assertFalse(pa.check_t1())
        self.assertFalse(pa.check_s())
        self.assertTrue(pa.check_m())
        self.assertTrue(pa.check_l())
        self.assertEqual(pa.zhegalkin_polynomial(), "0")
        self.assertEqual(pa.essential_variables(), {"a": False, "b": False})

    def test_derivative_computation(self):
        vec = [0, 1, 1, 0]  # XOR
        pa = PostAnalyzer(vec, ["a", "b"])
        d_a = pa.partial_derivative("a")
        self.assertEqual(d_a.vector, [1, 1])
        self.assertEqual(d_a.variables, ["b"])

        d_ab = pa.mixed_derivative(["a", "b"])
        self.assertEqual(d_ab.vector, [0])
        self.assertEqual(d_ab.variables, [])

    def test_vector_to_form_conversion(self):
        v = [0, 0, 1, 1]
        self.assertIn("a", PostAnalyzer.vector_to_sdnf(v, ["a", "b"]))
        self.assertIn("¬a", PostAnalyzer.vector_to_sknf([1, 1, 0, 0], ["a", "b"]))

    def test_non_monotonic_function(self):
        # Функция XOR не монотонна
        vec = [0, 1, 1, 0]
        pa = PostAnalyzer(vec, ["a", "b"])
        self.assertFalse(pa.check_m())

    def test_self_dual_false(self):
        vec = [0, 0, 0, 0]
        pa = PostAnalyzer(vec, ["a", "b"])
        self.assertFalse(pa.check_s())

    def test_essential_variables(self):
        vec = [0, 1, 0, 1]  # зависит от b
        pa = PostAnalyzer(vec, ["a", "b"])
        self.assertEqual(pa.essential_variables(), {"a": False, "b": True})

    def test_partial_derivative_missing_var(self):
        vec = [0, 1, 1, 0]
        pa = PostAnalyzer(vec, ["a", "b"])
        res = pa.partial_derivative("c")  # переменной нет
        self.assertEqual(res.vector, vec)
        self.assertEqual(res.variables, ["a", "b"])

    def test_mixed_derivative_error(self):
        vec = [0, 1, 1, 0]
        pa = PostAnalyzer(vec, ["a", "b"])
        with self.assertRaises(ValueError):
            pa.mixed_derivative(["c"])

    def test_vector_to_sknf_all_ones(self):
        vec = [1, 1, 1, 1]
        self.assertEqual(PostAnalyzer.vector_to_sknf(vec, ["a", "b"]), "1")

    def test_invalid_vector_size(self):
        # Покрывает строку 17 (проверка размера вектора в __init__)
        with self.assertRaises(ValueError):
            PostAnalyzer([0, 1], ["a", "b"])  # должно быть 4 элемента

    def test_monotonic_function(self):
        # Покрывает строку 29 (цикл в check_m без срабатывания условия)
        vec = [0, 0, 0, 1]  # a & b
        pa = PostAnalyzer(vec, ["a", "b"])
        self.assertTrue(pa.check_m())

    def test_vector_to_sdnf_empty(self):
        # Покрывает строку 119 (проверка any(vec) в vector_to_sdnf)
        vec = [0, 0, 0, 0]
        self.assertEqual(PostAnalyzer.vector_to_sdnf(vec, ["a", "b"]), "0")
