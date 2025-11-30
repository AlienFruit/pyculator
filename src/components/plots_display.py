"""Component для отображения графиков в правой панели."""
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Optional, List, Callable


class PlotsDisplay:
    """Класс для отображения графиков в отдельной панели."""
    
    def __init__(self, parent, on_close: Optional[Callable] = None):
        """
        Инициализация компонента отображения графиков.
        
        Args:
            parent: Родительский виджет
            on_close: Callback при закрытии панели
        """
        self.parent = parent
        self.on_close = on_close
        
        self.frame = ctk.CTkFrame(parent)
        # Frame упаковываем сразу, но родительский контейнер будет скрыт
        self.frame.pack(fill="both", expand=True)
        
        # Заголовок с кнопкой закрытия
        header_frame = ctk.CTkFrame(self.frame, corner_radius=0)
        header_frame.pack(fill="x")
        
        label = ctk.CTkLabel(
            header_frame,
            text="Графики",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.pack(side="left", padx=5)
        
        # Кнопка закрытия
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=30,
            height=30,
            command=self.close,
            fg_color="transparent",
            hover_color="gray",
            text_color=("gray10", "gray90")
        )
        close_btn.pack(side="right", padx=5)
        
        # Скроллируемый фрейм для графиков
        self.plots_scrollable_frame = ctk.CTkScrollableFrame(self.frame)
        self.plots_scrollable_frame.pack(fill="both", expand=True)
        
        # Привязка событий прокрутки для обновления canvas
        self._bind_scroll_events()
        
        # Список canvas для графиков
        self.plot_canvases: List[FigureCanvasTkAgg] = []
    
    def _bind_scroll_events(self):
        """Привязка событий прокрутки для обновления canvas."""
        # Используем простой подход - обновляем canvas только после окончания прокрутки
        # Не перехватываем события прокрутки, чтобы не мешать работе скроллбара
        try:
            scrollbar = self.plots_scrollable_frame._parent_canvas._scrollbar
            if scrollbar:
                # Обновляем canvas только после окончания перетаскивания скроллбара
                scrollbar.bind("<ButtonRelease-1>", self._on_scrollbar_release)
        except AttributeError:
            pass
    
    def _on_scrollbar_release(self, event=None):
        """Обработка окончания перетаскивания скроллбара."""
        # Обновляем видимые canvas после небольшой задержки
        self.frame.after(100, self._update_visible_canvases)
    
    def _update_visible_canvases(self):
        """Обновление видимых canvas после прокрутки."""
        for canvas in self.plot_canvases:
            try:
                widget = canvas.get_tk_widget()
                if widget.winfo_viewable():
                    canvas.draw_idle()
            except Exception:
                pass
    
    def clear(self):
        """Очистка всех графиков."""
        # Очищаем все canvas
        for canvas in self.plot_canvases:
            try:
                # Получаем фигуру перед уничтожением виджета
                figure = canvas.figure
                # Уничтожаем виджет
                widget = canvas.get_tk_widget()
                # Отвязываем все события перед уничтожением
                try:
                    widget.unbind_all("<Button-1>")
                    widget.unbind_all("<ButtonRelease-1>")
                except Exception:
                    pass
                widget.destroy()
                # Закрываем фигуру matplotlib после уничтожения виджета
                plt.close(figure)
            except Exception as e:
                print(f"Error при очистке canvas: {e}")
        self.plot_canvases.clear()
        
        # Очищаем скроллируемый фрейм
        for widget in self.plots_scrollable_frame.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass
    
    def display_plot(self, figure: plt.Figure):
        """
        Отображение графика matplotlib.
        
        Args:
            figure: Объект Figure matplotlib
        """
        print(f"DEBUG display_plot: Adding figure {figure}")
        # Создаем фрейм для текущего графика
        plot_frame = ctk.CTkFrame(self.plots_scrollable_frame, corner_radius=0)
        plot_frame.pack(anchor="center")
        
        # Встраиваем график
        plot_canvas = FigureCanvasTkAgg(figure, plot_frame)
        
        # Настраиваем параметры figure для лучшей производительности
        figure.set_tight_layout(True)
        
        # Используем draw для первоначальной отрисовки
        plot_canvas.draw()
        widget = plot_canvas.get_tk_widget()
        
        # Настраиваем параметры виджета для лучшей производительности при прокрутке
        widget.configure(highlightthickness=0, borderwidth=0)
        
        # Упаковываем виджет - используем pack без fill для правильного определения размеров
        widget.pack(side="top")
        
        # Привязываем события обновления к самому виджету canvas
        widget.bind("<Visibility>", lambda e: plot_canvas.draw_idle())
        
        # Принудительно обновляем размеры после упаковки
        plot_frame.update_idletasks()
        widget.update_idletasks()
        # Обновляем размеры скроллируемого фрейма после добавления каждого графика
        self.plots_scrollable_frame.update_idletasks()
        
        # Сохраняем canvas в список
        self.plot_canvases.append(plot_canvas)
        print(f"DEBUG display_plot: Canvas added, total canvases: {len(self.plot_canvases)}")
    
    def display_plots(self, figures: List[plt.Figure]):
        """
        Отображение нескольких графиков matplotlib.
        
        Args:
            figures: Список объектов Figure matplotlib
        """
        print(f"DEBUG display_plots: Received {len(figures)} figures")
        self.clear()
        
        for i, figure in enumerate(figures):
            print(f"DEBUG display_plots: Processing figure {i+1}/{len(figures)}")
            self.display_plot(figure)
        
        # Показываем панель если есть графики
        if figures:
            print(f"DEBUG display_plots: Showing panel with {len(figures)} figures")
            self.show()
            # Принудительно обновляем интерфейс и размеры
            self.frame.update_idletasks()
            self.plots_scrollable_frame.update_idletasks()
            self.parent.update_idletasks()
            # Обновляем родительский контейнер
            try:
                self.parent.master.update_idletasks()
            except:
                pass
            # Обновляем размеры скроллируемого фрейма после задержки, чтобы canvas успели отрисоваться
            self.frame.after(200, self._refresh_scrollable_frame)
            print(f"DEBUG display_plots: Panel should be visible now")
    
    def _refresh_scrollable_frame(self):
        """Обновление размеров скроллируемого фрейма."""
        try:
            # Принудительно обновляем размеры всех виджетов в скроллируемом фрейме
            for widget in self.plots_scrollable_frame.winfo_children():
                widget.update_idletasks()
                for child in widget.winfo_children():
                    child.update_idletasks()
            
            # Обновляем сам скроллируемый фрейм
            self.plots_scrollable_frame.update_idletasks()
            
            # Обновляем canvas скроллируемого фрейма для правильного расчета размеров
            scrollable_canvas = self.plots_scrollable_frame._parent_canvas
            scrollable_canvas.update_idletasks()
            
            # Принудительно пересчитываем размеры прокручиваемой области
            inner_frame = self.plots_scrollable_frame._scrollable_frame
            inner_frame.update_idletasks()
        except Exception as e:
            print(f"DEBUG _refresh_scrollable_frame error: {e}")
            pass
    
    def show(self):
        """Show панель графиков."""
        print(f"DEBUG PlotsDisplay.show: Showing plots panel")
        # Упаковываем родительский контейнер (plots_panel)
        try:
            self.parent.pack_info()
            print(f"DEBUG: Parent already packed")
        except:
            # Родительский контейнер не упакован, упаковываем его
            print(f"DEBUG: Packing parent container")
            self.parent.pack(side="right", fill="both", expand=True, padx=(5, 5))
    
    def hide(self):
        """Скрыть панель графиков."""
        print(f"DEBUG PlotsDisplay.hide: Hiding plots panel")
        try:
            self.parent.pack_forget()
            print(f"DEBUG: Parent unpacked")
        except:
            print(f"DEBUG: Parent was not packed")
    
    def close(self):
        """Close панель графиков."""
        # Сначала скрываем панель, потом очищаем графики
        self.hide()
        # Небольшая задержка перед очисткой, чтобы избежать проблем с событиями
        self.frame.after(10, self._clear_after_hide)
    
    def _clear_after_hide(self):
        """Очистка графиков после скрытия панели."""
        self.clear()
        # Вызываем callback после очистки
        if self.on_close:
            self.on_close()

