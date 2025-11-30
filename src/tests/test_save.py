#!/usr/bin/env python3
"""Test сохранения и загрузки данных."""
from utils.data_manager import DataManager

def test_save_load():
    """Тестирование сохранения и загрузки."""
    dm = DataManager()

    # Тестовый код
    test_code = 'print("Hello from .py file!")\nx = 42\nprint(f"x = {x}")'

    print("Сохраняем код...")
    result = dm.save_data(test_code)
    print(f"Результат сохранения: {result}")

    print("\nЗагружаем код...")
    loaded_code = dm.get_code()
    print(f"Загруженный код: {repr(loaded_code)}")

    print(f"\nКод совпадает: {loaded_code.strip() == test_code}")

if __name__ == "__main__":
    test_save_load()
