from constants import TOTAL_BITS, DIVISION_PRECISION, SIGN_BIT_INDEX
from core.binary_codes import BinaryConverter
from core.utils import BitUtils


class BinaryOps:

    @staticmethod
    def add_comp(x, y):
        cx = BinaryConverter.to_additional_code(x)
        cy = BinaryConverter.to_additional_code(y)
        s, _ = BitUtils.add_unsigned(cx, cy)
        return s

    @staticmethod
    def sub_comp(x, y):
        cx = BinaryConverter.to_additional_code(x)
        cneg = BinaryConverter.to_additional_code(-y)
        d, _ = BitUtils.add_unsigned(cx, cneg)
        return d

    @staticmethod
    def mul_raw(p, q):
        sign_bit = "1" if (p < 0) ^ (q < 0) else "0"
        up = BinaryConverter.decimal_to_binary(abs(p))
        uq = BinaryConverter.decimal_to_binary(abs(q))

        acc = ["0"] * TOTAL_BITS
        for pos in range(TOTAL_BITS - 1, 0, -1):
            if uq[pos] == "1":
                shift = (TOTAL_BITS - 1) - pos
                shifted = up[shift:] + ["0"] * shift
                acc, _ = BitUtils.add_unsigned(acc, shifted)

        acc[SIGN_BIT_INDEX] = sign_bit
        return acc

    @staticmethod
    def div_raw(dividend, divisor):
        out_sign = "1" if (dividend < 0) ^ (divisor < 0) else "0"
        a_abs = abs(dividend)
        b_abs = abs(divisor)
        int_part = a_abs // b_abs
        rem_start = a_abs % b_abs

        fract = []
        rem = rem_start
        for _ in range(DIVISION_PRECISION):
            rem <<= 1
            if rem >= b_abs:
                fract.append("1")
                rem -= b_abs
            else:
                fract.append("0")

        int_bits = BinaryConverter.decimal_to_binary(int_part)
        int_bits[SIGN_BIT_INDEX] = out_sign
        rem_bits = BinaryConverter.decimal_to_binary(rem_start)
        return int_bits, rem_bits, fract
