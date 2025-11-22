"""
Тестовый файл для проверки всплывающих подсказок в редакторе.

Инструкция по проверке:
1. Откройте этот файл в редакторе
2. Наведите курсор на любую функцию ниже
3. Подождите 500мс - должна появиться подсказка с документацией
"""

# Встроенные функции Python - наведите курсор на них
print("test")
len([1, 2, 3])
range(10)
str(123)
int("42")
list([1, 2, 3])
dict(a=1, b=2)
tuple([1, 2, 3])
set([1, 2, 3])

# Примеры с библиотеками
import math
math.sqrt(16)  # Наведите на sqrt
math.sin(3.14)  # Наведите на sin
math.cos(0)     # Наведите на cos

import os
os.path.join("folder", "file.txt")  # Наведите на join
os.getcwd()  # Наведите на getcwd

# Пример пользовательской функции с документацией
def calculate_sum(a, b):
    """
    Вычисляет сумму двух чисел.
    
    Args:
        a: Первое число
        b: Второе число
    
    Returns:
        Сумма a и b
    
    Example:
        >>> calculate_sum(2, 3)
        5
    """
    return a + b

# Наведите курсор на функцию выше
result = calculate_sum(5, 10)

# Пример класса с документацией
class Calculator:
    """
    Простой калькулятор для выполнения базовых операций.
    
    Attributes:
        value: Текущее значение калькулятора
    """
    
    def __init__(self, initial_value=0):
        """
        Инициализирует калькулятор.
        
        Args:
            initial_value: Начальное значение (по умолчанию 0)
        """
        self.value = initial_value
    
    def add(self, number):
        """
        Добавляет число к текущему значению.
        
        Args:
            number: Число для добавления
        
        Returns:
            Новое значение калькулятора
        """
        self.value += number
        return self.value
    
    def multiply(self, number):
        """
        Умножает текущее значение на число.
        
        Args:
            number: Множитель
        
        Returns:
            Новое значение калькулятора
        """
        self.value *= number
        return self.value

# Наведите курсор на класс или его методы
calc = Calculator(10)
calc.add(5)  # Наведите на add
calc.multiply(2)  # Наведите на multiply

