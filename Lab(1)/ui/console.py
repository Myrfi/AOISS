from core.codec import Codec
from core.binary_ops import BinaryOps
from core.float_codec import FloatCodec
from core.bcd_excess3 import BCDExcess3
from ui.menu import Menu


class ConsoleUI:
    @staticmethod
    def print_bits(title, bits, decimal_value=None, is_ieee=False):
        print(f"{title}:")
        bits_str = "".join(bits)

        if is_ieee and len(bits_str) == 32:
            formatted_str = f"{bits_str[0]} {bits_str[1:9]} {bits_str[9:]}"
            print(f"  2-ой формат: {formatted_str}")
        else:
            print(f"  2-ой формат: {bits_str}")

        if decimal_value is not None:
            print(f"  10-ый формат: {decimal_value}")

    def run(self):
        conv = Codec()
        while True:
            Menu.show()
            choice = input("Выбор: ").strip()
            if choice == "0":
                break

            try:
                if choice == "1":
                    n = int(input("Введите число: "))
                    d = conv.to_direct(n)
                    r = conv.to_inverse(n)
                    c = conv.to_complement(n)
                    self.print_bits("Прямой", d)
                    self.print_bits("Обратный", r)
                    self.print_bits("Дополнительный", c)

                elif choice == "2":
                    a = int(input("A: "))
                    b = int(input("B: "))
                    res = BinaryOps.add_comp(a, b)
                    dec_val = conv.from_complement(res)
                    self.print_bits("Сумма", res, dec_val)

                elif choice == "3":
                    a = int(input("Уменьшаемое: "))
                    b = int(input("Вычитаемое: "))
                    res = BinaryOps.sub_comp(a, b)
                    dec_val = conv.from_complement(res)
                    self.print_bits("Разность", res, dec_val)

                elif choice == "4":
                    a = int(input("A: "))
                    b = int(input("B: "))
                    res = BinaryOps.mul_raw(a, b)
                    self.print_bits("Умножение", res)

                elif choice == "5":
                    a = int(input("Делимое: "))
                    b = int(input("Делитель: "))
                    q_bits, rem_bits, frac = BinaryOps.div_raw(a, b)
                    self.print_bits("Целая часть", q_bits)
                    self.print_bits("Остаток", rem_bits)
                    frac_str = "".join(frac)
                    print(f"  Дробная часть: {frac_str}")

                elif choice in ["6", "7", "8", "9"]:
                    a = float(input("A: "))
                    b = float(input("B: "))
                    if choice == "6":
                        bits, val = FloatCodec.add(a, b)
                    elif choice == "7":
                        bits, val = FloatCodec.sub(a, b)
                    elif choice == "8":
                        bits, val = FloatCodec.mul(a, b)
                    else:
                        bits, val = FloatCodec.div(a, b)
                    self.print_bits("IEEE-754 Результат", bits, val, is_ieee=True)

                elif choice == "10":
                    a = int(input("A: "))
                    b = int(input("B: "))
                    res = BCDExcess3.add(a, b)
                    res_str = "".join(res)
                    formatted_bcd = " ".join(res_str[i:i+4] for i in range(0, 32, 4))
                    dec_sum = a + b
                    print("Excess-3 Результат:")
                    print(f"  2-ой формат: {formatted_bcd}")
                    print(f"  10-ый формат: {dec_sum}")

            except Exception as e:
                print(f"Ошибка: {e}")
