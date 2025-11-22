"""Компонент панели инструментов."""
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from typing import Callable, Optional


class Toolbar:
    """Класс для панели инструментов с кнопками управления."""
    
    def __init__(self, parent,
                 on_create: Optional[Callable] = None,
                 on_save: Optional[Callable] = None,
                 on_run: Optional[Callable] = None,
                 on_select_directory: Optional[Callable] = None):
        """
        Инициализация панели инструментов.

        Args:
            parent: Родительский виджет
            on_create: Callback для кнопки "Создать"
            on_save: Callback для кнопки "Сохранить файл"
            on_run: Callback для кнопки "Выполнить код"
            on_select_directory: Callback для кнопки "Выбрать директорию"
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="x", padx=5, pady=5)
        
        self.on_create = on_create
        self.on_save = on_save
        self.on_run = on_run
        self.on_select_directory = on_select_directory

        # Кнопка "Выбрать директорию"
        self.dir_btn = ctk.CTkButton(
            self.frame,
            text="📁",  # Иконка папки
            command=self._handle_select_directory,
            width=50,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.dir_btn.pack(side="left", padx=2)

        # Кнопка "Создать"
        self.create_btn = ctk.CTkButton(
            self.frame,
            text="📄",  # Иконка для создания файла
            command=self._handle_create,
            width=50,
            height=35,
            font=ctk.CTkFont(size=16)
        )
        self.create_btn.pack(side="left", padx=2)

        # Кнопка "Сохранить файл" (неактивна по умолчанию)
        self.save_btn = ctk.CTkButton(
            self.frame,
            text="💾",  # Иконка для сохранения
            command=self._handle_save,
            width=50,
            height=35,
            font=ctk.CTkFont(size=16),
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=2)

        # Кнопка "Выполнить код"
        self.run_btn = ctk.CTkButton(
            self.frame,
            text="▶",  # Иконка для выполнения с пробелами для центрирования
            command=self._handle_run,
            width=50,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.run_btn.pack(side="left", padx=2)

        # Добавляем подсказки для кнопок
        self._add_tooltips()

    def _add_tooltips(self):
        """Добавление подсказок для кнопок."""
        try:
            from tkinter import ttk
            # Создаем стиль для подсказок
            style = ttk.Style()
            style.configure("Custom.TButton", relief="flat")

                # Добавляем подсказки через привязку событий
            self.dir_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Выбрать директорию"))
            self.dir_btn.bind("<Leave>", self._hide_tooltip)

            self.create_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Создать новый файл"))
            self.create_btn.bind("<Leave>", self._hide_tooltip)

            self.save_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Сохранить файл"))
            self.save_btn.bind("<Leave>", self._hide_tooltip)

            self.run_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Выполнить код"))
            self.run_btn.bind("<Leave>", self._hide_tooltip)

        except ImportError:
            # Если ttk недоступен, просто пропускаем подсказки
            pass

    def _show_tooltip(self, event, text):
        """Показать подсказку."""
        try:
            if hasattr(self, 'tooltip_label'):
                self.tooltip_label.destroy()

            # Получаем координаты кнопки
            x = event.widget.winfo_rootx() + event.widget.winfo_width() // 2
            y = event.widget.winfo_rooty() - 25

            # Создаем метку с подсказкой
            self.tooltip_label = ctk.CTkLabel(
                self.frame,
                text=text,
                font=ctk.CTkFont(size=10),
                fg_color="#333333",
                corner_radius=4,
                text_color="white"
            )

            # Позиционируем подсказку
            self.tooltip_label.place(x=x - self.frame.winfo_rootx(),
                                   y=y - self.frame.winfo_rooty(),
                                   anchor="center")

        except Exception:
            pass

    def _hide_tooltip(self, event):
        """Скрыть подсказку."""
        try:
            if hasattr(self, 'tooltip_label'):
                self.tooltip_label.destroy()
                delattr(self, 'tooltip_label')
        except Exception:
            pass

    def _handle_select_directory(self):
        """Обработчик кнопки выбора директории."""
        if self.on_select_directory:
            self.on_select_directory()

    def _handle_create(self):
        """Обработчик кнопки создания файла."""
        if self.on_create:
            self.on_create()

    def set_save_enabled(self, enabled: bool):
        """
        Управление состоянием кнопки сохранения.

        Args:
            enabled: True для активации, False для деактивации
        """
        if enabled:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")

    def _handle_save(self):
        """Обработчик кнопки сохранения файла."""
        if self.on_save:
            self.on_save()
    
    def _handle_run(self):
        """Обработчик кнопки выполнения кода."""
        if self.on_run:
            self.on_run()
    
    @staticmethod
    def save_file_dialog() -> Optional[str]:
        """
        Открытие диалога выбора файла для сохранения.
        
        Returns:
            Путь к файлу или None если отменено
        """
        return filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python файлы", "*.py"), ("Все файлы", "*.*")]
        )
    
    @staticmethod
    def show_info(title: str, message: str):
        """Показать информационное сообщение."""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error(title: str, message: str):
        """Показать сообщение об ошибке."""
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_string(title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """
        Показать диалог ввода строки.
        
        Args:
            title: Заголовок диалога
            prompt: Текст подсказки
            initial_value: Начальное значение
        
        Returns:
            Введенная строка или None если отменено
        """
        result = simpledialog.askstring(title, prompt, initialvalue=initial_value)
        return result if result else None

