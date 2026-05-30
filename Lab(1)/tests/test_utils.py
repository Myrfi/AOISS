from constants import TOTAL_BITS
from core.utils import BitUtils


def test_bit_utils():
    zeroes = ["0"] * TOTAL_BITS
    ones = ["1"] * TOTAL_BITS

    # Сложение
    res, carry = BitUtils.add_unsigned(zeroes, ones)
    assert res == ones
    assert carry == "0"

    # Инверсия
    assert BitUtils.invert_bits(zeroes) == ones

    # Прибавление 1 (проверяем, что последний бит стал 1)
    added = BitUtils.add_one(zeroes)
    assert added[-1] == "1"