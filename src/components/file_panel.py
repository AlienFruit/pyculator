"""Компонент панели файлов."""
import customtkinter as ctk
import os
from tkinter import filedialog
from typing import Callable, Optional, List
from utils.data_manager import get_data_directory


class FilePanel:
    """Класс для панели со списком файлов."""
    
    def __init__(self, parent, 
                 on_file_select: Optional[Callable[[str], None]] = None,
                 on_directory_change: Optional[Callable[[str], None]] = None,
                 initial_directory: Optional[str] = None):
        """
        Инициализация панели файлов.
        
        Args:
            parent: Родительский виджет
            on_file_select: Callback при выборе файла (принимает путь к файлу)
            on_directory_change: Callback при смене директории (принимает путь к директории)
            initial_directory: Начальная директория (если None, используется папка data)
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.frame.pack_propagate(False)
        self.frame.configure(width=250)
        
        self.on_file_select = on_file_select
        self.on_directory_change = on_directory_change
        
        # Используем переданную директорию или папку data по умолчанию
        if initial_directory and os.path.isdir(initial_directory):
            self.current_directory = initial_directory
        else:
            self.current_directory = get_data_directory()
        self.selected_file = None
        
        # Отображение текущей директории
        self.dir_label = ctk.CTkLabel(
            self.frame,
            text=self._truncate_path(self.current_directory),
            font=ctk.CTkFont(size=10),
            wraplength=230
        )
        self.dir_label.pack(pady=5, padx=10)
        
        # Разделитель
        #separator = ctk.CTkFrame(self.frame, height=2, fg_color="gray")
        #separator.pack(fill="x", padx=10, pady=5)
        
        # Список файлов
        #files_label = ctk.CTkLabel(
        #    self.frame,
        #    text="Файлы:",
        #    font=ctk.CTkFont(size=11, weight="bold")
        #)
        #files_label.pack(pady=(5, 5), padx=10, anchor="w")
        
        # Скроллируемый список файлов
        self.file_listbox_frame = ctk.CTkScrollableFrame(self.frame)
        self.file_listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Словарь для хранения кнопок файлов
        self.file_buttons = {}
        
        # Обновление списка файлов
        self.refresh_file_list()
    
    def _truncate_path(self, path: str, max_length: int = 30) -> str:
        """
        Обрезание пути для отображения.
        
        Args:
            path: Путь для обрезки
            max_length: Максимальная длина
        
        Returns:
            Обрезанный путь
        """
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
    
    def _select_directory(self):
        """Выбор директории."""
        directory = filedialog.askdirectory(initialdir=self.current_directory)
        
        if directory:
            self.set_directory(directory)
    
    def set_directory(self, directory: str):
        """
        Установка текущей директории.

        Args:
            directory: Путь к директории
        """
        if os.path.isdir(directory):
            self.current_directory = directory
            self.dir_label.configure(text=self._truncate_path(self.current_directory))
            self.refresh_file_list()
    
    def refresh_file_list(self):
        """Обновление списка файлов."""
        # Очистка существующих кнопок и виджетов
        for widget in self.file_listbox_frame.winfo_children():
            widget.destroy()
        self.file_buttons.clear()
        self.selected_file = None

        # Получение списка файлов
        files = self._get_files()

        if not files:
            no_files_label = ctk.CTkLabel(
                self.file_listbox_frame,
                text="Нет файлов",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            no_files_label.pack(pady=10)
        else:
            # Создание кнопок для каждого файла
            for file_name in sorted(files):
                file_path = os.path.join(self.current_directory, file_name)
                self._create_file_button(file_name, file_path)
    
    def _get_files(self) -> List[str]:
        """
        Получение списка файлов в текущей директории.

        Returns:
            Список имен файлов
        """
        try:
            files = os.listdir(self.current_directory)
            return [f for f in files if os.path.isfile(os.path.join(self.current_directory, f))]
        except Exception as e:
            print(f"Ошибка чтения директории: {e}")
            return []
    
    def _create_file_button(self, file_name: str, file_path: str):
        """
        Создание кнопки для файла.
        
        Args:
            file_name: Имя файла
            file_path: Полный путь к файлу
        """
        button = ctk.CTkButton(
            self.file_listbox_frame,
            text=file_name,
            command=lambda: self._select_file(file_path),
            width=200,
            height=30,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        button.pack(fill="x", pady=2, padx=5)
        self.file_buttons[file_path] = button
    
    def _select_file(self, file_path: str):
        """
        Выбор файла.
        
        Args:
            file_path: Путь к выбранному файлу
        """
        # Сброс выделения предыдущего файла
        if self.selected_file and self.selected_file in self.file_buttons:
            self.file_buttons[self.selected_file].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )
        
        # Выделение текущего файла
        self.selected_file = file_path
        if file_path in self.file_buttons:
            self.file_buttons[file_path].configure(
                fg_color=("gray75", "gray25"),
                text_color=("gray10", "gray90")
            )
        
        # Вызов callback
        if self.on_file_select:
            self.on_file_select(file_path)
    
    def get_current_directory(self) -> str:
        """
        Получение текущей директории.
        
        Returns:
            Путь к текущей директории
        """
        return self.current_directory
    
    def get_selected_file(self) -> Optional[str]:
        """
        Получение выбранного файла.
        
        Returns:
            Путь к выбранному файлу или None
        """
        return self.selected_file

