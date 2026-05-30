import unittest

from core.parser import ExpressionParser, ExpressionError


class ParsingScenarios(unittest.TestCase):
    def test_expression_evaluation(self):
        p = ExpressionParser("!(!a→!b)∨c")
        self.assertEqual(p.evaluate({"a": 1, "b": 0, "c": 0}), 0)
        self.assertEqual(p.evaluate({"a": 0, "b": 0, "c": 0}), 0)
        self.assertEqual(p.evaluate({"a": 1, "b": 1, "c": 1}), 1)
        self.assertIn("->", p.postfix)

    def test_equivalence_handling(self):
        p = ExpressionParser("a~b")
        self.assertEqual(p.evaluate({"a": 0, "b": 0}), 1)
        self.assertEqual(p.evaluate({"a": 0, "b": 1}), 0)

    def test_invalid_character_raises(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a#b")

    def test_missing_closing_parenthesis(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a&b")

    def test_unary_operator_without_operand(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("!")

    def test_variable_order_correctness(self):
        p = ExpressionParser("e|a|c")
        self.assertEqual(p.variables(), ["a", "c", "e"])

    def test_missing_operand_after_binary(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a&")

    def test_extra_closing_parenthesis(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a))")

    def test_empty_expression(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("")

    def test_invalid_operator_placement(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("&a")

    def test_missing_operand_before_parenthesis(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a()")

    def test_missing_right_operand_for_implication(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a->")

    def test_missing_right_operand_for_or(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a|")

    def test_missing_right_operand_for_and(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a&")

    def test_missing_operator_after_parenthesis(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a)b")

    def test_not_after_operand(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("a!")
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a)!")

    def test_binary_after_open_paren(self):
        with self.assertRaises(ExpressionError):
            ExpressionParser("(&a)")

    def test_binary_operator_at_start(self):
        for op in ("&", "|", "->"):
            with self.assertRaises(ExpressionError):
                ExpressionParser(f"{op}a")

    def test_unary_not_without_operand(self):
        # Покрывает строку 79 (если там проверка на отсутствие операнда после '!')
        with self.assertRaises(ExpressionError):
            ExpressionParser("!")
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a)&!")

    def test_binary_operator_missing_left_operand(self):
        # Покрывает строку 141 (ошибка при бинарном операторе в начале)
        with self.assertRaises(ExpressionError):
            ExpressionParser("&a")
        with self.assertRaises(ExpressionError):
            ExpressionParser("|a")
        with self.assertRaises(ExpressionError):
            ExpressionParser("->a")

    def test_incorrect_parentheses_usage(self):
        # Покрывает строки 152-154 (пустые скобки, неверная позиция ')', лишние скобки)
        with self.assertRaises(ExpressionError):
            ExpressionParser("()")
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a))")
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a&b)()")
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a")

    def test_expression_ends_with_binary_operator(self):
        # Покрывает строку 168 (выражение заканчивается бинарным оператором)
        for op in ("&", "|", "->", "~"):
            with self.assertRaises(ExpressionError):
                ExpressionParser(f"a{op}")
        with self.assertRaises(ExpressionError):
            ExpressionParser("a~")

    def test_missing_operand_after_not_complex(self):
        # Возможно, строка 79 срабатывает только в определённом контексте
        with self.assertRaises(ExpressionError):
            ExpressionParser("a&!")

    def test_binary_operator_with_missing_right_in_parentheses(self):
        # Для строки 141 или 168
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a|)")

    def test_expression_with_only_operator(self):
        # Бинарный оператор без операндов – строка 141
        for op in ("&", "|", "->", "~"):
            with self.assertRaises(ExpressionError):
                ExpressionParser(op)

    def test_expression_with_only_parentheses(self):
        # Пустые скобки – строка 152-154
        with self.assertRaises(ExpressionError):
            ExpressionParser("()")

    def test_expression_ending_with_binary_after_parenthesis(self):
        # Выражение заканчивается бинарным оператором – строка 168
        with self.assertRaises(ExpressionError):
            ExpressionParser("(a&b)&")