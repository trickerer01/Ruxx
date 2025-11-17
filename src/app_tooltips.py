# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from tkinter import END, SOLID, Listbox, Toplevel, Widget

__all__ = ('WidgetToolTip',)


class ToolTipBase(ABC):
    def __init__(self, widget: Widget, timed: bool, bgcolor='#ffffdd', appear_delay=1000, border_width=1, relief=SOLID) -> None:
        self.widget: Widget = widget
        self.timed: bool = timed
        self.tipwindow: Toplevel | None = None
        self.id: str | None = None
        self.bgcolor: str = bgcolor or '#ffffdd'
        self.appear_delay: int = appear_delay or 1000
        self.border_width: int = border_width or 1
        self.relief = relief or SOLID
        if not self.timed:
            self.widget.bind('<Enter>', self.enter)
            self.widget.bind('<Leave>', self.leave)
            self.widget.bind('<ButtonPress>', self.leave)

    def enter(self, *_) -> None:
        self.schedule()

    def leave(self, *_) -> None:
        self.unschedule()
        self.hidetip()

    def schedule(self) -> None:
        self.unschedule()
        self.id = self.widget.after(self.appear_delay, (self.showtip, self.hidetip)[bool(self.timed and self.tipwindow)])

    def unschedule(self) -> None:
        my_id = self.id
        self.id: str | None = None
        if my_id:
            self.widget.after_cancel(my_id)

    def showtip(self) -> None:
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry(f'+{x:.0f}+{y:.0f}')
        self._showcontents()
        if self.timed:
            self.schedule()

    def hidetip(self) -> None:
        tw = self.tipwindow
        self.tipwindow: Toplevel | None = None
        if tw:
            tw.destroy()

    @abstractmethod
    def _showcontents(self) -> None:
        ...


class WidgetToolTip(ToolTipBase):
    def __init__(self, widget: Widget, items: Iterable[str] | Callable[[], Iterable[str]], **kwargs) -> None:
        super().__init__(widget, **kwargs)
        self.items = items if callable(items) else list(items or ('Tooltip is missing!',))

    def _showcontents(self) -> None:
        contents = self.items() if callable(self.items) else self.items
        box = Listbox(self.tipwindow, background=self.bgcolor, relief=self.relief, borderwidth=self.border_width, height=len(contents))
        if self.timed:
            box.bind('<ButtonPress>', self.leave)

        box.pack()
        for item in contents:
            box.insert(END, item)
        # autoconfig width
        box.configure(width=0)

#
#
#########################################
