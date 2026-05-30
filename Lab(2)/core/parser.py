from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from constants import VALID_VARIABLES

class ExpressionError(ValueError):
    pass

@dataclass
class _Node:
    pass

@dataclass
class _VarNode(_Node):
    name: str

@dataclass
class _NotNode(_Node):
    child: _Node

@dataclass
class _BinNode(_Node):
    op: str
    left: _Node
    right: _Node

class ExpressionParser:
    """Рекурсивный парсер логических выражений."""

    _SYMBOLS = {
        '¬': '!', '∧': '&', '∨': '|', '→': '->', '↔': '~'
    }

    def __init__(self, raw_expression: str):
        self.raw = self._normalize(raw_expression)
        self.tokens = self._tokenize(self.raw)
        self._pos = 0
        self._ast = self._parse_implication()
        if self._pos != len(self.tokens):
            raise ExpressionError("Лишние символы после выражения")
        self.postfix = self._ast_to_postfix(self._ast)
        self._vars = None

    def _normalize(self, s: str) -> str:
        s = s.replace(' ', '')
        for old, new in self._SYMBOLS.items():
            s = s.replace(old, new)
        return s

    def _tokenize(self, s: str) -> List[str]:
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch in VALID_VARIABLES or ch in '()':
                tokens.append(ch)
                i += 1
            elif ch == '-' and i+1 < n and s[i+1] == '>':
                tokens.append('->')
                i += 2
            elif ch in ('!', '&', '|', '~'):
                tokens.append(ch)
                i += 1
            else:
                raise ExpressionError(f"Неизвестный символ: {ch}")
        return tokens

    def _peek(self) -> Optional[str]:
        return self.tokens[self._pos] if self._pos < len(self.tokens) else None

    def _consume(self, expected: Optional[str] = None) -> str:
        if self._pos >= len(self.tokens):
            raise ExpressionError("Неожиданный конец выражения")
        tok = self.tokens[self._pos]
        if expected is not None and tok != expected:
            raise ExpressionError(f"Ожидалось {expected}, получено {tok}")
        self._pos += 1
        return tok

    def _parse_primary(self) -> _Node:
        tok = self._peek()
        if tok is None:
            raise ExpressionError("Неожиданный конец")
        if tok == '(':
            self._consume('(')
            node = self._parse_implication()
            self._consume(')')
            return node
        if tok in VALID_VARIABLES:
            self._consume()
            return _VarNode(tok)
        if tok == '!':
            self._consume('!')
            return _NotNode(self._parse_primary())
        raise ExpressionError(f"Неожиданный токен: {tok}")

    def _parse_implication(self) -> _Node:
        left = self._parse_equivalence()
        while self._peek() == '->':
            self._consume('->')
            right = self._parse_equivalence()
            left = _BinNode('->', left, right)
        return left

    def _parse_equivalence(self) -> _Node:
        left = self._parse_or()
        while self._peek() == '~':
            self._consume('~')
            right = self._parse_or()
            left = _BinNode('~', left, right)
        return left

    def _parse_or(self) -> _Node:
        left = self._parse_and()
        while self._peek() == '|':
            self._consume('|')
            right = self._parse_and()
            left = _BinNode('|', left, right)
        return left

    def _parse_and(self) -> _Node:
        left = self._parse_primary()
        while self._peek() == '&':
            self._consume('&')
            right = self._parse_primary()
            left = _BinNode('&', left, right)
        return left

    def _ast_to_postfix(self, node: _Node) -> List[str]:
        if isinstance(node, _VarNode):
            return [node.name]
        if isinstance(node, _NotNode):
            return self._ast_to_postfix(node.child) + ['!']
        if isinstance(node, _BinNode):
            left = self._ast_to_postfix(node.left)
            right = self._ast_to_postfix(node.right)
            return left + right + [node.op]
        raise ExpressionError("Неизвестный узел AST")

    def evaluate(self, values: Dict[str, int]) -> int:
        stack = []
        for token in self.postfix:
            if token in VALID_VARIABLES:
                stack.append(bool(values[token]))
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
            elif token == '->':
                b = stack.pop()
                a = stack.pop()
                stack.append((not a) or b)
            elif token == '~':
                b = stack.pop()
                a = stack.pop()
                stack.append(a == b)
            else:
                raise ExpressionError(f"Неизвестный оператор: {token}")
        return int(stack[0])

    def variables(self) -> List[str]:
        if self._vars is None:
            seen = set()
            for tok in self.tokens:
                if tok in VALID_VARIABLES:
                    seen.add(tok)
            self._vars = sorted(seen, key=VALID_VARIABLES.index)
        return self._vars