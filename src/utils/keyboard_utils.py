"""Утилиты для работы с клавиатурой и буфером обмена."""
import tkinter as tk
from typing import Optional, Callable


def copy_to_clipboard(widget: tk.Widget, text: str) -> bool:
    """
    Универсальная функция копирования текста в буфер обмена.

    Args:
        widget: Виджет для доступа к буферу обмена
        text: Текст для копирования

    Returns:
        True если успешно, False в случае ошибки
    """
    try:
        widget.clipboard_clear()
        widget.clipboard_append(text)
        return True
    except Exception as e:
        print(f"Ошибка копирования в буфер обмена: {e}")
        return False


def get_selected_text(widget: tk.Text) -> Optional[str]:
    """
    Получение выделенного текста из виджета.

    Args:
        widget: Текстовый виджет

    Returns:
        Выделенный текст или None если нет выделения
    """
    try:
        if widget.tag_ranges("sel"):
            return widget.get("sel.first", "sel.last")
    except tk.TclError:
        pass
    return None


def has_selection(widget: tk.Text) -> bool:
    """
    Проверка наличия выделенного текста.

    Args:
        widget: Текстовый виджет

    Returns:
        True если есть выделение, False иначе
    """
    try:
        return bool(widget.tag_ranges("sel"))
    except tk.TclError:
        return False


def get_clipboard_text(widget: tk.Widget) -> Optional[str]:
    """
    Получение текста из буфера обмена.

    Args:
        widget: Виджет для доступа к буферу обмена

    Returns:
        Текст из буфера обмена или None если буфер пуст или недоступен
    """
    try:
        return widget.clipboard_get()
    except tk.TclError:
        return None


def bind_case_insensitive(widget: tk.Widget, key_combination: str, handler: Callable, add: str = "") -> None:
    """
    Привязка обработчика с учетом обоих регистров клавиши.

    Args:
        widget: Виджет для привязки
        key_combination: Комбинация клавиш (например, "<Control-c>")
        handler: Обработчик события
        add: Флаг добавления ("+" для добавления без перезаписи)
    """
    # Извлекаем модификаторы и клавишу
    if key_combination.startswith("<") and key_combination.endswith(">"):
        # Разделяем на модификаторы и клавишу
        parts = key_combination[1:-1].split("-")
        if len(parts) > 1:
            modifiers = "-".join(parts[:-1])
            key = parts[-1]
            # Привязываем оба варианта регистра
            widget.bind(f"<{modifiers}-{key.lower()}>", handler, add=add)
            widget.bind(f"<{modifiers}-{key.upper()}>", handler, add=add)
        else:
            # Нет модификаторов, просто клавиша
            key = parts[0]
            widget.bind(f"<{key.lower()}>", handler, add=add)
            widget.bind(f"<{key.upper()}>", handler, add=add)
    else:
        # Нестандартный формат, привязываем как есть
        widget.bind(key_combination, handler, add=add)

