"""Упрощенный редактор Python кода на базе tkinter.Text без сложных обработчиков."""
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext


class PythonEditorSimple:
    """Простой редактор кода без сложных обработчиков событий - максимум надежности."""
    
    def __init__(self, parent, initial_code: str = ""):
        """
        Инициализация редактора кода.

        Args:
            parent: Родительский виджет (CTkFrame)
            initial_code: Начальный код для отображения
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True)

        # Контейнер для текстового редактора
        text_container = tk.Frame(self.frame, bg=self._get_bg_color())
        text_container.pack(fill="both", expand=True)

        # Создание текстового виджета с прокруткой
        # Минимум настроек - максимум надежности
        self.text_widget = scrolledtext.ScrolledText(
            text_container,
            wrap="none",
            font=("Consolas", 12),
            bg="#1e1e1e" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#d4d4d4" if ctk.get_appearance_mode() == "Dark" else "#000000",
            insertbackground="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            selectbackground="#264f78" if ctk.get_appearance_mode() == "Dark" else "#316ac5",
            selectforeground="#ffffff",
            undo=True,
            maxundo=50
        )
        self.text_widget.pack(fill="both", expand=True)
        
        # ТОЛЬКО контекстное меню - никаких других обработчиков событий
        self.text_widget.bind("<Button-3>", self._show_context_menu)
        
        # Вставка начального кода
        if initial_code:
            self.text_widget.insert("1.0", initial_code)
    
    def _get_bg_color(self) -> str:
        """Получение цвета фона в зависимости от темы."""
        return "#1e1e1e" if ctk.get_appearance_mode() == "Dark" else "#ffffff"
    
    def _show_context_menu(self, event):
        """Показ контекстного меню с опциями копирования/вставки."""
        try:
            context_menu = tk.Menu(self.text_widget, tearoff=0)
            
            # Проверяем, есть ли выделенный текст
            has_selection = bool(self.text_widget.tag_ranges("sel"))
            
            # Опции меню
            if has_selection:
                context_menu.add_command(
                    label="Копировать (Ctrl+C)", 
                    command=self._copy_text
                )
                context_menu.add_command(
                    label="Вырезать (Ctrl+X)", 
                    command=self._cut_text
                )
            else:
                context_menu.add_command(label="Копировать (Ctrl+C)", state="disabled")
                context_menu.add_command(label="Вырезать (Ctrl+X)", state="disabled")
            
            # Проверяем, есть ли текст в буфере обмена
            try:
                clipboard_text = self.text_widget.clipboard_get()
                has_clipboard = bool(clipboard_text)
            except tk.TclError:
                has_clipboard = False
            
            if has_clipboard:
                context_menu.add_command(
                    label="Вставить (Ctrl+V)", 
                    command=self._paste_text
                )
            else:
                context_menu.add_command(label="Вставить (Ctrl+V)", state="disabled")
            
            context_menu.add_separator()
            context_menu.add_command(
                label="Выделить всё (Ctrl+A)", 
                command=self._select_all
            )
            
            # Показываем меню
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Освобождаем меню после использования
                context_menu.grab_release()
        except Exception as e:
            print(f"Error показа контекстного меню: {e}")
    
    def _copy_text(self):
        """Копирование выделенного текста."""
        try:
            if self.text_widget.tag_ranges("sel"):
                selected_text = self.text_widget.get("sel.first", "sel.last")
                if selected_text:
                    self.text_widget.clipboard_clear()
                    self.text_widget.clipboard_append(selected_text)
        except Exception as e:
            print(f"Error копирования: {e}")
    
    def _cut_text(self):
        """Вырезание выделенного текста."""
        try:
            if self.text_widget.tag_ranges("sel"):
                selected_text = self.text_widget.get("sel.first", "sel.last")
                if selected_text:
                    self.text_widget.clipboard_clear()
                    self.text_widget.clipboard_append(selected_text)
                    self.text_widget.delete("sel.first", "sel.last")
        except Exception as e:
            print(f"Error вырезания: {e}")
    
    def _paste_text(self):
        """Вставка текста из буфера обмена."""
        try:
            clipboard_text = self.text_widget.clipboard_get()
            if clipboard_text:
                # Удаляем выделенный текст, если есть
                if self.text_widget.tag_ranges("sel"):
                    self.text_widget.delete("sel.first", "sel.last")
                # Вставляем текст в позицию курсора
                self.text_widget.insert("insert", clipboard_text)
        except tk.TclError:
            pass
        except Exception as e:
            print(f"Error вставки: {e}")
    
    def _select_all(self):
        """Выделение всего текста."""
        try:
            self.text_widget.tag_add("sel", "1.0", "end-1c")
            self.text_widget.mark_set("insert", "1.0")
            self.text_widget.see("insert")
        except Exception as e:
            print(f"Error выделения всего: {e}")
    
    def get_code(self) -> str:
        """Получение кода из редактора."""
        return self.text_widget.get("1.0", "end-1c")
    
    def set_code(self, code: str):
        """Установка кода в редактор."""
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", code)
    
    def clear(self):
        """Очистка редактора."""
        self.text_widget.delete("1.0", "end")

