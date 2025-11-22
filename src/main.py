"""Точка входа в приложение Python калькулятора."""
import customtkinter as ctk
from app import PythonCalculatorApp

# Настройка темы CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main():
    """Главная функция запуска приложения."""
    root = ctk.CTk()
    app = PythonCalculatorApp(root)
    
    # Сохранение данных при закрытии
    def on_closing():
        app.save_on_close()
        # Дополнительное закрытие всех фигур matplotlib для гарантии
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
