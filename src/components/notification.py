"""Component for displaying toast notifications."""
import customtkinter as ctk
import tkinter as tk
from typing import Optional


class Notification:
    """Class for displaying temporary notifications (toast)."""
    
    _active_notifications = []
    
    @staticmethod
    def show(parent: tk.Widget, message: str, duration: int = 2500):
        """
        Show notification.

        Args:
            parent: Parent widget
            message: Notification text
            duration: Display duration in milliseconds (default 2.5 seconds)
        """
        # Close previous notifications on the same widget
        Notification._close_all_for_parent(parent)

        # Create notification window
        notification_window = tk.Toplevel(parent)
        notification_window.wm_overrideredirect(True)
        notification_window.attributes('-topmost', True)

        # Determine position (in top right corner of parent)
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()

        # Get theme for colors
        is_dark = ctk.get_appearance_mode() == "Dark"

        # Color setup
        if is_dark:
            bg_color = "#2d2d2d"
            fg_color = "#d4d4d4"
            border_color = "#555555"
        else:
            bg_color = "#ffffff"
            fg_color = "#000000"
            border_color = "#cccccc"

        # Frame with border
        frame = tk.Frame(
            notification_window,
            bg=border_color,
            relief="solid",
            borderwidth=1
        )
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        # Inner frame with background
        inner_frame = tk.Frame(
            frame,
            bg=bg_color,
            padx=15,
            pady=10
        )
        inner_frame.pack(fill="both", expand=True)

        # Notification text
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

        # Calculate window size
        notification_window.update_idletasks()
        window_width = notification_window.winfo_reqwidth()
        window_height = notification_window.winfo_reqheight()

        # Position in top right corner with offset
        offset_x = 20
        offset_y = 20
        x = parent_x + parent_width - window_width - offset_x
        y = parent_y + offset_y

        notification_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Save reference for subsequent closing
        notification_data = {
            'window': notification_window,
            'parent': parent,
            'timer': None
        }
        Notification._active_notifications.append(notification_data)

        # Automatic closing after specified time
        def close_notification():
            Notification._close(notification_window)

        notification_data['timer'] = parent.after(duration, close_notification)

        # Close on click
        notification_window.bind("<Button-1>", lambda e: close_notification())
        label.bind("<Button-1>", lambda e: close_notification())
    
    @staticmethod
    def _close(window: tk.Toplevel):
        """Close specific notification."""
        try:
            # Find and remove from list
            for notification in Notification._active_notifications[:]:
                if notification['window'] == window:
                    # Cancel timer if not yet executed
                    if notification['timer']:
                        try:
                            notification['parent'].after_cancel(notification['timer'])
                        except:
                            pass
                    Notification._active_notifications.remove(notification)
                    break

            # Close window
            window.destroy()
        except Exception as e:
            print(f"Error closing notification: {e}")
    
    @staticmethod
    def _close_all_for_parent(parent: tk.Widget):
        """Close all notifications for specified parent."""
        notifications_to_close = [
            n for n in Notification._active_notifications
            if n['parent'] == parent
        ]
        for notification in notifications_to_close:
            Notification._close(notification['window'])

