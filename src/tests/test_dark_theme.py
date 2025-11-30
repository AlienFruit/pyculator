#!/usr/bin/env python3
"""Test цветовой схемы MarkdownOutputDisplay в темной теме."""

import customtkinter as ctk
from components.output_markdown import MarkdownOutputDisplay

def test_dark_theme():
    """Тестирование темной темы."""
    # Создаем главное окно
    root = ctk.CTk()
    root.title("Test темной темы MarkdownOutputDisplay")

    # Устанавливаем темную тему
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root.geometry("800x600")

    # Создаем экземпляр MarkdownOutputDisplay
    output_display = MarkdownOutputDisplay(root)

    # Добавляем тестовый контент
    test_markdown = """
# Test темной темы

Это обычный текст, который должен быть **белым** на темном фоне.

## Цвета элементов:

- **Жирный текст**: должен быть желтым (#ffd43b)
- *Курсивный текст*: должен быть розовым (#dda0dd)
- `Инлайн код`: должен быть бирюзовым на сером фоне

## Блоки кода:

```python
def hello_world():
    print("Hello, World!")
    return "Привет, мир!"
```

## Списки:

1. Первый элемент списка
2. Второй элемент списка
3. Третий элемент списка

### Ссылки:
[Это ссылка](https://example.com) - должна быть синей и подчеркнутой.

### Сообщения:
<span class="success">Успешное выполнение кода</span>
<span class="error">Error выполнения</span>
"""

    output_display.append_markdown(test_markdown)

    # Button переключения темы
    def toggle_theme():
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        theme_button.configure(text=f"Theme: {new_mode}")
        print(f"Переключено на {new_mode} тему")

    theme_button = ctk.CTkButton(
        root,
        text="Theme: Dark",
        command=toggle_theme
    )
    theme_button.pack(pady=5)

    # Добавляем информацию
    info = ctk.CTkLabel(
        root,
        text="Check цветов:\n- Основной текст: должен быть белым в темной теме, черным в светлой\n- Фон: темно-серый в темной, белый в светлой\n- Жирный: желтый (#ffd43b)\n- Курсив: розовый (#dda0dd)\n- Code: бирюзовый (#69db7c)\n- Фон кода: серый (#3a3a3a)",
        font=ctk.CTkFont(size=10),
        wraplength=700
    )
    info.pack(pady=5)

    print("Test темной темы запущен!")
    print("Если текст белый и хорошо читаемый - проблема решена!")

    # Запускаем главный цикл
    root.mainloop()

if __name__ == "__main__":
    test_dark_theme()
