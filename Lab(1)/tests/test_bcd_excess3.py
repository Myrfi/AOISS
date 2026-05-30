from core.bcd_excess3 import BCDExcess3


def test_bcd_excess3():
    # Кодирование одиночных цифр
    assert BCDExcess3.encode_digit(0) == ["0", "0", "1", "1"]  # 0+3 = 3
    assert BCDExcess3.encode_digit(9) == ["1", "1", "0", "0"]  # 9+3 = 12

    # Сложение с коррекцией (проверяем обе ветки: с переносом и без)
    # 18 + 15 = 33. Здесь будут ветки как carry=1, так и carry=0
    res = BCDExcess3.add(18, 15)
    assert len(res) == 32