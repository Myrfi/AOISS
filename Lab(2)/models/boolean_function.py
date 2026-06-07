from __future__ import annotations

from itertools import product
from typing import Dict, List, Set, Tuple


class LogicError(Exception):
    pass


class TruthAnalyzer:

    def __init__(self, formula: str):
        self._expr = formula
        self._post, self._varlist = self._to_postfix(formula)
        self._size = 1 << len(self._varlist)
        self._table = self._build_table()

    @staticmethod
    def _to_postfix(expr: str) -> Tuple[List[str], List[str]]:
        def _prep(s: str) -> str:
            s = ''.join(s.split())
            mp = {'¬': '!', '∧': '&', '∨': '|', '→': '>', '↔': '=', '⇒': '>', '⇔': '=', '←': '>'}
            for k, v in mp.items():
                s = s.replace(k, v)
            return s.replace('->', '>').replace('<-', '>').replace('<->', '=')

        prep = _prep(expr)
        prec = {'!': 4, '&': 3, '|': 2, '>': 1, '=': 0}
        output = []
        stack = []
        vars_set = set()
        i = 0
        n = len(prep)
        while i < n:
            ch = prep[i]
            if ch.isalpha():
                output.append(ch)
                vars_set.add(ch)
                i += 1
            elif ch == '(':
                stack.append(ch)
                i += 1
            elif ch == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack or stack[-1] != '(':
                    raise LogicError("Mismatched parentheses")
                stack.pop()
                i += 1
            elif ch in '!&|>=':
                if ch == '!':
                    stack.append(ch)
                    i += 1
                else:
                    while (stack and stack[-1] != '(' and
                           prec.get(stack[-1], -1) >= prec.get(ch, -1)):
                        output.append(stack.pop())
                    stack.append(ch)
                    i += 1
            else:
                raise LogicError(f"Invalid character '{ch}'")
        while stack:
            top = stack.pop()
            if top == '(':
                raise LogicError("Mismatched parentheses")
            output.append(top)
        return output, sorted(vars_set)

    def _eval_postfix(self, post: List[str], assign: Dict[str, int]) -> int:
        stack = []
        for tok in post:
            if tok.isalpha():
                stack.append(bool(assign[tok]))
            elif tok == '!':
                a = stack.pop()
                stack.append(not a)
            elif tok == '&':
                b = stack.pop()
                a = stack.pop()
                stack.append(a and b)
            elif tok == '|':
                b = stack.pop()
                a = stack.pop()
                stack.append(a or b)
            elif tok == '>':
                b = stack.pop()
                a = stack.pop()
                stack.append((not a) or b)
            elif tok == '=':
                b = stack.pop()
                a = stack.pop()
                stack.append(a == b)
            else:
                raise LogicError(f"Unknown operator {tok}")
        return int(stack[0])

    def _build_table(self) -> List[Tuple[Dict[str, int], int]]:
        n = len(self._varlist)
        table = []
        for bits in range(1 << n):
            assign = {self._varlist[i]: (bits >> (n - 1 - i)) & 1 for i in range(n)}
            res = self._eval_postfix(self._post, assign)
            table.append((assign, res))
        return table

    @property
    def variables(self) -> List[str]:
        return self._varlist.copy()

    @property
    def vector(self) -> List[int]:
        return [row[1] for row in self._table]

    @property
    def size(self) -> int:
        return self._size

    def to_bin(self) -> str:
        return ''.join(str(v) for _, v in self._table)

    def to_int(self) -> int:
        return int(self.to_bin(), 2)

    def minterms_repr(self) -> str:
        ones = [str(i) for i, (_, v) in enumerate(self._table) if v == 1]
        return f"Σm({', '.join(ones)})" if ones else "Σm()"

    def maxterms_repr(self) -> str:
        zeros = [str(i) for i, (_, v) in enumerate(self._table) if v == 0]
        return f"ΠM({', '.join(zeros)})" if zeros else "ΠM()"

    def _term(self, idx: int, sop: bool) -> str:
        n = len(self._varlist)
        parts = []
        for i, var in enumerate(self._varlist):
            bit = (idx >> (n - 1 - i)) & 1
            if sop:
                parts.append(var if bit == 1 else f"¬{var}")
            else:
                parts.append(var if bit == 0 else f"¬{var}")
        op = ' ∧ ' if sop else ' ∨ '
        return '(' + op.join(parts) + ')'

    def to_sop(self) -> str:
        terms = [self._term(i, True) for i, (_, v) in enumerate(self._table) if v == 1]
        return ' ∨ '.join(terms) if terms else "0"

    def to_pos(self) -> str:
        clauses = [self._term(i, False) for i, (_, v) in enumerate(self._table) if v == 0]
        return ' ∧ '.join(clauses) if clauses else "1"

    def to_table_str(self) -> str:
        header = " | ".join(self._varlist + ["F"])
        sep = '-' * len(header)
        lines = [header, sep]
        for assign, res in self._table:
            row = [str(assign[v]) for v in self._varlist]
            lines.append(" | ".join(row + [str(res)]))
        return "\n".join(lines)

    def get_assignment(self, index: int) -> Dict[str, int]:
        n = len(self._varlist)
        return {self._varlist[i]: (index >> (n - 1 - i)) & 1 for i in range(n)}
