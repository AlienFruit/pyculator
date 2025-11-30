"""Hotkeys help dialog."""
import customtkinter as ctk
import tkinter as tk
from typing import List, Tuple, Optional
from utils.hotkey_manager import HotkeyManager


class HotkeysHelpDialog:
    """Dialog window with list of all hotkeys."""
    
    def __init__(self, parent: tk.Widget, hotkey_manager: Optional[HotkeyManager] = None):
        """
        Initialize help dialog.

        Args:
            parent: Parent widget
            hotkey_manager: Hotkey manager (optional)
        """
        self.parent = parent
        self.hotkey_manager = hotkey_manager
        
        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Hotkeys")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()

        # Center window
        self._center_window()

        # Create UI
        self._create_ui()

        # Focus on window
        self.window.focus_set()
    
    def _center_window(self):
        """Center window relative to parent."""
        try:
            self.window.update_idletasks()
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            window_width = self.window.winfo_reqwidth()
            window_height = self.window.winfo_reqheight()
            
            x = parent_x + (parent_width - window_width) // 2
            y = parent_y + (parent_height - window_height) // 2
            
            self.window.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Error centering window: {e}")
            # Use default values
            self.window.geometry("600x500+100+100")
    
    def _create_ui(self):
        """Create dialog interface."""
        try:
            # Main container
            main_frame = ctk.CTkFrame(self.window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text="Hotkeys",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 10))

            # Search field
            search_frame = ctk.CTkFrame(main_frame)
            search_frame.pack(fill="x", pady=(0, 10))

            search_label = ctk.CTkLabel(search_frame, text="Search:")
            search_label.pack(side="left", padx=(0, 5))

            self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter to search...")
            self.search_entry.pack(side="left", fill="x", expand=True)
            self.search_entry.bind("<KeyRelease>", self._on_search)

            # Scrollable frame for hotkeys list
            scroll_frame = ctk.CTkScrollableFrame(main_frame)
            scroll_frame.pack(fill="both", expand=True)

            # Get hotkeys list
            hotkeys = self._get_hotkeys_list()

            # Group by categories
            categories = self._group_by_category(hotkeys)

            # Display by categories
            self.hotkey_labels = []
            for category, items in categories.items():
                # Category header
                category_label = ctk.CTkLabel(
                    scroll_frame,
                    text=category,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                category_label.pack(anchor="w", pady=(10, 5), padx=5)
                self.hotkey_labels.append(category_label)

                # Category items
                for key, description in items:
                    item_frame = ctk.CTkFrame(scroll_frame)
                    item_frame.pack(fill="x", padx=5, pady=2)
                    
                    key_label = ctk.CTkLabel(
                        item_frame,
                        text=key,
                        font=ctk.CTkFont(family="Consolas", size=12),
                        width=150,
                        anchor="w"
                    )
                    key_label.pack(side="left", padx=10, pady=5)
                    
                    desc_label = ctk.CTkLabel(
                        item_frame,
                        text=description,
                        anchor="w"
                    )
                    desc_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
                    
                    self.hotkey_labels.append((item_frame, key, description))
            
            # Close button (outside category loop)
            close_btn = ctk.CTkButton(
                main_frame,
                text="Close",
                command=self.window.destroy,
                width=100
            )
            close_btn.pack(pady=(10, 0))
        except Exception as e:
            print(f"Error creating help dialog UI: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_hotkeys_list(self) -> List[Tuple[str, str]]:
        """Get list of all hotkeys."""
        # Base hotkeys list
        default_hotkeys = [
            ("F5", "Execute code"),
            ("Ctrl+N", "Create new file"),
            ("Ctrl+S", "Save file"),
            ("Ctrl+C", "Copy selected text"),
            ("Ctrl+V", "Paste from clipboard"),
            ("Ctrl+X", "Cut selected text"),
            ("Ctrl+A", "Select all text"),
            ("Ctrl+Space", "Show autocompletion"),
            ("Tab", "Insert autocompletion (when active)"),
            ("Escape", "Close autocompletion"),
            ("Delete", "Delete file (if no selected text)"),
            ("F1", "Show hotkeys help"),
        ]
        
        # If manager exists, get additional bindings
        if self.hotkey_manager:
            manager_bindings = self.hotkey_manager.get_all_bindings()
            # Add unique bindings from manager
            manager_keys = {key: desc for key, _, desc in manager_bindings}
            for key, desc in manager_keys.items():
                if not any(key == dk[0] for dk in default_hotkeys):
                    default_hotkeys.append((key, desc))
        
        return default_hotkeys
    
    def _group_by_category(self, hotkeys: List[Tuple[str, str]]) -> dict:
        """Group hotkeys by categories."""
        categories = {
            "Files": [],
            "Editor": [],
            "Autocompletion": [],
            "General": []
        }
        
        for key, description in hotkeys:
            key_lower = key.lower()
            desc_lower = description.lower()
            
            if "file" in desc_lower or "save" in desc_lower or "create" in desc_lower or "delete" in desc_lower:
                categories["Files"].append((key, description))
            elif "autocomplet" in desc_lower or "tab" in key_lower or "escape" in key_lower or "space" in key_lower:
                categories["Autocompletion"].append((key, description))
            elif "copy" in desc_lower or "paste" in desc_lower or "cut" in desc_lower or "select" in desc_lower or "execute" in desc_lower or "f5" in key_lower:
                categories["Editor"].append((key, description))
            else:
                categories["General"].append((key, description))
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _on_search(self, event=None):
        """Handle search."""
        search_text = self.search_entry.get().lower()

        # Show/hide items based on search
        for item in self.hotkey_labels:
            if isinstance(item, tuple):
                item_frame, key, description = item
                if search_text in key.lower() or search_text in description.lower():
                    item_frame.pack(fill="x", pady=2, padx=5)
                else:
                    item_frame.pack_forget()
            else:
                # For category headers - always show
                pass
