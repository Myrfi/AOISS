from core.arithmetic import BinaryArithmetic
from core.binary_codes import BinaryConverter
from constants import TOTAL_BITS, DIVISION_PRECISION, SIGN_BIT_INDEX

def test_binary_arithmetic():
    # Сложение
    res_add = BinaryArithmetic.add_additional(10, -3)
    assert BinaryConverter.from_additional_code(res_add) == 7

    # Вычитание
    res_sub = BinaryArithmetic.subtract_additional(10, 15)
    assert BinaryConverter.from_additional_code(res_sub) == -5

    # Умножение
    res_mul_pos = BinaryArithmetic.multiply_direct(4, 2)
    assert res_mul_pos[0] == "0"  # Знак +
    res_mul_neg = BinaryArithmetic.multiply_direct(-4, 2)
    assert res_mul_neg[0] == "1"  # Знак -

    # Деление
    q, r, f = BinaryArithmetic.divide_direct(10, -3)
    assert q[0] == "1"  # Знак -
    q, r, f = BinaryArithmetic.divide_direct(4, 2)
    assert q[0] == "0"