#!/usr/bin/env python3
"""Тестовый скрипт для проверки MarkdownOutputDisplay."""

import customtkinter as ctk
from components.output_markdown import MarkdownOutputDisplay

def test_markdown_output():
    """Тестирование MarkdownOutputDisplay."""
    # Создаем главное окно
    root = ctk.CTk()
    root.title("Тест MarkdownOutputDisplay")
    root.geometry("800x600")

    # Создаем экземпляр MarkdownOutputDisplay
    output_display = MarkdownOutputDisplay(root)

    # Тестируем различные типы контента

    # 1. Простой текст
    output_display.append_text("=== Тестирование MarkdownOutputDisplay ===\n\n", "success")

    # 2. Текст с ошибками
    output_display.append_text("Это сообщение об ошибке\n", "error")

    # 3. Markdown контент
    markdown_content = """
# Заголовок первого уровня

## Заголовок второго уровня

### Заголовок третьего уровня

Это обычный текст с **жирным** и *курсивным* форматированием.

Вот пример `инлайн кода`.

```
# Блок кода на Python
def hello_world():
    print("Hello, World!")
    return True
```

### Списки:

- Первый элемент
- Второй элемент
- Третий элемент

1. Нумерованный элемент 1
2. Нумерованный элемент 2
3. Нумерованный элемент 3

### Ссылка
[Посетите GitHub](https://github.com)

### Таблица

| Заголовок 1 | Заголовок 2 | Заголовок 3 |
|-------------|-------------|-------------|
| Ячейка 1    | Ячейка 2    | Ячейка 3    |
| Данные 1    | Данные 2    | Данные 3    |
"""

    output_display.append_markdown(markdown_content)

    # 4. Тестируем display_result
    output_display.append_text("\n\n=== Тестирование display_result ===\n", "success")

    test_stdout = """
# Результат выполнения кода

Код выполнен успешно!

```
Результат вычисления: 42
```

**Время выполнения:** 0.05 секунды
"""

    test_stderr = "Warning: Deprecated function used"
    test_exception = None

    output_display.display_result(test_stdout, test_stderr, test_exception, enable_markdown=True)

    # Запускаем главный цикл
    root.mainloop()

if __name__ == "__main__":
    test_markdown_output()
