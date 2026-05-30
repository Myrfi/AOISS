from constants import TOTAL_BITS, DIVISION_PRECISION, SIGN_BIT_INDEX
from core.binary_codes import BinaryConverter
from core.utils import BitUtils


class BinaryArithmetic:
    @staticmethod
    def add_additional(a, b):
        bits_a = BinaryConverter.to_additional_code(a)
        bits_b = BinaryConverter.to_additional_code(b)
        result, _ = BitUtils.add_unsigned(bits_a, bits_b)
        return result

    @staticmethod
    def subtract_additional(a, b):
        # a - b это a + (-b)
        bits_a = BinaryConverter.to_additional_code(a)
        bits_neg_b = BinaryConverter.to_additional_code(-b)
        result, _ = BitUtils.add_unsigned(bits_a, bits_neg_b)
        return result

    @staticmethod
    def multiply_direct(a, b):
        sign = "1" if (a < 0) != (b < 0) else "0"
        a_bits = BinaryConverter.decimal_to_binary(abs(a))
        b_bits = BinaryConverter.decimal_to_binary(abs(b))

        result = ["0"] * TOTAL_BITS
        for i in range(TOTAL_BITS - 1, 0, -1):
            if b_bits[i] == "1":
                # Сдвиг a_bits влево
                shift = (TOTAL_BITS - 1) - i
                shifted_a = a_bits[shift:] + ["0"] * shift
                result, _ = BitUtils.add_unsigned(result, shifted_a)

        result[SIGN_BIT_INDEX] = sign
        return result

    @staticmethod
    def divide_direct(a, b):
        sign = "1" if (a < 0) != (b < 0) else "0"
        q_int = abs(a) // abs(b)
        rem = abs(a) % abs(b)
        rem_initial = abs(a) % abs(b)

        frac_bits = []
        for _ in range(DIVISION_PRECISION):
            rem *= 2
            if rem >= abs(b):
                frac_bits.append("1")
                rem -= abs(b)
            else:
                frac_bits.append("0")

        q_bits = BinaryConverter.decimal_to_binary(q_int)
        q_bits[SIGN_BIT_INDEX] = sign
        return q_bits, BinaryConverter.decimal_to_binary(rem_initial), frac_bits