"""Модуль для управления сохранением и загрузкой данных приложения."""
import json
import os
from typing import Dict, Optional, Tuple


def get_data_directory() -> str:
    """
    Получение пути к директории для хранения Python файлов.

    Returns:
        Путь к директории data
    """
    # Получаем директорию, где находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Переходим в корневую директорию проекта
    project_root = os.path.dirname(script_dir)
    # Создаем путь к папке data
    data_dir = os.path.join(project_root, "data")
    # Создаем папку если её нет
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def get_app_state_file() -> str:
    """
    Получение пути к файлу состояния приложения.
    
    Returns:
        Путь к файлу app_state.json в корне проекта
    """
    # Получаем директорию, где находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Переходим в корневую директорию проекта
    project_root = os.path.dirname(script_dir)
    # Возвращаем путь к файлу app_state.json в корне проекта
    return os.path.join(project_root, "app_state.json")


class DataManager:
    """Класс для управления данными приложения в Python файлах."""

    def __init__(self, data_file: Optional[str] = None, directory: Optional[str] = None):
        """
        Инициализация менеджера данных.

        Args:
            data_file: Путь к файлу данных (если None, используется calculator_data.py в directory)
            directory: Директория для работы с файлами (если None, используется папка data)
        """
        if directory is None:
            directory = get_data_directory()

        self.directory = directory

        if data_file is None:
            data_file = os.path.join(directory, "calculator_data.py")

        self.data_file = data_file
        self._default_code = (
            "# Введите ваш Python код здесь\n"
            "# Например:\n"
            "print('Привет, мир!')\n"
            "result = 2 + 2\n"
            "print(f'Результат: {result}')"
        )
    
    def load_data(self) -> Dict:
        """
        Загрузка данных из Python файла.

        Returns:
            Словарь с данными приложения (только код)
        """
        if not os.path.exists(self.data_file):
            return {"code": ""}

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                code = f.read()
                return {"code": code}
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return {"code": ""}
    
    def save_data(self, code: str) -> bool:
        """
        Сохранение данных в Python файл.

        Args:
            code: Код для сохранения

        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
            return False
    
    def get_code(self) -> str:
        """
        Получение сохраненного кода.
        
        Returns:
            Сохраненный код или код по умолчанию
        """
        data = self.load_data()
        code = data.get("code", "")
        return code if code else self._default_code
    
    def load_data_from_file(self, file_path: str) -> Dict:
        """
        Загрузка данных из указанного Python файла.

        Args:
            file_path: Путь к Python файлу

        Returns:
            Словарь с данными приложения (только код)
        """
        if not os.path.exists(file_path):
            return {"code": ""}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                return {"code": code}
        except Exception as e:
            print(f"Ошибка загрузки данных из {file_path}: {e}")
            return {"code": ""}
    
    def save_data_to_file(self, file_path: str, code: str) -> bool:
        """
        Сохранение данных в указанный Python файл.

        Args:
            file_path: Путь к Python файлу
            code: Код для сохранения

        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            # Создаем директорию, если её нет
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Ошибка сохранения данных в {file_path}: {e}")
            return False
    
    def set_directory(self, directory: str):
        """
        Установка директории для работы.

        Args:
            directory: Путь к директории
        """
        if os.path.isdir(directory):
            self.directory = directory
            # Обновляем путь к файлу данных по умолчанию
            self.data_file = os.path.join(directory, "calculator_data.py")
    
    def get_data_directory(self) -> str:
        """
        Получение пути к директории для хранения Python файлов.

        Returns:
            Путь к директории data
        """
        return get_data_directory()
    
    def get_window_size(self) -> Tuple[int, int]:
        """
        Получение сохраненного размера окна из app_state.json.

        Returns:
            Кортеж (width, height)
        """
        state = self.load_app_state()
        window_size = state.get("window_size", {})
        return (
            window_size.get("width", 1400),
            window_size.get("height", 700)
        )

    def get_splitter_position(self) -> float:
        """
        Получение сохраненной позиции разделителя.

        Returns:
            Позиция разделителя (от 0.0 до 1.0, где 0.5 - центр)
        """
        state = self.load_app_state()
        return state.get("splitter_position", 0.5)

    def save_splitter_position(self, position: float) -> bool:
        """
        Сохранение позиции разделителя.

        Args:
            position: Позиция разделителя (от 0.0 до 1.0)

        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            state_file = get_app_state_file()

            # Загружаем текущее состояние
            current_state = self.load_app_state()

            # Обновляем позицию разделителя
            current_state["splitter_position"] = max(0.0, min(1.0, position))

            # Сохраняем состояние
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения позиции разделителя: {e}")
            return False
    
    def load_app_state(self) -> Dict:
        """
        Загрузка состояния приложения из файла app_state.json.
        
        Returns:
            Словарь с состоянием приложения
        """
        state_file = get_app_state_file()
        if not os.path.exists(state_file):
            return {
                "current_directory": get_data_directory(),
                "last_file": None,
                "window_size": {"width": 1400, "height": 700},
                "splitter_position": 0.5
            }
        
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                # Проверяем, что директория существует
                if "current_directory" in state:
                    if not os.path.isdir(state["current_directory"]):
                        state["current_directory"] = get_data_directory()
                else:
                    state["current_directory"] = get_data_directory()
                
                # Убеждаемся, что window_size есть в состоянии
                if "window_size" not in state:
                    state["window_size"] = {"width": 1400, "height": 700}
                
                return state
        except Exception as e:
            print(f"Ошибка загрузки состояния приложения: {e}")
            return {
                "current_directory": get_data_directory(),
                "last_file": None,
                "window_size": {"width": 1400, "height": 700},
                "splitter_position": 0.5
            }
    
    def save_app_state(self, current_directory: Optional[str] = None, last_file: Optional[str] = None, window_size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Сохранение состояния приложения в файл app_state.json.
        
        Args:
            current_directory: Текущая выбранная директория
            last_file: Последний открытый файл
            window_size: Размер окна (width, height)
        
        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            state_file = get_app_state_file()
            
            # Загружаем текущее состояние, чтобы сохранить другие параметры
            current_state = self.load_app_state()
            
            # Обновляем только переданные параметры
            if current_directory is not None:
                current_state["current_directory"] = current_directory
            if last_file is not None:
                current_state["last_file"] = last_file
            if window_size is not None:
                current_state["window_size"] = {
                    "width": window_size[0],
                    "height": window_size[1]
                }
            
            # Сохраняем состояние
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения состояния приложения: {e}")
            return False
    
    def get_current_directory(self) -> str:
        """
        Получение сохраненной текущей директории из состояния приложения.
        
        Returns:
            Путь к текущей директории или папка data по умолчанию
        """
        state = self.load_app_state()
        directory = state.get("current_directory", get_data_directory())
        # Проверяем, что директория существует
        if os.path.isdir(directory):
            return directory
        return get_data_directory()
    
    def get_last_file(self) -> Optional[str]:
        """
        Получение последнего открытого файла из состояния приложения.
        
        Returns:
            Путь к последнему файлу или None
        """
        state = self.load_app_state()
        last_file = state.get("last_file")
        # Проверяем, что файл существует
        if last_file and os.path.exists(last_file):
            return last_file
        return None
    
    def clean_data_files(self, directory: Optional[str] = None) -> int:
        """
        Конвертация старых JSON файлов в Python файлы.

        Args:
            directory: Директория для конвертации (если None, используется папка data)

        Returns:
            Количество конвертированных файлов
        """
        if directory is None:
            directory = get_data_directory()

        if not os.path.isdir(directory):
            print(f"Директория {directory} не существует")
            return 0

        converted_count = 0

        # Проходим по всем JSON файлам в директории
        for filename in os.listdir(directory):
            if not filename.endswith('.json'):
                continue

            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                continue

            try:
                # Загружаем данные из JSON файла
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Получаем код
                code = data.get("code", "")

                # Создаем новое имя файла с расширением .py
                new_filename = filename.replace('.json', '.py')
                new_file_path = os.path.join(directory, new_filename)

                # Сохраняем код в новый .py файл
                with open(new_file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                # Удаляем старый JSON файл
                os.remove(file_path)

                converted_count += 1
                print(f"Конвертирован файл: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Ошибка при конвертации файла {filename}: {e}")

        return converted_count

