"""Альтернативная реализация вывода - консольный вывод (пример)."""
import customtkinter as ctk
from typing import Optional
from components.output_interface import IOutputDisplay


class ConsoleOutputDisplay(IOutputDisplay):
    """Простая консольная реализация вывода (пример альтернативной реализации)."""
    
    def __init__(self, parent):
        """
        Инициализация компонента вывода.
        
        Args:
            parent: Родительский виджет
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True)
        
        # Заголовок
        label = ctk.CTkLabel(
            self.frame,
            text="Консольный вывод",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.pack(pady=5)
        
        # Простой текстовый виджет без markdown поддержки
        self.textbox = ctk.CTkTextbox(
            self.frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            corner_radius=0
        )
        self.textbox.pack(fill="both", expand=True)
        
        # Настройка тегов для цветного текста
        self.textbox.tag_config("error", foreground="red")
        self.textbox.tag_config("success", foreground="green")
    
    @property
    def frame(self):
        """Возвращает основной фрейм компонента для размещения в интерфейсе."""
        return self._frame
    
    def clear(self):
        """Очистка вывода."""
        if self.textbox:
            self.textbox.delete("1.0", "end")
        self.clear_plot()
    
    def clear_plot(self):
        """Удаление всех графиков."""
        # Графики очищаются в PlotsDisplay
        pass
    
    def append_text(self, text: str, tag: Optional[str] = None):
        """
        Добавление текста в вывод.
        
        Args:
            text: Текст для добавления
            tag: Тег для форматирования (например, "error", "success")
        """
        if not self.textbox:
            return
        if tag:
            self.textbox.insert("end", text, tag)
        else:
            self.textbox.insert("end", text)
    
    def append_markdown(self, text: str):
        """
        Добавление markdown текста в вывод (без форматирования в этой реализации).
        
        Args:
            text: Текст с markdown разметкой
        """
        # Просто вставляем текст как есть, без парсинга markdown
        self.append_text(text)
    
    def display_result(self, stdout: str, stderr: str, exception: Optional[str] = None, enable_markdown: bool = True):
        """
        Отображение результатов выполнения кода.
        
        Args:
            stdout: Стандартный вывод
            stderr: Вывод ошибок
            exception: Текст исключения если было
            enable_markdown: Включить поддержку markdown форматирования (игнорируется)
        """
        self.clear()
        
        has_output = False
        
        if stdout:
            #self.append_text("Вывод:\n", "success")
            self.append_text(stdout + "\n")
            has_output = True
        
        if stderr:
            self.append_text("Ошибки:\n", "error")
            self.append_text(stderr + "\n", "error")
            has_output = True
        
        if exception:
            error_msg = f"Ошибка выполнения: {exception}\n"
            self.append_text(error_msg, "error")
            has_output = True
        
        if not has_output:
            self.append_text("Код выполнен успешно. Нет вывода.\n", "success")

