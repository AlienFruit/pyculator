"""Toolbar component."""
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from typing import Callable, Optional


class Toolbar:
    """Toolbar class with control buttons."""

    def __init__(self, parent,
                 on_create: Optional[Callable] = None,
                 on_save: Optional[Callable] = None,
                 on_run: Optional[Callable] = None,
                 on_select_directory: Optional[Callable] = None):
        """
        Initialize toolbar.

        Args:
            parent: Parent widget
            on_create: Callback for "Create" button
            on_save: Callback for "Save file" button
            on_run: Callback for "Run code" button
            on_select_directory: Callback for "Select directory" button
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="x", padx=5, pady=5)
        
        self.on_create = on_create
        self.on_save = on_save
        self.on_run = on_run
        self.on_select_directory = on_select_directory

        # "Select directory" button
        self.dir_btn = ctk.CTkButton(
            self.frame,
            text="📁",  # Folder icon
            command=self._handle_select_directory,
            width=50,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.dir_btn.pack(side="left", padx=2)

        # "Create" button
        self.create_btn = ctk.CTkButton(
            self.frame,
            text="📄",  # File creation icon
            command=self._handle_create,
            width=50,
            height=35,
            font=ctk.CTkFont(size=16)
        )
        self.create_btn.pack(side="left", padx=2)

        # "Save file" button (disabled by default)
        self.save_btn = ctk.CTkButton(
            self.frame,
            text="💾",  # Save icon
            command=self._handle_save,
            width=50,
            height=35,
            font=ctk.CTkFont(size=16),
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=2)

        # "Run code" button
        self.run_btn = ctk.CTkButton(
            self.frame,
            text="▶",  # Run icon with spaces for centering
            command=self._handle_run,
            width=50,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.run_btn.pack(side="left", padx=2)

        # Add tooltips for buttons
        self._add_tooltips()

    def _add_tooltips(self):
        """Add tooltips for buttons."""
        try:
            from tkinter import ttk
            # Create style for tooltips
            style = ttk.Style()
            style.configure("Custom.TButton", relief="flat")

                # Add tooltips via event binding
            self.dir_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Select directory"))
            self.dir_btn.bind("<Leave>", self._hide_tooltip)

            self.create_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Create new file"))
            self.create_btn.bind("<Leave>", self._hide_tooltip)

            self.save_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Save file"))
            self.save_btn.bind("<Leave>", self._hide_tooltip)

            self.run_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Run code"))
            self.run_btn.bind("<Leave>", self._hide_tooltip)

        except ImportError:
            # If ttk is not available, just skip tooltips
            pass

    def _show_tooltip(self, event, text):
        """Show tooltip."""
        try:
            if hasattr(self, 'tooltip_label'):
                self.tooltip_label.destroy()

            # Get button coordinates
            x = event.widget.winfo_rootx() + event.widget.winfo_width() // 2
            y = event.widget.winfo_rooty() - 25

            # Create tooltip label
            self.tooltip_label = ctk.CTkLabel(
                self.frame,
                text=text,
                font=ctk.CTkFont(size=10),
                fg_color="#333333",
                corner_radius=4,
                text_color="white"
            )

            # Position tooltip
            self.tooltip_label.place(x=x - self.frame.winfo_rootx(),
                                   y=y - self.frame.winfo_rooty(),
                                   anchor="center")

        except Exception:
            pass

    def _hide_tooltip(self, event):
        """Hide tooltip."""
        try:
            if hasattr(self, 'tooltip_label'):
                self.tooltip_label.destroy()
                delattr(self, 'tooltip_label')
        except Exception:
            pass

    def _handle_select_directory(self):
        """Handle directory selection button."""
        if self.on_select_directory:
            self.on_select_directory()

    def _handle_create(self):
        """Handle file creation button."""
        if self.on_create:
            self.on_create()

    def set_save_enabled(self, enabled: bool):
        """
        Control save button state.

        Args:
            enabled: True to enable, False to disable
        """
        if enabled:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")

    def _handle_save(self):
        """Handle file save button."""
        if self.on_save:
            self.on_save()

    def _handle_run(self):
        """Handle code run button."""
        if self.on_run:
            self.on_run()
    
    @staticmethod
    def save_file_dialog() -> Optional[str]:
        """
        Open file selection dialog for saving.

        Returns:
            File path or None if cancelled
        """
        return filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

    @staticmethod
    def show_info(title: str, message: str):
        """Show informational message."""
        messagebox.showinfo(title, message)

    @staticmethod
    def show_error(title: str, message: str):
        """Show error message."""
        messagebox.showerror(title, message)

    @staticmethod
    def ask_string(title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """
        Show string input dialog.

        Args:
            title: Dialog title
            prompt: Prompt text
            initial_value: Initial value

        Returns:
            Entered string or None if cancelled
        """
        result = simpledialog.askstring(title, prompt, initialvalue=initial_value)
        return result if result else None

