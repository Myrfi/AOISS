from __future__ import annotations

from typing import Dict, List, Set, Union


class LogicFormulaError(Exception):
    pass


class LogicEvaluator:

    def __init__(self, formula: str):
        self._original = formula
        self._rpn = self._compile(self._preprocess(formula))
        self._vars = None

    def _preprocess(self, s: str) -> str:
        s = ''.join(s.split())
        replacements = {
            '¬': '!', '∧': '&', '∨': '|', '→': '>', '↔': '=',
            '⇒': '>', '⇔': '=', '←': '>'
        }
        for old, new in replacements.items():
            s = s.replace(old, new)
        s = s.replace('->', '>').replace('<-', '>').replace('<->', '=')
        return s

    def _compile(self, expr: str) -> List[str]:
        precedence = {'!': 4, '&': 3, '|': 2, '>': 1, '=': 0}
        output = []
        stack = []
        i = 0
        n = len(expr)
        while i < n:
            ch = expr[i]
            if ch.isalpha():
                output.append(ch)
                i += 1
            elif ch == '(':
                stack.append(ch)
                i += 1
            elif ch == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack or stack[-1] != '(':
                    raise LogicFormulaError("Несогласованные скобки")
                stack.pop()
                i += 1
            elif ch in '!&|>=':
                if ch == '!':
                    stack.append(ch)
                    i += 1
                else:
                    while (stack and stack[-1] != '(' and
                           precedence.get(stack[-1], -1) >= precedence.get(ch, -1)):
                        output.append(stack.pop())
                    stack.append(ch)
                    i += 1
            else:
                raise LogicFormulaError(f"Недопустимый символ '{ch}'")
        while stack:
            top = stack.pop()
            if top == '(':
                raise LogicFormulaError("Несогласованные скобки")
            output.append(top)
        return output

    def evaluate(self, assignment: Dict[str, int]) -> int:
        stack = []
        for token in self._rpn:
            if token.isalpha():
                val = assignment.get(token)
                if val is None:
                    raise LogicFormulaError(f"Переменная {token} не задана")
                stack.append(bool(val))
            elif token == '!':
                a = stack.pop()
                stack.append(not a)
            elif token == '&':
                b = stack.pop()
                a = stack.pop()
                stack.append(a and b)
            elif token == '|':
                b = stack.pop()
                a = stack.pop()
                stack.append(a or b)
            elif token == '>':
                b = stack.pop()
                a = stack.pop()
                stack.append((not a) or b)
            elif token == '=':
                b = stack.pop()
                a = stack.pop()
                stack.append(a == b)
            else:
                raise LogicFormulaError(f"Неизвестный оператор {token}")
        if len(stack) != 1:
            raise LogicFormulaError("Ошибка вычисления")
        return int(stack[0])

    def variables(self) -> List[str]:
        if self._vars is None:
            seen: Set[str] = set()
            for tok in self._rpn:
                if tok.isalpha():
                    seen.add(tok)
            self._vars = sorted(seen)
        return self._vars

    def postfix(self) -> List[str]:
        return self._rpn.copy()
