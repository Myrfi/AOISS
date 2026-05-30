from src.data import populate_with_defaults
from src.hash_table import HashTable
from src.utils import display_ui_menu


def run_app() -> None:
    ht_instance = HashTable(size=23)
    populate_with_defaults(ht_instance)

    while True:
        display_ui_menu()
        action = input("Укажите номер операции: ").strip()

        if action == "1":
            word = input("Слово: ")
            desc = input("Толкование: ")
            ht_instance.insert(word, desc)
        elif action == "2":
            word = input("Какой термин искать? ")
            ht_instance.search(word)
        elif action == "3":
            word = input("Какой термин убрать? ")
            ht_instance.delete(word)
        elif action == "4":
            ht_instance.print_table()
        elif action == "5":
            ht_instance.print_load_factor()
        elif action == "0":
            print("Выход из системы. До свидания!")
            break
        else:
            print("Внимание: введена неверная команда (требуется от 0 до 5).")


if __name__ == "__main__":
    run_app()