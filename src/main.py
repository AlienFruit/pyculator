"""Entry point for Python Calculator application."""
import customtkinter as ctk
import os
import sys
from app import PythonCalculatorApp

# Setup CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main():
    """Main function to launch the application."""
    root = ctk.CTk()
    
    # Set window icon (ICO format)
    # Determine icon path considering PyInstaller
    if getattr(sys, 'frozen', False):
        # Если приложение собрано PyInstaller, используем временную папку
        base_path = sys._MEIPASS
    else:
        # Обычный режим - используем папку с исходным файлом
        base_path = os.path.dirname(__file__)
    
    icon_path = os.path.join(base_path, "calculator2.ico")
    if os.path.exists(icon_path):
        try:
            # Для ICO используем iconbitmap() - это стандартный метод для Windows
            root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed to set icon: {e}")
    
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
