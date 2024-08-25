# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from abc import ABC, abstractmethod
from tkinter import Listbox, Toplevel, Widget, END, SOLID
from typing import Optional, Iterable, Union, Callable

__all__ = ('WidgetToolTip',)


class ToolTipBase(ABC):
    def __init__(self, widget: Widget, timed: bool, bgcolor='#ffffdd', appear_delay=1000, border_width=1, relief=SOLID) -> None:
        self.widget = widget
        self.timed = timed
        self.tipwindow: Optional[Toplevel] = None
        self.id: Optional[str] = None
        self.bgcolor = bgcolor or '#ffffdd'
        self.appear_delay = appear_delay or 1000
        self.border_width = border_width or 1
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
        if self.timed and self.tipwindow:
            self.id = self.widget.after(self.appear_delay, self.hidetip)
        else:
            self.id = self.widget.after(self.appear_delay, self.showtip)

    def unschedule(self) -> None:
        my_id = self.id
        self.id: Optional[str] = None
        if my_id:
            self.widget.after_cancel(my_id)

    def showtip(self) -> None:
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(1)
        self.tipwindow.wm_geometry(f'+{x:.0f}+{y:.0f}')
        self._showcontents()
        if self.timed:
            self.schedule()

    def hidetip(self) -> None:
        tw = self.tipwindow
        self.tipwindow: Optional[Toplevel] = None
        if tw:
            tw.destroy()

    @abstractmethod
    def _showcontents(self) -> None:
        ...


class WidgetToolTip(ToolTipBase):
    def __init__(self, widget: Widget, items: Union[Iterable[str], Callable[[], Iterable[str]]], **kwargs) -> None:
        super().__init__(widget, **kwargs)
        self.items = items if callable(items) else list(items or ('Tooltip is missing!',))

    def _showcontents(self) -> None:
        contents = self.items() if callable(self.items) else self.items
        box = Listbox(self.tipwindow, background=self.bgcolor, relief=self.relief, borderwidth=self.border_width,
                      height=len(contents))
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
