# Тестовый файл для проверки всплывающих подсказок
# Наведите курсор на функции ниже и подождите 500мс

# Встроенные функции Python
print("test")
len([1, 2, 3])
range(10)
str(123)
int("42")

# Примеры с библиотеками
import math
math.sqrt(16)  # Наведите курсор на sqrt
math.sin(3.14)  # Наведите курсор на sin

import os
os.path.join("folder", "file.txt")  # Наведите курсор на join

# Пример пользовательской функции с документацией
def calculate_sum(a, b):
    """
    Вычисляет сумму двух чисел.
    
    Args:
        a: Первое число
        b: Второе число
    
    Returns:
        Сумма a и b
    """
    return a + b

# Наведите курсор на функцию выше
result = calculate_sum(5, 10)

# Пример класса с документацией
class Calculator:
    """
    Simple калькулятор для выполнения базовых операций.
    """
    
    def __init__(self, initial_value=0):
        """Инициализирует калькулятор."""
        self.value = initial_value
    
    def add(self, number):
        """
        Добавляет число к текущему значению.
        
        Args:
            number: Число для добавления
        """
        self.value += number
        return self.value

calc = Calculator(10)
calc.add(5)  # Наведите курсор на add



