#!/usr/bin/env python3
"""Test полностью минималистичного интерфейса."""

import customtkinter as ctk
from components.toolbar import Toolbar
from components.file_panel import FilePanel
from components.python_editor import PythonEditor
from components.output_markdown import MarkdownOutputDisplay

def test_minimal_interface():
    """Тестирование минималистичного интерфейса без заголовков и кнопок."""
    root = ctk.CTk()
    root.title("Test минималистичного интерфейса")
    root.geometry("900x600")

    # Создаем тулбар
    toolbar = Toolbar(root)

    # Создаем основной контейнер
    main_container = ctk.CTkFrame(root)
    main_container.pack(fill="both", expand=True, padx=5, pady=5)

    # Панель файлов
    file_panel = FilePanel(main_container)

    # Рабочая область
    work_area = ctk.CTkFrame(main_container)
    work_area.pack(side="left", fill="both", expand=True, padx=(5, 0))

    # Редактор
    editor_container = ctk.CTkFrame(work_area)
    editor_container.pack(fill="both", expand=True, padx=5, pady=(5, 2.5))
    editor = PythonEditor(editor_container)

    # Output результатов (теперь без кнопки копирования)
    output_container = ctk.CTkFrame(work_area)
    output_container.pack(fill="both", expand=True, padx=5, pady=(2.5, 5))
    output = MarkdownOutputDisplay(output_container)

    # Добавляем демонстрационный контент
    output.append_markdown("""
# Демонстрация чистого интерфейса

Это **жирный текст** и *курсивный текст* для демонстрации markdown.

```python
print("Code выполняется корректно!")
```

## Преимущества:

- Полностью чистый интерфейс
- Никаких лишних заголовков
- Минималистичный дизайн
- Фокус на контенте
    """)

    # Добавляем информацию
    info = ctk.CTkLabel(
        root,
        text="🚀 Минималистичный интерфейс:\n\n✅ Убраны все заголовки ('Файлы', 'Редактор', 'Результаты')\n✅ Убрана кнопка копирования\n✅ Только функциональные иконки в тулбаре\n✅ Максимум места для контента\n\nКопирование: Ctrl+C, ПКМ → меню, двойной клик для окна",
        font=ctk.CTkFont(size=11),
        justify="left"
    )
    info.pack(pady=10)

    print("Test минималистичного интерфейса запущен!")
    print("Interface стал максимально чистым и функциональным.")

    root.mainloop()

if __name__ == "__main__":
    test_minimal_interface()
