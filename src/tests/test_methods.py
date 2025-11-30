#!/usr/bin/env python3
"""Test методов DataManager."""
from utils.data_manager import DataManager

def test_methods():
    """Тестирование методов."""
    dm = DataManager()

    print("Test load_data_from_file...")
    result = dm.load_data_from_file('data/test.py')
    print(f"Загружено из test.py: {len(result['code'])} символов")

    print("\nТест save_data_to_file...")
    success = dm.save_data_to_file('data/temp_test.py', 'print("temporary file")')
    print(f"Сохранение в temp_test.py: {success}")

    if success:
        with open('data/temp_test.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Содержимое temp_test.py: {repr(content)}")

if __name__ == "__main__":
    test_methods()
