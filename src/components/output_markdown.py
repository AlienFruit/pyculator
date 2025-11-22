"""Реализация OutputDisplay с поддержкой markdown через CTkTextbox."""
import customtkinter as ctk
import tkinter as tk
from typing import Optional
from components.output_interface import IOutputDisplay
import re


class MarkdownOutputDisplay(IOutputDisplay):
    """Класс для отображения результатов выполнения кода с поддержкой markdown через tkhtmlview."""

    def __init__(self, parent):
        """
        Инициализация компонента вывода с поддержкой markdown.

        Args:
            parent: Родительский виджет
        """
        self._frame = ctk.CTkFrame(parent)
        self._frame.pack(fill="both", expand=True)

        # Текстовый виджет для отображения markdown
        self.textbox = ctk.CTkTextbox(
            self._frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            corner_radius=0
        )
        self.textbox.pack(fill="both", expand=True)

        # Настройка тегов для цветового оформления
        self._setup_tags()

        # Переменная для хранения текущего HTML содержимого
        self._current_html = ""

        # Слушатель изменения темы
        ctk.AppearanceModeTracker.add(self._on_theme_change)

        # Настройка контекстного меню для копирования
        self._setup_context_menu()

        # Привязка горячих клавиш
        self._bind_hotkeys()

    def _setup_tags(self):
        """Настройка тегов для цветового оформления текста."""
        is_dark = ctk.get_appearance_mode() == "Dark"

        # Цвета для темной темы
        if is_dark:
            colors = {
                'error': '#ff6b6b',
                'success': '#51cf66',
                'header1': '#74c0fc',
                'header2': '#69db7c',
                'header3': '#ffd43b',
                'code': '#69db7c',
                'code_bg': '#3a3a3a',
                'bold': '#ffd43b',
                'italic': '#dda0dd',
                'link': '#74c0fc'
            }
        else:
            colors = {
                'error': '#dc3545',
                'success': '#28a745',
                'header1': '#0066cc',
                'header2': '#009900',
                'header3': '#cc6600',
                'code': '#0066cc',
                'code_bg': '#f8f9fa',
                'bold': '#000000',
                'italic': '#333333',
                'link': '#0066cc'
            }

        # Настройка тегов (только цвета, без font из-за ограничений CTkTextbox)
        self.textbox.tag_config("error", foreground=colors['error'])
        self.textbox.tag_config("success", foreground=colors['success'])
        self.textbox.tag_config("md_header1", foreground=colors['header1'])
        self.textbox.tag_config("md_header2", foreground=colors['header2'])
        self.textbox.tag_config("md_header3", foreground=colors['header3'])
        self.textbox.tag_config("md_bold", foreground=colors['bold'])
        self.textbox.tag_config("md_italic", foreground=colors['italic'])
        self.textbox.tag_config("md_code", foreground=colors['code'], background=colors['code_bg'])
        self.textbox.tag_config("md_codeblock", foreground=colors['code'], background=colors['code_bg'])
        self.textbox.tag_config("md_link", foreground=colors['link'], underline=True)
        self.textbox.tag_config("md_list", foreground=colors.get('text', '#ffffff' if is_dark else '#000000'))

    def _on_theme_change(self):
        """Обработчик изменения темы."""
        self._setup_tags()

    def _setup_context_menu(self):
        """Настройка контекстного меню для копирования текста."""
        # Создаем контекстное меню
        self.context_menu = tk.Menu(self._frame, tearoff=0)
        self.context_menu.add_command(label="Копировать выделенный текст", command=self._copy_selected_text)
        self.context_menu.add_command(label="Копировать весь текст", command=self._copy_all_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Очистить", command=self.clear)

        # Привязываем контекстное меню к текстовому виджету
        self.textbox.bind("<Button-3>", self._show_context_menu)

    def _bind_hotkeys(self):
        """Привязка горячих клавиш."""
        # Получаем внутренний текстовый виджет
        text_widget = self.textbox._textbox
        
        # Ctrl+C для копирования выделенного текста (только когда фокус на этом виджете)
        text_widget.bind("<Control-c>", self._copy_selected_text, add="+")
        # Ctrl+A для выделения всего текста (только когда фокус на этом виджете)
        text_widget.bind("<Control-a>", lambda e: self._select_all(), add="+")
        # НЕ устанавливаем фокус автоматически - это может мешать редактору кода

    def _show_context_menu(self, event):
        """Показ контекстного меню."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _copy_selected_text(self, event=None):
        """Копирование выделенного текста."""
        try:
            selected_text = self.textbox.get("sel.first", "sel.last")
            if selected_text:
                self._frame.clipboard_clear()
                self._frame.clipboard_append(selected_text)
                print(f"Выделенный текст скопирован ({len(selected_text)} символов)")
        except tk.TclError:
            # Нет выделенного текста, копируем весь
            self._copy_all_text()

    def _select_all(self, event=None):
        """Выделение всего текста."""
        self.textbox.tag_add("sel", "1.0", "end")
        return "break"  # Предотвращаем стандартное поведение

    def _copy_all_text(self):
        """Копирование всего текста в буфер обмена."""
        try:
            # Получаем весь текст из текстового виджета
            text_content = self.textbox.get("1.0", "end-1c")

            # Копируем в буфер обмена
            self._frame.clipboard_clear()
            self._frame.clipboard_append(text_content)

            # Показываем уведомление в консоли
            print(f"Текст скопирован в буфер обмена ({len(text_content)} символов)")

        except Exception as e:
            print(f"Ошибка копирования текста: {e}")


    def _parse_markdown(self, text: str):
        """
        Парсинг markdown текста и применение форматирования.

        Args:
            text: Текст с markdown разметкой
        """
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Заголовки
            if line.startswith('# '):
                header_text = line[2:].strip().upper()  # Делаем заголовок заглавными буквами
                self._insert_with_tags("==> " + header_text + " <==\n", "md_header1")
                i += 1
                continue
            elif line.startswith('## '):
                header_text = line[3:].strip()
                self._insert_with_tags("→ " + header_text + "\n", "md_header2")
                i += 1
                continue
            elif line.startswith('### '):
                header_text = line[4:].strip()
                self._insert_with_tags("- " + header_text + " -\n", "md_header3")
                i += 1
                continue

            # Блоки кода (многострочные)
            if line.strip().startswith('```'):
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    # Добавляем рамку вокруг блока кода
                    self.textbox.insert("end", "┌─ Код ─────────────────────────────────\n", "md_code")
                    code_text = '\n'.join(code_lines) + '\n'
                    self.textbox.insert("end", code_text, "md_codeblock")
                    self.textbox.insert("end", "└───────────────────────────────────────\n", "md_code")
                i += 1
                continue

            # Списки
            if re.match(r'^\s*[-*+]\s+', line):
                # Заменяем маркеры списка на более заметные
                list_line = re.sub(r'^\s*[-*+]\s+', '• ', line)
                self._insert_with_tags(list_line + "\n", "md_list")
                i += 1
                continue
            elif re.match(r'^\s*\d+\.\s+', line):
                # Нумерованные списки оставляем как есть
                self._insert_with_tags(line + "\n", "md_list")
                i += 1
                continue

            # Обработка инлайн markdown в строке
            self._insert_inline_markdown(line + "\n")
            i += 1

    def _insert_with_tags(self, text: str, tag: str):
        """Вставка текста с тегом."""
        self.textbox.insert("end", text, tag)

    def _insert_inline_markdown(self, line: str):
        """
        Вставка строки с обработкой инлайн markdown элементов.

        Args:
            line: Строка для обработки
        """
        if not line.strip():
            self.textbox.insert("end", line)
            return

        # Обработка инлайн кода `code` (приоритет выше)
        parts = []
        last_end = 0

        for match in re.finditer(r'`([^`]+)`', line):
            # Текст до кода
            if match.start() > last_end:
                text_before = line[last_end:match.start()]
                if text_before:
                    parts.append(("text", text_before))

            # Код
            code_text = match.group(1)
            parts.append(("code", code_text))
            last_end = match.end()

        # Остаток текста
        if last_end < len(line):
            text_after = line[last_end:]
            if text_after:
                parts.append(("text", text_after))

        if not parts:
            parts = [("text", line)]

        # Вставляем части с соответствующими тегами
        for part_type, part_text in parts:
            if part_type == "code":
                self.textbox.insert("end", part_text, "md_code")
            else:
                # Обработка жирного и курсива в обычном тексте
                self._insert_formatted_text(part_text)

    def _insert_formatted_text(self, text: str):
        """
        Вставка текста с форматированием (жирный, курсив).

        Args:
            text: Текст для вставки
        """
        # Обработка жирного текста **text**
        parts = []
        last_end = 0

        for match in re.finditer(r'\*\*([^*]+)\*\*', text):
            if match.start() > last_end:
                text_before = text[last_end:match.start()]
                if text_before:
                    parts.append(("normal", text_before))
            parts.append(("bold", "●" + match.group(1) + "●"))  # Добавляем маркеры
            last_end = match.end()

        if last_end < len(text):
            text_after = text[last_end:]
            if text_after:
                parts.append(("normal", text_after))

        if not parts:
            parts = [("normal", text)]

        # Вставляем части
        for part_type, part_text in parts:
            if part_type == "bold":
                self.textbox.insert("end", part_text, "md_bold")
            else:
                # Обработка курсива
                self._insert_italic_text(part_text)

    def _insert_italic_text(self, text: str):
        """
        Вставка текста с обработкой курсива.

        Args:
            text: Текст для вставки
        """
        parts = []
        last_end = 0

        for match in re.finditer(r'\*([^*]+)\*', text):
            if match.start() > last_end:
                text_before = text[last_end:match.start()]
                if text_before:
                    parts.append(("normal", text_before))
            parts.append(("italic", "‹" + match.group(1) + "›"))  # Добавляем маркеры
            last_end = match.end()

        if last_end < len(text):
            text_after = text[last_end:]
            if text_after:
                parts.append(("normal", text_after))

        if not parts:
            parts = [("normal", text)]

        # Вставляем части
        for part_type, part_text in parts:
            if part_type == "italic":
                self.textbox.insert("end", part_text, "md_italic")
            else:
                self.textbox.insert("end", part_text)

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

        # Вставляем текст с тегом
        if tag:
            self.textbox.insert("end", text, tag)
        else:
            self.textbox.insert("end", text)

    def append_markdown(self, text: str):
        """
        Добавление markdown текста в вывод с полным форматированием.

        Args:
            text: Текст с markdown разметкой
        """
        if self.textbox:
            # Используем улучшенный парсинг markdown в CTkTextbox
            self._parse_markdown(text)

    def display_result(self, stdout: str, stderr: str, exception: Optional[str] = None, enable_markdown: bool = True):
        """
        Отображение результатов выполнения кода.

        Args:
            stdout: Стандартный вывод
            stderr: Вывод ошибок
            exception: Текст исключения если было
            enable_markdown: Включить поддержку markdown форматирования
        """
        self.clear()

        has_output = False

        if stdout:
            #self.append_text("Вывод:\n", "success")
            if enable_markdown:
                self.append_markdown(stdout)
            else:
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

