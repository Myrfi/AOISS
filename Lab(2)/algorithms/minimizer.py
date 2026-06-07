from __future__ import annotations

import enum
from collections import deque
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union


class LogicForm(enum.IntEnum):
    SOP = 1
    POS = 0


@dataclass(slots=True, frozen=True)
class Cube:
    ones: int
    dontc: int
    covered_mask: int = field(hash=False, compare=False)

    @property
    def literals(self) -> int:
        return (self.ones & ~self.dontc).bit_count()

    def to_str(self, bits: int, symbols: Sequence[str]) -> str:
        out = []
        for pos in range(bits - 1, -1, -1):
            if (self.dontc >> pos) & 1:
                out.append('-')
            else:
                out.append('1' if (self.ones >> pos) & 1 else '0')
        return ''.join(out)


@dataclass(slots=True)
class MergeSnapshot:
    level: int
    cubes: Tuple[str, ...]


class QMCKernel:
    __slots__ = ('_data', '_names', '_dim', '_cache')

    def __init__(self, truth_vector: Sequence[int], var_labels: Sequence[str]):
        self._data = list(truth_vector)
        self._names = list(var_labels)
        self._dim = len(self._names)
        expected = 1 << self._dim
        if len(self._data) != expected:
            raise ValueError(f"Need {expected} values, got {len(self._data)}")
        self._cache = {}

    def _indices_of(self, form: LogicForm) -> List[int]:
        target = 1 if form == LogicForm.SOP else 0
        return [i for i, v in enumerate(self._data) if v == target]

    @staticmethod
    def _try_merge(a: Cube, b: Cube) -> Optional[Tuple[int, int]]:
        if a.dontc != b.dontc:
            return None
        diff = (a.ones ^ b.ones) & ~a.dontc
        if diff == 0 or (diff & (diff - 1)) != 0:
            return None
        return (a.ones & b.ones, a.dontc | diff)

    def _make_start_cubes(self, form: LogicForm) -> List[Cube]:
        return [Cube(ones=i, dontc=0, covered_mask=1 << i) for i in self._indices_of(form)]

    def _compute_primes_and_stages(self, start: List[Cube]) -> Tuple[List[MergeSnapshot], List[Cube]]:
        current = start[:]
        stages = []
        primes = []
        step = 0

        while current:
            step += 1
            stages.append(MergeSnapshot(
                level=step,
                cubes=tuple(c.to_str(self._dim, self._names) for c in current)
            ))

            used = set()
            merged_dict = {}
            n = len(current)
            for i in range(n):
                for j in range(i + 1, n):
                    res = self._try_merge(current[i], current[j])
                    if res is None:
                        continue
                    new_ones, new_dc = res
                    combined_cover = current[i].covered_mask | current[j].covered_mask
                    key = (new_ones, new_dc)
                    if key not in merged_dict or merged_dict[key].covered_mask != combined_cover:
                        merged_dict[key] = Cube(new_ones, new_dc, combined_cover)
                    used.update([i, j])

            for idx, cub in enumerate(current):
                if idx not in used:
                    primes.append(cub)

            if not merged_dict:
                break
            current = list(merged_dict.values())

        return stages, primes

    def _build_coverage_index(self, primes: List[Cube], form: LogicForm) -> Dict[int, List[Cube]]:
        all_minterms = set(self._indices_of(form))
        coverage = {mt: [] for mt in all_minterms}
        for cub in primes:
            for mt in all_minterms:
                if (cub.covered_mask >> mt) & 1:
                    coverage[mt].append(cub)
        return coverage

    @staticmethod
    def _cube_cost(cube: Cube) -> int:
        return cube.literals

    def _select_minimum_cover(self, primes: List[Cube], form: LogicForm) -> List[str]:
        all_mts = set(self._indices_of(form))
        if not all_mts:
            return []

        cov_map = self._build_coverage_index(primes, form)

        essential_cubes = []
        for mt, cube_list in cov_map.items():
            if len(cube_list) == 1:
                essential_cubes.append(cube_list[0])

        selected = []
        remaining = all_mts.copy()
        for cub in dict.fromkeys(essential_cubes):
            if cub not in selected:
                selected.append(cub)
                remaining.discard(cub.covered_mask)

        covered_by_selected = 0
        for cub in selected:
            covered_by_selected |= cub.covered_mask
        remaining_mts = {mt for mt in all_mts if not ((covered_by_selected >> mt) & 1)}

        rest = [cub for cub in primes if cub not in selected]

        best_cover = []
        best_cost = (float('inf'), float('inf'))
        for r in range(1, len(rest) + 1):
            for combo in combinations(rest, r):
                covered = 0
                total_lit = 0
                for cub in combo:
                    covered |= cub.covered_mask
                    total_lit += cub.literals
                if all((covered >> mt) & 1 for mt in remaining_mts):
                    cost = (total_lit, len(combo))
                    if cost < best_cost:
                        best_cover = list(combo)
                        best_cost = cost

        selected.extend(best_cover)

        patterns = []
        seen = set()
        for cub in selected:
            pat = cub.to_str(self._dim, self._names)
            if pat not in seen:
                patterns.append(pat)
                seen.add(pat)
        patterns.sort()
        return patterns

    def _cube_to_expr(self, pattern: str, form: LogicForm) -> str:
        parts = []
        for sym, ch in zip(self._names, pattern):
            if ch == '-':
                continue
            if form == LogicForm.SOP:
                parts.append(sym if ch == '1' else f"¬{sym}")
            else:
                parts.append(sym if ch == '0' else f"¬{sym}")
        if not parts:
            return "1" if form == LogicForm.SOP else "0"
        connector = " ∧ " if form == LogicForm.SOP else " ∨ "
        if len(parts) == 1:
            return parts[0]
        return f"({connector.join(parts)})"

    def _assemble_expression(self, patterns: List[str], form: LogicForm) -> str:
        if not patterns:
            return "0" if form == LogicForm.SOP else "1"
        terms = [self._cube_to_expr(p, form) for p in patterns]
        terms.sort()
        sep = " ∨ " if form == LogicForm.SOP else " ∧ "
        return sep.join(terms)

    def run(self, form: Union[str, LogicForm] = "SOP") -> Dict:
        if isinstance(form, str):
            form = LogicForm.SOP if form.upper() in ("SOP", "DNF") else LogicForm.POS
        start = self._make_start_cubes(form)
        stages, primes = self._compute_primes_and_stages(start)
        selected = self._select_minimum_cover(primes, form)
        return {
            "form": form.name,
            "start": [c.to_str(self._dim, self._names) for c in start],
            "steps": stages,
            "prime_cubes": [c.to_str(self._dim, self._names) for c in primes],
            "chosen": selected,
            "result": self._assemble_expression(selected, form),
        }

    def with_coverage_table(self, form: Union[str, LogicForm] = "SOP") -> Dict:
        if isinstance(form, str):
            form = LogicForm.SOP if form.upper() in ("SOP", "DNF") else LogicForm.POS
        start = self._make_start_cubes(form)
        stages, primes = self._compute_primes_and_stages(start)
        selected = self._select_minimum_cover(primes, form)
        targets = self._indices_of(form)
        table = []
        for c in primes:
            pat = c.to_str(self._dim, self._names)
            row = {
                "cube": pat,
                "expr": self._cube_to_expr(pat, form),
                "covers": [1 if (c.covered_mask >> t) & 1 else 0 for t in targets],
            }
            table.append(row)
        return {
            "form": form.name,
            "start": [c.to_str(self._dim, self._names) for c in start],
            "steps": stages,
            "prime_cubes": [c.to_str(self._dim, self._names) for c in primes],
            "table": table,
            "chosen": selected,
            "result": self._assemble_expression(selected, form),
        }

    @staticmethod
    def _gray_code(bits: int) -> List[str]:
        if bits == 0:
            return [""]
        prev = QMCKernel._gray_code(bits - 1)
        return ["0" + x for x in prev] + ["1" + x for x in reversed(prev)]

    def _karnaugh_axes(self):
        d = self._dim
        if d == 2:
            return ["a"], ["b"], None
        if d == 3:
            return [self._names[0]], self._names[1:], None
        if d == 4:
            return self._names[:2], self._names[2:], None
        if d == 5:
            return self._names[:2], self._names[2:4], self._names[4]
        raise NotImplementedError("Karnaugh map only for 2..5 variables")

    def _kmap_structure(self, form: LogicForm) -> Dict:
        rvars, cvars, extra = self._karnaugh_axes()
        rcode = self._gray_code(len(rvars))
        ccode = self._gray_code(len(cvars))
        layers = []
        if extra is None:
            grid = [(rc, [self._data[int(rc + cc, 2)] for cc in ccode]) for rc in rcode]
            layers.append({"extra": None, "grid": grid, "row_codes": rcode, "col_codes": ccode})
        else:
            for eb in ('0', '1'):
                grid = [(rc, [self._data[int(rc + cc + eb, 2)] for cc in ccode]) for rc in rcode]
                layers.append({"extra": eb, "grid": grid, "row_codes": rcode, "col_codes": ccode})
        min_result = self.run(form)
        return {"layers": layers, "result": min_result["result"]}

    def karnaugh_maps(self) -> Dict:
        return {"SOP": self._kmap_structure(LogicForm.SOP), "POS": self._kmap_structure(LogicForm.POS)}
