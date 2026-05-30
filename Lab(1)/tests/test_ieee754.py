from constants import TOTAL_BITS
from core.ieee754 import IEEE754Float


def test_ieee754():
    # Разные ветки нормализации
    assert IEEE754Float.encode(0.0) == ["0"] * TOTAL_BITS
    assert IEEE754Float.encode(1.5)[0] == "0"  # Целая часть > 0
    assert IEEE754Float.encode(-0.25)[0] == "1"  # Целая 0, есть дробная

    # Арифметические обертки (проверка значений)
    _, v = IEEE754Float.add(1.5, 2.5)
    assert v == 4.0
    _, v = IEEE754Float.subtract(2.5, 1.5)
    assert v == 1.0
    _, v = IEEE754Float.multiply(2.0, 3.0)
    assert v == 6.0
    _, v = IEEE754Float.divide(6.0, 2.0)
    assert v == 3.0