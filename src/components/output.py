"""Компонент для отображения результатов выполнения кода."""
import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Optional, List
import re
from components.output_interface import IOutputDisplay

# Markdown форматирование реализовано через парсинг в CTkTextbox
# HtmlFrame отключен из-за конфликтов с CustomTkinter событиями


class OutputDisplay(IOutputDisplay):
    """Класс для отображения результатов выполнения кода."""
    
    def __init__(self, parent):
        """
        Инициализация компонента вывода.
        
        Args:
            parent: Родительский виджет
        """
        self._frame = ctk.CTkFrame(parent)
        self._frame.pack(fill="both", expand=True)
        
        # Текстовый виджет с поддержкой markdown форматирования
        # Используем CTkTextbox вместо HtmlFrame из-за конфликтов с CustomTkinter событиями
        self.textbox = ctk.CTkTextbox(
            self._frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            corner_radius=0
        )
        self.textbox.pack(fill="both", expand=True)
        
        # Настройка тегов для цветного текста
        self.textbox.tag_config("error", foreground="red")
        self.textbox.tag_config("success", foreground="green")
        
        # Настройка тегов для markdown форматирования
        # CTkTextbox не поддерживает font в tag_config, используем только цвет и underline
        is_dark = ctk.get_appearance_mode() == "Dark"
        if is_dark:
            self.textbox.tag_config("md_header1", foreground="#569cd6")  # Синий для заголовков
            self.textbox.tag_config("md_header2", foreground="#4ec9b0")  # Бирюзовый для подзаголовков
            self.textbox.tag_config("md_header3", foreground="#ce9178")  # Оранжевый для подподзаголовков
            self.textbox.tag_config("md_bold", foreground="#dcdcaa")  # Желтый для жирного текста
            self.textbox.tag_config("md_italic", foreground="#d4d4d4")  # Светло-серый для курсива
            self.textbox.tag_config("md_code", foreground="#4ec9b0")  # Бирюзовый для кода
            self.textbox.tag_config("md_codeblock", foreground="#4ec9b0")  # Бирюзовый для блоков кода
            self.textbox.tag_config("md_link", foreground="#569cd6", underline=True)
            self.textbox.tag_config("md_list", foreground="#d4d4d4")
        else:
            self.textbox.tag_config("md_header1", foreground="#0066cc")  # Синий для заголовков
            self.textbox.tag_config("md_header2", foreground="#009900")  # Зеленый для подзаголовков
            self.textbox.tag_config("md_header3", foreground="#cc6600")  # Оранжевый для подподзаголовков
            self.textbox.tag_config("md_bold", foreground="#000000")  # Черный для жирного текста
            self.textbox.tag_config("md_italic", foreground="#333333")  # Темно-серый для курсива
            self.textbox.tag_config("md_code", foreground="#0066cc")  # Синий для кода
            self.textbox.tag_config("md_codeblock", foreground="#0066cc")  # Синий для блоков кода
            self.textbox.tag_config("md_link", foreground="#0066cc", underline=True)
            self.textbox.tag_config("md_list", foreground="#000000")
        
        # Графики теперь отображаются в отдельной панели справа
    
    @property
    def frame(self):
        """Возвращает основной фрейм компонента для размещения в интерфейсе."""
        return self._frame
    
    def _get_bg_color(self) -> str:
        """Получение цвета фона в зависимости от темы."""
        return "#212325" if ctk.get_appearance_mode() == "Dark" else "#ebebeb"
    
    def clear(self):
        """Очистка вывода."""
        if self.textbox:
            self.textbox.delete("1.0", "end")
        self.clear_plot()
    
    def clear_plot(self):
        """Удаление всех графиков (графики теперь в отдельной панели)."""
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
                self._insert_with_tags(line[2:] + "\n", "md_header1")
                i += 1
                continue
            elif line.startswith('## '):
                self._insert_with_tags(line[3:] + "\n", "md_header2")
                i += 1
                continue
            elif line.startswith('### '):
                self._insert_with_tags(line[4:] + "\n", "md_header3")
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
                    code_text = '\n'.join(code_lines) + '\n'
                    self.textbox.insert("end", code_text, "md_codeblock")
                i += 1
                continue
            
            # Списки
            if re.match(r'^\s*[-*+]\s+', line):
                self._insert_with_tags(line + "\n", "md_list")
                i += 1
                continue
            elif re.match(r'^\s*\d+\.\s+', line):
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
            parts.append(("bold", match.group(1)))
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
            parts.append(("italic", match.group(1)))
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
    
    def append_markdown(self, text: str):
        """
        Добавление markdown текста в вывод с форматированием.
        
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
    
    # Методы display_plot и display_plots удалены - графики теперь в PlotsDisplay

