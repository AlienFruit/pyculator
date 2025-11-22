# Markdown Demonstration File
# This file contains examples of various Markdown formatting elements

markdown_content = """
# Markdown Formatting Examples

## Headers

# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header

## Text Formatting

This is **bold text**, this is *italic text*, and this is ***bold italic text***.

You can also use `inline code` formatting within sentences.

## Code Blocks

### Python Code Example
```python
def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript Code Example
```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet("World"));
```

## Lists

### Unordered Lists
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

### Ordered Lists
1. First item
2. Second item
3. Third item
   1. Nested numbered item
   2. Another nested item

## Tables

| Feature | Description | Example |
|---------|-------------|---------|
| Bold | **text** | `**text**` |
| Italic | *text* | `*text*` |
| Code | `code` | `` `code` `` |
| Link | [text](url) | `[text](url)` |

## Blockquotes

> This is a blockquote.
>
> It can span multiple lines.
>
>> And can be nested.

## Links and Images

### Links
[OpenAI](https://openai.com) is an AI research company.

### Images
![Python Logo](https://www.python.org/static/community_logos/python-logo.png)

## Horizontal Rules

---

Above is a horizontal rule.

## Task Lists

- [x] Completed task
- [ ] Incomplete task
- [x] Another completed task

## Mathematical Expressions

You can include mathematical expressions using LaTeX-style syntax:

Inline math: $E = mc^2$

Block math:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

## Strikethrough

This is ~~strikethrough text~~.

## Highlighting

You can use ==highlighted text== for emphasis.

## Footnotes

Here's a sentence with a footnote.[^1]

[^1]: This is the footnote content.

## Definition Lists

Term 1
: Definition 1

Term 2
: Definition 2
  - Sub-definition

## Abbreviations

The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium

---

*This markdown demonstration shows various formatting options available in modern markdown parsers.*
"""

print(markdown_content)
