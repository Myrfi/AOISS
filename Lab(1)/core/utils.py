from constants import TOTAL_BITS


class BitOps:

    @staticmethod
    def add_bits(x, y):
        out = ['0'] * TOTAL_BITS
        carry = 0
        for idx in range(TOTAL_BITS - 1, -1, -1):
            sx = 1 if x[idx] == '1' else 0
            sy = 1 if y[idx] == '1' else 0
            s = sx + sy + carry
            out[idx] = '1' if (s & 1) else '0'
            carry = 1 if s >= 2 else 0
        return out, '1' if carry else '0'

    @staticmethod
    def flip_bits(data, start=0):
        flipped = data[:]
        for i in range(start, len(flipped)):
            flipped[i] = '0' if flipped[i] == '1' else '1'
        return flipped

    @staticmethod
    def increment(code):
        one = ['0'] * TOTAL_BITS
        one[-1] = '1'
        inc, _ = BitOps.add_bits(code, one)
        return inc
