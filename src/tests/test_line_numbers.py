#!/usr/bin/env python3
"""Тестовый скрипт для проверки функциональности номеров строк."""

import customtkinter as ctk
from components.python_editor import PythonEditor

def test_line_numbers():
    """Тестирование номеров строк."""
    # Создание основного окна
    root = ctk.CTk()
    root.title("Тест номеров строк")
    root.geometry("800x600")

    # Создание редактора с номерами строк
    editor = PythonEditor(root, show_line_numbers=True)

    # Тестовый код
    test_code = """def hello_world():
    print("Hello, World!")
    return "success"

# Вызов функции
result = hello_world()
print(f"Result: {result}")"""

    editor.set_code(test_code)

    # Кнопка для переключения номеров строк
    def toggle_lines():
        editor.toggle_line_numbers()
        btn_text = "Показать номера строк" if not editor.line_numbers_visible() else "Скрыть номера строк"
        toggle_btn.configure(text=btn_text)

    toggle_btn = ctk.CTkButton(root, text="Скрыть номера строк", command=toggle_lines)
    toggle_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    test_line_numbers()
