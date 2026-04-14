"""File panel component with tree view."""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
from tkinter import filedialog
from typing import Callable, Optional
from utils.data_manager import get_data_directory


class FilePanel:
    """File panel class with tree view for files and folders."""

    def __init__(self, parent,
                 on_file_select: Optional[Callable[[str], None]] = None,
                 on_directory_change: Optional[Callable[[str], None]] = None,
                 on_delete: Optional[Callable[[], None]] = None,
                 initial_directory: Optional[str] = None):
        """
        Initialize file panel.

        Args:
            parent: Parent widget
            on_file_select: Callback on file selection (takes file path)
            on_directory_change: Callback on directory change (takes directory path)
            on_delete: Callback on delete key press
            initial_directory: Initial directory (if None, data folder is used)
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.frame.pack_propagate(False)
        self.frame.configure(width=250)

        self.on_file_select = on_file_select
        self.on_directory_change = on_directory_change
        self.on_delete = on_delete

        # Use provided directory or data folder by default
        if initial_directory and os.path.isdir(initial_directory):
            self.current_directory = initial_directory
        else:
            self.current_directory = get_data_directory()
        
        self.selected_file = None
        self.selected_folder = None

        # Display current directory
        self.dir_label = ctk.CTkLabel(
            self.frame,
            text=self._truncate_path(self.current_directory),
            font=ctk.CTkFont(size=10),
            wraplength=230
        )
        self.dir_label.pack(pady=5, padx=10)

        # Scrollable tree view
        self.tree_frame = ctk.CTkFrame(self.frame)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(self.tree_frame, show="tree")
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>", self._on_delete_key)

        # Configure tree style
        self._configure_tree_style()
        
        # Apply style to tree
        self.tree.configure(style="FileTree.Treeview")

        # Update file tree
        self.refresh_file_list()

    def _configure_tree_style(self):
        """Configure treeview style to match app theme."""
        style = ttk.Style()
        
        # Dark theme colors matching CustomTkinter dark mode
        bg_color = "#2b2b2b"  # Dark background
        fg_color = "#ffffff"  # White text
        selected_bg = "#1f538d"  # Blue selection (matches CTk blue theme)
        hover_color = "#3a3a3a"  # Slightly lighter for hover
        
        style.theme_use('default')
        
        style.configure(
            "FileTree.Treeview",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=bg_color,
            borderwidth=0,
            font=('Segoe UI', 10),
            rowheight=28
        )
        style.configure(
            "FileTree.Treeview.Heading",
            background=bg_color,
            foreground=fg_color,
            borderwidth=0,
            font=('Segoe UI', 10, 'bold')
        )
        style.map(
            "FileTree.Treeview",
            background=[('selected', selected_bg)],
            foreground=[('selected', '#ffffff')],
            fieldbackground=[('selected', selected_bg)]
        )
        style.map(
            "FileTree.Treeview.Heading",
            background=[('active', hover_color)]
        )

    def _apply_theme_colors(self):
        """Apply theme colors to tree based on current appearance mode."""
        style = ttk.Style()
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        if is_dark:
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            selected_bg = "#1f538d"
        else:
            bg_color = "#ffffff"
            fg_color = "#000000"
            selected_bg = "#c7ddff"
        
        style.configure(
            "FileTree.Treeview",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=bg_color
        )
        style.configure(
            "FileTree.Treeview.Heading",
            background=bg_color,
            foreground=fg_color
        )
        style.map(
            "FileTree.Treeview",
            background=[('selected', selected_bg)],
            fieldbackground=[('selected', selected_bg)]
        )

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
        """Refresh file tree."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.selected_file = None
        self.selected_folder = None

        # Build tree
        self._populate_tree(self.current_directory, "")

    def _populate_tree(self, directory: str, parent_iid: str):
        """
        Populate tree with files and folders.

        Args:
            directory: Current directory path
            parent_iid: Parent item ID in treeview
        """
        try:
            items = os.listdir(directory)
        except Exception as e:
            print(f"Error reading directory: {e}")
            return

        # Separate files and directories
        dirs = []
        files = []
        
        for item in items:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            elif os.path.isfile(item_path):
                files.append(item)

        # Add directories first
        for dir_name in sorted(dirs):
            dir_path = os.path.join(directory, dir_name)
            # Insert folder node
            folder_iid = self.tree.insert(
                parent_iid,
                "end",
                text=f"📁 {dir_name}",
                open=False,
                tags=("folder",)
            )
            # Store full path in node data
            self.tree.item(folder_iid, values=(dir_path,))
            
            # Add a dummy item to show expand arrow (will be populated on expand)
            self.tree.insert(folder_iid, "end", text="Loading...", tags=("dummy",))

        # Add files
        for file_name in sorted(files):
            file_path = os.path.join(directory, file_name)
            # Only show .py files and other relevant files
            if file_name.endswith('.py') or not file_name.startswith('.'):
                file_iid = self.tree.insert(
                    parent_iid,
                    "end",
                    text=f"📄 {file_name}",
                    tags=("file",)
                )
                self.tree.item(file_iid, values=(file_path,))

        # Bind expand event
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_expand)

    def _on_tree_expand(self, event):
        """Handle tree item expansion."""
        item = self.tree.focus()
        if not item:
            return
        
        item_values = self.tree.item(item, "values")
        if not item_values:
            return
            
        item_path = item_values[0]
        
        # Check if this is a folder
        tags = self.tree.item(item, "tags")
        if "folder" not in tags:
            return
        
        # Remove dummy item if exists
        children = self.tree.get_children(item)
        for child in children:
            child_tags = self.tree.item(child, "tags")
            if "dummy" in child_tags:
                self.tree.delete(child)
                break
        
        # If no children, populate
        if not self.tree.get_children(item):
            self._populate_tree(item_path, item)

    def _on_tree_select(self, event):
        """Handle tree item selection."""
        # Use selection() instead of focus() - it's more reliable for clicks
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_values = self.tree.item(item, "values")
        if not item_values:
            return
            
        item_path = item_values[0]
        tags = self.tree.item(item, "tags")
        
        if "folder" in tags:
            # Folder selected
            self.selected_folder = item_path
            self.selected_file = None
        elif "file" in tags:
            # File selected
            self.selected_file = item_path
            self.selected_folder = None
            
            # Call file select callback
            if self.on_file_select:
                self.on_file_select(item_path)

    def _select_file(self, file_path: str):
        """
        Select file in tree.

        Args:
            file_path: Path to selected file
        """
        # Find and select the file in tree
        def _find_file(item_iid: str) -> bool:
            """Recursively find file in tree."""
            item_values = self.tree.item(item_iid, "values")
            if item_values and item_values[0] == file_path:
                # Select this item
                self.tree.focus(item_iid)
                self.tree.selection_set(item_iid)
                
                # Update selected state
                self.selected_file = file_path
                self.selected_folder = None
                return True
            
            # Check children
            for child_iid in self.tree.get_children(item_iid):
                if _find_file(child_iid):
                    return True
            
            return False

        # Search from root
        for root_item in self.tree.get_children():
            if _find_file(root_item):
                # Call callback
                if self.on_file_select:
                    self.on_file_select(file_path)
                return

    def _on_double_click(self, event):
        """Handle double click on folder to expand/collapse."""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        tags = self.tree.item(item, "tags")
        if "folder" in tags:
            # Toggle folder state
            if self.tree.item(item, "open"):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)

    def _on_delete_key(self, event):
        """Handle Delete key press."""
        # Get currently selected item in tree
        selection = self.tree.selection()
        if not selection:
            return "break"
        
        item = selection[0]
        item_values = self.tree.item(item, "values")
        if not item_values:
            return "break"
        
        item_path = item_values[0]
        tags = self.tree.item(item, "tags")
        
        # Update selection state
        if "folder" in tags:
            self.selected_folder = item_path
            self.selected_file = None
        elif "file" in tags:
            self.selected_file = item_path
            self.selected_folder = None
        
        if self.on_delete:
            self.on_delete()
        return "break"

    def get_selected_path(self) -> Optional[str]:
        """
        Get currently selected path (file or folder).

        Returns:
            Path to selected item or None
        """
        return self.selected_file or self.selected_folder

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

    def _expand_to_directory(self, dir_path: str):
        """
        Expand tree to show the specified directory and select it.

        Args:
            dir_path: Full path to directory to expand to
        """
        def _find_and_expand(item_iid: str, target_path: str) -> bool:
            """Recursively find and expand to target directory."""
            item_values = self.tree.item(item_iid, "values")
            if not item_values:
                return False
            
            item_path = item_values[0]
            
            # Found target directory
            if item_path == target_path:
                # Clear existing children and repopulate
                for child in self.tree.get_children(item_iid):
                    self.tree.delete(child)
                # Repopulate with fresh data
                self._populate_tree(target_path, item_iid)
                self.tree.item(item_iid, open=True)
                return True
            
            # Check children
            for child_iid in self.tree.get_children(item_iid):
                child_tags = self.tree.item(child_iid, "tags")
                if "folder" in child_tags:
                    # Expand folder before checking children
                    if not self.tree.item(child_iid, "open"):
                        # Populate children if needed
                        child_values = self.tree.item(child_iid, "values")
                        if child_values:
                            self._populate_tree(child_values[0], child_iid)
                        self.tree.item(child_iid, open=True)
                    
                    if _find_and_expand(child_iid, target_path):
                        return True
            
            return False

        # Start from root
        for root_item in self.tree.get_children():
            root_values = self.tree.item(root_item, "values")
            if root_values and root_values[0] == dir_path:
                # Clear and repopulate root folder
                for child in self.tree.get_children(root_item):
                    self.tree.delete(child)
                self._populate_tree(dir_path, root_item)
                self.tree.item(root_item, open=True)
                return
            root_tags = self.tree.item(root_item, "tags")
            if "folder" in root_tags:
                if _find_and_expand(root_item, dir_path):
                    return

    def update_theme_colors(self):
        """Update tree colors when theme changes."""
        self._apply_theme_colors()
