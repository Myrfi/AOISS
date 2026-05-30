from core.binary_codes import BinaryConverter
from core.arithmetic import BinaryArithmetic
from core.ieee754 import IEEE754Float
from core.bcd_excess3 import BCDExcess3
from ui.menu import Menu


class ConsoleUI:
    @staticmethod
    def print_bits(title, bits, decimal_value=None, is_ieee=False):
        print(f"{title}:")
        bits_str = "".join(bits)

        # Если это формат IEEE-754, делим строку на 1, 8 и 23 бита
        if is_ieee and len(bits_str) == 32:
            formatted_str = f"{bits_str[0]} {bits_str[1:9]} {bits_str[9:]}"
            print(f"  2-ой формат: {formatted_str}")
        else:
            print(f"  2-ой формат: {bits_str}")

        if decimal_value is not None:
            print(f"  10-ый формат: {decimal_value}")

    def run(self):
        while True:
            Menu.show()
            choice = input("Выбор: ").strip()
            if choice == "0":
                break

            try:
                if choice == "1":
                    n = int(input("Введите число: "))
                    d = BinaryConverter.to_direct_code(n)
                    r = BinaryConverter.to_reverse_code(n)
                    c = BinaryConverter.to_additional_code(n)
                    self.print_bits("Прямой", d)
                    self.print_bits("Обратный", r)
                    self.print_bits("Дополнительный", c)

                elif choice == "2":
                    a = int(input("A: "))
                    b = int(input("B: "))
                    res = BinaryArithmetic.add_additional(a, b)
                    dec_val = BinaryConverter.from_additional_code(res)
                    self.print_bits("Сумма", res, dec_val)

                elif choice == "3":
                    a = int(input("Уменьшаемое: "))
                    b = int(input("Вычитаемое: "))
                    res = BinaryArithmetic.subtract_additional(a, b)
                    dec_val = BinaryConverter.from_additional_code(res)
                    self.print_bits("Разность", res, dec_val)

                elif choice == "4":
                    a = int(input("A: "))
                    b = int(input("B: "))
                    res = BinaryArithmetic.multiply_direct(a, b)
                    self.print_bits("Умножение", res)

                elif choice == "5":
                    a = int(input("Делимое: "))
                    b = int(input("Делитель: "))
                    q, r, frac = BinaryArithmetic.divide_direct(a, b)
                    self.print_bits("Целая часть", q)
                    self.print_bits("Остаток", r)
                    frac_str = "".join(frac)
                    print(f"  Дробная часть: {frac_str}")

                elif choice in ["6", "7", "8", "9"]:
                    a = float(input("A: "))
                    b = float(input("B: "))
                    if choice == "6": bits, val = IEEE754Float.add(a, b)
                    if choice == "7": bits, val = IEEE754Float.subtract(a, b)
                    if choice == "8": bits, val = IEEE754Float.multiply(a, b)
                    if choice == "9": bits, val = IEEE754Float.divide(a, b)

                    # Передаем флаг is_ieee=True для красивого разделения
                    self.print_bits("IEEE-754 Результат", bits, val, is_ieee=True)

                elif choice == "10":
                    a = int(input("A: "))
                    b = int(input("B: "))

                    res = BCDExcess3.add(a, b)

                    res_str = "".join(res)
                    formatted_bcd = " ".join(res_str[i:i + 4] for i in range(0, 32, 4))
                    dec_sum = a + b

                    print("Excess-3 Результат:")
                    print(f"  2-ой формат: {formatted_bcd}")
                    print(f"  10-ый формат: {dec_sum}")

            except Exception as e:
                print(f"Ошибка: {e}")