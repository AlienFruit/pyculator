"""Entry point for Python Calculator application."""
import customtkinter as ctk
from app import PythonCalculatorApp

# Setup CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main():
    """Main function to launch the application."""
    root = ctk.CTk()
    app = PythonCalculatorApp(root)
    
    # Save data on closing
    def on_closing():
        app.save_on_close()
        # Additional closing of all matplotlib figures for guarantee
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
