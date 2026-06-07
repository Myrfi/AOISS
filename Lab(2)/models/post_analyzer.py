from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Sequence, Tuple


class FuncProperties:

    def __init__(self, table: Sequence[int], labels: Sequence[str]):
        self._data = tuple(table)
        self._names = tuple(labels)
        self._n = len(self._names)
        if len(self._data) != 1 << self._n:
            raise ValueError("Invalid table size")

    def is_const0(self) -> bool:
        return self._data[0] == 0

    def is_const1(self) -> bool:
        return self._data[-1] == 1

    def is_selfdual(self) -> bool:
        sz = len(self._data)
        for i in range(sz >> 1):
            if self._data[i] == self._data[sz - 1 - i]:
                return False
        return True

    def is_monotone(self) -> bool:
        sz = len(self._data)
        for low in range(sz):
            for high in range(sz):
                if (low & high) == low and self._data[low] > self._data[high]:
                    return False
        return True

    def _transform(self, seq: Tuple[int, ...]) -> Tuple[int, ...]:
        res = list(seq)
        step = 1
        while step < len(res):
            for i in range(len(res)):
                if i & step:
                    res[i] ^= res[i ^ step]
            step <<= 1
        return tuple(res)

    def anf(self) -> Tuple[int, ...]:
        return self._transform(self._data)

    def is_affine(self) -> bool:
        coeffs = self.anf()
        for i, c in enumerate(coeffs):
            if c and (i.bit_count() > 1):
                return False
        return True

    def anf_str(self) -> str:
        coeffs = self.anf()
        terms = []
        for idx, c in enumerate(coeffs):
            if not c:
                continue
            if idx == 0:
                terms.append("1")
                continue
            mask = f"{idx:0{self._n}b}"
            mon = "".join(self._names[j] for j, b in enumerate(mask) if b == '1')
            terms.append(mon)
        return " ⊕ ".join(terms) if terms else "0"

    def essential(self) -> Dict[str, bool]:
        res = {}
        for pos, var in enumerate(self._names):
            bit = 1 << (self._n - 1 - pos)
            needed = any(self._data[i] != self._data[i | bit] for i in range(len(self._data)) if not (i & bit))
            res[var] = needed
        return res

    def _diff(self, vec: Tuple[int, ...], dim: int, pos: int) -> Tuple[int, ...]:
        step = 1 << (dim - 1 - pos)
        out = []
        for i in range(0, len(vec), step << 1):
            for j in range(step):
                out.append(vec[i + j] ^ vec[i + j + step])
        return tuple(out)

    def derivative(self, var: str, cur_vec: Tuple[int, ...] = None, cur_dim: int = None) -> Tuple[Tuple[int, ...], Tuple[str, ...]]:
        if cur_vec is None:
            cur_vec = self._data
            cur_names = self._names
            cur_dim = self._n
        else:
            cur_names = [f"x{i}" for i in range(cur_dim)]  # fallback, but better pass names
        if var not in cur_names:
            return cur_vec, tuple(cur_names)
        idx = cur_names.index(var)
        new_vec = self._diff(cur_vec, cur_dim, idx)
        new_names = tuple(v for v in cur_names if v != var)
        return new_vec, new_names

    def multi_derivative(self, vars: Sequence[str]) -> Tuple[Tuple[int, ...], Tuple[str, ...]]:
        cur_vec = self._data
        cur_names = self._names
        cur_dim = self._n
        for v in vars:
            cur_vec, cur_names = self.derivative(v, cur_vec, cur_dim)
            cur_dim = len(cur_names)
        return cur_vec, cur_names

    @staticmethod
    def to_sop(vec: Sequence[int], labels: Sequence[str]) -> str:
        if not any(vec):
            return "0"
        n = len(labels)
        terms = []
        for idx, val in enumerate(vec):
            if not val:
                continue
            bits = f"{idx:0{n}b}"
            literals = [labels[j] if bits[j] == '1' else f"¬{labels[j]}" for j in range(n)]
            terms.append("(" + " ∧ ".join(literals) + ")")
        return " ∨ ".join(terms)

    @staticmethod
    def to_pos(vec: Sequence[int], labels: Sequence[str]) -> str:
        if not vec or all(vec):
            return "1"
        n = len(labels)
        clauses = []
        for idx, val in enumerate(vec):
            if val:
                continue
            bits = f"{idx:0{n}b}"
            literals = [labels[j] if bits[j] == '0' else f"¬{labels[j]}" for j in range(n)]
            clauses.append("(" + " ∨ ".join(literals) + ")")
        return " ∧ ".join(clauses)
