"""Context manager for managing bindtags in Tkinter."""
import tkinter as tk
from typing import Optional


class BindTagContext:
    """
    Context manager for safe bindtags management.

    Usage:
        with BindTagContext(widget, "MyTag"):
            widget.bind_class("MyTag", "<Key>", handler)
            # Bindings are active
        # Tag automatically removed when exiting context
    """
    
    def __init__(self, widget: tk.Widget, tag_name: str):
        """
        Initialize context manager.

        Args:
            widget: Widget for bindtags management
            tag_name: Tag name for adding/removing
        """
        self.widget = widget
        self.tag_name = tag_name
        self._tag_was_present = False
    
    def __enter__(self):
        """
        Enter context - add tag if not present.

        Returns:
            self for use in with statement
        """
        try:
            current_tags = list(self.widget.bindtags())
            self._tag_was_present = self.tag_name in current_tags
            
            if not self._tag_was_present:
                # Add tag to beginning of list for priority
                current_tags.insert(0, self.tag_name)
                self.widget.bindtags(current_tags)
        except Exception as e:
            print(f"Error adding tag {self.tag_name}: {e}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context - remove tag if it was added by us.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False - don't suppress exceptions
        """
        try:
            # Remove tag only if we added it
            if not self._tag_was_present:
                current_tags = list(self.widget.bindtags())
                if self.tag_name in current_tags:
                    current_tags.remove(self.tag_name)
                    self.widget.bindtags(current_tags)
        except Exception as e:
            print(f"Error removing tag {self.tag_name}: {e}")

        # Don't suppress exceptions
        return False

