#!/usr/bin/env python3
"""Test отображения иконок в тулбаре."""

import customtkinter as ctk
from components.toolbar import Toolbar

def test_toolbar_icons():
    """Тестирование отображения иконок в тулбаре."""
    root = ctk.CTk()
    root.title("Test иконок тулбара")
    root.geometry("400x150")

    # Создаем тулбар
    toolbar = Toolbar(root)

    # Добавляем информацию
    info = ctk.CTkLabel(
        root,
        text="Новые иконки в тулбаре:\n\n📄 Create файл\n💾 Save файл\n▶️ Execute код\n\nНаведите курсор на кнопки для подсказок!",
        font=ctk.CTkFont(size=12),
        justify="left"
    )
    info.pack(pady=20)

    print("Test иконок тулбара запущен!")
    print("Кнопки теперь показывают иконки вместо текста.")

    root.mainloop()

if __name__ == "__main__":
    test_toolbar_icons()
