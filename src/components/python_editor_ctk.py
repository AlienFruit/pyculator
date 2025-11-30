"""Альтернативный редактор Python кода на базе CTkTextbox с надежным копированием/вставкой."""
import customtkinter as ctk
import tkinter as tk
import re
from typing import Optional, List

try:
    import jedi
    JEDI_AVAILABLE = True
except ImportError:
    JEDI_AVAILABLE = False
    print("Предупреждение: jedi недоступен, автодополнение будет ограничено")


class PythonEditorCTk:
    """Editor кода на базе CTkTextbox с надежной поддержкой копирования/вставки."""
    
    def __init__(self, parent, initial_code: str = ""):
        """
        Инициализация редактора кода.

        Args:
            parent: Родительский виджет (CTkFrame)
            initial_code: Начальный код для отображения
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True)
        
        # Используем CTkTextbox - он имеет встроенную поддержку стандартных комбинаций клавиш
        self.textbox = ctk.CTkTextbox(
            self.frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
            undo=True
        )
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Получаем внутренний текстовый виджет для дополнительных настроек
        self.text_widget = self.textbox._textbox
        
        # Настройка автодополнения
        self.autocomplete_active = False
        self.autocomplete_listbox = None
        self.autocomplete_window = None
        
        # Привязка событий для автодополнения (минимальные, чтобы не мешать стандартным комбинациям)
        # Используем add="+" чтобы не перезаписывать стандартные привязки
        self.text_widget.bind("<Control-space>", lambda e: self._try_autocomplete(), add="+")
        self.text_widget.bind("<Tab>", self._on_tab, add="+")
        self.text_widget.bind("<Escape>", self._close_autocomplete, add="+")
        
        # Обработчик клика мыши - только для закрытия автодополнения, не блокируем стандартное поведение
        self.text_widget.bind("<Button-1>", lambda e: self._close_autocomplete() or None, add="+")
        
        # Контекстное меню для дополнительных опций
        self.text_widget.bind("<Button-3>", self._show_context_menu, add="+")
        
        # Явные обработчики для стандартных комбинаций клавиш через CTkTextbox
        # Это гарантирует, что копирование/вставка будут работать всегда
        self.text_widget.bind("<Control-c>", self._handle_copy, add="+")
        self.text_widget.bind("<Control-C>", self._handle_copy, add="+")
        self.text_widget.bind("<Control-v>", self._handle_paste, add="+")
        self.text_widget.bind("<Control-V>", self._handle_paste, add="+")
        self.text_widget.bind("<Control-x>", self._handle_cut, add="+")
        self.text_widget.bind("<Control-X>", self._handle_cut, add="+")
        self.text_widget.bind("<Control-a>", self._handle_select_all, add="+")
        self.text_widget.bind("<Control-A>", self._handle_select_all, add="+")
        
        # Вставка начального кода
        if initial_code:
            self.textbox.insert("1.0", initial_code)
    
    def _on_tab(self, event):
        """Обработка Tab для автодополнения."""
        if self.autocomplete_active and self.autocomplete_listbox:
            if self.autocomplete_listbox.size() > 0:
                self._insert_autocomplete(0)
                return "break"
        return None
    
    def _try_autocomplete(self):
        """Попытка показать автодополнение."""
        if not JEDI_AVAILABLE:
            return
        
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))
            code = self.text_widget.get("1.0", cursor_pos)
            
            # В jedi 0.19+ API изменился: используем Script(code).complete(line, col)
            script = jedi.Script(code)
            completions = script.complete(line, col)
            filtered_completions = [c for c in completions if not c.name.startswith('_') or c.name.startswith('__')]
            
            if filtered_completions:
                self._show_autocomplete(filtered_completions, line, col)
        except Exception:
            pass
    
    def _show_autocomplete(self, completions: List, line: int, col: int):
        """Показ окна автодополнения."""
        self._close_autocomplete()
        
        bbox = self.text_widget.bbox(f"{line}.{col}")
        if not bbox:
            return
        
        x, y, width, height = bbox
        
        self.autocomplete_window = tk.Toplevel(self.text_widget)
        self.autocomplete_window.wm_overrideredirect(True)
        self.autocomplete_window.wm_geometry(f"+{self.text_widget.winfo_rootx() + x}+{self.text_widget.winfo_rooty() + y + height}")
        
        is_dark = ctk.get_appearance_mode() == "Dark"
        self.autocomplete_listbox = tk.Listbox(
            self.autocomplete_window,
            height=min(len(completions), 10),
            font=("Consolas", 10),
            bg="#2d2d2d" if is_dark else "#ffffff",
            fg="#d4d4d4" if is_dark else "#000000",
            selectbackground="#264f78" if is_dark else "#316ac5",
            selectforeground="#ffffff"
        )
        self.autocomplete_listbox.pack()
        
        for completion in completions[:20]:
            name = completion.name
            if completion.type:
                display_text = f"{name} ({completion.type})"
            else:
                display_text = name
            self.autocomplete_listbox.insert(tk.END, display_text)
        
        self.autocomplete_listbox.bind("<Double-Button-1>", lambda e: self._insert_autocomplete())
        self.autocomplete_listbox.bind("<Return>", lambda e: self._insert_autocomplete())
        self.autocomplete_listbox.bind("<Escape>", lambda e: self._close_autocomplete())
        
        if self.autocomplete_listbox.size() > 0:
            self.autocomplete_listbox.selection_set(0)
            self.autocomplete_listbox.activate(0)
        
        self.autocomplete_active = True
        self.autocomplete_listbox.focus_set()
    
    def _insert_autocomplete(self, index: Optional[int] = None):
        """Вставка выбранного автодополнения."""
        if not self.autocomplete_listbox:
            return
        
        if index is None:
            selection = self.autocomplete_listbox.curselection()
            if not selection:
                return
            index = selection[0]
        
        item_text = self.autocomplete_listbox.get(index)
        name = item_text.split('(')[0].strip()
        
        cursor_pos = self.text_widget.index(tk.INSERT)
        line, col = map(int, cursor_pos.split('.'))
        line_text = self.text_widget.get(f"{line}.0", cursor_pos)
        
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.?)([a-zA-Z_][a-zA-Z0-9_]*)?$', line_text)
        if match:
            if '.' in match.group(0):
                dot_pos = line_text.rfind('.')
                start_col = col - (col - dot_pos - 1)
                self.text_widget.delete(f"{line}.{start_col}", cursor_pos)
                self.text_widget.insert(f"{line}.{start_col}", name)
            else:
                start_col = col - len(match.group(1))
                self.text_widget.delete(f"{line}.{start_col}", cursor_pos)
                self.text_widget.insert(f"{line}.{start_col}", name)
        else:
            self.text_widget.insert(cursor_pos, name)
        
        self._close_autocomplete()
    
    def _close_autocomplete(self, event=None):
        """Закрытие окна автодополнения."""
        if self.autocomplete_window:
            self.autocomplete_window.destroy()
            self.autocomplete_window = None
            self.autocomplete_listbox = None
            self.autocomplete_active = False
        if event:
            return None
    
    def _handle_copy(self, event=None):
        """Обработчик копирования."""
        try:
            if self.text_widget.tag_ranges("sel"):
                selected_text = self.text_widget.get("sel.first", "sel.last")
                if selected_text:
                    self.text_widget.clipboard_clear()
                    self.text_widget.clipboard_append(selected_text)
            return "break"
        except Exception as e:
            print(f"Error копирования: {e}")
            return None
    
    def _handle_cut(self, event=None):
        """Обработчик вырезания."""
        try:
            if self.text_widget.tag_ranges("sel"):
                selected_text = self.text_widget.get("sel.first", "sel.last")
                if selected_text:
                    self.text_widget.clipboard_clear()
                    self.text_widget.clipboard_append(selected_text)
                    self.text_widget.delete("sel.first", "sel.last")
            return "break"
        except Exception as e:
            print(f"Error вырезания: {e}")
            return None
    
    def _handle_paste(self, event=None):
        """Обработчик вставки."""
        try:
            clipboard_text = self.text_widget.clipboard_get()
            if clipboard_text:
                # Удаляем выделенный текст, если есть
                if self.text_widget.tag_ranges("sel"):
                    self.text_widget.delete("sel.first", "sel.last")
                # Вставляем текст в позицию курсора
                self.text_widget.insert("insert", clipboard_text)
            return "break"
        except tk.TclError:
            return "break"
        except Exception as e:
            print(f"Error вставки: {e}")
            return None
    
    def _handle_select_all(self, event=None):
        """Обработчик выделения всего."""
        try:
            self.text_widget.tag_add("sel", "1.0", "end-1c")
            self.text_widget.mark_set("insert", "1.0")
            self.text_widget.see("insert")
            return "break"
        except Exception as e:
            print(f"Error выделения всего: {e}")
            return None
    
    def _show_context_menu(self, event):
        """Показ контекстного меню."""
        try:
            context_menu = tk.Menu(self.text_widget, tearoff=0)
            
            has_selection = bool(self.text_widget.tag_ranges("sel"))
            
            if has_selection:
                context_menu.add_command(label="Копировать (Ctrl+C)", command=self._handle_copy)
                context_menu.add_command(label="Вырезать (Ctrl+X)", command=self._handle_cut)
            else:
                context_menu.add_command(label="Копировать (Ctrl+C)", state="disabled")
                context_menu.add_command(label="Вырезать (Ctrl+X)", state="disabled")
            
            try:
                clipboard_text = self.text_widget.clipboard_get()
                has_clipboard = bool(clipboard_text)
            except tk.TclError:
                has_clipboard = False
            
            if has_clipboard:
                context_menu.add_command(label="Вставить (Ctrl+V)", command=self._handle_paste)
            else:
                context_menu.add_command(label="Вставить (Ctrl+V)", state="disabled")
            
            context_menu.add_separator()
            context_menu.add_command(label="Выделить всё (Ctrl+A)", command=self._handle_select_all)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        except Exception as e:
            print(f"Error показа контекстного меню: {e}")
    
    def get_code(self) -> str:
        """Получение кода из редактора."""
        return self.textbox.get("1.0", "end-1c")
    
    def set_code(self, code: str):
        """Установка кода в редактор."""
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", code)
    
    def clear(self):
        """Очистка редактора."""
        self.textbox.delete("1.0", "end")

