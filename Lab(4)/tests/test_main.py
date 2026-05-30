import builtins

import main
from src.utils import display_ui_menu


def test_ui_menu_output(capsys):
    display_ui_menu()

    stdout = capsys.readouterr().out
    assert "[1] Зарегистрировать новый термин" in stdout
    assert "[0] Завершить работу" in stdout


def test_full_application_flow(monkeypatch, capsys):
    mocked_inputs = iter(
        [
            "1",
            "деепричастие",
            "особая форма глагола",
            "2",
            "деепричастие",
            "3",
            "деепричастие",
            "4",
            "5",
            "9",
            "0",
        ]
    )

    monkeypatch.setattr(builtins, "input", lambda _: next(mocked_inputs))

    main.run_app()

    stdout = capsys.readouterr().out
    assert "Обнаружено значение: особая форма глагола" in stdout
    assert "Успех: очищен слот" in stdout
    assert "Состояние хеш-таблицы" in stdout
    assert "Метрика заполненности" in stdout
    assert "Внимание: введена неверная команда" in stdout
    assert "Выход из системы. До свидания!" in stdout