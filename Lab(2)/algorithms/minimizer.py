from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import List, Sequence, Tuple, Dict

@dataclass(frozen=True)
class Implicant:
    mask: int
    dontcare: int
    covered: frozenset[int]

    @property
    def literal_count(self) -> int:
        return bin(self.mask & ~self.dontcare).count('1')

@dataclass(frozen=True)
class MergeStage:
    stage_number: int
    terms: Tuple[str, ...]

class Minimizer:
    def __init__(self, vector: Sequence[int], variables: Sequence[str]):
        self.vec = list(vector)
        self.vars = list(variables)
        self.n = len(self.vars)
        if len(self.vec) != (1 << self.n):
            raise ValueError("Размер вектора должен быть 2^n")

    def _targets(self, mode: str) -> List[int]:
        need = 1 if mode == 'DNF' else 0
        return [i for i, v in enumerate(self.vec) if v == need]

    @staticmethod
    def _mask_pair(m1: int, dc1: int, m2: int, dc2: int) -> Tuple[int, int] | None:
        if dc1 != dc2:
            return None

        diff = (m1 ^ m2) & ~dc1
        if diff == 0:
            return None
        if (diff & (diff - 1)) != 0:
            return None

        new_mask = m1 & m2
        new_dc = dc1 | diff
        return (new_mask, new_dc)

    def _initial_implicants(self, mode: str) -> List[Tuple[int, int, int]]:
        targets = self._targets(mode)
        return [(idx, 0, idx) for idx in targets]

    def _prime_implicants_with_stages(self, start: List[Tuple[int, int, int]]) -> Tuple[List[MergeStage], List[Tuple[int, int]]]:
        current = start
        stages = []
        primes = []
        stage_no = 1

        while current:
            str_terms = [self._to_pattern(m, dc) for (m, dc, _) in current]
            stages.append(MergeStage(stage_no, tuple(str_terms)))

            used = set()
            next_dict = {}
            for i in range(len(current)):
                for j in range(i+1, len(current)):
                    m1, dc1, _ = current[i]
                    m2, dc2, _ = current[j]
                    merged = self._mask_pair(m1, dc1, m2, dc2)
                    if merged is not None:
                        nm, ndc = merged
                        cov = current[i][2] | current[j][2]
                        key = (nm, ndc)
                        if key not in next_dict or next_dict[key][2] != cov:
                            next_dict[key] = (nm, ndc, cov)
                        used.add(i)
                        used.add(j)

            for i, (m, dc, _) in enumerate(current):
                if i not in used:
                    primes.append((m, dc))

            if not next_dict:
                break
            current = list(next_dict.values())
            stage_no += 1

        return stages, primes

    def _to_pattern(self, mask: int, dontcare: int) -> str:
        s = []
        for i in range(self.n):
            bitpos = self.n - 1 - i
            if (dontcare >> bitpos) & 1:
                s.append('-')
            else:
                s.append('1' if (mask >> bitpos) & 1 else '0')
        return ''.join(s)

    def _build_implicants(self, primes: List[Tuple[int, int]], mode: str) -> List[Implicant]:
        targets = set(self._targets(mode))
        result = []
        for m, dc in primes:
            mask = m & ~dc
            covered = frozenset(t for t in targets if (t & ~dc) == mask)
            result.append(Implicant(m, dc, covered))
        return result

    def _min_cover(self, implicants: List[Implicant], universe: Set[int]) -> List[Implicant]:
        if not universe:
            return []
        best = None
        best_cost = None
        for r in range(1, len(implicants) + 1):
            for combo in combinations(implicants, r):
                cover = set().union(*(imp.covered for imp in combo))
                if universe.issubset(cover):
                    cost = (sum(imp.literal_count for imp in combo), len(combo))
                    if best_cost is None or cost < best_cost:
                        best = list(combo)
                        best_cost = cost
        return best or []

    def _select_cover(self, primes: List[Tuple[int, int]], mode: str) -> List[str]:
        implicants = self._build_implicants(primes, mode)
        universe = set(self._targets(mode))
        if not universe:
            return []

        coverage = {idx: [] for idx in universe}
        for imp in implicants:
            for idx in imp.covered:
                coverage[idx].append(imp)

        essential = []
        for idx, lst in coverage.items():
            if len(lst) == 1:
                essential.append(lst[0])

        selected = []
        remaining = set(universe)
        for imp in dict.fromkeys(essential):
            if imp not in selected:
                selected.append(imp)
                remaining -= imp.covered

        rest = [imp for imp in implicants if imp not in selected]
        selected.extend(self._min_cover(rest, remaining))

        # Уникальные паттерны в детерминированном порядке (по строке)
        unique = []
        seen = set()
        for imp in selected:
            pat = self._to_pattern(imp.mask, imp.dontcare)
            if pat not in seen:
                unique.append(pat)
                seen.add(pat)
        # Сортируем паттерны для предсказуемого порядка
        unique.sort()
        return unique

    def _expr_from_pattern(self, pattern: str, mode: str) -> str:
        parts = []
        for var, ch in zip(self.vars, pattern):
            if ch == '-':
                continue
            if mode == 'DNF':
                parts.append(var if ch == '1' else f"¬{var}")
            else:
                parts.append(var if ch == '0' else f"¬{var}")
        if not parts:
            return "1" if mode == 'DNF' else "0"
        if mode == 'DNF':
            return parts[0] if len(parts) == 1 else "(" + " ∧ ".join(parts) + ")"
        else:
            return parts[0] if len(parts) == 1 else "(" + " ∨ ".join(parts) + ")"

    def _format(self, patterns: List[str], mode: str) -> str:
        if not patterns:
            return "0" if mode == 'DNF' else "1"
        # Преобразуем в выражения и сортируем по строке выражения (алфавитный порядок)
        terms = [self._expr_from_pattern(p, mode) for p in patterns]
        terms.sort()
        sep = " ∨ " if mode == 'DNF' else " ∧ "
        return sep.join(terms)

    def calculation_method(self, mode: str = "DNF") -> Dict:
        mode = mode.upper()
        initial = self._initial_implicants(mode)
        init_str = [self._to_pattern(m, dc) for (m, dc, _) in initial]
        stages, primes = self._prime_implicants_with_stages(initial)
        selected = self._select_cover(primes, mode)
        return {
            "mode": mode,
            "initial_terms": init_str,
            "stages": stages,
            "prime_implicants": [self._to_pattern(m, dc) for m, dc in primes],
            "selected_patterns": selected,
            "result": self._format(selected, mode),
        }

    def table_method(self, mode: str = "DNF") -> Dict:
        mode = mode.upper()
        initial = self._initial_implicants(mode)
        init_str = [self._to_pattern(m, dc) for (m, dc, _) in initial]
        stages, primes = self._prime_implicants_with_stages(initial)
        implicants = self._build_implicants(primes, mode)
        targets = self._targets(mode)
        table_rows = []
        for imp in implicants:
            pat = self._to_pattern(imp.mask, imp.dontcare)
            row = {
                "pattern": pat,
                "expression": self._expr_from_pattern(pat, mode),
                "coverage": [1 if t in imp.covered else 0 for t in targets],
            }
            table_rows.append(row)
        selected = self._select_cover(primes, mode)
        return {
            "mode": mode,
            "initial_terms": init_str,
            "stages": stages,
            "prime_implicants": [self._to_pattern(m, dc) for m, dc in primes],
            "coverage_table": table_rows,
            "selected_patterns": selected,
            "result": self._format(selected, mode),
        }

    def _gray(self, bits: int) -> List[str]:
        if bits == 0:
            return [""]
        prev = self._gray(bits-1)
        return ["0"+x for x in prev] + ["1"+x for x in reversed(prev)]

    def _karno_layout(self):
        if self.n == 2:
            return ["a"], ["b"], None
        if self.n == 3:
            return [self.vars[0]], self.vars[1:], None
        if self.n == 4:
            return self.vars[:2], self.vars[2:], None
        if self.n == 5:
            return self.vars[:2], self.vars[2:4], self.vars[4]
        raise ValueError("Карта Карно для 2..5 переменных")

    def _karno_grid(self, mode: str) -> Dict:
        row_vars, col_vars, extra = self._karno_layout()
        row_codes = self._gray(len(row_vars))
        col_codes = self._gray(len(col_vars))
        layers = []
        if extra is None:
            grid = []
            for rc in row_codes:
                row = []
                for cc in col_codes:
                    idx_str = rc + cc
                    if self.n == 2:
                        idx = int(idx_str, 2)
                    elif self.n == 3:
                        idx = int(rc + cc, 2)
                    else:
                        idx = int(rc + cc, 2)
                    row.append(self.vec[idx])
                grid.append((rc, row))
            layers.append({"extra_value": None, "rows": grid, "row_codes": row_codes, "col_codes": col_codes})
        else:
            for eb in ('0','1'):
                grid = []
                for rc in row_codes:
                    row = []
                    for cc in col_codes:
                        idx_str = rc + cc + eb
                        idx = int(idx_str, 2)
                        row.append(self.vec[idx])
                    grid.append((rc, row))
                layers.append({"extra_value": eb, "rows": grid, "row_codes": row_codes, "col_codes": col_codes})
        minimized = self.calculation_method(mode)
        return {"layers": layers, "result": minimized["result"]}

    def karnaugh_method(self) -> Dict:
        return {"dnf": self._karno_grid("DNF"), "knf": self._karno_grid("KNF")}
