#!/usr/bin/env python3
"""
Демонстрация использования MarkdownOutputDisplay в приложении Python Calculator.

Для использования новой реализации замените строку в app.py:
    self.output: IOutputDisplay = OutputDisplay(output_container)

на:
    from components.output_markdown import MarkdownOutputDisplay
    self.output: IOutputDisplay = MarkdownOutputDisplay(output_container)
"""

import customtkinter as ctk
from components.output_markdown import MarkdownOutputDisplay

def demo_markdown_output():
    """Демонстрация MarkdownOutputDisplay."""
    # Создаем главное окно
    root = ctk.CTk()
    root.title("Демо MarkdownOutputDisplay")
    root.geometry("900x700")

    # Создаем экземпляр MarkdownOutputDisplay
    output_display = MarkdownOutputDisplay(root)

    # Добавляем различные типы контента для демонстрации

    # 1. Заголовок
    output_display.append_text("# Демонстрация MarkdownOutputDisplay\n\n", "success")

    # 2. Описание
    description = """
## Возможности

Эта реализация OutputDisplay использует библиотеку **tkhtmlview** для полноценного
отображения markdown контента с:

- Полной поддержкой HTML форматирования
- Подсветкой синтаксиса для блоков кода
- Таблицами и списками
- Ссылками и изображениями
- Адаптивными темами (светлая/темная)
"""

    output_display.append_markdown(description)

    # 3. Примеры кода
    output_display.append_text("\n## Примеры кода\n", "success")

    code_examples = """
### Python код с подсветкой

```python
def fibonacci(n):
    \"\"\"Вычисление числа Фибоначчи.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Пример использования
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### Математические выражения

```python
import math

# Вычисление площади круга
def circle_area(radius):
    return math.pi * radius ** 2

radius = 5
area = circle_area(radius)
print(f"Площадь круга с радиусом {radius} = {area:.2f}")
```
"""

    output_display.append_markdown(code_examples)

    # 4. Таблицы
    output_display.append_text("\n## Таблицы\n", "success")

    table_md = """
| Функция | Описание | Пример |
|---------|----------|---------|
| `print()` | Вывод текста | `print("Hello")` |
| `len()` | Длина объекта | `len([1,2,3])` |
| `range()` | Диапазон чисел | `range(5)` |
| `sum()` | Сумма элементов | `sum([1,2,3])` |
"""

    output_display.append_markdown(table_md)

    # 5. Списки
    output_display.append_text("\n## Списки\n", "success")

    lists_md = """
### Нумерованный список
1. Первый элемент
2. Второй элемент
3. Третий элемент

### Маркированный список
- Элемент 1
- Элемент 2
  - Подэлемент 2.1
  - Подэлемент 2.2
- Элемент 3
"""

    output_display.append_markdown(lists_md)

    # 6. Демонстрация display_result
    output_display.append_text("\n## Результат выполнения кода\n", "success")

    sample_stdout = """
```
Результат выполнения:
Число Фибоначчи F(10) = 55
Площадь круга = 78.54
```

**Время выполнения:** 0.023 секунды
**Статус:** ✅ Успешно
"""

    sample_stderr = "Warning: Используется устаревшая функция print без скобок"

    output_display.display_result(sample_stdout, sample_stderr, None, enable_markdown=True)

    # Запускаем главный цикл
    root.mainloop()

if __name__ == "__main__":
    print("Запуск демонстрации MarkdownOutputDisplay...")
    print("Для использования в основном приложении замените в app.py:")
    print("    self.output: IOutputDisplay = OutputDisplay(output_container)")
    print("на:")
    print("    from components.output_markdown import MarkdownOutputDisplay")
    print("    self.output: IOutputDisplay = MarkdownOutputDisplay(output_container)")
    print()

    demo_markdown_output()
