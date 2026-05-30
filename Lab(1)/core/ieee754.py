from constants import TOTAL_BITS


class IEEE754Float:
    @staticmethod
    def encode(value):
        if value == 0.0:
            return ["0"] * TOTAL_BITS

        sign = "1" if value < 0 else "0"
        val = abs(value)

        int_part = int(val)
        frac_part = val - int_part

        # Целая часть в биты
        int_bits = []
        while int_part > 0:
            int_bits.insert(0, str(int_part % 2))
            int_part //= 2

        # Дробная часть в биты
        frac_bits = []
        while frac_part > 0 and len(frac_bits) < 32:
            frac_part *= 2
            frac_bits.append(str(int(frac_part)))
            frac_part -= int(frac_part)

        # Нормализация
        if int_bits:
            exponent = len(int_bits) - 1
            mantissa = int_bits[1:] + frac_bits
        else:
            if "1" in frac_bits:
                first_one = frac_bits.index("1")
                exponent = -(first_one + 1)
                mantissa = frac_bits[first_one + 1:]
            else:
                exponent = 0
                mantissa = []

        # Смещение экспоненты
        exp_val = exponent + 127
        exp_bits = ["0"] * 8
        for i in range(7, -1, -1):
            exp_bits[i] = "1" if exp_val % 2 != 0 else "0"
            exp_val //= 2

        mantissa_bits = (mantissa + ["0"] * 23)[:23]
        return [sign] + exp_bits + mantissa_bits

    @staticmethod
    def add(a, b):
        return IEEE754Float.encode(a + b), a + b

    @staticmethod
    def subtract(a, b):
        return IEEE754Float.encode(a - b), a - b

    @staticmethod
    def multiply(a, b):
        return IEEE754Float.encode(a * b), a * b

    @staticmethod
    def divide(a, b):
        return IEEE754Float.encode(a / b), a / b