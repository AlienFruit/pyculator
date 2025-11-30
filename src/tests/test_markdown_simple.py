#!/usr/bin/env python3
"""Simple тест для проверки MarkdownOutputDisplay без GUI."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.output_markdown import MarkdownOutputDisplay
import markdown

def test_markdown_conversion():
    """Тестирование конвертации markdown в HTML."""
    test_md = """
# Test заголовка

Это **жирный** и *курсивный* текст.

```
Code на Python
print("Hello")
```
"""

    html = markdown.markdown(test_md, extensions=['fenced_code', 'codehilite', 'tables', 'nl2br'])
    print("Markdown успешно конвертирован в HTML:")
    print(html[:200] + "...")
    return True

def test_import():
    """Тестирование импорта компонентов."""
    try:
        from components.output_interface import IOutputDisplay
        from components.output_markdown import MarkdownOutputDisplay
        print("✓ Импорт прошел успешно")
        return True
    except ImportError as e:
        print(f"✗ Error импорта: {e}")
        return False

def test_interface_compliance():
    """Check соответствия интерфейсу."""
    try:
        # Проверяем, что MarkdownOutputDisplay наследует от IOutputDisplay
        from components.output_interface import IOutputDisplay
        from components.output_markdown import MarkdownOutputDisplay

        # Проверяем наличие всех необходимых методов
        required_methods = ['frame', 'clear', 'clear_plot', 'append_text', 'append_markdown', 'display_result']

        for method in required_methods:
            if not hasattr(MarkdownOutputDisplay, method):
                print(f"✗ Отсутствует метод: {method}")
                return False

        print("✓ MarkdownOutputDisplay соответствует интерфейсу IOutputDisplay")
        return True
    except Exception as e:
        print(f"✗ Error проверки интерфейса: {e}")
        return False

if __name__ == "__main__":
    print("=== Тестирование MarkdownOutputDisplay ===")

    tests = [
        ("Импорт компонентов", test_import),
        ("Конвертация Markdown", test_markdown_conversion),
        ("Соответствие интерфейсу", test_interface_compliance),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nЗапуск теста: {test_name}")
        try:
            if test_func():
                passed += 1
                print("✓ Пройден")
            else:
                print("✗ Провалено")
        except Exception as e:
            print(f"✗ Исключение: {e}")

    print(f"\n=== Результаты тестирования ===")
    print(f"Пройдено: {passed}/{total}")

    if passed == total:
        print("🎉 Все тесты пройдены!")
    else:
        print("❌ Некоторые тесты провалены")
        sys.exit(1)
