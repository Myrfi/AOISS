from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Dict

@dataclass(frozen=True)
class DerivativeResult:
    vector: List[int]
    variables: List[str]

class PostAnalyzer:
    def __init__(self, vector: Sequence[int], variables: Sequence[str]):
        self.vec = list(vector)
        self.vars = list(variables)
        self.n = len(self.vars)
        if len(self.vec) != (1 << self.n):
            raise ValueError("Размер вектора должен быть 2^n")

    def check_t0(self) -> bool:
        return self.vec[0] == 0

    def check_t1(self) -> bool:
        return self.vec[-1] == 1

    def check_s(self) -> bool:
        for i in range(len(self.vec)):
            if self.vec[i] == self.vec[-1-i]:
                return False
        return True

    def check_m(self) -> bool:
        # монотонность: если x <= y (побитово), то f(x) <= f(y)
        size = len(self.vec)
        for x in range(size):
            for y in range(size):
                if (x & y) == x and self.vec[x] > self.vec[y]:
                    return False
        return True

    def _mobius(self, arr: List[int]) -> List[int]:
        res = arr[:]
        sz = len(res)
        step = 1
        while step < sz:
            for i in range(sz):
                if i & step:
                    res[i] ^= res[i ^ step]
            step <<= 1
        return res

    def zhegalkin_coefficients(self) -> List[int]:
        return self._mobius(self.vec)

    def check_l(self) -> bool:
        coeffs = self.zhegalkin_coefficients()
        for i, c in enumerate(coeffs):
            if c == 1 and bin(i).count('1') > 1:
                return False
        return True

    def zhegalkin_polynomial(self) -> str:
        coeffs = self.zhegalkin_coefficients()
        terms = []
        for i, c in enumerate(coeffs):
            if c == 0:
                continue
            if i == 0:
                terms.append("1")
                continue
            bits = f"{i:0{self.n}b}"
            monom = ''.join(self.vars[j] for j, b in enumerate(bits) if b == '1')
            terms.append(monom)
        return " ⊕ ".join(terms) if terms else "0"

    def essential_variables(self) -> Dict[str, bool]:
        res = {}
        for pos, var in enumerate(self.vars):
            mask = 1 << (self.n - 1 - pos)
            ess = False
            for i in range(len(self.vec)):
                if i & mask: continue
                if self.vec[i] != self.vec[i | mask]:
                    ess = True
                    break
            res[var] = ess
        return res

    def _diff(self, vec: List[int], pos: int, bits: int) -> List[int]:
        step = 1 << (bits - 1 - pos)
        out = []
        for i in range(len(vec)):
            if i & step: continue
            out.append(vec[i] ^ vec[i | step])
        return out

    def partial_derivative(self, target_var: str, vector=None, variables=None) -> DerivativeResult:
        vec = list(vector) if vector is not None else self.vec
        vars_list = list(variables) if variables is not None else self.vars
        if target_var not in vars_list:
            return DerivativeResult(vec, vars_list)
        idx = vars_list.index(target_var)
        new_vec = self._diff(vec, idx, len(vars_list))
        new_vars = [v for v in vars_list if v != target_var]
        return DerivativeResult(new_vec, new_vars)

    def mixed_derivative(self, target_vars: Sequence[str]) -> DerivativeResult:
        cur_vec = list(self.vec)
        cur_vars = list(self.vars)
        for tv in target_vars:
            if tv not in cur_vars:
                raise ValueError(f"Переменная {tv} отсутствует")
            res = self.partial_derivative(tv, cur_vec, cur_vars)
            cur_vec, cur_vars = res.vector, res.variables
        return DerivativeResult(cur_vec, cur_vars)

    @staticmethod
    def vector_to_sdnf(vec: Sequence[int], vars_list: Sequence[str]) -> str:
        if not any(vec):
            return "0"
        n = len(vars_list)
        terms = []
        for idx, val in enumerate(vec):
            if val != 1:
                continue
            bits = f"{idx:0{n}b}"
            literals = [v if b == '1' else f"¬{v}" for v, b in zip(vars_list, bits)]
            terms.append("(" + " ∧ ".join(literals) + ")")
        return " ∨ ".join(terms)

    @staticmethod
    def vector_to_sknf(vec: Sequence[int], vars_list: Sequence[str]) -> str:
        if not vec or all(v == 1 for v in vec):
            return "1"
        n = len(vars_list)
        clauses = []
        for idx, val in enumerate(vec):
            if val != 0:
                continue
            bits = f"{idx:0{n}b}"
            literals = [v if b == '0' else f"¬{v}" for v, b in zip(vars_list, bits)]
            clauses.append("(" + " ∨ ".join(literals) + ")")
        return " ∧ ".join(clauses)