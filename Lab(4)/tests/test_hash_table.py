import pytest

from src.data import DEFAULT_TERMS, populate_with_defaults
from src.hash_table import HashCell, HashTable


def test_v_calculation_is_correct():
    ht = HashTable()

    assert ht.calculate_v("существительное") == 18 * 33 + 20
    assert ht.h1(614) == 16
    assert ht.h2(614) == 21


@pytest.mark.parametrize("bad_key", ["", "а", "aб", "1а"])
def test_calculation_raises_on_bad_inputs(bad_key):
    ht = HashTable()
    with pytest.raises(ValueError):
        ht.calculate_v(bad_key)


def test_constructor_validates_min_size():
    with pytest.raises(ValueError):
        HashTable(size=19)


def test_insertion_and_finding_with_collisions(capsys):
    ht = HashTable()

    assert ht.insert("существительное", "предмет") is True
    assert ht.insert("суффикс", "часть слова") is True

    res1 = ht.search("существительное")
    res2 = ht.search("суффикс")

    assert res1 is not None
    assert res2 is not None
    assert res1.value == "предмет"
    assert res2.value == "часть слова"
    assert res1.h == res2.h == 16
    assert res1.key != res2.key

    stdout_log = capsys.readouterr().out
    assert "Итерация 1" in stdout_log


def test_insertion_blocks_duplicates(capsys):
    ht = HashTable()

    assert ht.insert("глагол", "действие") is True
    assert ht.insert("глагол", "дубликат") is False

    found_cells = [c for c in ht.table if c.has_data and c.key == "глагол"]
    assert len(found_cells) == 1
    assert found_cells[0].value == "действие"
    assert "Отмена: термин уже существует" in capsys.readouterr().out


def test_insertion_fails_gracefully_on_empty_keys():
    ht = HashTable()

    assert ht.insert("", "пусто") is False
    assert ht.insert("ab", "латиница") is False


def test_lazy_delete_keeps_chain_intact():
    ht = HashTable()
    ht.insert("предлог", "служебная часть речи")
    ht.insert("причастие", "форма глагола")

    assert ht.delete("предлог") is True
    freed_slot = ht.table[16]

    assert freed_slot.has_data is False
    assert freed_slot.is_freed is True
    assert ht.search("причастие").value == "форма глагола"
    assert ht.search("предлог") is None


def test_insertion_reclaims_tombstone_cells():
    ht = HashTable()
    ht.insert("предлог", "служебная часть речи")
    ht.insert("причастие", "форма глагола")
    ht.delete("предлог")

    assert ht.insert("приставка", "часть слова перед корнем") is True

    reclaimed = ht.table[16]
    assert reclaimed.key == "приставка"
    assert reclaimed.has_data is True
    assert reclaimed.is_freed is False


def test_delete_handles_non_existent():
    ht = HashTable()

    assert ht.delete("наречие") is False
    assert ht.delete("x") is False


def test_search_handles_non_existent():
    ht = HashTable()

    assert ht.search("наречие") is None
    assert ht.search("x") is None


def test_load_factor_computation():
    ht = HashTable()
    populate_with_defaults(ht, display_info=False)

    assert len(DEFAULT_TERMS) == 12
    assert ht.load_factor() == pytest.approx(12 / 23)


def test_load_factor_printing(capsys):
    ht = HashTable()
    ht.insert("союз", "служебная часть речи")

    ht.print_load_factor()

    assert "Метрика заполненности: 1 из 23 (α = 0.04)" in capsys.readouterr().out


def test_printing_displays_proper_flags(capsys):
    ht = HashTable()
    ht.insert("предлог", "служебная часть речи")
    ht.delete("предлог")

    ht.print_table()

    stdout_log = capsys.readouterr().out
    assert "Состояние хеш-таблицы" in stdout_log
    assert "удалено" in stdout_log
    assert "свободно" in stdout_log


def test_helper_functions_work():
    ht = HashTable()

    assert ht._get_state(HashCell(has_data=True)) == "занято"
    assert ht._get_state(HashCell(is_freed=True)) == "удалено"
    assert ht._get_state(HashCell()) == "свободно"

    assert ht._truncate("коротко", 10) == "коротко"
    assert ht._truncate("очень длинная строка", 8) == "очень..."