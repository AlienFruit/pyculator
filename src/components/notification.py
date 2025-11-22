"""Компонент для отображения toast-уведомлений."""
import customtkinter as ctk
import tkinter as tk
from typing import Optional


class Notification:
    """Класс для отображения временных уведомлений (toast)."""
    
    _active_notifications = []
    
    @staticmethod
    def show(parent: tk.Widget, message: str, duration: int = 2500):
        """
        Показать уведомление.
        
        Args:
            parent: Родительский виджет
            message: Текст уведомления
            duration: Длительность отображения в миллисекундах (по умолчанию 2.5 секунды)
        """
        # Закрываем предыдущие уведомления на том же виджете
        Notification._close_all_for_parent(parent)
        
        # Создаем окно уведомления
        notification_window = tk.Toplevel(parent)
        notification_window.wm_overrideredirect(True)
        notification_window.attributes('-topmost', True)
        
        # Определяем позицию (в правом верхнем углу родителя)
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        
        # Получаем тему для цветов
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        # Настройка цветов
        if is_dark:
            bg_color = "#2d2d2d"
            fg_color = "#d4d4d4"
            border_color = "#555555"
        else:
            bg_color = "#ffffff"
            fg_color = "#000000"
            border_color = "#cccccc"
        
        # Фрейм с рамкой
        frame = tk.Frame(
            notification_window,
            bg=border_color,
            relief="solid",
            borderwidth=1
        )
        frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Внутренний фрейм с фоном
        inner_frame = tk.Frame(
            frame,
            bg=bg_color,
            padx=15,
            pady=10
        )
        inner_frame.pack(fill="both", expand=True)
        
        # Текст уведомления
        label = tk.Label(
            inner_frame,
            text=message,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 10),
            wraplength=300,
            justify="left"
        )
        label.pack()
        
        # Вычисляем размер окна
        notification_window.update_idletasks()
        window_width = notification_window.winfo_reqwidth()
        window_height = notification_window.winfo_reqheight()
        
        # Позиционируем в правом верхнем углу с отступом
        offset_x = 20
        offset_y = 20
        x = parent_x + parent_width - window_width - offset_x
        y = parent_y + offset_y
        
        notification_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Сохраняем ссылку для последующего закрытия
        notification_data = {
            'window': notification_window,
            'parent': parent,
            'timer': None
        }
        Notification._active_notifications.append(notification_data)
        
        # Автоматическое закрытие через указанное время
        def close_notification():
            Notification._close(notification_window)
        
        notification_data['timer'] = parent.after(duration, close_notification)
        
        # Закрытие при клике
        notification_window.bind("<Button-1>", lambda e: close_notification())
        label.bind("<Button-1>", lambda e: close_notification())
    
    @staticmethod
    def _close(window: tk.Toplevel):
        """Закрыть конкретное уведомление."""
        try:
            # Находим и удаляем из списка
            for notification in Notification._active_notifications[:]:
                if notification['window'] == window:
                    # Отменяем таймер если он еще не выполнился
                    if notification['timer']:
                        try:
                            notification['parent'].after_cancel(notification['timer'])
                        except:
                            pass
                    Notification._active_notifications.remove(notification)
                    break
            
            # Закрываем окно
            window.destroy()
        except Exception as e:
            print(f"Ошибка закрытия уведомления: {e}")
    
    @staticmethod
    def _close_all_for_parent(parent: tk.Widget):
        """Закрыть все уведомления для указанного родителя."""
        notifications_to_close = [
            n for n in Notification._active_notifications
            if n['parent'] == parent
        ]
        for notification in notifications_to_close:
            Notification._close(notification['window'])

