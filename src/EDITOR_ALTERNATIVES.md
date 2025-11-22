# Альтернативные редакторы кода

В проекте доступны три варианта редактора кода для решения проблем с копированием/вставкой.

## Доступные редакторы

### 1. PythonEditorSimple (РЕКОМЕНДУЕТСЯ)
**Файл:** `components/python_editor_simple.py`

**Особенности:**
- ✅ Максимальная надежность копирования/вставки
- ✅ Минимум обработчиков событий - стандартные комбинации клавиш работают всегда
- ✅ Простая реализация без сложной логики
- ✅ Поддержка контекстного меню (правая кнопка мыши)
- ❌ Нет подсветки синтаксиса
- ❌ Нет автодополнения

**Использование:**
```python
from components.python_editor_simple import PythonEditorSimple as PythonEditor
```

### 2. PythonEditorCTk
**Файл:** `components/python_editor_ctk.py`

**Особенности:**
- ✅ Использует CTkTextbox из CustomTkinter
- ✅ Встроенная поддержка стандартных комбинаций клавиш
- ✅ Поддержка автодополнения (если установлен jedi)
- ✅ Контекстное меню
- ❌ Нет подсветки синтаксиса

**Использование:**
```python
from components.python_editor_ctk import PythonEditorCTk as PythonEditor
```

### 3. PythonEditor (оригинальный)
**Файл:** `components/python_editor.py`

**Особенности:**
- ✅ Полная подсветка синтаксиса Python
- ✅ Автодополнение с jedi
- ✅ Всплывающие подсказки
- ❌ Могут быть проблемы с копированием/вставкой из-за сложных обработчиков событий

**Использование:**
```python
from components.python_editor import PythonEditor
```

## Как переключиться между редакторами

Откройте файл `app.py` и измените строку импорта:

**Текущая настройка (PythonEditorSimple):**
```python
from components.python_editor_simple import PythonEditorSimple as PythonEditor
```

**Для использования CTkTextbox редактора:**
```python
from components.python_editor_ctk import PythonEditorCTk as PythonEditor
```

**Для использования оригинального редактора:**
```python
from components.python_editor import PythonEditor
```

## Рекомендации

1. **Если проблемы с копированием/вставкой** - используйте `PythonEditorSimple`
2. **Если нужен автодополнение** - используйте `PythonEditorCTk`
3. **Если нужна подсветка синтаксиса** - используйте оригинальный `PythonEditor` (но могут быть проблемы с копированием)

## Стандартные комбинации клавиш

Все редакторы поддерживают:
- `Ctrl+C` - Копировать
- `Ctrl+V` - Вставить
- `Ctrl+X` - Вырезать
- `Ctrl+A` - Выделить всё

Также доступно контекстное меню по правой кнопке мыши.

