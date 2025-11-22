"""Диалог справки по горячим клавишам."""
import customtkinter as ctk
import tkinter as tk
from typing import List, Tuple, Optional
from utils.hotkey_manager import HotkeyManager


class HotkeysHelpDialog:
    """Диалоговое окно со списком всех горячих клавиш."""
    
    def __init__(self, parent: tk.Widget, hotkey_manager: Optional[HotkeyManager] = None):
        """
        Инициализация диалога справки.
        
        Args:
            parent: Родительский виджет
            hotkey_manager: Менеджер горячих клавиш (опционально)
        """
        self.parent = parent
        self.hotkey_manager = hotkey_manager
        
        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Горячие клавиши")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self._center_window()
        
        # Создаем UI
        self._create_ui()
        
        # Фокус на окне
        self.window.focus_set()
    
    def _center_window(self):
        """Центрирование окна относительно родителя."""
        try:
            self.window.update_idletasks()
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            window_width = self.window.winfo_reqwidth()
            window_height = self.window.winfo_reqheight()
            
            x = parent_x + (parent_width - window_width) // 2
            y = parent_y + (parent_height - window_height) // 2
            
            self.window.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Ошибка центрирования окна: {e}")
            # Используем значения по умолчанию
            self.window.geometry("600x500+100+100")
    
    def _create_ui(self):
        """Создание интерфейса диалога."""
        try:
            # Основной контейнер
            main_frame = ctk.CTkFrame(self.window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Заголовок
            title_label = ctk.CTkLabel(
                main_frame,
                text="Горячие клавиши",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 10))
            
            # Поле поиска
            search_frame = ctk.CTkFrame(main_frame)
            search_frame.pack(fill="x", pady=(0, 10))
            
            search_label = ctk.CTkLabel(search_frame, text="Поиск:")
            search_label.pack(side="left", padx=(0, 5))
            
            self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Введите для поиска...")
            self.search_entry.pack(side="left", fill="x", expand=True)
            self.search_entry.bind("<KeyRelease>", self._on_search)
            
            # Скроллируемый фрейм для списка горячих клавиш
            scroll_frame = ctk.CTkScrollableFrame(main_frame)
            scroll_frame.pack(fill="both", expand=True)
            
            # Получаем список горячих клавиш
            hotkeys = self._get_hotkeys_list()
            
            # Группируем по категориям
            categories = self._group_by_category(hotkeys)
            
            # Отображаем по категориям
            self.hotkey_labels = []
            for category, items in categories.items():
                # Заголовок категории
                category_label = ctk.CTkLabel(
                    scroll_frame,
                    text=category,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                category_label.pack(anchor="w", pady=(10, 5), padx=5)
                self.hotkey_labels.append(category_label)
                
                # Элементы категории
                for key, description in items:
                    item_frame = ctk.CTkFrame(scroll_frame)
                    item_frame.pack(fill="x", padx=5, pady=2)
                    
                    key_label = ctk.CTkLabel(
                        item_frame,
                        text=key,
                        font=ctk.CTkFont(family="Consolas", size=12),
                        width=150,
                        anchor="w"
                    )
                    key_label.pack(side="left", padx=10, pady=5)
                    
                    desc_label = ctk.CTkLabel(
                        item_frame,
                        text=description,
                        anchor="w"
                    )
                    desc_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
                    
                    self.hotkey_labels.append((item_frame, key, description))
            
            # Кнопка закрытия (вне цикла категорий)
            close_btn = ctk.CTkButton(
                main_frame,
                text="Закрыть",
                command=self.window.destroy,
                width=100
            )
            close_btn.pack(pady=(10, 0))
        except Exception as e:
            print(f"Ошибка создания UI диалога справки: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_hotkeys_list(self) -> List[Tuple[str, str]]:
        """Получить список всех горячих клавиш."""
        # Базовый список горячих клавиш
        default_hotkeys = [
            ("F5", "Выполнить код"),
            ("Ctrl+N", "Создать новый файл"),
            ("Ctrl+S", "Сохранить файл"),
            ("Ctrl+C", "Копировать выделенный текст"),
            ("Ctrl+V", "Вставить из буфера обмена"),
            ("Ctrl+X", "Вырезать выделенный текст"),
            ("Ctrl+A", "Выделить весь текст"),
            ("Ctrl+Space", "Показать автодополнение"),
            ("Tab", "Вставить автодополнение (когда активно)"),
            ("Escape", "Закрыть автодополнение"),
            ("Delete", "Удалить файл (если нет выделенного текста)"),
            ("F1", "Показать справку по горячим клавишам"),
        ]
        
        # Если есть менеджер, получаем дополнительные привязки
        if self.hotkey_manager:
            manager_bindings = self.hotkey_manager.get_all_bindings()
            # Добавляем уникальные привязки из менеджера
            manager_keys = {key: desc for key, _, desc in manager_bindings}
            for key, desc in manager_keys.items():
                if not any(key == dk[0] for dk in default_hotkeys):
                    default_hotkeys.append((key, desc))
        
        return default_hotkeys
    
    def _group_by_category(self, hotkeys: List[Tuple[str, str]]) -> dict:
        """Группировка горячих клавиш по категориям."""
        categories = {
            "Файлы": [],
            "Редактор": [],
            "Автодополнение": [],
            "Общие": []
        }
        
        for key, description in hotkeys:
            key_lower = key.lower()
            desc_lower = description.lower()
            
            if "файл" in desc_lower or "сохран" in desc_lower or "созда" in desc_lower or "удал" in desc_lower:
                categories["Файлы"].append((key, description))
            elif "автодополн" in desc_lower or "tab" in key_lower or "escape" in key_lower or "space" in key_lower:
                categories["Автодополнение"].append((key, description))
            elif "копир" in desc_lower or "встав" in desc_lower or "вырез" in desc_lower or "выдел" in desc_lower or "выполн" in desc_lower or "f5" in key_lower:
                categories["Редактор"].append((key, description))
            else:
                categories["Общие"].append((key, description))
        
        # Удаляем пустые категории
        return {k: v for k, v in categories.items() if v}
    
    def _on_search(self, event=None):
        """Обработка поиска."""
        search_text = self.search_entry.get().lower()
        
        # Показываем/скрываем элементы в зависимости от поиска
        for item in self.hotkey_labels:
            if isinstance(item, tuple):
                item_frame, key, description = item
                if search_text in key.lower() or search_text in description.lower():
                    item_frame.pack(fill="x", pady=2, padx=5)
                else:
                    item_frame.pack_forget()
            else:
                # Для заголовков категорий - показываем всегда
                pass
