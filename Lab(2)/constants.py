from __future__ import annotations

# Допустимые имена переменных (до 5 штук)
VALID_VARIABLES = ('a', 'b', 'c', 'd', 'e')

# Приоритет операторов (чем больше число, тем выше)
PRECEDENCE = {
    '!': 5,
    '&': 4,
    '|': 3,
    '->': 2,
    '~': 1,
}

# Ассоциативность: 'left' или 'right'
ASSOCIATIVITY = {
    '!': 'right',
    '&': 'left',
    '|': 'left',
    '->': 'right',
    '~': 'left',
}

OPERATORS = set(PRECEDENCE)
UNARY_OPERATORS = {'!'}
BINARY_OPERATORS = {'&', '|', '->', '~'}