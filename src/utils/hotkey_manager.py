"""Централизованный менеджер горячих клавиш."""
import tkinter as tk
from typing import Dict, List, Tuple, Optional, Callable
from collections import defaultdict


class HotkeyBinding:
    """Класс для хранения информации о привязке горячей клавиши."""

    def __init__(self, key_combination: str, handler: Callable, component: str, description: str = "", widget: Optional[tk.Widget] = None):
        """
        Инициализация привязки.

        Args:
            key_combination: Комбинация клавиш (например, "<Control-c>")
            handler: Обработчик события
            component: Имя компонента, регистрирующего привязку
            description: Описание действия
            widget: Виджет, к которому привязана клавиша (None для root)
        """
        self.key_combination = key_combination
        self.handler = handler
        self.component = component
        self.description = description
        self.widget = widget
        self.bound = False

    def __repr__(self):
        return f"HotkeyBinding({self.key_combination}, {self.component}, {self.description})"


class HotkeyManager:
    """Централизованный менеджер для управления горячими клавишами."""

    def __init__(self, root: tk.Widget):
        """
        Инициализация менеджера горячих клавиш.

        Args:
            root: Корневой виджет приложения
        """
        self.root = root
        # Словарь: key_combination -> список привязок
        self._bindings: Dict[str, List[HotkeyBinding]] = defaultdict(list)
        # Словарь для быстрого поиска по компоненту
        self._component_bindings: Dict[str, List[HotkeyBinding]] = defaultdict(list)

    def register(self, key_combination: str, handler: Callable, component: str, 
                 description: str = "", widget: Optional[tk.Widget] = None, 
                 case_sensitive: bool = False) -> bool:
        """
        Регистрация горячей клавиши.

        Args:
            key_combination: Комбинация клавиш (например, "<Control-c>")
            handler: Обработчик события
            component: Имя компонента (например, "PythonEditor")
            description: Описание действия для пользователя
            widget: Виджет для привязки (None для root)
            case_sensitive: Учитывать ли регистр клавиши

        Returns:
            True если успешно зарегистрировано, False если конфликт
        """
        # Проверяем конфликты
        if key_combination in self._bindings:
            existing = self._bindings[key_combination]
            if existing and not case_sensitive:
                # Предупреждение о потенциальном конфликте
                print(f"Предупреждение: Комбинация {key_combination} уже используется компонентами: {[b.component for b in existing]}")

        # Создаем обертку для обработчика с логированием ошибок
        def wrapped_handler(event):
            try:
                return handler(event)
            except Exception as e:
                print(f"Ошибка в обработчике горячей клавиши {key_combination} (компонент {component}): {e}")
                return None

        # Создаем привязку
        binding = HotkeyBinding(key_combination, wrapped_handler, component, description, widget)

        # Регистрируем
        target_widget = widget if widget else self.root
        target_widget.bind(key_combination, wrapped_handler, add="+")
        binding.bound = True

        # Сохраняем в словарях
        self._bindings[key_combination].append(binding)
        self._component_bindings[component].append(binding)

        return True

    def register_case_insensitive(self, key_combination: str, handler: Callable, 
                                  component: str, description: str = "", 
                                  widget: Optional[tk.Widget] = None) -> bool:
        """
        Регистрация горячей клавиши с автоматической поддержкой обоих регистров.

        Args:
            key_combination: Комбинация клавиш (например, "<Control-c>")
            handler: Обработчик события
            component: Имя компонента
            description: Описание действия
            widget: Виджет для привязки (None для root)

        Returns:
            True если успешно зарегистрировано
        """
        try:
            from utils.keyboard_utils import bind_case_insensitive
        except ImportError:
            # Fallback если импорт не работает
            bind_case_insensitive = None

        # Создаем обертку для обработчика с логированием ошибок
        def wrapped_handler(event):
            try:
                return handler(event)
            except Exception as e:
                print(f"Ошибка в обработчике горячей клавиши {key_combination} (компонент {component}): {e}")
                return None

        # Регистрируем оба варианта
        if bind_case_insensitive:
            bind_case_insensitive(widget if widget else self.root, key_combination, wrapped_handler, add="+")
        else:
            # Fallback: регистрируем вручную
            target_widget = widget if widget else self.root
            # Извлекаем модификаторы и клавишу
            if key_combination.startswith("<") and key_combination.endswith(">"):
                parts = key_combination[1:-1].split("-")
                if len(parts) > 1:
                    modifiers = "-".join(parts[:-1])
                    key = parts[-1]
                    target_widget.bind(f"<{modifiers}-{key.lower()}>", wrapped_handler, add="+")
                    target_widget.bind(f"<{modifiers}-{key.upper()}>", wrapped_handler, add="+")
                else:
                    key = parts[0]
                    target_widget.bind(f"<{key.lower()}>", wrapped_handler, add="+")
                    target_widget.bind(f"<{key.upper()}>", wrapped_handler, add="+")

        # Создаем привязку для записи (регистрируем как одну запись)
        binding = HotkeyBinding(key_combination, wrapped_handler, component, description, widget)
        binding.bound = True

        self._bindings[key_combination].append(binding)
        self._component_bindings[component].append(binding)

        return True

    def unregister(self, key_combination: str, component: str) -> bool:
        """
        Отмена регистрации горячей клавиши для конкретного компонента.

        Args:
            key_combination: Комбинация клавиш
            component: Имя компонента

        Returns:
            True если успешно отменено, False если не найдено
        """
        if key_combination not in self._bindings:
            return False

        # Находим привязки для этого компонента
        bindings_to_remove = [b for b in self._bindings[key_combination] if b.component == component]

        if not bindings_to_remove:
            return False

        # Отвязываем от виджета
        for binding in bindings_to_remove:
            target_widget = binding.widget if binding.widget else self.root
            try:
                target_widget.unbind(key_combination)
            except Exception as e:
                print(f"Ошибка при отвязывании {key_combination}: {e}")

        # Удаляем из словарей
        self._bindings[key_combination] = [b for b in self._bindings[key_combination] if b.component != component]
        if not self._bindings[key_combination]:
            del self._bindings[key_combination]

        self._component_bindings[component] = [b for b in self._component_bindings[component] if b.key_combination != key_combination]

        return True

    def unregister_component(self, component: str) -> int:
        """
        Отмена всех регистраций для компонента.

        Args:
            component: Имя компонента

        Returns:
            Количество отмененных привязок
        """
        if component not in self._component_bindings:
            return 0

        bindings = self._component_bindings[component].copy()
        count = 0

        for binding in bindings:
            if self.unregister(binding.key_combination, component):
                count += 1

        return count

    def get_all_bindings(self) -> List[Tuple[str, str, str]]:
        """
        Получить список всех привязок.

        Returns:
            Список кортежей (комбинация клавиш, компонент, описание)
        """
        result = []
        for key_combination, bindings in self._bindings.items():
            for binding in bindings:
                result.append((key_combination, binding.component, binding.description))
        return result

    def get_bindings_by_component(self, component: str) -> List[HotkeyBinding]:
        """
        Получить все привязки для компонента.

        Args:
            component: Имя компонента

        Returns:
            Список привязок
        """
        return self._component_bindings.get(component, []).copy()

    def get_bindings_by_key(self, key_combination: str) -> List[HotkeyBinding]:
        """
        Получить все привязки для комбинации клавиш.

        Args:
            key_combination: Комбинация клавиш

        Returns:
            Список привязок
        """
        return self._bindings.get(key_combination, []).copy()

    def has_conflicts(self) -> List[Tuple[str, List[str]]]:
        """
        Проверить наличие конфликтов (несколько компонентов на одну комбинацию).

        Returns:
            Список кортежей (комбинация клавиш, список компонентов)
        """
        conflicts = []
        for key_combination, bindings in self._bindings.items():
            if len(bindings) > 1:
                components = [b.component for b in bindings]
                conflicts.append((key_combination, components))
        return conflicts

