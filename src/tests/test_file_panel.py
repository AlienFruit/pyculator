#!/usr/bin/env python3
"""Тест отображения всех файлов в FilePanel."""

import customtkinter as ctk
from components.file_panel import FilePanel
import os

def test_file_panel():
    """Тестирование FilePanel с отображением всех файлов."""
    root = ctk.CTk()
    root.title("Тест FilePanel")
    root.geometry("400x600")

    # Создаем FilePanel
    file_panel = FilePanel(
        root,
        initial_directory="data"
    )

    # Получаем список файлов
    files = file_panel._get_files()
    print(f"Найдено файлов: {len(files)}")
    print("Файлы:")
    for file in sorted(files):
        print(f"  - {file}")

    # Запускаем интерфейс
    root.mainloop()

if __name__ == "__main__":
    test_file_panel()
