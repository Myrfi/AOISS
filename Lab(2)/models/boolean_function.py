from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, List

from constants import VALID_VARIABLES
from core.parser import ExpressionParser

@dataclass(frozen=True)
class TruthTableRow:
    assignment: Dict[str, int]
    result: int

class BooleanFunction:
    def __init__(self, expression: str | ExpressionParser):
        self.parser = expression if isinstance(expression, ExpressionParser) else ExpressionParser(expression)
        self.vars = self.parser.variables()
        if len(self.vars) > len(VALID_VARIABLES):
            raise ValueError("Не более 5 переменных")
        self.truth = []
        self.bits = []
        self._fill()

    @property
    def size(self) -> int:
        return len(self.bits)

    @property
    def vector(self) -> List[int]:
        return self.bits.copy()

    @property
    def variables(self) -> List[str]:
        return self.vars.copy()

    @property
    def table(self) -> List[TruthTableRow]:
        return self.truth.copy()

    def _fill(self) -> None:
        n = len(self.vars)
        for idx in range(1 << n):
            assign = {v: (idx >> (n-1-i)) & 1 for i, v in enumerate(self.vars)}
            res = self.parser.evaluate(assign)
            self.truth.append(TruthTableRow(assign, res))
            self.bits.append(res)

    def vector_string(self) -> str:
        return ''.join(str(b) for b in self.bits)

    def index_form(self) -> int:
        return int(self.vector_string(), 2)

    def numeric_sdnf(self) -> str:
        ones = [str(i) for i, v in enumerate(self.bits) if v == 1]
        return f"Σm({', '.join(ones)})" if ones else "Σm()"

    def numeric_sknf(self) -> str:
        zeros = [str(i) for i, v in enumerate(self.bits) if v == 0]
        return f"ΠM({', '.join(zeros)})" if zeros else "ΠM()"

    def _make_term(self, idx: int, mode: str) -> str:
        n = len(self.vars)
        parts = []
        for i, v in enumerate(self.vars):
            bit = (idx >> (n-1-i)) & 1
            if mode == 'sdnf':
                parts.append(v if bit == 1 else f"¬{v}")
            else:
                parts.append(v if bit == 0 else f"¬{v}")
        return '(' + (' ∧ ' if mode == 'sdnf' else ' ∨ ').join(parts) + ')'

    def sdnf(self) -> str:
        terms = [self._make_term(i, 'sdnf') for i, v in enumerate(self.bits) if v == 1]
        return ' ∨ '.join(terms) if terms else "0"

    def sknf(self) -> str:
        clauses = [self._make_term(i, 'sknf') for i, v in enumerate(self.bits) if v == 0]
        return ' ∧ '.join(clauses) if clauses else "1"

    def truth_table(self) -> str:
        header = " | ".join(self.vars + ["F"])
        lines = [header, '-' * len(header)]
        for row in self.truth:
            values = [str(row.assignment[v]) for v in self.vars]
            lines.append(" | ".join(values + [str(row.result)]))
        return "\n".join(lines)

    def assignment_at(self, index: int) -> Dict[str, int]:
        n = len(self.vars)
        return {v: (index >> (n-1-i)) & 1 for i, v in enumerate(self.vars)}