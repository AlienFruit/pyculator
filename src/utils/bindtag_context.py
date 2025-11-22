"""Контекстный менеджер для управления bindtags в Tkinter."""
import tkinter as tk
from typing import Optional


class BindTagContext:
    """
    Контекстный менеджер для безопасного управления bindtags.
    
    Использование:
        with BindTagContext(widget, "MyTag"):
            widget.bind_class("MyTag", "<Key>", handler)
            # Привязки активны
        # Тег автоматически удален при выходе из контекста
    """
    
    def __init__(self, widget: tk.Widget, tag_name: str):
        """
        Инициализация контекстного менеджера.

        Args:
            widget: Виджет для управления bindtags
            tag_name: Имя тега для добавления/удаления
        """
        self.widget = widget
        self.tag_name = tag_name
        self._tag_was_present = False
    
    def __enter__(self):
        """
        Вход в контекст - добавляем тег если его нет.
        
        Returns:
            self для использования в with statement
        """
        try:
            current_tags = list(self.widget.bindtags())
            self._tag_was_present = self.tag_name in current_tags
            
            if not self._tag_was_present:
                # Добавляем тег в начало списка для приоритета
                current_tags.insert(0, self.tag_name)
                self.widget.bindtags(current_tags)
        except Exception as e:
            print(f"Ошибка при добавлении тега {self.tag_name}: {e}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из контекста - удаляем тег если он был добавлен нами.
        
        Args:
            exc_type: Тип исключения (если было)
            exc_val: Значение исключения
            exc_tb: Трассировка исключения
            
        Returns:
            False - не подавляем исключения
        """
        try:
            # Удаляем тег только если мы его добавили
            if not self._tag_was_present:
                current_tags = list(self.widget.bindtags())
                if self.tag_name in current_tags:
                    current_tags.remove(self.tag_name)
                    self.widget.bindtags(current_tags)
        except Exception as e:
            print(f"Ошибка при удалении тега {self.tag_name}: {e}")
        
        # Не подавляем исключения
        return False

