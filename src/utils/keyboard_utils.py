"""Utilities for keyboard and clipboard operations."""
import tkinter as tk
from typing import Optional, Callable


def copy_to_clipboard(widget: tk.Widget, text: str) -> bool:
    """
    Universal function for copying text to clipboard.

    Args:
        widget: Widget for clipboard access
        text: Text to copy

    Returns:
        True if successful, False on error
    """
    try:
        widget.clipboard_clear()
        widget.clipboard_append(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False


def get_selected_text(widget: tk.Text) -> Optional[str]:
    """
    Get selected text from widget.

    Args:
        widget: Text widget

    Returns:
        Selected text or None if no selection
    """
    try:
        if widget.tag_ranges("sel"):
            return widget.get("sel.first", "sel.last")
    except tk.TclError:
        pass
    return None


def has_selection(widget: tk.Text) -> bool:
    """
    Check for selected text presence.

    Args:
        widget: Text widget

    Returns:
        True if selection exists, False otherwise
    """
    try:
        return bool(widget.tag_ranges("sel"))
    except tk.TclError:
        return False


def get_clipboard_text(widget: tk.Widget) -> Optional[str]:
    """
    Get text from clipboard.

    Args:
        widget: Widget for clipboard access

    Returns:
        Text from clipboard or None if clipboard is empty or unavailable
    """
    try:
        return widget.clipboard_get()
    except tk.TclError:
        return None


def bind_case_insensitive(widget: tk.Widget, key_combination: str, handler: Callable, add: str = "") -> None:
    """
    Bind handler considering both key cases.

    Args:
        widget: Widget for binding
        key_combination: Key combination (e.g., "<Control-c>")
        handler: Event handler
        add: Add flag ("+" for adding without overwriting)
    """
    # Extract modifiers and key
    if key_combination.startswith("<") and key_combination.endswith(">"):
        # Split into modifiers and key
        parts = key_combination[1:-1].split("-")
        if len(parts) > 1:
            modifiers = "-".join(parts[:-1])
            key = parts[-1]
            # Bind both case variants
            widget.bind(f"<{modifiers}-{key.lower()}>", handler, add=add)
            widget.bind(f"<{modifiers}-{key.upper()}>", handler, add=add)
        else:
            # No modifiers, just key
            key = parts[0]
            widget.bind(f"<{key.lower()}>", handler, add=add)
            widget.bind(f"<{key.upper()}>", handler, add=add)
    else:
        # Non-standard format, bind as is
        widget.bind(key_combination, handler, add=add)

