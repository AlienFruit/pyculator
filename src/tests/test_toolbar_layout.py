#!/usr/bin/env python3
"""Test новой раскладки кнопок в тулбаре."""

import customtkinter as ctk
from components.toolbar import Toolbar

def test_toolbar_layout():
    """Тестирование новой раскладки кнопок."""
    root = ctk.CTk()
    root.title("Test раскладки тулбара")
    root.geometry("500x120")

    # Создаем тулбар
    toolbar = Toolbar(root)

    # Добавляем информацию
    info = ctk.CTkLabel(
        root,
        text="Новая раскладка кнопок в тулбаре:\n\n📁 Выбрать директорию | 📄 Create файл | 💾 Save файл | ▶️ Execute код\n\nВсе кнопки теперь в одном ряду в верхней части окна!",
        font=ctk.CTkFont(size=11),
        justify="left"
    )
    info.pack(pady=15)

    print("Test раскладки запущен!")
    print("Button выбора директории теперь в тулбаре.")

    root.mainloop()

if __name__ == "__main__":
    test_toolbar_layout()
