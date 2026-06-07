from typing import List
from constants import TOTAL_BITS, SIGN_BIT_INDEX
from core.utils import BitUtils


class Codec:

    def __init__(self, word_size: int = TOTAL_BITS):
        self._size = word_size
        self._sign_pos = word_size - 1

    def _abs_to_bits(self, value: int) -> List[str]:
        result = ['0'] * self._size
        num = abs(value)
        for idx in range(self._size - 1, 0, -1):
            result[idx] = '1' if (num & 1) else '0'
            num >>= 1
        return result

    def to_direct(self, num: int) -> List[str]:
        bits = self._abs_to_bits(num)
        if num < 0:
            bits[self._sign_pos] = '1'
        return bits

    def to_inverse(self, num: int) -> List[str]:
        direct = self.to_direct(num)
        if num >= 0:
            return direct
        return BitUtils.invert_bits(direct, start=1)

    def to_complement(self, num: int) -> List[str]:
        if num >= 0:
            return self.to_direct(num)
        inv = self.to_inverse(num)
        return BitUtils.add_one(inv)

    def from_complement(self, bits: List[str]) -> int:
        if bits[self._sign_pos] == '0':
            val = 0
            for i in range(1, self._size):
                if bits[i] == '1':
                    val += 1 << (self._size - 1 - i)
            return val
        else:
            inverted = ['1' if b == '0' else '0' for b in bits]
            inverted[self._sign_pos] = '0'
            plus_one = BitUtils.add_one(inverted)
            val = 0
            for i in range(1, self._size):
                if plus_one[i] == '1':
                    val += 1 << (self._size - 1 - i)
            return -val
