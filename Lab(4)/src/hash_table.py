from dataclasses import dataclass
from typing import Optional


@dataclass
class HashCell:
    key: Optional[str] = None
    value: Optional[str] = None
    V: Optional[int] = None
    h: Optional[int] = None
    has_data: bool = False
    is_freed: bool = False


class HashTable:
    RUS_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

    def __init__(self, size: int = 23):
        if size < 20:
            raise ValueError("Вместимость таблицы не может быть меньше 20 элементов")

        self.size = size
        self.table = [HashCell() for _ in range(self.size)]

    def calculate_v(self, word: str) -> int:
        """Перевод первых двух букв слова в числовое значение V."""
        clean_word = word.strip().upper()

        if len(clean_word) < 2:
            raise ValueError("Длина ключа должна составлять как минимум 2 символа")

        char1, char2 = clean_word[0], clean_word[1]

        if char1 not in self.RUS_CHARS or char2 not in self.RUS_CHARS:
            raise ValueError("Для ключа требуются символы кириллицы (первые 2 знака)")

        idx1 = self.RUS_CHARS.index(char1)
        idx2 = self.RUS_CHARS.index(char2)

        return (idx1 * 33) + idx2

    def h1(self, num_v: int) -> int:
        return num_v % self.size

    def h2(self, num_v: int) -> int:
        return 1 + (num_v % (self.size - 1))

    def insert(self, key: str, value: str) -> bool:
        """Вставка элемента с разрешением коллизий (двойное хеширование)."""
        term = key.strip().lower()
        if not term:
            print("Сбой: пустой ключ недопустим.")
            return False

        try:
            val_v = self.calculate_v(term)
        except ValueError as err:
            print(f"Сбой: {err}")
            return False

        base_hash = self.h1(val_v)
        step = self.h2(val_v)
        saved_freed_idx = None

        print(f"Попытка вставки: ключ='{term}', V={val_v}, h={base_hash}")
        current_idx = base_hash

        for attempt in range(self.size):
            cell = self.table[current_idx]
            print(f"  Итерация {attempt}: проверяем индекс {current_idx}")

            if cell.has_data and cell.key == term:
                print("  Отмена: термин уже существует (дубликат).")
                return False

            if cell.is_freed and saved_freed_idx is None:
                saved_freed_idx = current_idx

            if not cell.has_data and not cell.is_freed:
                final_idx = saved_freed_idx if saved_freed_idx is not None else current_idx
                self._update_cell(final_idx, term, value, val_v, base_hash)
                print(f"  Успех: запись помещена в слот {final_idx}.")
                return True

            current_idx = (current_idx + step) % self.size

        if saved_freed_idx is not None:
            self._update_cell(saved_freed_idx, term, value, val_v, base_hash)
            print(f"  Успех: запись заняла освобожденный слот {saved_freed_idx}.")
            return True

        print("  Отмена: нет свободных мест (переполнение).")
        return False

    def search(self, key: str) -> Optional[HashCell]:
        """Поиск значения по ключу."""
        term = key.strip().lower()

        try:
            val_v = self.calculate_v(term)
        except ValueError as err:
            print(f"Сбой: {err}")
            return None

        base_hash = self.h1(val_v)
        step = self.h2(val_v)
        current_idx = base_hash

        print(f"Процесс поиска: ключ='{term}', V={val_v}, h={base_hash}")

        for attempt in range(self.size):
            cell = self.table[current_idx]
            print(f"  Итерация {attempt}: индекс = {current_idx}, состояние = {self._get_state(cell)}")

            if not cell.has_data and not cell.is_freed:
                print("  Результат: ничего не найдено.")
                return None

            if cell.has_data and cell.key == term:
                print(f"  Обнаружено значение: {cell.value}")
                return cell

            current_idx = (current_idx + step) % self.size

        print("  Результат: ничего не найдено.")
        return None

    def delete(self, key: str) -> bool:
        """Ленивое удаление"""
        term = key.strip().lower()

        try:
            val_v = self.calculate_v(term)
        except ValueError as err:
            print(f"Сбой: {err}")
            return False

        base_hash = self.h1(val_v)
        step = self.h2(val_v)
        current_idx = base_hash

        print(f"Процесс удаления: ключ='{term}', V={val_v}, h={base_hash}")

        for attempt in range(self.size):
            cell = self.table[current_idx]
            print(f"  Итерация {attempt}: индекс = {current_idx}, состояние = {self._get_state(cell)}")

            if not cell.has_data and not cell.is_freed:
                print("  Ошибка: объект отсутствует, удалять нечего.")
                return False

            if cell.has_data and cell.key == term:
                cell.has_data = False
                cell.is_freed = True
                print(f"  Успех: очищен слот {current_idx}.")
                return True

            current_idx = (current_idx + step) % self.size

        print("  Ошибка: объект отсутствует, удалять нечего.")
        return False

    def print_table(self) -> None:
        """Вывод содержимого хеш-таблицы."""
        val_w = 54
        separator = "=" * 128

        print("\n[ Состояние хеш-таблицы ]")
        print(separator)
        print(
            f"{'Слот':<6} | "
            f"{'Слово-ключ':<18} | "
            f"{'Описание (данные)':<{val_w}} | "
            f"{'V':<6} | "
            f"{'h':<4} | "
            f"{'Флаг':<10}"
        )
        print(separator)

        for i, cell in enumerate(self.table):
            k = cell.key if cell.key else "<пусто>"
            v = self._truncate(cell.value, val_w) if cell.value else "<пусто>"
            val = str(cell.V) if cell.V is not None else "-"
            h = str(cell.h) if cell.h is not None else "-"

            print(
                f"{i:<6} | "
                f"{k:<18} | "
                f"{v:<{val_w}} | "
                f"{val:<6} | "
                f"{h:<4} | "
                f"{self._get_state(cell):<10}"
            )
        print(separator)

    def load_factor(self) -> float:
        used_slots = sum(1 for c in self.table if c.has_data)
        return used_slots / self.size

    def print_load_factor(self) -> None:
        used_slots = sum(1 for c in self.table if c.has_data)
        print(f"Метрика заполненности: {used_slots} из {self.size} (α = {self.load_factor():.2f})")

    def _update_cell(self, idx: int, key: str, value: str, v: int, h: int) -> None:
        self.table[idx] = HashCell(
            key=key, value=value, V=v, h=h,
            has_data=True, is_freed=False
        )

    def _get_state(self, cell: HashCell) -> str:
        if cell.has_data:
            return "занято"
        return "удалено" if cell.is_freed else "свободно"

    def _truncate(self, s: str, limit: int) -> str:
        return s if len(s) <= limit else s[:limit - 3] + "..."