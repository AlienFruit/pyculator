#!/usr/bin/env python3
"""Тест выделения совпадающего текста."""
import customtkinter as ctk
from components.python_editor import PythonEditor

def test_highlight():
    """Тестирование выделения совпадающего текста."""
    root = ctk.CTk()
    root.title("Тест выделения совпадений")
    root.geometry("800x600")

    # Создаем редактор
    editor = PythonEditor(root)

    # Устанавливаем тестовый код с повторяющимися словами
    test_code = '''def hello():
    print("hello world")
    return "hello"

def goodbye():
    print("goodbye world")
    return "goodbye"

# Another hello function
def another_hello():
    message = "hello again"
    print(message)
    return message

# Test with print statements
print("This is a test")
print("Another print statement")
print("Final print here")'''

    editor.set_code(test_code)

    root.mainloop()

if __name__ == "__main__":
    test_highlight()
