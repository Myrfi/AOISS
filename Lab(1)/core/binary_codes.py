from constants import TOTAL_BITS, SIGN_BIT_INDEX
from core.utils import BitUtils

class BinaryConverter:
    @staticmethod
    def decimal_to_binary(number):
        """Перевод модуля числа в двоичный массив (делением на 2)"""
        res = ["0"] * TOTAL_BITS
        n = abs(number)
        for i in range(TOTAL_BITS - 1, 0, -1):
            res[i] = "1" if n % 2 != 0 else "0"
            n //= 2
        return res

    @staticmethod
    def to_direct_code(number):
        bits = BinaryConverter.decimal_to_binary(number)
        if number < 0:
            bits[SIGN_BIT_INDEX] = "1"
        return bits

    @staticmethod
    def to_reverse_code(number):
        direct = BinaryConverter.to_direct_code(number)
        if number >= 0:
            return direct
        return BitUtils.invert_bits(direct, 1)

    @staticmethod
    def to_additional_code(number):
        if number >= 0:
            return BinaryConverter.to_direct_code(number)
        reverse = BinaryConverter.to_reverse_code(number)
        return BitUtils.add_one(reverse)

    @staticmethod
    def from_additional_code(bits):
        """Перевод из доп. кода в 10-ное число (для проверки)"""
        res = 0
        if bits[SIGN_BIT_INDEX] == "1":
            res = -(2 ** (TOTAL_BITS - 1))
        for i in range(1, TOTAL_BITS):
            if bits[i] == "1":
                res += 2 ** (TOTAL_BITS - 1 - i)
        return res