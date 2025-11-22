# Примеры работы с графиками matplotlib
# Выполните код и графики появятся в окне результатов

import matplotlib.pyplot as plt
import numpy as np

# Пример 1: Простой график синуса
print("Создание графика sin(x)...")
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('График функции sin(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# Пример 2: Несколько графиков на одном рисунке
print("\nСоздание графика с несколькими функциями...")
x = np.linspace(0, 4 * np.pi, 200)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) * np.cos(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y1, 'r-', label='sin(x)', linewidth=2)
plt.plot(x, y2, 'b-', label='cos(x)', linewidth=2)
plt.plot(x, y3, 'g--', label='sin(x)*cos(x)', linewidth=2)
plt.title('Тригонометрические функции')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# Пример 3: Точечный график (scatter plot)
print("\nСоздание точечного графика...")
n = 100
x = np.random.randn(n)
y = np.random.randn(n)
colors = np.random.rand(n)
sizes = 1000 * np.random.rand(n)

plt.figure(figsize=(8, 6))
plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
plt.colorbar(label='Цвет')
plt.title('Точечный график (Scatter Plot)')
plt.xlabel('X координата')
plt.ylabel('Y координата')
plt.grid(True, alpha=0.3)
plt.show()

# Пример 4: Гистограмма
print("\nСоздание гистограммы...")
data = np.random.normal(100, 15, 1000)

plt.figure(figsize=(8, 6))
plt.hist(data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.title('Гистограмма нормального распределения')
plt.xlabel('Значение')
plt.ylabel('Частота')
plt.grid(True, alpha=0.3, axis='y')
plt.show()

# Пример 5: График с подграфиками (subplots)
print("\nСоздание графика с несколькими подграфиками...")
x = np.linspace(0, 10, 100)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Подграфик 1: Линейный график
axes[0, 0].plot(x, np.sin(x), 'r-')
axes[0, 0].set_title('sin(x)')
axes[0, 0].grid(True, alpha=0.3)

# Подграфик 2: Квадратичная функция
axes[0, 1].plot(x, x**2, 'g-')
axes[0, 1].set_title('x²')
axes[0, 1].grid(True, alpha=0.3)

# Подграфик 3: Экспонента
axes[1, 0].plot(x, np.exp(-x), 'b-')
axes[1, 0].set_title('e^(-x)')
axes[1, 0].grid(True, alpha=0.3)

# Подграфик 4: Логарифм
axes[1, 1].plot(x, np.log(x + 1), 'm-')
axes[1, 1].set_title('ln(x+1)')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\nВсе графики созданы успешно!")