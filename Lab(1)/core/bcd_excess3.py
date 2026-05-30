from core.utils import BitUtils


class BCDExcess3:
    @staticmethod
    def encode_digit(d):
        """Перевод одной цифры в 4 бита Excess-3 (+3)"""
        val = d + 3
        bits = ["0"] * 4
        for i in range(3, -1, -1):
            bits[i] = "1" if val % 2 != 0 else "0"
            val //= 2
        return bits

    @staticmethod
    def encode(number):
        s = str(abs(number)).zfill(8)  # 8 цифр
        res = []
        for char in s:
            res.extend(BCDExcess3.encode_digit(int(char)))
        return res

    @staticmethod
    def add_4_bits(a, b, carry_in):
        res = ["0"] * 4
        c = carry_in
        for i in range(3, -1, -1):
            total = (1 if a[i] == "1" else 0) + (1 if b[i] == "1" else 0) + c
            res[i] = "1" if total % 2 != 0 else "0"
            c = 1 if total >= 2 else 0
        return res, c

    @staticmethod
    def add(a, b):
        if (a >= 0 and b >= 0) or (a < 0 and b < 0):
            result_abs = abs(a) + abs(b)
            sign = -1 if (a < 0 and b < 0) else 1
            bits = BCDExcess3.encode(result_abs)
            return bits
        else:
            abs_a = abs(a)
            abs_b = abs(b)
            if abs_a >= abs_b:
                result_abs = abs_a - abs_b
                sign = 1 if a >= 0 else -1
            else:
                result_abs = abs_b - abs_a
                sign = 1 if b >= 0 else -1
            bits = BCDExcess3.encode(result_abs)
            return bits