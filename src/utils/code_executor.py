"""Module for executing Python code and capturing results."""
import io
import os
import sys
import importlib
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Tuple, Optional, List
import matplotlib
# Use TkAgg backend for tkinter compatibility, but disable automatic window opening
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


class CodeExecutor:
    """Class for executing Python code and getting results."""

    def __init__(self):
        """Initialize code executor."""
        # Disable matplotlib interactive mode (so plt.show() doesn't block execution)
        plt.ioff()

        # Important: pass reference to the same plt module so plots are saved
        self.available_modules = {
            'plt': plt,  # This is a reference to the global plt module
            'np': np,
            'numpy': np,
            'matplotlib': plt,
            'sys': sys,
            'os': os
        }
    
    def execute(self, code: str, working_directory: Optional[str] = None) -> Dict:
        """
        Execute Python code.

        Args:
            code: Code to execute
            working_directory: Working directory for execution (if None, current is used)

        Returns:
            Dictionary with execution results:
            {
                'stdout': str - standard output,
                'stderr': str - error output,
                'exception': str - exception text if any,
                'has_plot': bool - are there active plots
            }
        """
        if not code.strip():
            return {
                'stdout': '',
                'stderr': 'Error: Code cannot be empty',
                'exception': None,
                'has_plot': False
            }
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        result = {
            'stdout': '',
            'stderr': '',
            'exception': None,
            'has_plot': False,
            'figure_numbers': []
        }
        
        # Save current working directory
        original_cwd = os.getcwd()

        try:
            # Change working directory if specified
            if working_directory and os.path.isdir(working_directory):
                os.chdir(working_directory)
                # Add working directory to module search path
                if working_directory not in sys.path:
                    sys.path.insert(0, working_directory)
                
                # Reload modules from working directory before execution
                self._reload_modules_from_directory(working_directory)

            # Plots are cleared in app.py before calling execute

            # Create wrapper for plt.show() that won't open windows
            def show_wrapper(*args, **kwargs):
                """Wrapper for plt.show() that prevents opening separate windows."""
                # Don't open windows, but plots should be saved
                # In non-interactive mode plots are saved automatically
                pass

            # Code execution
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                local_namespace = self.available_modules.copy()
                # Redefine plt.show so it doesn't open windows
                local_namespace['plt'].show = show_wrapper
                # Also redefine in global namespace for imported modules
                import matplotlib.pyplot as plt_module
                original_show = plt_module.show
                plt_module.show = show_wrapper

                try:
                    # Execute code
                    exec(code, {"__builtins__": __builtins__}, local_namespace)

                    # After execution check plots
                    # plt in local_namespace is a reference to the global module,
                    # so plots should be available through global plt
                finally:
                    # Restore original show
                    plt_module.show = original_show
            
            # Get output
            result['stdout'] = stdout_capture.getvalue()
            result['stderr'] = stderr_capture.getvalue()

            # Get all active plots
            figure_numbers = plt.get_fignums()
            result['has_plot'] = len(figure_numbers) > 0
            result['figure_numbers'] = figure_numbers

        except Exception as e:
            result['exception'] = str(e)
            result['stderr'] = stderr_capture.getvalue()
        finally:
            # Restore original working directory
            try:
                os.chdir(original_cwd)
            except Exception:
                # Ignore directory restoration errors
                pass

            # Remove working directory from sys.path
            try:
                if working_directory and working_directory in sys.path:
                    sys.path.remove(working_directory)
            except Exception:
                # Ignore sys.path restoration errors
                pass

        return result
    
    def _reload_modules_from_directory(self, directory: str) -> None:
        """
        Reload all modules that were imported from the specified directory.
        
        Args:
            directory: Directory path to check for modules
        """
        if not directory or not os.path.isdir(directory):
            return
        
        # Normalize directory path for comparison
        directory = os.path.abspath(directory)
        directory_normalized = directory.lower()
        
        # Find and reload modules that were imported from this directory
        modules_to_reload = []
        
        for module_name, module in list(sys.modules.items()):
            # Skip built-in modules, standard library, and system modules
            if module_name.startswith('_'):
                continue
            
            try:
                module_file = getattr(module, '__file__', None)
                if not module_file:
                    continue
                
                module_path = os.path.abspath(module_file)
                module_path_normalized = module_path.lower()
                
                # Check if module file is in the working directory
                # Handle both .py files and __pycache__ files
                if directory_normalized in module_path_normalized:
                    # For __pycache__ files, get the parent directory
                    if '__pycache__' in module_path:
                        module_dir = os.path.dirname(os.path.dirname(module_path))
                    else:
                        module_dir = os.path.dirname(module_path)
                    
                    # Check if module directory matches working directory
                    if os.path.abspath(module_dir).lower() == directory_normalized:
                        # Only reload .py modules (skip .pyc, .pyd, etc.)
                        if module_path.endswith('.py') or '__pycache__' in module_path:
                            modules_to_reload.append(module_name)
                    
            except (AttributeError, TypeError, OSError):
                # Skip modules that can't be checked
                continue
        
        # Reload modules
        for module_name in modules_to_reload:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
            except (ImportError, AttributeError, TypeError, ValueError):
                # Some modules can't be reloaded (e.g., C extensions, already deleted)
                # This is expected and we can ignore it
                pass
    
    def get_figure(self) -> Optional[plt.Figure]:
        """
        Get current matplotlib figure.

        Returns:
            Figure object or None
        """
        if plt.get_fignums():
            return plt.gcf()
        return None
    
    def get_all_figures(self) -> List[plt.Figure]:
        """
        Get all active matplotlib figures.

        Returns:
            List of Figure objects
        """
        figures = []
        figure_numbers = plt.get_fignums()
        for fig_num in figure_numbers:
            try:
                fig = plt.figure(fig_num)
                figures.append(fig)
            except Exception as e:
                # Ignore figure retrieval errors
                pass
        return figures

