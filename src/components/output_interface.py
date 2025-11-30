"""Интерфейс для компонентов вывода результатов выполнения кода."""
from abc import ABC, abstractmethod
from typing import Optional


class IOutputDisplay(ABC):
    """Абстрактный интерфейс для отображения результатов выполнения кода."""
    
    @property
    @abstractmethod
    def frame(self):
        """Возвращает основной фрейм компонента для размещения в интерфейсе."""
        pass
    
    @abstractmethod
    def clear(self):
        """Очистка вывода."""
        pass
    
    @abstractmethod
    def clear_plot(self):
        """Удаление всех графиков."""
        pass
    
    @abstractmethod
    def append_text(self, text: str, tag: Optional[str] = None):
        """
        Добавление текста в вывод.
        
        Args:
            text: Текст для добавления
            tag: Тег для форматирования (например, "error", "success")
        """
        pass
    
    @abstractmethod
    def append_markdown(self, text: str):
        """
        Добавление markdown текста в вывод с форматированием.
        
        Args:
            text: Текст с markdown разметкой
        """
        pass
    
    @abstractmethod
    def display_result(self, stdout: str, stderr: str, exception: Optional[str] = None, enable_markdown: bool = True):
        """
        Отображение результатов выполнения кода.
        
        Args:
            stdout: Стандартный вывод
            stderr: Output ошибок
            exception: Текст исключения если было
            enable_markdown: Включить поддержку markdown форматирования
        """
        pass

