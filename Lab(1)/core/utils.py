from constants import TOTAL_BITS


class BitUtils:
    @staticmethod
    def add_unsigned(a, b):
        """Простое сложение двух массивов бит столбиком"""
        result = ["0"] * TOTAL_BITS
        carry = 0
        for i in range(TOTAL_BITS - 1, -1, -1):
            bit_a = 1 if a[i] == "1" else 0
            bit_b = 1 if b[i] == "1" else 0
            total = bit_a + bit_b + carry

            result[i] = "1" if total % 2 != 0 else "0"
            carry = 1 if total >= 2 else 0

        return result, "1" if carry else "0"

    @staticmethod
    def invert_bits(bits, start_index=0):
        """Замена 0 на 1 и наоборот"""
        res = bits[:]
        for i in range(start_index, len(res)):
            res[i] = "1" if res[i] == "0" else "0"
        return res

    @staticmethod
    def add_one(bits):
        """Прибавление единицы (нужно для доп. кода)"""
        one = ["0"] * TOTAL_BITS
        one[-1] = "1"
        res, _ = BitUtils.add_unsigned(bits, one)
        return res