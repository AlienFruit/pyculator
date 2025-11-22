# Интерфейс для компонентов вывода

## Описание

Реализован интерфейс `IOutputDisplay` для компонентов вывода результатов выполнения кода. Это позволяет создавать различные реализации вывода и легко переключаться между ними.

## Структура

- **`output_interface.py`** - Определяет абстрактный интерфейс `IOutputDisplay`
- **`output.py`** - Основная реализация с поддержкой Markdown форматирования
- **`output_console.py`** - Пример альтернативной реализации (простой консольный вывод)

## Интерфейс IOutputDisplay

Интерфейс определяет следующие методы:

### Свойства
- `frame` - Основной фрейм компонента для размещения в интерфейсе

### Методы
- `clear()` - Очистка вывода
- `clear_plot()` - Удаление всех графиков
- `append_text(text: str, tag: Optional[str] = None)` - Добавление текста в вывод
- `append_markdown(text: str)` - Добавление markdown текста с форматированием
- `display_result(stdout: str, stderr: str, exception: Optional[str] = None, enable_markdown: bool = True)` - Отображение результатов выполнения кода

## Использование

### Текущая реализация (с Markdown)

```python
from components.output import OutputDisplay
from components.output_interface import IOutputDisplay

output: IOutputDisplay = OutputDisplay(parent_container)
```

### Альтернативная реализация (простой вывод)

```python
from components.output_console import ConsoleOutputDisplay
from components.output_interface import IOutputDisplay

output: IOutputDisplay = ConsoleOutputDisplay(parent_container)
```

### Переключение реализаций в app.py

В файле `app.py` можно легко переключиться между реализациями:

```python
# Текущая реализация с Markdown
self.output: IOutputDisplay = OutputDisplay(output_container)

# Или простая консольная реализация
# self.output: IOutputDisplay = ConsoleOutputDisplay(output_container)
```

## Создание новой реализации

Чтобы создать новую реализацию вывода:

1. Создайте новый класс, наследующийся от `IOutputDisplay`
2. Реализуйте все абстрактные методы интерфейса
3. Убедитесь, что класс имеет атрибут `frame` для размещения в интерфейсе

Пример:

```python
from components.output_interface import IOutputDisplay
from typing import Optional
import customtkinter as ctk

class MyCustomOutput(IOutputDisplay):
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        # ... ваша инициализация
    
    def clear(self):
        # ... ваша реализация
    
    # ... остальные методы
```

## Преимущества

1. **Расширяемость** - Легко добавлять новые реализации вывода
2. **Гибкость** - Можно переключаться между реализациями без изменения остального кода
3. **Тестируемость** - Можно создавать mock-реализации для тестирования
4. **Разделение ответственности** - Интерфейс четко определяет контракт для компонентов вывода

