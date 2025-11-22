#!/usr/bin/env python3
"""Тест чистого интерфейса без заголовков."""

import customtkinter as ctk
from components.toolbar import Toolbar
from components.file_panel import FilePanel
from components.python_editor import PythonEditor
from components.output_markdown import MarkdownOutputDisplay

def test_clean_interface():
    """Тестирование чистого интерфейса без заголовков."""
    root = ctk.CTk()
    root.title("Тест чистого интерфейса")
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

    # Вывод результатов
    output_container = ctk.CTkFrame(work_area)
    output_container.pack(fill="both", expand=True, padx=5, pady=(2.5, 5))
    output = MarkdownOutputDisplay(output_container)

    # Добавляем информацию
    info = ctk.CTkLabel(
        root,
        text="Чистый интерфейс без заголовков:\n\n• Панель файлов - без заголовка 'Файлы'\n• Редактор кода - без заголовка 'Редактор Python кода'\n• Вывод результатов - без заголовка 'Результаты выполнения'\n\nИнтерфейс стал более минималистичным!",
        font=ctk.CTkFont(size=11),
        justify="left"
    )
    info.pack(pady=10)

    print("Тест чистого интерфейса запущен!")
    print("Все заголовки убраны для более чистого вида.")

    root.mainloop()

if __name__ == "__main__":
    test_clean_interface()
