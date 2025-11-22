"""Main application for Python Calculator."""
import customtkinter as ctk
import tkinter as tk
import os
# Code editor selection:
# 1. PythonEditor - full editor with syntax highlighting and autocompletion (may have copy issues)
# 2. PythonEditorCTk - editor based on CTkTextbox (reliable copy/paste, no syntax highlighting)
# 3. PythonEditorSimple - simplified editor without complex handlers (maximum reliability)
from components.python_editor import PythonEditor
# Альтернативы:
# from components.python_editor_ctk import PythonEditorCTk as PythonEditor
# from components.python_editor_simple import PythonEditorSimple as PythonEditor
from components.output import OutputDisplay  # Old implementation (with manual parsing)
from components.output_markdown import MarkdownOutputDisplay  # New implementation (with tkhtmlview)
# Alternative implementation: from components.output_console import ConsoleOutputDisplay
from components.output_interface import IOutputDisplay
from components.plots_display import PlotsDisplay
from components.toolbar import Toolbar
from components.file_panel import FilePanel
from utils.data_manager import DataManager
from utils.code_executor import CodeExecutor


class PythonCalculatorApp:
    """Main application class."""
    
    def __init__(self, root):
        """
        Initialize the application.

        Args:
            root: Root CustomTkinter window
        """
        self.root = root
        self.root.title("Python Калькулятор")
        
        # Currently selected file
        self.current_file = None
        
        # Initialize managers
        self.data_manager = DataManager()
        self.code_executor = CodeExecutor()

        # Load saved data
        saved_data = self.data_manager.load_data()
        window_size = self.data_manager.get_window_size()
        self.root.geometry(f"{window_size[0]}x{window_size[1]}")
        
        # Create UI components
        self._create_ui()

        # Editor is empty by default (no file selected)
        self.editor.clear()
    
    def _create_ui(self):
        """Create the user interface."""
        # Toolbar
        self.toolbar = Toolbar(
            self.root,
            on_create=self.handle_create_file,
            on_save=self.handle_save_file,
            on_run=self.handle_run_code,
            on_select_directory=self.handle_select_directory
        )
        # Save button is disabled by default
        self.toolbar.set_save_enabled(False)
        
        # Main container for file panel and work area
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True)

        # Load saved application state
        saved_state = self.data_manager.load_app_state()
        saved_directory = saved_state.get("current_directory")
        if saved_directory and os.path.isdir(saved_directory):
            initial_directory = saved_directory
        else:
            from utils.data_manager import get_data_directory
            initial_directory = get_data_directory()

        # File panel (left side)
        self.file_panel = FilePanel(
            main_container,
            on_file_select=self.handle_file_select,
            on_directory_change=self.handle_directory_change,
            initial_directory=initial_directory
        )
        # Set directory in data_manager
        self.data_manager.set_directory(initial_directory)
        
        # Load the last opened file if it existed
        last_file = self.data_manager.get_last_file()
        if last_file:
            # Small delay for complete UI initialization
            self.root.after(100, lambda: self._load_last_file(last_file))
        
        # Container for editor and text output (center)
        work_area = ctk.CTkFrame(main_container)
        work_area.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Create PanedWindow to separate editor and output
        is_dark = ctk.get_appearance_mode() == "Dark"
        splitter_bg = "#2b2b2b" if is_dark else "#e5e5e5"
        self.splitter = tk.PanedWindow(
            work_area,
            orient=tk.VERTICAL,
            sashwidth=8,
            sashrelief=tk.RAISED,
            bg=splitter_bg
        )
        self.splitter.pack(fill="both", expand=True)

        # Code editor (top panel)
        editor_container = ctk.CTkFrame(self.splitter)
        self.editor = PythonEditor(editor_container)
        self.splitter.add(editor_container, minsize=200)

        # Text output results area (bottom panel)
        output_container = ctk.CTkFrame(self.splitter)
        # Output implementations (can be easily switched):
        # Old implementation (manual parsing): OutputDisplay(output_container)
        # Console implementation: ConsoleOutputDisplay(output_container)
        # New implementation (tkhtmlview + markdown): MarkdownOutputDisplay(output_container)
        self.output: IOutputDisplay = MarkdownOutputDisplay(output_container)
        self.splitter.add(output_container, minsize=150)

        # Load and apply saved splitter position after complete UI initialization
        # Use multiple attempts with increasing delay for reliability
        self.root.after(200, lambda: self._load_splitter_position(attempt=1))
        self.root.after(500, lambda: self._load_splitter_position(attempt=2))
        self.root.after(1000, lambda: self._load_splitter_position(attempt=3))

        # Bind handler for splitter position changes
        self.splitter.bind('<ButtonRelease-1>', self._on_splitter_moved)
        # Position is saved only on button release to prevent artifacts

        # Add theme change listener to update splitter colors
        ctk.AppearanceModeTracker.add(self._update_splitter_colors)

        # Bind window appearance handler for final position loading
        self.root.bind('<Map>', self._on_window_mapped)

        # Plots panel (right side) - hidden by default
        self.plots_panel = ctk.CTkFrame(main_container)
        # Don't pack the panel immediately - it will appear only when there are plots
        self.plots_display = PlotsDisplay(self.plots_panel, on_close=self._on_plots_panel_close)
    
    def handle_run_code(self):
        """Handle code execution."""
        code = self.editor.get_code()

        # Clear previous plots and hide panel
        self.plots_display.clear()
        self.plots_display.hide()

        # Clear matplotlib plots before executing new code
        import matplotlib.pyplot as plt
        # Save information about current plots before clearing (for debugging)
        old_figures = plt.get_fignums()
        if old_figures:
            print(f"DEBUG: Closing {len(old_figures)} old figures before execution")
        plt.close('all')

        # Determine working directory for code execution
        if self.current_file:
            # If a file is open, execute in its directory
            current_directory = os.path.dirname(self.current_file)
        else:
            # If no file is open, use selected directory
            current_directory = self.file_panel.get_current_directory()

        result = self.code_executor.execute(code, working_directory=current_directory)

        # Display results
        self.output.display_result(
            stdout=result['stdout'],
            stderr=result['stderr'],
            exception=result['exception']
        )

        # Display plots if any (in right panel)
        if result['has_plot']:
            print(f"DEBUG app: has_plot=True, figure_numbers={result.get('figure_numbers', [])}")
            figures = self.code_executor.get_all_figures()
            print(f"DEBUG app: get_all_figures returned {len(figures)} figures")
            if figures:
                print(f"DEBUG app: Displaying {len(figures)} figures")
                # Display all plots in right panel (panel will show automatically)
                self.plots_display.display_plots(figures)
            else:
                print(f"DEBUG app: No figures from get_all_figures, trying get_figure()")
                # If plots not obtained but has_plot=True, try to get current plot
                figure = self.code_executor.get_figure()
                print(f"DEBUG app: get_figure() returned {figure is not None}")
                if figure:
                    self.plots_display.display_plots([figure])
        else:
            print(f"DEBUG app: has_plot=False, no plots to display")

    def _on_plots_panel_close(self):
        """Handle plots panel closing."""
        # Panel is already closed in PlotsDisplay.close()
        # Additional logic can be added here if needed
        # DO NOT call anything that might close the application
        pass
    
    def handle_create_file(self):
        """Handle creating a new file."""
        # Request file name
        file_name = Toolbar.ask_string(
            "Create file",
            "Enter file name (without .py extension):",
            ""
        )
        
        if file_name:
            # Remove extension if user specified it
            if file_name.endswith('.py'):
                file_name = file_name[:-3]

            if not file_name.strip():
                Toolbar.show_error("Error", "File name cannot be empty")
                return

            # Form full path (use current directory from file_panel)
            current_dir = self.file_panel.get_current_directory()
            file_path = os.path.join(current_dir, f"{file_name}.py")

            # Check if file already exists
            if os.path.exists(file_path):
                Toolbar.show_error("Error", f"File {file_name}.py already exists")
                return
            
            try:
                # Create new file with default code
                default_code = (
                    "# Enter your Python code here\n"
                    "# For example:\n"
                    "print('Hello, world!')\n"
                    "result = 2 + 2\n"
                    "print(f'Result: {result}')"
                )
                self.data_manager.save_data_to_file(file_path, default_code)

                # Update file list
                self.file_panel.refresh_file_list()

                # Select created file (this will call handle_file_select, which will save state)
                self.file_panel._select_file(file_path)

            except Exception as e:
                Toolbar.show_error("Error", f"Failed to create file: {str(e)}")
    
    def handle_save_file(self):
        """Handle saving file."""
        if not self.current_file:
            return

        try:
            self._save_current_file()
            Toolbar.show_info("Success", f"File saved: {os.path.basename(self.current_file)}")
        except Exception as e:
            Toolbar.show_error("Error", f"Failed to save file: {str(e)}")
    
    def handle_file_select(self, file_path: str):
        """
        Handle file selection from panel.

        Args:
            file_path: Path to selected file
        """
        try:
            # Load data from selected file
            data = self.data_manager.load_data_from_file(file_path)
            code = data.get("code", "")

            # Set code in editor
            self.editor.set_code(code)

            # Save current file
            self.current_file = file_path

            # Save last opened file in application state
            self.data_manager.save_app_state(last_file=file_path)

            # Enable save button
            self.toolbar.set_save_enabled(True)
        except Exception as e:
            Toolbar.show_error("Error", f"Failed to load file: {str(e)}")
    
    def handle_select_directory(self):
        """Handle directory selection through toolbar."""
        from tkinter import filedialog
        import os

        # Get current directory from file_panel
        current_dir = self.file_panel.get_current_directory() if hasattr(self.file_panel, 'get_current_directory') else os.getcwd()

        # Check if directory exists, otherwise use home or current
        if not os.path.isdir(current_dir):
            current_dir = os.path.expanduser("~")  # User's home directory
            if not os.path.isdir(current_dir):
                current_dir = os.getcwd()  # Current working directory

        # Open directory selection dialog
        directory = filedialog.askdirectory(initialdir=current_dir)

        if directory:
            # Call directory change handler
            self.handle_directory_change(directory)

    def handle_directory_change(self, directory: str):
        """
        Handle directory change.

        Args:
            directory: Path to new directory
        """
        # Update file panel (without calling callback to avoid recursion)
        if hasattr(self.file_panel, 'current_directory'):
            self.file_panel.current_directory = directory
        if hasattr(self.file_panel, 'dir_label'):
            self.file_panel.dir_label.configure(text=self.file_panel._truncate_path(directory))
        self.file_panel.refresh_file_list()

        # Update data manager
        self.data_manager.set_directory(directory)

        # Save current file before directory change
        if self.current_file:
            self._save_current_file()

        # Save new directory in application state
        self.data_manager.save_app_state(current_directory=directory)

        # Reset current file
        self.current_file = None

        # Disable save button
        self.toolbar.set_save_enabled(False)

        # Clear editor (nothing is displayed)
        self.editor.clear()
    
    def _save_current_file(self):
        """Save current file."""
        if not self.current_file:
            return

        code = self.editor.get_code()

        # Save to currently selected file
        self.data_manager.save_data_to_file(self.current_file, code)
    
    def _load_last_file(self, file_path: str):
        """Load last opened file."""
        try:
            if os.path.exists(file_path):
                self.file_panel._select_file(file_path)
        except Exception as e:
            print(f"Failed to load last file: {e}")
    
    def save_on_close(self):
        """Save data on application close."""
        # Save current file if selected
        if self.current_file:
            self._save_current_file()

        # Save current directory, window size and splitter position
        current_dir = self.file_panel.get_current_directory()
        window_size = (self.root.winfo_width(), self.root.winfo_height())

        # Get current splitter position
        try:
            sash_pos = self.splitter.sash_coord(0)
            if sash_pos:
                work_area_height = self.splitter.winfo_height()
                if work_area_height > 0:
                    splitter_position = sash_pos[1] / work_area_height
                else:
                    splitter_position = 0.5
            else:
                splitter_position = 0.5
        except:
            splitter_position = 0.5

        self.data_manager.save_app_state(
            current_directory=current_dir,
            last_file=self.current_file,
            window_size=window_size
        )
        # Save splitter position separately
        self.data_manager.save_splitter_position(splitter_position)
        
        # Clear plots and close all matplotlib figures
        try:
            self.plots_display.clear()
            # Close all remaining matplotlib figures
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception as e:
            print(f"Error closing plots: {e}")

    def _on_window_configure(self, event=None):
        """Handle window resize - saves splitter position."""
        import time
        current_time = time.time()

        # Save position no more often than once every 0.5 seconds
        if current_time - getattr(self, '_last_save_time', 0) > 0.5:
            try:
                self._on_splitter_moved()
                self._last_save_time = current_time
            except:
                pass

    def _on_window_mapped(self, event=None):
        """Handle window appearance - final position loading attempt."""
        # Wait a bit more after window appears
        self.root.after(100, lambda: self._load_splitter_position(attempt=4))

    def _load_splitter_position(self, attempt=1):
        """Load and apply saved splitter position."""
        try:
            position = self.data_manager.get_splitter_position()

            if 0.0 <= position <= 1.0:
                # Force window geometry update before getting sizes
                self.root.update_idletasks()

                # Get work area dimensions
                work_area_height = self.splitter.winfo_height()

                # Check that height is sufficient for correct positioning
                if work_area_height > 400:  # Sum of minimum sizes + small margin
                    # Calculate absolute splitter position
                    editor_height = int(work_area_height * position)
                    # Limit position within allowed bounds
                    editor_height = max(200, min(editor_height, work_area_height - 150))

                    # Apply position
                    self.splitter.sash_place(0, 0, editor_height)

                    # Update geometry again and verify result
                    self.root.after(10, lambda: self._verify_and_adjust_position(position, attempt))
                else:
                    # If sizes are not ready yet, try later
                    if attempt < 4:
                        self.root.after(200, lambda: self._load_splitter_position(attempt + 1))
        except Exception as e:
            print(f"Error loading splitter position: {e}")

    def _verify_and_adjust_position(self, expected_position, attempt):
        """Verify and adjust splitter position."""
        try:
            self.root.update_idletasks()  # Update geometry

            sash_pos = self.splitter.sash_coord(0)
            height = self.splitter.winfo_height()

            if sash_pos and height > 0:
                actual_position = sash_pos[1] / height
                diff = abs(actual_position - expected_position)

                if diff > 0.05:  # If difference is significant, try to correct
                    # Calculate required correction
                    correction = int((expected_position - actual_position) * height)
                    new_editor_height = sash_pos[1] + correction

                    # Limit correction
                    new_editor_height = max(200, min(new_editor_height, height - 150))

                    # Apply correction
                    self.splitter.sash_place(0, 0, new_editor_height)
        except Exception as e:
            print(f"Error verifying position: {e}")

    def _on_splitter_moved(self, event=None):
        """Handle splitter movement."""
        try:
            # Get current splitter position
            sash_pos = self.splitter.sash_coord(0)
            if sash_pos:
                work_area_height = self.splitter.winfo_height()
                if work_area_height > 0:
                    position = sash_pos[1] / work_area_height
                    # Save position
                    self.data_manager.save_splitter_position(position)
        except Exception as e:
            print(f"Error saving splitter position: {e}")

    def _update_splitter_colors(self):
        """Update splitter background color when theme changes."""
        try:
            is_dark = ctk.get_appearance_mode() == "Dark"
            # Use static colors instead of dynamic theme retrieval
            bg_color = "#2b2b2b" if is_dark else "#e5e5e5"
            self.splitter.configure(bg=bg_color)
        except Exception as e:
            print(f"Error updating splitter color: {e}")


