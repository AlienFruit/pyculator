# Examples of working with matplotlib charts
# Run the code and the charts will appear in the results window

import matplotlib.pyplot as plt
import numpy as np

# Example 1: Simple sine graph
print("Creating sin(x) graph...")
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('Graph of sin(x) function')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# Example 2: Multiple graphs on one figure
print("\nCreating graph with multiple functions...")
x = np.linspace(0, 4 * np.pi, 200)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) * np.cos(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y1, 'r-', label='sin(x)', linewidth=2)
plt.plot(x, y2, 'b-', label='cos(x)', linewidth=2)
plt.plot(x, y3, 'g--', label='sin(x)*cos(x)', linewidth=2)
plt.title('Trigonometric functions')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# Example 3: Scatter plot
print("\nCreating scatter plot...")
n = 100
x = np.random.randn(n)
y = np.random.randn(n)
colors = np.random.rand(n)
sizes = 1000 * np.random.rand(n)

plt.figure(figsize=(8, 6))
plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
plt.colorbar(label='Color')
plt.title('Scatter Plot')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.grid(True, alpha=0.3)
plt.show()

# Example 4: Histogram
print("\nCreating histogram...")
data = np.random.normal(100, 15, 1000)

plt.figure(figsize=(8, 6))
plt.hist(data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.title('Normal Distribution Histogram')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3, axis='y')
plt.show()

# Example 5: Graph with subplots
print("\nCreating graph with multiple subplots...")
x = np.linspace(0, 10, 100)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Subplot 1: Linear graph
axes[0, 0].plot(x, np.sin(x), 'r-')
axes[0, 0].set_title('sin(x)')
axes[0, 0].grid(True, alpha=0.3)

# Subplot 2: Quadratic function
axes[0, 1].plot(x, x**2, 'g-')
axes[0, 1].set_title('x²')
axes[0, 1].grid(True, alpha=0.3)

# Subplot 3: Exponential
axes[1, 0].plot(x, np.exp(-x), 'b-')
axes[1, 0].set_title('e^(-x)')
axes[1, 0].grid(True, alpha=0.3)

# Subplot 4: Logarithm
axes[1, 1].plot(x, np.log(x + 1), 'm-')
axes[1, 1].set_title('ln(x+1)')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\nAll graphs created successfully!")