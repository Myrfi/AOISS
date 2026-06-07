from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import List, Sequence, Set, Tuple, Dict, Optional
from collections import defaultdict

@dataclass(frozen=True)
class Implicant:
    mask: int
    dontcare: int
    covered: frozenset[int]

    @property
    def literal_count(self) -> int:
        return bin(self.mask & ~self.dontcare).count('1')

@dataclass
class MergeStep:
    step_no: int
    terms: Tuple[str, ...]

@dataclass
class QMCResult:
    mode: str
    initial_terms: List[str]
    merge_steps: List[MergeStep]
    prime_implicants: List[str]
    selected_patterns: List[str]
    expression: str

class BooleanMinimizer:
    def __init__(self, truth_vector: Sequence[int], var_names: Sequence[str]):
        self.vector = list(truth_vector)
        self.vars = list(var_names)
        self.nbits = len(self.vars)
        if len(self.vector) != (1 << self.nbits):
            raise ValueError("Vector length must be 2**n")

    def _get_active_indices(self, mode: str) -> List[int]:
        target = 1 if mode == 'DNF' else 0
        return [i for i, v in enumerate(self.vector) if v == target]

    @staticmethod
    def _merge_terms(m1: int, dc1: int, m2: int, dc2: int) -> Optional[Tuple[int, int]]:
        if dc1 != dc2:
            return None
        diff = (m1 ^ m2) & ~dc1
        if diff == 0 or (diff & (diff - 1)) != 0:
            return None
        return (m1 & m2, dc1 | diff)

    def _make_start_terms(self, mode: str) -> List[Tuple[int, int, int]]:
        return [(idx, 0, idx) for idx in self._get_active_indices(mode)]

    def _render_term(self, mask: int, dontcare: int) -> str:
        bits = []
        for pos in range(self.nbits - 1, -1, -1):
            if (dontcare >> pos) & 1:
                bits.append('-')
            else:
                bits.append('1' if (mask >> pos) & 1 else '0')
        return ''.join(bits)

    def _compute_primes_and_stages(self, start_terms: List[Tuple[int, int, int]]) -> Tuple[List[MergeStep], List[Tuple[int, int]]]:
        current = start_terms
        stages = []
        primes = []
        step = 1

        while current:
            # сохраняем этап
            str_terms = [self._render_term(m, dc) for (m, dc, _) in current]
            stages.append(MergeStep(step, tuple(str_terms)))

            used = set()
            next_map = {}
            for i in range(len(current)):
                for j in range(i+1, len(current)):
                    m1, dc1, _ = current[i]
                    m2, dc2, _ = current[j]
                    merged = self._merge_terms(m1, dc1, m2, dc2)
                    if merged:
                        nm, ndc = merged
                        cov = current[i][2] | current[j][2]
                        key = (nm, ndc)
                        # сохраняем максимальное покрытие
                        if key not in next_map or next_map[key][2] != cov:
                            next_map[key] = (nm, ndc, cov)
                        used.add(i)
                        used.add(j)

            for i, (m, dc, _) in enumerate(current):
                if i not in used:
                    primes.append((m, dc))

            if not next_map:
                break
            current = list(next_map.values())
            step += 1

        return stages, primes

    def _create_implicant_objects(self, primes: List[Tuple[int, int]], mode: str) -> List[Implicant]:
        targets = set(self._get_active_indices(mode))
        result = []
        for m, dc in primes:
            base = m & ~dc
            covered = frozenset(t for t in targets if (t & ~dc) == base)
            result.append(Implicant(m, dc, covered))
        return result

    def _exhaustive_cover(self, implicants: List[Implicant], universe: Set[int]) -> List[Implicant]:
        if not universe:
            return []
        best_cover = None
        best_cost = None
        for r in range(1, len(implicants) + 1):
            for combo in combinations(implicants, r):
                cover = set().union(*(imp.covered for imp in combo))
                if universe.issubset(cover):
                    cost = (sum(imp.literal_count for imp in combo), len(combo))
                    if best_cost is None or cost < best_cost:
                        best_cover = list(combo)
                        best_cost = cost
        return best_cover or []

    def _choose_essential_and_minimal(self, primes: List[Tuple[int, int]], mode: str) -> List[str]:
        implicants = self._create_implicant_objects(primes, mode)
        all_indices = set(self._get_active_indices(mode))
        if not all_indices:
            return []

        # карта покрытия
        coverage_map = {idx: [] for idx in all_indices}
        for imp in implicants:
            for idx in imp.covered:
                coverage_map[idx].append(imp)

        # существенные импликанты
        essential_imps = []
        for idx, imp_list in coverage_map.items():
            if len(imp_list) == 1:
                essential_imps.append(imp_list[0])

        selected = []
        remaining = set(all_indices)
        # уникализация
        for imp in dict.fromkeys(essential_imps):
            if imp not in selected:
                selected.append(imp)
                remaining -= imp.covered

        rest = [imp for imp in implicants if imp not in selected]
        selected.extend(self._exhaustive_cover(rest, remaining))

        # сбор уникальных паттернов
        patterns = []
        seen = set()
        for imp in selected:
            pat = self._render_term(imp.mask, imp.dontcare)
            if pat not in seen:
                patterns.append(pat)
                seen.add(pat)
        patterns.sort()
        return patterns

    def _pattern_to_expression(self, pattern: str, mode: str) -> str:
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
        op = " ∧ " if mode == 'DNF' else " ∨ "
        return parts[0] if len(parts) == 1 else f"({op.join(parts)})"

    def _join_expressions(self, patterns: List[str], mode: str) -> str:
        if not patterns:
            return "0" if mode == 'DNF' else "1"
        terms = [self._pattern_to_expression(p, mode) for p in patterns]
        terms.sort()
        sep = " ∨ " if mode == 'DNF' else " ∧ "
        return sep.join(terms)

    def run_qmc(self, mode: str = "DNF") -> QMCResult:
        mode = mode.upper()
        start = self._make_start_terms(mode)
        init_str = [self._render_term(m, dc) for (m, dc, _) in start]
        stages, primes = self._compute_primes_and_stages(start)
        selected = self._choose_essential_and_minimal(primes, mode)
        return QMCResult(
            mode=mode,
            initial_terms=init_str,
            merge_stages=stages,
            prime_implicants=[self._render_term(m, dc) for m, dc in primes],
            selected_patterns=selected,
            expression=self._join_expressions(selected, mode),
        )

    def generate_coverage_table(self, mode: str = "DNF") -> Dict:
        mode = mode.upper()
        start = self._make_start_terms(mode)
        init_str = [self._render_term(m, dc) for (m, dc, _) in start]
        stages, primes = self._compute_primes_and_stages(start)
        implicants = self._create_implicant_objects(primes, mode)
        targets = self._get_active_indices(mode)
        table_rows = []
        for imp in implicants:
            pat = self._render_term(imp.mask, imp.dontcare)
            row = {
                "pattern": pat,
                "expression": self._pattern_to_expression(pat, mode),
                "coverage": [1 if t in imp.covered else 0 for t in targets],
            }
            table_rows.append(row)
        selected = self._choose_essential_and_minimal(primes, mode)
        return {
            "mode": mode,
            "initial_terms": init_str,
            "stages": stages,
            "prime_implicants": [self._render_term(m, dc) for m, dc in primes],
            "coverage_table": table_rows,
            "selected_patterns": selected,
            "result": self._join_expressions(selected, mode),
        }

    # --- Карты Карно ---
    def _gray_sequence(self, bits: int) -> List[str]:
        if bits == 0:
            return [""]
        prev = self._gray_sequence(bits-1)
        return ["0"+x for x in prev] + ["1"+x for x in reversed(prev)]

    def _get_kmap_axes(self):
        n = self.nbits
        if n == 2:
            return ["a"], ["b"], None
        if n == 3:
            return [self.vars[0]], self.vars[1:], None
        if n == 4:
            return self.vars[:2], self.vars[2:], None
        if n == 5:
            return self.vars[:2], self.vars[2:4], self.vars[4]
        raise ValueError("Карта Карно для 2..5 переменных")

    def _build_kmap_layers(self, mode: str) -> Dict:
        row_vars, col_vars, extra = self._get_kmap_axes()
        row_codes = self._gray_sequence(len(row_vars))
        col_codes = self._gray_sequence(len(col_vars))
        layers = []

        if extra is None:
            grid = []
            for rc in row_codes:
                row = []
                for cc in col_codes:
                    idx_str = rc + cc
                    # для n=2,3,4 одинаково
                    idx = int(idx_str, 2)
                    row.append(self.vector[idx])
                grid.append((rc, row))
            layers.append({"extra_value": None, "rows": grid,
                          "row_codes": row_codes, "col_codes": col_codes})
        else:
            for extra_bit in ('0','1'):
                grid = []
                for rc in row_codes:
                    row = []
                    for cc in col_codes:
                        idx_str = rc + cc + extra_bit
                        idx = int(idx_str, 2)
                        row.append(self.vector[idx])
                    grid.append((rc, row))
                layers.append({"extra_value": extra_bit, "rows": grid,
                              "row_codes": row_codes, "col_codes": col_codes})

        result = self.run_qmc(mode)
        return {"layers": layers, "result": result.expression}

    def build_karnaugh_maps(self) -> Dict:
        return {"dnf": self._build_kmap_layers("DNF"), "knf": self._build_kmap_layers("KNF")}
