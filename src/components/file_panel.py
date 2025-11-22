"""File panel component."""
import customtkinter as ctk
import os
from tkinter import filedialog
from typing import Callable, Optional, List
from utils.data_manager import get_data_directory


class FilePanel:
    """File panel class with file list."""

    def __init__(self, parent,
                 on_file_select: Optional[Callable[[str], None]] = None,
                 on_directory_change: Optional[Callable[[str], None]] = None,
                 initial_directory: Optional[str] = None):
        """
        Initialize file panel.

        Args:
            parent: Parent widget
            on_file_select: Callback on file selection (takes file path)
            on_directory_change: Callback on directory change (takes directory path)
            initial_directory: Initial directory (if None, data folder is used)
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.frame.pack_propagate(False)
        self.frame.configure(width=250)
        
        self.on_file_select = on_file_select
        self.on_directory_change = on_directory_change
        
        # Use provided directory or data folder by default
        if initial_directory and os.path.isdir(initial_directory):
            self.current_directory = initial_directory
        else:
            self.current_directory = get_data_directory()
        self.selected_file = None

        # Display current directory
        self.dir_label = ctk.CTkLabel(
            self.frame,
            text=self._truncate_path(self.current_directory),
            font=ctk.CTkFont(size=10),
            wraplength=230
        )
        self.dir_label.pack(pady=5, padx=10)

        # Separator
        #separator = ctk.CTkFrame(self.frame, height=2, fg_color="gray")
        #separator.pack(fill="x", padx=10, pady=5)

        # File list
        #files_label = ctk.CTkLabel(
        #    self.frame,
        #    text="Files:",
        #    font=ctk.CTkFont(size=11, weight="bold")
        #)
        #files_label.pack(pady=(5, 5), padx=10, anchor="w")

        # Scrollable file list
        self.file_listbox_frame = ctk.CTkScrollableFrame(self.frame)
        self.file_listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Dictionary to store file buttons
        self.file_buttons = {}

        # Update file list
        self.refresh_file_list()
    
    def _truncate_path(self, path: str, max_length: int = 30) -> str:
        """
        Truncate path for display.

        Args:
            path: Path to truncate
            max_length: Maximum length

        Returns:
            Truncated path
        """
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
    
    def _select_directory(self):
        """Select directory."""
        directory = filedialog.askdirectory(initialdir=self.current_directory)

        if directory:
            self.set_directory(directory)

    def set_directory(self, directory: str):
        """
        Set current directory.

        Args:
            directory: Path to directory
        """
        if os.path.isdir(directory):
            self.current_directory = directory
            self.dir_label.configure(text=self._truncate_path(self.current_directory))
            self.refresh_file_list()
    
    def refresh_file_list(self):
        """Refresh file list."""
        # Clear existing buttons and widgets
        for widget in self.file_listbox_frame.winfo_children():
            widget.destroy()
        self.file_buttons.clear()
        self.selected_file = None

        # Get file list
        files = self._get_files()

        if not files:
            no_files_label = ctk.CTkLabel(
                self.file_listbox_frame,
                text="No files",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            no_files_label.pack(pady=10)
        else:
            # Create buttons for each file
            for file_name in sorted(files):
                file_path = os.path.join(self.current_directory, file_name)
                self._create_file_button(file_name, file_path)
    
    def _get_files(self) -> List[str]:
        """
        Get list of files in current directory.

        Returns:
            List of file names
        """
        try:
            files = os.listdir(self.current_directory)
            return [f for f in files if os.path.isfile(os.path.join(self.current_directory, f))]
        except Exception as e:
            print(f"Error reading directory: {e}")
            return []
    
    def _create_file_button(self, file_name: str, file_path: str):
        """
        Create button for file.

        Args:
            file_name: File name
            file_path: Full file path
        """
        button = ctk.CTkButton(
            self.file_listbox_frame,
            text=file_name,
            command=lambda: self._select_file(file_path),
            width=200,
            height=30,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        button.pack(fill="x", pady=2, padx=5)
        self.file_buttons[file_path] = button
    
    def _select_file(self, file_path: str):
        """
        Select file.

        Args:
            file_path: Path to selected file
        """
        # Reset previous file selection
        if self.selected_file and self.selected_file in self.file_buttons:
            self.file_buttons[self.selected_file].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )

        # Highlight current file
        self.selected_file = file_path
        if file_path in self.file_buttons:
            self.file_buttons[file_path].configure(
                fg_color=("gray75", "gray25"),
                text_color=("gray10", "gray90")
            )

        # Call callback
        if self.on_file_select:
            self.on_file_select(file_path)
    
    def get_current_directory(self) -> str:
        """
        Get current directory.

        Returns:
            Path to current directory
        """
        return self.current_directory

    def get_selected_file(self) -> Optional[str]:
        """
        Get selected file.

        Returns:
            Path to selected file or None
        """
        return self.selected_file

