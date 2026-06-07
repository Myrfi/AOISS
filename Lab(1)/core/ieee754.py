from struct import pack, unpack


class FloatCodec:

    @staticmethod
    def pack(x: float) -> int:
        return unpack('>I', pack('>f', x))[0]

    @staticmethod
    def unpack(bits: int) -> float:
        return unpack('>f', pack('>I', bits))[0]

    @classmethod
    def to_bits(cls, value: float) -> list:
        if value == 0.0:
            return ['0'] * 32
        bits = cls.pack(value)
        return [str((bits >> i) & 1) for i in range(31, -1, -1)]

    @classmethod
    def from_bits(cls, bits: list) -> float:
        if all(b == '0' for b in bits):
            return 0.0
        val = 0
        for b in bits:
            val = (val << 1) | (1 if b == '1' else 0)
        return cls.unpack(val)

    @classmethod
    def add(cls, a: float, b: float) -> tuple:
        res = a + b
        return cls.to_bits(res), res

    @classmethod
    def sub(cls, a: float, b: float) -> tuple:
        res = a - b
        return cls.to_bits(res), res

    @classmethod
    def mul(cls, a: float, b: float) -> tuple:
        res = a * b
        return cls.to_bits(res), res

    @classmethod
    def div(cls, a: float, b: float) -> tuple:
        res = a / b
        return cls.to_bits(res), res
