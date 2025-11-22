#!/usr/bin/env python3
"""
Demonstration of using MarkdownOutputDisplay in Python Calculator application.

To use the new implementation, replace the line in app.py:
    self.output: IOutputDisplay = OutputDisplay(output_container)

with:
    from components.output_markdown import MarkdownOutputDisplay
    self.output: IOutputDisplay = MarkdownOutputDisplay(output_container)
"""

import customtkinter as ctk
from components.output_markdown import MarkdownOutputDisplay

def demo_markdown_output():
    """Demonstrate MarkdownOutputDisplay."""
    # Create main window
    root = ctk.CTk()
    root.title("MarkdownOutputDisplay Demo")
    root.geometry("900x700")

    # Create MarkdownOutputDisplay instance
    output_display = MarkdownOutputDisplay(root)

    # Add various types of content for demonstration

    # 1. Header
    output_display.append_text("# MarkdownOutputDisplay Demonstration\n\n", "success")

    # 2. Description
    description = """
## Features

This OutputDisplay implementation uses the **tkhtmlview** library for full
markdown content display with:

- Full HTML formatting support
- Syntax highlighting for code blocks
- Tables and lists
- Links and images
- Adaptive themes (light/dark)
"""

    output_display.append_markdown(description)

    # 3. Code examples
    output_display.append_text("\n## Code Examples\n", "success")

    code_examples = """
### Python code with highlighting

```python
def fibonacci(n):
    \"\"\"Calculate Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Usage example
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### Mathematical expressions

```python
import math

# Calculate circle area
def circle_area(radius):
    return math.pi * radius ** 2

radius = 5
area = circle_area(radius)
print(f"Circle area with radius {radius} = {area:.2f}")
```
"""

    output_display.append_markdown(code_examples)

    # 4. Tables
    output_display.append_text("\n## Tables\n", "success")

    table_md = """
| Function | Description | Example |
|----------|-------------|---------|
| `print()` | Print text | `print("Hello")` |
| `len()` | Object length | `len([1,2,3])` |
| `range()` | Number range | `range(5)` |
| `sum()` | Sum of elements | `sum([1,2,3])` |
"""

    output_display.append_markdown(table_md)

    # 5. Lists
    output_display.append_text("\n## Lists\n", "success")

    lists_md = """
### Numbered list
1. First element
2. Second element
3. Third element

### Bulleted list
- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2
- Item 3
"""

    output_display.append_markdown(lists_md)

    # 6. Demonstrate display_result
    output_display.append_text("\n## Code Execution Result\n", "success")

    sample_stdout = """
```
Execution result:
Fibonacci number F(10) = 55
Circle area = 78.54
```

**Execution time:** 0.023 seconds
**Status:** ✅ Successful
"""

    sample_stderr = "Warning: Using deprecated print function without parentheses"

    output_display.display_result(sample_stdout, sample_stderr, None, enable_markdown=True)

    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    print("Starting MarkdownOutputDisplay demonstration...")
    print("To use in the main application, replace in app.py:")
    print("    self.output: IOutputDisplay = OutputDisplay(output_container)")
    print("with:")
    print("    from components.output_markdown import MarkdownOutputDisplay")
    print("    self.output: IOutputDisplay = MarkdownOutputDisplay(output_container)")
    print()

    demo_markdown_output()
