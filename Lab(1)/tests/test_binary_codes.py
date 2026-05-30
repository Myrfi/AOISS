from core.binary_codes import BinaryConverter


def test_binary_converter():
    # Проверка перевода туда и обратно
    assert BinaryConverter.from_additional_code(BinaryConverter.to_additional_code(5)) == 5
    assert BinaryConverter.from_additional_code(BinaryConverter.to_additional_code(-5)) == -5

    # Прямой и обратный коды
    dir_pos = BinaryConverter.to_direct_code(10)
    dir_neg = BinaryConverter.to_direct_code(-10)
    assert dir_pos[0] == "0"
    assert dir_neg[0] == "1"

    rev_pos = BinaryConverter.to_reverse_code(10)
    rev_neg = BinaryConverter.to_reverse_code(-10)
    assert rev_pos == dir_pos
    assert rev_neg[0] == "1"