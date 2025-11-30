"""Component редактора Python кода."""
import customtkinter as ctk


class CodeEditor:
    """Класс для редактирования Python кода."""
    
    def __init__(self, parent, initial_code: str = ""):
        """
        Инициализация редактора кода.
        
        Args:
            parent: Родительский виджет
            initial_code: Начальный код для отображения
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True)
        
        # Текстовое поле редактора
        self.textbox = ctk.CTkTextbox(
            self.frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none"
        )
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Вставка начального кода
        if initial_code:
            self.textbox.insert("1.0", initial_code)
    
    def get_code(self) -> str:
        """
        Получение кода из редактора.
        
        Returns:
            Текст кода
        """
        return self.textbox.get("1.0", "end-1c")
    
    def set_code(self, code: str):
        """
        Установка кода в редактор.
        
        Args:
            code: Code для установки
        """
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", code)
    
    def clear(self):
        """Очистка редактора."""
        self.textbox.delete("1.0", "end")

