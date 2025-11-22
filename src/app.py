"""Главное приложение Python калькулятора."""
import customtkinter as ctk
import tkinter as tk
import os
# Выбор редактора кода:
# 1. PythonEditor - полный редактор с подсветкой синтаксиса и автодополнением (может иметь проблемы с копированием)
# 2. PythonEditorCTk - редактор на базе CTkTextbox (надежное копирование/вставка, без подсветки синтаксиса)
# 3. PythonEditorSimple - упрощенный редактор без сложных обработчиков (максимальная надежность)
from components.python_editor import PythonEditor
# Альтернативы:
# from components.python_editor_ctk import PythonEditorCTk as PythonEditor
# from components.python_editor_simple import PythonEditorSimple as PythonEditor
from components.output import OutputDisplay  # Старая реализация (с ручным парсингом)
from components.output_markdown import MarkdownOutputDisplay  # Новая реализация (с tkhtmlview)
# Альтернативная реализация: from components.output_console import ConsoleOutputDisplay
from components.output_interface import IOutputDisplay
from components.plots_display import PlotsDisplay
from components.toolbar import Toolbar
from components.file_panel import FilePanel
from utils.data_manager import DataManager
from utils.code_executor import CodeExecutor


class PythonCalculatorApp:
    """Главный класс приложения."""
    
    def __init__(self, root):
        """
        Инициализация приложения.
        
        Args:
            root: Корневое окно CustomTkinter
        """
        self.root = root
        self.root.title("Python Калькулятор")
        
        # Текущий выбранный файл
        self.current_file = None
        
        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.code_executor = CodeExecutor()
        
        # Загрузка сохраненных данных
        saved_data = self.data_manager.load_data()
        window_size = self.data_manager.get_window_size()
        self.root.geometry(f"{window_size[0]}x{window_size[1]}")
        
        # Создание компонентов интерфейса
        self._create_ui()
        
        # Редактор пустой по умолчанию (файл не выбран)
        self.editor.clear()
    
    def _create_ui(self):
        """Создание пользовательского интерфейса."""
        # Панель инструментов
        self.toolbar = Toolbar(
            self.root,
            on_create=self.handle_create_file,
            on_save=self.handle_save_file,
            on_run=self.handle_run_code,
            on_select_directory=self.handle_select_directory
        )
        # Кнопка сохранения неактивна по умолчанию
        self.toolbar.set_save_enabled(False)
        
        # Основной контейнер для панели файлов и рабочей области
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Загружаем сохраненное состояние приложения
        saved_state = self.data_manager.load_app_state()
        saved_directory = saved_state.get("current_directory")
        if saved_directory and os.path.isdir(saved_directory):
            initial_directory = saved_directory
        else:
            from utils.data_manager import get_data_directory
            initial_directory = get_data_directory()
        
        # Панель файлов (слева)
        self.file_panel = FilePanel(
            main_container,
            on_file_select=self.handle_file_select,
            on_directory_change=self.handle_directory_change,
            initial_directory=initial_directory
        )
        # Устанавливаем директорию в data_manager
        self.data_manager.set_directory(initial_directory)
        
        # Загружаем последний открытый файл, если он был
        last_file = self.data_manager.get_last_file()
        if last_file:
            # Небольшая задержка для полной инициализации интерфейса
            self.root.after(100, lambda: self._load_last_file(last_file))
        
        # Контейнер для редактора и вывода текста (по центру)
        work_area = ctk.CTkFrame(main_container)
        work_area.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Создаем PanedWindow для разделения редактора и вывода
        is_dark = ctk.get_appearance_mode() == "Dark"
        splitter_bg = "#2b2b2b" if is_dark else "#e5e5e5"
        self.splitter = tk.PanedWindow(
            work_area,
            orient=tk.VERTICAL,
            sashwidth=8,
            sashrelief=tk.RAISED,
            bg=splitter_bg
        )
        self.splitter.pack(fill="both", expand=True)

        # Редактор кода (верхняя панель)
        editor_container = ctk.CTkFrame(self.splitter)
        self.editor = PythonEditor(editor_container)
        self.splitter.add(editor_container, minsize=200)

        # Область вывода результатов текста (нижняя панель)
        output_container = ctk.CTkFrame(self.splitter)
        # Реализации вывода (можно легко переключаться):
        # Старая реализация (ручной парсинг): OutputDisplay(output_container)
        # Консольная реализация: ConsoleOutputDisplay(output_container)
        # Новая реализация (tkhtmlview + markdown): MarkdownOutputDisplay(output_container)
        self.output: IOutputDisplay = MarkdownOutputDisplay(output_container)
        self.splitter.add(output_container, minsize=150)

        # Загружаем и применяем сохраненную позицию разделителя после полной инициализации UI
        # Используем несколько попыток с увеличивающейся задержкой для надежности
        self.root.after(200, lambda: self._load_splitter_position(attempt=1))
        self.root.after(500, lambda: self._load_splitter_position(attempt=2))
        self.root.after(1000, lambda: self._load_splitter_position(attempt=3))

        # Привязываем обработчик изменения позиции разделителя
        self.splitter.bind('<ButtonRelease-1>', self._on_splitter_moved)
        # Позиция сохраняется только при отпускании кнопки для предотвращения артефактов

        # Добавляем слушатель изменения темы для обновления цвета разделителя
        ctk.AppearanceModeTracker.add(self._update_splitter_colors)

        # Привязываем обработчик появления окна для финальной загрузки позиции
        self.root.bind('<Map>', self._on_window_mapped)

        # Панель графиков (справа) - скрыта по умолчанию
        self.plots_panel = ctk.CTkFrame(main_container)
        # Не упаковываем панель сразу - она появится только когда есть графики
        self.plots_display = PlotsDisplay(self.plots_panel, on_close=self._on_plots_panel_close)
    
    def handle_run_code(self):
        """Обработчик выполнения кода."""
        code = self.editor.get_code()

        # Очищаем предыдущие графики и скрываем панель
        self.plots_display.clear()
        self.plots_display.hide()

        # Очищаем matplotlib графики перед выполнением нового кода
        import matplotlib.pyplot as plt
        # Сохраняем информацию о текущих графиках перед очисткой (для отладки)
        old_figures = plt.get_fignums()
        if old_figures:
            print(f"DEBUG: Closing {len(old_figures)} old figures before execution")
        plt.close('all')

        # Определяем рабочую директорию для выполнения кода
        if self.current_file:
            # Если открыт файл, выполняем в его директории
            current_directory = os.path.dirname(self.current_file)
        else:
            # Если файл не открыт, используем выбранную директорию
            current_directory = self.file_panel.get_current_directory()

        result = self.code_executor.execute(code, working_directory=current_directory)

        # Отображение результатов
        self.output.display_result(
            stdout=result['stdout'],
            stderr=result['stderr'],
            exception=result['exception']
        )

        # Отображение графиков если есть (в правой панели)
        if result['has_plot']:
            print(f"DEBUG app: has_plot=True, figure_numbers={result.get('figure_numbers', [])}")
            figures = self.code_executor.get_all_figures()
            print(f"DEBUG app: get_all_figures returned {len(figures)} figures")
            if figures:
                print(f"DEBUG app: Displaying {len(figures)} figures")
                # Отображаем все графики в правой панели (панель покажется автоматически)
                self.plots_display.display_plots(figures)
            else:
                print(f"DEBUG app: No figures from get_all_figures, trying get_figure()")
                # Если графики не получены, но has_plot=True, пробуем получить текущий график
                figure = self.code_executor.get_figure()
                print(f"DEBUG app: get_figure() returned {figure is not None}")
                if figure:
                    self.plots_display.display_plots([figure])
        else:
            print(f"DEBUG app: has_plot=False, no plots to display")

    def _on_plots_panel_close(self):
        """Обработчик закрытия панели графиков."""
        # Панель уже закрыта в PlotsDisplay.close()
        # Здесь можно добавить дополнительную логику если нужно
        # НЕ вызываем ничего, что может закрыть приложение
        pass
    
    def handle_create_file(self):
        """Обработчик создания нового файла."""
        # Запрос названия файла
        file_name = Toolbar.ask_string(
            "Создать файл",
            "Введите название файла (без расширения .json):",
            ""
        )
        
        if file_name:
            # Убираем расширение если пользователь его указал
            if file_name.endswith('.py'):
                file_name = file_name[:-3]
            
            if not file_name.strip():
                Toolbar.show_error("Ошибка", "Название файла не может быть пустым")
                return
            
            # Формируем полный путь (используем текущую директорию из file_panel)
            current_dir = self.file_panel.get_current_directory()
            file_path = os.path.join(current_dir, f"{file_name}.py")
            
            # Проверяем, не существует ли файл
            if os.path.exists(file_path):
                Toolbar.show_error("Ошибка", f"Файл {file_name}.json уже существует")
                return
            
            try:
                # Создаем новый файл с кодом по умолчанию
                default_code = (
                    "# Введите ваш Python код здесь\n"
                    "# Например:\n"
                    "print('Привет, мир!')\n"
                    "result = 2 + 2\n"
                    "print(f'Результат: {result}')"
                )
                self.data_manager.save_data_to_file(file_path, default_code)
                
                # Обновляем список файлов
                self.file_panel.refresh_file_list()
                
                # Выбираем созданный файл (это вызовет handle_file_select, который сохранит состояние)
                self.file_panel._select_file(file_path)
                
            except Exception as e:
                Toolbar.show_error("Ошибка", f"Не удалось создать файл: {str(e)}")
    
    def handle_save_file(self):
        """Обработчик сохранения файла."""
        if not self.current_file:
            return
        
        try:
            self._save_current_file()
            Toolbar.show_info("Успех", f"Файл сохранен: {os.path.basename(self.current_file)}")
        except Exception as e:
            Toolbar.show_error("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def handle_file_select(self, file_path: str):
        """
        Обработчик выбора файла из панели.

        Args:
            file_path: Путь к выбранному файлу
        """
        try:
            # Загрузка данных из выбранного файла
            data = self.data_manager.load_data_from_file(file_path)
            code = data.get("code", "")
            
            # Установка кода в редактор
            self.editor.set_code(code)
            
            # Сохранение текущего файла
            self.current_file = file_path
            
            # Сохранение последнего открытого файла в состоянии приложения
            self.data_manager.save_app_state(last_file=file_path)
            
            # Активация кнопки сохранения
            self.toolbar.set_save_enabled(True)
        except Exception as e:
            Toolbar.show_error("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def handle_select_directory(self):
        """Обработчик выбора директории через тулбар."""
        from tkinter import filedialog
        import os

        # Получаем текущую директорию из file_panel
        current_dir = self.file_panel.get_current_directory() if hasattr(self.file_panel, 'get_current_directory') else os.getcwd()

        # Проверяем, существует ли директория, иначе используем домашнюю или текущую
        if not os.path.isdir(current_dir):
            current_dir = os.path.expanduser("~")  # Домашняя директория пользователя
            if not os.path.isdir(current_dir):
                current_dir = os.getcwd()  # Текущая рабочая директория

        # Открываем диалог выбора директории
        directory = filedialog.askdirectory(initialdir=current_dir)

        if directory:
            # Вызываем обработчик смены директории
            self.handle_directory_change(directory)

    def handle_directory_change(self, directory: str):
        """
        Обработчик смены директории.

        Args:
            directory: Путь к новой директории
        """
        # Обновление панели файлов (без вызова callback для избежания рекурсии)
        if hasattr(self.file_panel, 'current_directory'):
            self.file_panel.current_directory = directory
        if hasattr(self.file_panel, 'dir_label'):
            self.file_panel.dir_label.configure(text=self.file_panel._truncate_path(directory))
        self.file_panel.refresh_file_list()

        # Обновление менеджера данных
        self.data_manager.set_directory(directory)
        
        # Сохранение текущего файла перед сменой директории
        if self.current_file:
            self._save_current_file()
        
        # Сохранение новой директории в состоянии приложения
        self.data_manager.save_app_state(current_directory=directory)
        
        # Сброс текущего файла
        self.current_file = None
        
        # Деактивация кнопки сохранения
        self.toolbar.set_save_enabled(False)
        
        # Очистка редактора (ничего не отображается)
        self.editor.clear()
    
    def _save_current_file(self):
        """Сохранение текущего файла."""
        if not self.current_file:
            return
        
        code = self.editor.get_code()
        
        # Сохранение в текущий выбранный файл
        self.data_manager.save_data_to_file(self.current_file, code)
    
    def _load_last_file(self, file_path: str):
        """Загрузка последнего открытого файла."""
        try:
            if os.path.exists(file_path):
                self.file_panel._select_file(file_path)
        except Exception as e:
            print(f"Не удалось загрузить последний файл: {e}")
    
    def save_on_close(self):
        """Сохранение данных при закрытии приложения."""
        # Сохраняем текущий файл, если он выбран
        if self.current_file:
            self._save_current_file()

        # Сохраняем текущую директорию, размер окна и позицию разделителя
        current_dir = self.file_panel.get_current_directory()
        window_size = (self.root.winfo_width(), self.root.winfo_height())

        # Получаем текущую позицию разделителя
        try:
            sash_pos = self.splitter.sash_coord(0)
            if sash_pos:
                work_area_height = self.splitter.winfo_height()
                if work_area_height > 0:
                    splitter_position = sash_pos[1] / work_area_height
                else:
                    splitter_position = 0.5
            else:
                splitter_position = 0.5
        except:
            splitter_position = 0.5

        self.data_manager.save_app_state(
            current_directory=current_dir,
            last_file=self.current_file,
            window_size=window_size
        )
        # Сохраняем позицию разделителя отдельно
        self.data_manager.save_splitter_position(splitter_position)
        
        # Очищаем графики и закрываем все фигуры matplotlib
        try:
            self.plots_display.clear()
            # Закрываем все оставшиеся фигуры matplotlib
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception as e:
            print(f"Ошибка при закрытии графиков: {e}")

    def _on_window_configure(self, event=None):
        """Обработчик изменения размера окна - сохраняет позицию разделителя."""
        import time
        current_time = time.time()

        # Сохраняем позицию не чаще чем раз в 0.5 секунды
        if current_time - getattr(self, '_last_save_time', 0) > 0.5:
            try:
                self._on_splitter_moved()
                self._last_save_time = current_time
            except:
                pass

    def _on_window_mapped(self, event=None):
        """Обработчик появления окна - финальная попытка загрузки позиции."""
        # Ждем еще немного после появления окна
        self.root.after(100, lambda: self._load_splitter_position(attempt=4))

    def _load_splitter_position(self, attempt=1):
        """Загрузка и применение сохраненной позиции разделителя."""
        try:
            position = self.data_manager.get_splitter_position()

            if 0.0 <= position <= 1.0:
                # Принудительно обновляем геометрию окна перед получением размеров
                self.root.update_idletasks()

                # Получаем размеры рабочей области
                work_area_height = self.splitter.winfo_height()

                # Проверяем, что высота достаточная для корректного позиционирования
                if work_area_height > 400:  # Сумма минимальных размеров + небольшой запас
                    # Вычисляем абсолютную позицию разделителя
                    editor_height = int(work_area_height * position)
                    # Ограничиваем позицию в допустимых пределах
                    editor_height = max(200, min(editor_height, work_area_height - 150))

                    # Применяем позицию
                    self.splitter.sash_place(0, 0, editor_height)

                    # Еще раз обновляем геометрию и проверяем результат
                    self.root.after(10, lambda: self._verify_and_adjust_position(position, attempt))
                else:
                    # Если размеры еще не готовы, попробуем позже
                    if attempt < 4:
                        self.root.after(200, lambda: self._load_splitter_position(attempt + 1))
        except Exception as e:
            print(f"Ошибка загрузки позиции разделителя: {e}")

    def _verify_and_adjust_position(self, expected_position, attempt):
        """Проверка и корректировка позиции разделителя."""
        try:
            self.root.update_idletasks()  # Обновляем геометрию

            sash_pos = self.splitter.sash_coord(0)
            height = self.splitter.winfo_height()

            if sash_pos and height > 0:
                actual_position = sash_pos[1] / height
                diff = abs(actual_position - expected_position)

                if diff > 0.05:  # Если разница значительная, пробуем скорректировать
                    # Вычисляем нужную коррекцию
                    correction = int((expected_position - actual_position) * height)
                    new_editor_height = sash_pos[1] + correction

                    # Ограничиваем коррекцию
                    new_editor_height = max(200, min(new_editor_height, height - 150))

                    # Применяем коррекцию
                    self.splitter.sash_place(0, 0, new_editor_height)
        except Exception as e:
            print(f"Ошибка проверки позиции: {e}")

    def _on_splitter_moved(self, event=None):
        """Обработчик перемещения разделителя."""
        try:
            # Получаем текущую позицию разделителя
            sash_pos = self.splitter.sash_coord(0)
            if sash_pos:
                work_area_height = self.splitter.winfo_height()
                if work_area_height > 0:
                    position = sash_pos[1] / work_area_height
                    # Сохраняем позицию
                    self.data_manager.save_splitter_position(position)
        except Exception as e:
            print(f"Ошибка сохранения позиции разделителя: {e}")

    def _update_splitter_colors(self):
        """Обновление цвета фона разделителя при смене темы."""
        try:
            is_dark = ctk.get_appearance_mode() == "Dark"
            # Используем статические цвета вместо динамического получения из темы
            bg_color = "#2b2b2b" if is_dark else "#e5e5e5"
            self.splitter.configure(bg=bg_color)
        except Exception as e:
            print(f"Ошибка обновления цвета разделителя: {e}")


