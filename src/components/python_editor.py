"""
Улучшенный компонент редактора Python кода с подсветкой синтаксиса и автодополнением.

Автодополнение:
- Автоматически появляется при вводе точки (например, "str.")
- Автоматически появляется при вводе букв и цифр (с небольшой задержкой)
- Можно вызвать вручную нажатием Ctrl+Space
- Навигация: стрелки Вверх/Вниз для выбора, Tab или Enter для вставки, Escape для закрытия
- Использует библиотеку jedi для анализа кода и предложения вариантов
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import re
from typing import Optional, List, Tuple
from utils.keyboard_utils import copy_to_clipboard, get_selected_text, get_clipboard_text, bind_case_insensitive
from utils.bindtag_context import BindTagContext
from components.notification import Notification

try:
    from idlelib.colorizer import ColorDelegator
    from idlelib.percolator import Percolator
    IDLELIB_AVAILABLE = True
except ImportError:
    IDLELIB_AVAILABLE = False
    print("Предупреждение: idlelib недоступен, подсветка синтаксиса будет ограничена")

try:
    import jedi
    JEDI_AVAILABLE = True
except ImportError:
    JEDI_AVAILABLE = False
    print("Предупреждение: jedi недоступен, автодополнение будет ограничено")



class PythonEditor:
    """Класс для редактирования Python кода с подсветкой синтаксиса и автодополнением."""
    
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
        
        # Настройка подсветки синтаксиса
        if IDLELIB_AVAILABLE:
            try:
                self.colorizer = ColorDelegator()
                self.percolator = Percolator(self.text_widget)
                self.percolator.insertfilter(self.colorizer)
                # Настройка тегов для прозрачного фона
                self._configure_syntax_tags()
                # Настройка тега для выделения совпадений
                self._configure_match_highlight_tag()
            except Exception as e:
                print(f"Ошибка инициализации подсветки синтаксиса: {e}")
        
        # Настройка автодополнения
        self.autocomplete_active = False
        self.autocomplete_listbox = None
        self.autocomplete_window = None
        
        # Настройка всплывающих подсказок
        self.tooltip_active = False
        self.tooltip_window = None
        self.tooltip_timer = None

        # Настройка выделения совпадающего текста
        self.match_highlight_active = False

        # Настройка контекстного меню (как в окне вывода)
        self._setup_context_menu()
        
        # Callback для выполнения кода (устанавливается извне)
        self.run_code_callback = None
        # Callbacks для действий с файлами (устанавливаются извне)
        self.create_file_callback = None
        self.save_file_callback = None
        self.delete_file_callback = None
        
        # Привязка событий для автодополнения
        # События для навигации будут привязываться динамически при открытии автодополнения
        # Также привязываем общий KeyPress для закрытия подсказок и других обработок
        # ВАЖНО: используем add="+" чтобы не блокировать стандартные обработчики клавиатуры
        self.text_widget.bind("<KeyPress>", self._on_key_press, add="+")
        self.text_widget.bind("<KeyRelease>", self._on_key_release)
        self.text_widget.bind("<Tab>", self._on_tab, add="+")
        self.text_widget.bind("<Escape>", self._close_autocomplete, add="+")
        self.text_widget.bind("<F5>", self._on_f5)
        
        # ID привязок для навигации (для последующего отвязывания)
        self._nav_bind_ids = []
        # Имя специального тега для обработчиков автокомплита
        self._autocomplete_tag = None
        self.text_widget.bind("<Button-1>", self._on_mouse_click)
        self.text_widget.bind("<Button-3>", self._show_context_menu)  # Правая кнопка мыши
        self.text_widget.bind("<Control-space>", lambda e: self._try_autocomplete())
        
        # Явная привязка стандартных комбинаций клавиш для копирования/вставки
        # Используем утилиты для автоматической поддержки обоих регистров
        bind_case_insensitive(self.text_widget, "<Control-c>", self._copy_text, add="+")
        bind_case_insensitive(self.text_widget, "<Control-v>", self._paste_text, add="+")
        bind_case_insensitive(self.text_widget, "<Control-x>", self._cut_text, add="+")
        bind_case_insensitive(self.text_widget, "<Control-a>", self._select_all, add="+")
        # Горячие клавиши Ctrl+N и Ctrl+S теперь регистрируются глобально в app.py
        
        # Отслеживаем изменения текста для обновления подсветки после вставки
        self.text_widget.bind("<<Modified>>", self._on_text_modified)

        # Привязка событий для выделения совпадающего текста
        self.text_widget.bind("<<Selection>>", self._on_selection_changed)

        # Привязка событий для всплывающих подсказок
        self.text_widget.bind("<Motion>", self._on_mouse_motion)
        self.text_widget.bind("<Leave>", lambda e: self._close_tooltip())
        # KeyPress для закрытия подсказок обрабатывается в _on_key_press

        # Вставка начального кода
        if initial_code:
            self.text_widget.insert("1.0", initial_code)
            self._update_syntax_highlighting()
        
        # Устанавливаем правильный порядок bind tags сразу после создания виджета
        # Это критически важно для корректной работы горячих клавиш
        self._ensure_bindtags_order()
        
        # Устанавливаем фокус на редактор после полной инициализации
        # Это критически важно для корректной работы горячих клавиш
        self.text_widget.after(100, self._ensure_focus)
    
    def _get_bg_color(self) -> str:
        """Получение цвета фона в зависимости от темы."""
        return "#1e1e1e" if ctk.get_appearance_mode() == "Dark" else "#ffffff"
    
    def _configure_syntax_tags(self):
        """Настройка тегов подсветки синтаксиса с прозрачным фоном."""
        # Получаем цвет фона виджета
        bg_color = self.text_widget.cget("bg")
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        # Цвета для темной темы
        if is_dark:
            tag_colors = {
                "KEYWORD": "#569cd6",      # Синий для ключевых слов
                "BUILTIN": "#4ec9b0",      # Бирюзовый для встроенных функций
                "STRING": "#ce9178",        # Оранжевый для строк
                "COMMENT": "#6a9955",      # Зеленый для комментариев
                "DEFINITION": "#dcdcaa",   # Желтый для определений
                "CLASSNAME": "#4ec9b0",    # Бирюзовый для имен классов
            }
        else:
            # Цвета для светлой темы (стандартные цвета IDLE)
            tag_colors = {
                "KEYWORD": "#ff7700",      # Оранжевый
                "BUILTIN": "#900090",      # Фиолетовый
                "STRING": "#00aa00",       # Зеленый
                "COMMENT": "#dd0000",      # Красный
                "DEFINITION": "#0000ff",   # Синий
                "CLASSNAME": "#900090",    # Фиолетовый
            }
        
        # Список тегов, которые использует ColorDelegator
        syntax_tags = [
            "KEYWORD", "BUILTIN", "STRING", "COMMENT", "DEFINITION",
            "SYNC", "TODO", "ERROR", "BREAK", "KEYWORD2", "CLASSNAME"
        ]
        
        # Настраиваем каждый тег с прозрачным фоном и правильным цветом текста
        for tag in syntax_tags:
            try:
                # Получаем цвет для тега (если определен)
                foreground = tag_colors.get(tag)
                
                # Настраиваем тег с фоном, соответствующим фону виджета
                if foreground:
                    self.text_widget.tag_configure(tag, background=bg_color, foreground=foreground)
                else:
                    self.text_widget.tag_configure(tag, background=bg_color)
            except tk.TclError:
                # Тег еще не создан, создадим его с правильным фоном
                foreground = tag_colors.get(tag)
                if foreground:
                    self.text_widget.tag_configure(tag, background=bg_color, foreground=foreground)
                else:
                    self.text_widget.tag_configure(tag, background=bg_color)

    def _configure_match_highlight_tag(self):
        """Настройка тега для выделения совпадающего текста."""
        is_dark = ctk.get_appearance_mode() == "Dark"
        if is_dark:
            # Светло-синий фон для темной темы
            self.text_widget.tag_configure("match_highlight", background="#3d5a80", foreground="#ffffff")
        else:
            # Светло-желтый фон для светлой темы
            self.text_widget.tag_configure("match_highlight", background="#fef3c7", foreground="#000000")

    def _on_selection_changed(self, event=None):
        """Обработка изменения выделения текста."""
        # Очищаем предыдущие выделения совпадений
        self._clear_match_highlights()

        # Получаем выделенный текст
        try:
            selected_text = self.text_widget.get("sel.first", "sel.last")
        except tk.TclError:
            # Нет выделенного текста
            return

        # Если выделенный текст слишком короткий или содержит только пробелы, не выделяем
        if not selected_text or len(selected_text.strip()) < 2:
            return

        # Если выделенный текст слишком длинный, не выделяем (чтобы избежать проблем с производительностью)
        if len(selected_text) > 100:
            return

        # Находим и выделяем все совпадения
        self._highlight_matching_text(selected_text)

    def _highlight_matching_text(self, search_text: str):
        """Выделение всех совпадений заданного текста."""
        # Получаем весь текст
        full_text = self.text_widget.get("1.0", "end-1c")

        # Ищем все позиции совпадений (без учета регистра для лучшего UX)
        search_lower = search_text.lower()
        start_pos = "1.0"

        while True:
            # Ищем следующее совпадение
            start_idx = self.text_widget.search(
                search_text, start_pos, "end",
                nocase=True,  # Поиск без учета регистра
                exact=True    # Точное совпадение
            )

            if not start_idx:
                break

            # Вычисляем конечную позицию
            end_idx = self.text_widget.index(f"{start_idx}+{len(search_text)}c")

            # Проверяем, что это не то же самое выделение, которое уже есть
            if not self._is_current_selection(start_idx, end_idx):
                # Выделяем совпадение
                self.text_widget.tag_add("match_highlight", start_idx, end_idx)

            # Переходим к следующей позиции
            start_pos = end_idx

    def _is_current_selection(self, start_idx: str, end_idx: str) -> bool:
        """Проверка, является ли позиция текущим выделением."""
        try:
            sel_start = self.text_widget.index("sel.first")
            sel_end = self.text_widget.index("sel.last")
            return start_idx == sel_start and end_idx == sel_end
        except tk.TclError:
            return False

    def _clear_match_highlights(self):
        """Очистка всех выделений совпадений."""
        self.text_widget.tag_remove("match_highlight", "1.0", "end")

    def _update_syntax_highlighting(self):
        """Обновление подсветки синтаксиса."""
        if IDLELIB_AVAILABLE and hasattr(self, 'colorizer'):
            try:
                # Перезапуск подсветки
                self.percolator.removefilter(self.colorizer)
                self.colorizer = ColorDelegator()
                self.percolator.insertfilter(self.colorizer)
                # Перенастройка тегов для прозрачного фона
                self._configure_syntax_tags()
                # Настройка тега для выделения совпадений
                self._configure_match_highlight_tag()
            except Exception:
                pass

        # Очищаем выделения совпадений при изменении текста
        self._clear_match_highlights()
    
    def _on_key_release(self, event):
        """Обработка нажатия клавиш для автодополнения."""
        # ВАЖНО: Не обрабатываем стандартные комбинации клавиш - они обрабатываются отдельно
        # Проверяем, нажата ли клавиша Control
        if event.state & 0x4:  # Control нажат
            # Если это стандартные комбинации (C, V, X, A), полностью игнорируем
            if event.keysym.lower() in ['c', 'v', 'x', 'a']:
                return None  # Позволяем стандартным обработчикам работать
            return None  # Для других комбинаций с Control тоже пропускаем
        
        # Если автодополнение активно, стрелки Up/Down и Enter обрабатываются в _on_key_press
        # Здесь мы их игнорируем, чтобы они не мешали навигации по списку
        if self.autocomplete_active and self.autocomplete_listbox:
            if event.keysym in ['Up', 'Down', 'Return']:
                return None  # Эти клавиши обрабатываются в _on_key_press для автодополнения
        
        # Закрываем автодополнение при других клавишах навигации
        if event.keysym in ['Escape', 'Left', 'Right', 'Home', 'End']:
            self._close_autocomplete()
            return None
        
        # Автодополнение при вводе точки
        if event.char == '.':
            # Небольшая задержка для обработки точки
            self.text_widget.after(50, self._try_autocomplete)
        # Автодополнение при вводе букв, цифр и подчеркивания
        elif event.char and (event.char.isalnum() or event.char == '_'):
            # Обновляем автодополнение при вводе символов (оно само закроется, если нет предложений)
            self.text_widget.after(150, self._try_autocomplete)
        
        return None  # Не блокируем стандартное поведение
    
    def _on_mouse_click(self, event):
        """Обработка клика мыши."""
        self._close_autocomplete()
        # Очищаем выделения совпадений при клике
        self._clear_match_highlights()
        # Явно устанавливаем фокус на редактор для гарантированной работы горячих клавиш
        self.text_widget.focus_set()
        # Позволяем стандартному поведению работать
        return None
    
    def _ensure_bindtags_order(self):
        """Восстанавливает правильный порядок bind tags для гарантированной работы горячих клавиш."""
        try:
            # Восстанавливаем правильный порядок bind tags
            # Стандартный порядок для Text виджета: виджет -> класс -> родитель -> root -> all
            current_tags = list(self.text_widget.bindtags())
            
            # Убеждаемся, что виджет сам находится первым в списке bind tags
            # Это гарантирует, что привязки виджета обрабатываются первыми
            widget_str = str(self.text_widget)
            if current_tags[0] != widget_str:
                # Удаляем виджет из текущего списка, если он там есть
                if widget_str in current_tags:
                    current_tags.remove(widget_str)
                # Добавляем виджет в начало списка
                current_tags.insert(0, widget_str)
                self.text_widget.bindtags(current_tags)
        except Exception as e:
            print(f"Ошибка при восстановлении порядка bind tags: {e}")
    
    def _ensure_focus(self):
        """Устанавливает фокус на текстовый виджет редактора и восстанавливает правильный порядок bind tags."""
        try:
            # Восстанавливаем правильный порядок bind tags перед установкой фокуса
            self._ensure_bindtags_order()
            self.text_widget.focus_set()
        except Exception:
            pass
    
    def _on_key_press_up(self, event):
        """Обработка клавиши Вверх для навигации по автодополнению."""
        try:
            if self.autocomplete_active and self.autocomplete_listbox:
                self._autocomplete_navigate(event)
                return "break"
            return None
        except Exception as e:
            print(f"Ошибка обработки клавиши Вверх: {e}")
            return None
    
    def _on_key_press_down(self, event):
        """Обработка клавиши Вниз для навигации по автодополнению."""
        try:
            if self.autocomplete_active and self.autocomplete_listbox:
                self._autocomplete_navigate(event)
                return "break"
            return None
        except Exception as e:
            print(f"Ошибка обработки клавиши Вниз: {e}")
            return None
    
    def _on_key_press_return(self, event):
        """Обработка клавиши Enter для вставки автодополнения."""
        try:
            if self.autocomplete_active and self.autocomplete_listbox:
                self._insert_autocomplete()
                return "break"
            return None
        except Exception as e:
            print(f"Ошибка обработки клавиши Enter: {e}")
            return None
    
    def _on_key_press(self, event):
        """Обработка нажатия клавиш для закрытия подсказок."""
        try:
            # Закрываем всплывающие подсказки при нажатии любой клавиши
            self._close_tooltip()
            
            # Escape закрывает автодополнение
            if event.keysym == "Escape" and self.autocomplete_active:
                self._close_autocomplete()
                return "break"
            
            # Все остальные клавиши обрабатываются редактором как обычно
            return None
        except Exception as e:
            print(f"Ошибка в обработчике нажатия клавиши: {e}")
            return None
    
    def _on_f5(self, event):
        """Обработка нажатия F5 для выполнения кода."""
        try:
            if self.run_code_callback:
                self.run_code_callback()
            return "break"
        except Exception as e:
            print(f"Ошибка выполнения кода (F5): {e}")
            return None
    
    def _on_tab(self, event):
        """Обработка Tab для автодополнения."""
        try:
            if self.autocomplete_active and self.autocomplete_listbox:
                # Выбор первого элемента из списка
                if self.autocomplete_listbox.size() > 0:
                    self._insert_autocomplete(0)
                    return "break"
            return None
        except Exception as e:
            print(f"Ошибка обработки Tab для автодополнения: {e}")
            return None
    
    def _copy_text(self, event=None):
        """Копирование выделенного текста."""
        try:
            selected_text = get_selected_text(self.text_widget)
            if selected_text:
                copy_to_clipboard(self.text_widget, selected_text)
            return "break"  # Предотвращаем дальнейшую обработку
        except Exception as e:
            print(f"Ошибка копирования: {e}")
            return None
    
    def _cut_text(self, event=None):
        """Вырезание выделенного текста."""
        try:
            selected_text = get_selected_text(self.text_widget)
            if selected_text:
                # Копируем в буфер обмена
                copy_to_clipboard(self.text_widget, selected_text)
                # Удаляем выделенный текст
                self.text_widget.delete("sel.first", "sel.last")
                # Обновляем подсветку после вырезания
                self.text_widget.after(10, self._update_syntax_highlighting)
            return "break"
        except Exception as e:
            print(f"Ошибка вырезания: {e}")
            return None
    
    def _paste_text(self, event=None):
        """Вставка текста из буфера обмена."""
        try:
            clipboard_text = get_clipboard_text(self.text_widget)
            if clipboard_text:
                # Удаляем выделенный текст, если есть
                if self.text_widget.tag_ranges("sel"):
                    self.text_widget.delete("sel.first", "sel.last")
                
                # Вставляем текст в позицию курсора
                self.text_widget.insert("insert", clipboard_text)
                # Очищаем выделения совпадений
                self._clear_match_highlights()
                # Обновляем подсветку после вставки
                self.text_widget.after(10, self._update_syntax_highlighting)
            return "break"
        except Exception as e:
            print(f"Ошибка вставки: {e}")
            return None
    
    def _select_all(self, event=None):
        """Выделение всего текста."""
        try:
            self.text_widget.tag_add("sel", "1.0", "end-1c")
            self.text_widget.mark_set("insert", "1.0")
            self.text_widget.see("insert")
            return "break"
        except Exception as e:
            print(f"Ошибка выделения всего текста (Ctrl+A): {e}")
            return None
    
    def _setup_context_menu(self):
        """Настройка контекстного меню для копирования/вставки (как в окне вывода)."""
        # Создаем контекстное меню один раз при инициализации
        self.context_menu = tk.Menu(self.text_widget, tearoff=0)
        
        # Добавляем пункты меню
        self.context_menu.add_command(label="Копировать выделенный текст (Ctrl+C)", command=self._copy_text)
        self.context_menu.add_command(label="Вырезать выделенный текст (Ctrl+X)", command=self._cut_text)
        self.context_menu.add_command(label="Вставить (Ctrl+V)", command=self._paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить всё (Ctrl+A)", command=self._select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Копировать весь код", command=self._copy_all_code)
    
    def _copy_all_code(self):
        """Копирование всего кода из редактора."""
        try:
            code = self.get_code()
            if code:
                self.text_widget.clipboard_clear()
                self.text_widget.clipboard_append(code)
                print(f"Весь код скопирован в буфер обмена ({len(code)} символов)")
        except Exception as e:
            print(f"Ошибка копирования всего кода: {e}")
    
    def _show_context_menu(self, event):
        """Показ контекстного меню с опциями копирования/вставки."""
        try:
            # Обновляем состояние пунктов меню в зависимости от контекста
            has_selection = bool(self.text_widget.tag_ranges("sel"))
            
            # Обновляем состояние пунктов меню
            try:
                # Проверяем, есть ли текст в буфере обмена
                clipboard_text = self.text_widget.clipboard_get()
                has_clipboard = bool(clipboard_text)
            except tk.TclError:
                has_clipboard = False
            
            # Обновляем состояние пунктов меню
            if has_selection:
                self.context_menu.entryconfig(0, state="normal")  # Копировать выделенный
                self.context_menu.entryconfig(1, state="normal")  # Вырезать выделенный
            else:
                self.context_menu.entryconfig(0, state="disabled")  # Копировать выделенный
                self.context_menu.entryconfig(1, state="disabled")  # Вырезать выделенный
            
            if has_clipboard:
                self.context_menu.entryconfig(2, state="normal")  # Вставить
            else:
                self.context_menu.entryconfig(2, state="disabled")  # Вставить
            
            # Показываем меню
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Освобождаем меню после использования
                self.context_menu.grab_release()
        except Exception as e:
            print(f"Ошибка показа контекстного меню: {e}")
    
    def _try_autocomplete(self):
        """Попытка показать автодополнение."""
        if not JEDI_AVAILABLE:
            print("DEBUG: Jedi недоступен, автодополнение не работает")
            return
        
        try:
            # Получение текущей позиции курсора
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))
            
            # Получение кода до курсора
            code = self.text_widget.get("1.0", cursor_pos)
            
            # Если код пустой или только пробелы, не показываем автодополнение
            if not code.strip():
                return
            
            # Получение предложений от jedi
            # В jedi 0.19+ API изменился: используем Script(code).complete(line, col)
            script = jedi.Script(code)
            completions = script.complete(line, col)
            
            # Фильтруем предложения:
            # - Показываем все публичные методы/атрибуты (не начинающиеся с _)
            # - Или специальные методы (начинающиеся с __)
            # - Исключаем приватные методы (начинающиеся с _ но не __)
            filtered_completions = []
            for c in completions:
                name = c.name
                # Показываем публичные методы
                if not name.startswith('_'):
                    filtered_completions.append(c)
                # Показываем специальные методы (__init__, __str__ и т.д.)
                elif name.startswith('__') and name.endswith('__'):
                    filtered_completions.append(c)
            
            # Если есть предложения, показываем их
            if filtered_completions:
                self._show_autocomplete(filtered_completions, line, col)
            else:
                # Если нет предложений, закрываем окно автодополнения
                self._close_autocomplete()
        except Exception as e:
            # Игнорируем ошибки автодополнения (jedi может выдать ошибку на некорректном коде)
            pass
    
    def _show_autocomplete(self, completions: List, line: int, col: int):
        """Показ окна автодополнения."""
        self._close_autocomplete()
        
        # Получение позиции курсора в пикселях
        bbox = self.text_widget.bbox(f"{line}.{col}")
        if not bbox:
            return
        
        x, y, width, height = bbox
        
        # Получаем абсолютные координаты виджета
        widget_x = self.text_widget.winfo_rootx()
        widget_y = self.text_widget.winfo_rooty()
        
        # Вычисляем абсолютную позицию окна автодополнения
        window_x = widget_x + x
        window_y = widget_y + y + height
        
        # Создание окна автодополнения
        self.autocomplete_window = tk.Toplevel(self.text_widget)
        self.autocomplete_window.wm_overrideredirect(True)
        self.autocomplete_window.wm_geometry(f"+{window_x}+{window_y}")
        
        # Убеждаемся, что окно поверх других окон
        self.autocomplete_window.attributes('-topmost', True)
        
        # Создание списка предложений
        list_height = min(len(completions), 10)
        self.autocomplete_listbox = tk.Listbox(
            self.autocomplete_window,
            height=list_height,
            font=("Consolas", 10),
            bg="#2d2d2d" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#d4d4d4" if ctk.get_appearance_mode() == "Dark" else "#000000",
            selectbackground="#264f78" if ctk.get_appearance_mode() == "Dark" else "#316ac5",
            selectforeground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.autocomplete_listbox.pack()
        
        # Добавление предложений
        for completion in completions[:20]:  # Ограничиваем до 20 предложений
            name = completion.name
            if completion.type:
                display_text = f"{name} ({completion.type})"
            else:
                display_text = name
            self.autocomplete_listbox.insert(tk.END, display_text)
        
        # Привязка событий для мыши (работает даже без фокуса)
        self.autocomplete_listbox.bind("<Double-Button-1>", lambda e: self._insert_autocomplete())
        self.autocomplete_listbox.bind("<Button-1>", self._on_autocomplete_click)
        # Привязки для клавиатуры (если фокус случайно переключится на listbox)
        self.autocomplete_listbox.bind("<Return>", lambda e: self._insert_autocomplete())
        self.autocomplete_listbox.bind("<Escape>", lambda e: self._close_autocomplete())
        # При навигации стрелками в listbox возвращаем фокус в редактор
        def handle_nav(e):
            self.text_widget.focus_set()
            self._autocomplete_navigate(e)
        self.autocomplete_listbox.bind("<Up>", handle_nav)
        self.autocomplete_listbox.bind("<Down>", handle_nav)
        
        # Выбор первого элемента
        if self.autocomplete_listbox.size() > 0:
            self.autocomplete_listbox.selection_set(0)
            self.autocomplete_listbox.activate(0)
        
        self.autocomplete_active = True
        
        # Используем контекстный менеджер для управления bindtags
        # Это позволяет нашим обработчикам вызываться первыми, но не блокировать стандартное поведение
        # когда автокомплит неактивен
        autocomplete_tag = "AutocompleteHandlers"
        self._autocomplete_tag = autocomplete_tag
        
        # Сохраняем контекст для последующего закрытия
        self._bindtag_context = BindTagContext(self.text_widget, autocomplete_tag)
        self._bindtag_context.__enter__()
        
        # Привязываем события навигации к специальному тегу
        # Это позволяет нашим обработчикам вызываться первыми
        self.text_widget.bind_class(autocomplete_tag, "<Up>", self._on_key_press_up)
        self.text_widget.bind_class(autocomplete_tag, "<Down>", self._on_key_press_down)
        self.text_widget.bind_class(autocomplete_tag, "<Return>", self._on_key_press_return)
        
        # Обновляем окно, чтобы оно точно отобразилось
        self.autocomplete_window.update_idletasks()
        
        # НЕ переключаем фокус на listbox - оставляем фокус в редакторе
        # Навигация будет обрабатываться через привязки событий в редакторе
        # Это позволяет продолжать ввод в редактор, даже когда автодополнение активно
    
    def _autocomplete_navigate(self, event):
        """Навигация по списку автодополнения."""
        if not self.autocomplete_listbox:
            return "break"
        
        current = self.autocomplete_listbox.curselection()
        # Если нет выбранного элемента, выбираем первый
        if not current:
            current_index = 0
        else:
            current_index = current[0]
        
        max_index = self.autocomplete_listbox.size() - 1
        
        if event.keysym == "Up":
            new_index = max(0, current_index - 1)
        elif event.keysym == "Down":
            new_index = min(max_index, current_index + 1)
        else:
            return "break"
        
        self.autocomplete_listbox.selection_clear(0, tk.END)
        self.autocomplete_listbox.selection_set(new_index)
        self.autocomplete_listbox.activate(new_index)
        self.autocomplete_listbox.see(new_index)
        
        return "break"
    
    def _on_autocomplete_click(self, event):
        """Обработка клика на элемент автодополнения."""
        # Выбираем элемент под курсором мыши
        index = self.autocomplete_listbox.nearest(event.y)
        self.autocomplete_listbox.selection_clear(0, tk.END)
        self.autocomplete_listbox.selection_set(index)
        self.autocomplete_listbox.activate(index)
        # Возвращаем фокус в редактор
        self.text_widget.focus_set()
    
    def _insert_autocomplete(self, index: Optional[int] = None):
        """Вставка выбранного автодополнения."""
        if not self.autocomplete_listbox:
            return
        
        if index is None:
            selection = self.autocomplete_listbox.curselection()
            if not selection:
                return
            index = selection[0]
        
        # Получение текста предложения (без типа в скобках)
        item_text = self.autocomplete_listbox.get(index)
        # Извлекаем только имя (до скобки если есть)
        name = item_text.split('(')[0].strip()
        
        # Получение текущей позиции курсора
        cursor_pos = self.text_widget.index(tk.INSERT)
        line, col = map(int, cursor_pos.split('.'))
        
        # Получение текста до курсора для определения что нужно заменить
        line_text = self.text_widget.get(f"{line}.0", cursor_pos)
        
        # Поиск последнего идентификатора или точки
        # Ищем паттерн: идентификатор.часть_которую_заменяем
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.?)([a-zA-Z_][a-zA-Z0-9_]*)?$', line_text)
        if match:
            # Если есть точка, заменяем только часть после точки
            if '.' in match.group(0):
                # Находим позицию после последней точки
                dot_pos = line_text.rfind('.')
                start_col = col - (col - dot_pos - 1)
                self.text_widget.delete(f"{line}.{start_col}", cursor_pos)
                self.text_widget.insert(f"{line}.{start_col}", name)
            else:
                # Заменяем весь идентификатор
                start_col = col - len(match.group(1))
                self.text_widget.delete(f"{line}.{start_col}", cursor_pos)
                self.text_widget.insert(f"{line}.{start_col}", name)
        else:
            # Просто вставляем имя
            self.text_widget.insert(cursor_pos, name)
        
        self._close_autocomplete()
        # Убеждаемся, что фокус в редакторе
        self.text_widget.focus_set()
        self._update_syntax_highlighting()
    
    def _close_autocomplete(self, event=None):
        """Закрытие окна автодополнения."""
        try:
            if self.autocomplete_window:
                self.autocomplete_window.destroy()
                self.autocomplete_window = None
                self.autocomplete_listbox = None
                self.autocomplete_active = False
                
                # Отвязываем события навигации от специального тега
                if hasattr(self, '_autocomplete_tag') and self._autocomplete_tag:
                    try:
                        # Удаляем привязки от класса
                        self.text_widget.unbind_class(self._autocomplete_tag, "<Up>")
                        self.text_widget.unbind_class(self._autocomplete_tag, "<Down>")
                        self.text_widget.unbind_class(self._autocomplete_tag, "<Return>")
                    except Exception as e:
                        print(f"Ошибка при отвязывании событий автодополнения: {e}")
                
                # Закрываем контекстный менеджер для удаления тега
                if hasattr(self, '_bindtag_context') and self._bindtag_context:
                    try:
                        self._bindtag_context.__exit__(None, None, None)
                        self._bindtag_context = None
                    except Exception as e:
                        print(f"Ошибка при закрытии контекста bindtags: {e}")
                
                self._autocomplete_tag = None
                
                # Восстанавливаем правильный порядок bind tags и фокус на редакторе
                # Это критически важно для корректной работы горячих клавиш
                self._ensure_bindtags_order()
                self.text_widget.focus_set()
        except Exception as e:
            print(f"Ошибка при закрытии автодополнения: {e}")
        
        if event:
            return None
    
    def get_code(self) -> str:
        """
        Получение кода из редактора.

        Returns:
            Текст кода
        """
        return self.text_widget.get("1.0", "end-1c")
    
    def set_code(self, code: str):
        """
        Установка кода в редактор.

        Args:
            code: Код для установки
        """
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", code)
        self._update_syntax_highlighting()
        self.text_widget.after(10, self._ensure_focus)
    
    def clear(self):
        """Очистка редактора."""
        self.text_widget.delete("1.0", "end")
        self._update_syntax_highlighting()
        self.text_widget.after(10, self._ensure_focus)
    
    def set_run_code_callback(self, callback):
        """
        Установка callback для выполнения кода при нажатии F5.
        
        Args:
            callback: Функция без параметров, которая будет вызвана при нажатии F5
        """
        self.run_code_callback = callback
    
    def set_file_action_callbacks(self, create_callback=None, save_callback=None, delete_callback=None):
        """
        Установка callbacks для действий с файлами.
        
        Args:
            create_callback: Функция без параметров для создания нового файла (Ctrl+N)
            save_callback: Функция без параметров для сохранения файла (Ctrl+S)
            delete_callback: Функция без параметров для удаления файла (Del)
        """
        if create_callback:
            self.create_file_callback = create_callback
        if save_callback:
            self.save_file_callback = save_callback
        if delete_callback:
            self.delete_file_callback = delete_callback

    def _on_mouse_motion(self, event):
        """Обработка движения мыши для показа всплывающих подсказок."""
        # Отменяем предыдущий таймер
        if self.tooltip_timer:
            self.text_widget.after_cancel(self.tooltip_timer)
            self.tooltip_timer = None
        
        # Закрываем текущую подсказку при движении мыши
        if self.tooltip_active:
            self._close_tooltip()
        
        # Устанавливаем новый таймер (показываем подсказку через 300мс после остановки мыши)
        self.tooltip_timer = self.text_widget.after(300, lambda: self._show_tooltip(event))
    
    def _show_tooltip(self, event):
        """Показ всплывающей подсказки."""
        if not JEDI_AVAILABLE:
            return
        
        # Закрываем предыдущую подсказку если есть
        if self.tooltip_active:
            return
        
        try:
            # Получаем позицию курсора в тексте
            index = self.text_widget.index(f"@{event.x},{event.y}")
            line_str, col_str = index.split('.')
            line = int(line_str)
            col = int(col_str)
            
            # Получаем весь код
            code = self.text_widget.get("1.0", "end-1c")
            
            if not code.strip():
                return
            
            # В jedi номера строк начинаются с 1 (как в tkinter), но столбцы с 0
            # В tkinter столбцы тоже начинаются с 0, так что все ок
            
            # Получаем информацию о коде в этой позиции
            script = jedi.Script(code)
            
            # Получаем определения (что находится под курсором)
            definitions = list(script.infer(line, col))
            
            # Получаем сигнатуры вызовов функций
            signatures = list(script.get_signatures(line, col))
            
            # Если есть определения или сигнатуры, показываем подсказку
            if definitions or signatures:
                tooltip_text = self._format_tooltip(definitions, signatures)
                if tooltip_text and tooltip_text.strip():
                    self._display_tooltip(tooltip_text, event.x, event.y)
            else:
                # Для отладки: получаем слово под курсором
                try:
                    word_start = self.text_widget.index(f"{line}.{col} wordstart")
                    word_end = self.text_widget.index(f"{line}.{col} wordend")
                    word = self.text_widget.get(word_start, word_end).strip()
                    
                    # Если это похоже на функцию или переменную, пробуем найти её
                    if word and (word.isidentifier() or '.' in word):
                        # Пробуем найти определение в коде
                        script_all = jedi.Script(code)
                        # Ищем все определения этого слова
                        try:
                            # Пробуем найти определение через поиск
                            goto_definitions = script_all.goto(line, col, follow_imports=True)
                            if goto_definitions:
                                defs = list(goto_definitions)
                                if defs:
                                    tooltip_text = self._format_tooltip(defs, [])
                                    if tooltip_text and tooltip_text.strip():
                                        self._display_tooltip(tooltip_text, event.x, event.y)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception as e:
            # Выводим ошибку для отладки
            import traceback
            print(f"Ошибка при показе подсказки: {e}")
            print(f"Позиция: line={line if 'line' in locals() else 'N/A'}, col={col if 'col' in locals() else 'N/A'}")
            traceback.print_exc()
    
    def _format_tooltip(self, definitions: List, signatures: List) -> str:
        """Форматирование текста всплывающей подсказки."""
        parts = []
        
        # Добавляем сигнатуры функций
        if signatures:
            for sig in signatures[:2]:  # Показываем до 2 сигнатур
                try:
                    # Получаем имя функции
                    name = sig.name if hasattr(sig, 'name') else ''
                    
                    # Получаем параметры
                    params = []
                    if hasattr(sig, 'params'):
                        for param in sig.params:
                            try:
                                param_str = param.name if hasattr(param, 'name') else str(param)
                                if hasattr(param, 'description') and param.description:
                                    param_str += f": {param.description}"
                                params.append(param_str)
                            except Exception:
                                pass
                    
                    if name:
                        if params:
                            sig_str = f"{name}({', '.join(params)})"
                        else:
                            sig_str = f"{name}()"
                        parts.append(f"📋 {sig_str}")
                    else:
                        # Пробуем получить строковое представление
                        sig_str = str(sig)
                        if sig_str and sig_str != "None":
                            parts.append(f"📋 {sig_str}")
                except Exception as e:
                    # Пробуем просто строковое представление
                    try:
                        sig_str = str(sig)
                        if sig_str and sig_str != "None":
                            parts.append(f"📋 {sig_str}")
                    except Exception:
                        pass
        
        # Добавляем документацию из определений
        if definitions:
            for def_item in definitions[:1]:  # Показываем первое определение
                try:
                    # Получаем тип и имя
                    type_name = ''
                    name = ''
                    
                    if hasattr(def_item, 'type'):
                        type_name = def_item.type
                    if hasattr(def_item, 'name'):
                        name = def_item.name
                    
                    if name:
                        header = f"{type_name} {name}" if type_name else name
                        parts.append(f"🔍 {header}")
                    
                    # Получаем документацию
                    doc = None
                    if hasattr(def_item, 'docstring'):
                        try:
                            doc = def_item.docstring()
                        except Exception:
                            pass
                    
                    if doc and doc.strip():
                        # Ограничиваем длину документации
                        doc_lines = doc.strip().split('\n')[:8]  # Первые 8 строк
                        doc_short = '\n'.join(doc_lines)
                        if len(doc.strip()) > len(doc_short):
                            doc_short += "\n..."
                        parts.append(f"📖 {doc_short}")
                except Exception as e:
                    pass
        
        return "\n\n".join(parts) if parts else ""
    
    def _display_tooltip(self, text: str, x: int, y: int):
        """Отображение окна всплывающей подсказки."""
        self._close_tooltip()
        
        if not text.strip():
            return
        
        # Создание окна подсказки
        self.tooltip_window = tk.Toplevel(self.text_widget)
        self.tooltip_window.wm_overrideredirect(True)
        
        # Получаем абсолютные координаты виджета
        widget_x = self.text_widget.winfo_rootx()
        widget_y = self.text_widget.winfo_rooty()
        
        # Вычисляем позицию окна (рядом с курсором, но не за краем экрана)
        tooltip_x = widget_x + x + 20
        tooltip_y = widget_y + y + 20
        
        # Убеждаемся, что окно не выходит за границы экрана
        screen_width = self.text_widget.winfo_screenwidth()
        screen_height = self.text_widget.winfo_screenheight()
        
        # Предполагаемый размер окна (будет уточнен позже)
        estimated_width = 400
        estimated_height = 200
        
        if tooltip_x + estimated_width > screen_width:
            tooltip_x = widget_x + x - estimated_width - 20  # Слева от курсора
        if tooltip_y + estimated_height > screen_height:
            tooltip_y = widget_y + y - estimated_height - 20  # Выше курсора
        
        self.tooltip_window.wm_geometry(f"+{tooltip_x}+{tooltip_y}")
        
        # Настройка цветов в зависимости от темы
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#2d2d2d" if is_dark else "#ffffff"
        fg_color = "#d4d4d4" if is_dark else "#000000"
        border_color = "#555555" if is_dark else "#cccccc"
        
        # Фрейм с рамкой
        frame = tk.Frame(
            self.tooltip_window,
            bg=border_color,
            relief="solid",
            borderwidth=1
        )
        frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Текстовое поле для подсказки
        tooltip_text = tk.Text(
            frame,
            wrap="word",
            font=("Consolas", 10),
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            borderwidth=5,
            padx=8,
            pady=8,
            width=50,
            height=10
        )
        tooltip_text.pack(fill="both", expand=True)
        
        # Вставка текста
        tooltip_text.insert("1.0", text)
        tooltip_text.config(state="disabled")  # Только для чтения
        
        # Автоматическое изменение размера окна
        tooltip_text.update_idletasks()
        width = tooltip_text.winfo_reqwidth() + 20
        height = min(tooltip_text.winfo_reqheight() + 20, 300)
        self.tooltip_window.geometry(f"{width}x{height}")
        
        self.tooltip_active = True
        
        # Закрытие при клике
        self.tooltip_window.bind("<Button-1>", lambda e: self._close_tooltip())
    
    def _close_tooltip(self, event=None):
        """Закрытие всплывающей подсказки."""
        if self.tooltip_timer:
            self.text_widget.after_cancel(self.tooltip_timer)
            self.tooltip_timer = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.tooltip_active = False

        if event:
            return None

    def _on_text_modified(self, event=None):
        """Обработка изменения текста для обновления подсветки."""
        if self.text_widget.edit_modified():
            # Сбрасываем флаг модификации
            self.text_widget.edit_modified(False)
            # Обновляем подсветку синтаксиса
            self._update_syntax_highlighting()



