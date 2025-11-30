"""Alternative output implementation - console output (example)."""
import customtkinter as ctk
from typing import Optional
from components.output_interface import IOutputDisplay


class ConsoleOutputDisplay(IOutputDisplay):
    """Simple console output implementation (example of alternative implementation)."""
    
    def __init__(self, parent):
        """
        Initialize output component.

        Args:
            parent: Parent widget
        """
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True)
        
        # Title
        label = ctk.CTkLabel(
            self.frame,
            text="Console output",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.pack(pady=5)

        # Simple text widget without markdown support
        self.textbox = ctk.CTkTextbox(
            self.frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            corner_radius=0
        )
        self.textbox.pack(fill="both", expand=True)

        # Configure tags for colored text
        self.textbox.tag_config("error", foreground="red")
        self.textbox.tag_config("success", foreground="green")
    
    @property
    def frame(self):
        """Returns main component frame for placement in interface."""
        return self._frame
    
    def clear(self):
        """Clear output."""
        if self.textbox:
            self.textbox.delete("1.0", "end")
        self.clear_plot()
    
    def clear_plot(self):
        """Remove all plots."""
        # Plots are cleared in PlotsDisplay
        pass
    
    def append_text(self, text: str, tag: Optional[str] = None):
        """
        Add text to output.

        Args:
            text: Text to add
            tag: Formatting tag (e.g., "error", "success")
        """
        if not self.textbox:
            return
        if tag:
            self.textbox.insert("end", text, tag)
        else:
            self.textbox.insert("end", text)
    
    def append_markdown(self, text: str):
        """
        Add markdown text to output (no formatting in this implementation).

        Args:
            text: Text with markdown markup
        """
        # Just insert text as is, without markdown parsing
        self.append_text(text)
    
    def display_result(self, stdout: str, stderr: str, exception: Optional[str] = None, enable_markdown: bool = True):
        """
        Display code execution results.

        Args:
            stdout: Standard output
            stderr: Error output
            exception: Exception text if any
            enable_markdown: Enable markdown formatting support (ignored)
        """
        self.clear()
        
        has_output = False
        
        if stdout:
            #self.append_text("Output:\n", "success")
            self.append_text(stdout + "\n")
            has_output = True

        if stderr:
            self.append_text("Errors:\n", "error")
            self.append_text(stderr + "\n", "error")
            has_output = True

        if exception:
            error_msg = f"Execution error: {exception}\n"
            self.append_text(error_msg, "error")
            has_output = True

        if not has_output:
            self.append_text("Code executed successfully. No output.\n", "success")

