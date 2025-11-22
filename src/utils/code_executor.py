"""Модуль для выполнения Python кода и захвата результатов."""
import io
import os
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Tuple, Optional, List
import matplotlib
# Используем TkAgg бэкенд для совместимости с tkinter, но отключим автоматическое открытие окон
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


class CodeExecutor:
    """Класс для выполнения Python кода и получения результатов."""
    
    def __init__(self):
        """Инициализация исполнителя кода."""
        # Отключаем интерактивный режим matplotlib (чтобы plt.show() не блокировал выполнение)
        plt.ioff()
        
        # Важно: передаем ссылку на тот же модуль plt, чтобы графики сохранялись
        self.available_modules = {
            'plt': plt,  # Это ссылка на глобальный plt модуль
            'np': np,
            'numpy': np,
            'matplotlib': plt,
            'sys': sys,
            'os': os
        }
    
    def execute(self, code: str, working_directory: Optional[str] = None) -> Dict:
        """
        Выполнение Python кода.

        Args:
            code: Код для выполнения
            working_directory: Рабочая директория для выполнения (если None, используется текущая)

        Returns:
            Словарь с результатами выполнения:
            {
                'stdout': str - стандартный вывод,
                'stderr': str - вывод ошибок,
                'exception': str - текст исключения если было,
                'has_plot': bool - есть ли активные графики
            }
        """
        if not code.strip():
            return {
                'stdout': '',
                'stderr': 'Ошибка: Код не может быть пустым',
                'exception': None,
                'has_plot': False
            }
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        result = {
            'stdout': '',
            'stderr': '',
            'exception': None,
            'has_plot': False,
            'figure_numbers': []
        }
        
        # Сохраняем текущую рабочую директорию
        original_cwd = os.getcwd()

        try:
            # Меняем рабочую директорию если указана
            if working_directory and os.path.isdir(working_directory):
                os.chdir(working_directory)
                # Добавляем рабочую директорию в путь поиска модулей
                if working_directory not in sys.path:
                    sys.path.insert(0, working_directory)

            # Графики очищаются в app.py перед вызовом execute

            # Создаем обертку для plt.show(), которая не будет открывать окна
            def show_wrapper(*args, **kwargs):
                """Обертка для plt.show(), которая предотвращает открытие отдельных окон."""
                # Не открываем окна, но графики должны сохраниться
                # В неинтерактивном режиме графики сохраняются автоматически
                pass

            # Выполнение кода
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                local_namespace = self.available_modules.copy()
                # Переопределяем plt.show чтобы он не открывал окна
                local_namespace['plt'].show = show_wrapper
                # Также переопределяем в глобальном пространстве имен для импортированных модулей
                import matplotlib.pyplot as plt_module
                original_show = plt_module.show
                plt_module.show = show_wrapper
                
                try:
                    # Выполняем код
                    exec(code, {"__builtins__": __builtins__}, local_namespace)
                    
                    # После выполнения проверяем графики
                    # plt в local_namespace - это ссылка на глобальный модуль,
                    # поэтому графики должны быть доступны через глобальный plt
                finally:
                    # Восстанавливаем оригинальный show
                    plt_module.show = original_show
            
            # Получаем вывод
            result['stdout'] = stdout_capture.getvalue()
            result['stderr'] = stderr_capture.getvalue()
            
            # Получаем все активные графики
            figure_numbers = plt.get_fignums()
            result['has_plot'] = len(figure_numbers) > 0
            result['figure_numbers'] = figure_numbers
            
        except Exception as e:
            result['exception'] = str(e)
            result['stderr'] = stderr_capture.getvalue()
        finally:
            # Восстанавливаем исходную рабочую директорию
            try:
                os.chdir(original_cwd)
            except Exception:
                # Игнорируем ошибки восстановления директории
                pass

            # Убираем рабочую директорию из sys.path
            try:
                if working_directory and working_directory in sys.path:
                    sys.path.remove(working_directory)
            except Exception:
                # Игнорируем ошибки восстановления sys.path
                pass

        return result
    
    def get_figure(self) -> Optional[plt.Figure]:
        """
        Получение текущей фигуры matplotlib.
        
        Returns:
            Объект Figure или None
        """
        if plt.get_fignums():
            return plt.gcf()
        return None
    
    def get_all_figures(self) -> List[plt.Figure]:
        """
        Получение всех активных фигур matplotlib.
        
        Returns:
            Список объектов Figure
        """
        figures = []
        figure_numbers = plt.get_fignums()
        for fig_num in figure_numbers:
            try:
                fig = plt.figure(fig_num)
                figures.append(fig)
            except Exception as e:
                # Игнорируем ошибки получения фигур
                pass
        return figures

