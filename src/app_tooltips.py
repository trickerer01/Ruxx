# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from abc import abstractmethod, ABC
from tkinter import Listbox, Toplevel, END, SOLID, Widget
from typing import List, Optional

__all__ = ('WidgetToolTip',)


class ToolTipBase(ABC):
    def __init__(self, widget: Widget, timed: bool, bgcolor='#ffffdd', appear_delay=1000, border_width=1, relief=SOLID) -> None:
        self.widget = widget
        self.timed = timed
        self.tipwindow = None  # type: Optional[Toplevel]
        self.id = None  # type: Optional[str]
        self.x = self.y = 0
        if not self.timed:
            self._id1 = self.widget.bind('<Enter>', self.enter)
            self._id2 = self.widget.bind('<Leave>', self.leave)
            self._id3 = self.widget.bind('<ButtonPress>', self.leave)

        self.bgcolor = bgcolor or '#ffffdd'
        self.appear_delay = appear_delay or 1000
        self.border_width = border_width or 1
        self.relief = relief or SOLID

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
        self.id = None  # type: Optional[str]
        if my_id:
            self.widget.after_cancel(my_id)

    def showtip(self) -> None:
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f'+{x:.0f}+{y:.0f}')
        self._showcontents()
        if self.timed:
            self.schedule()

    def hidetip(self) -> None:
        tw = self.tipwindow
        self.tipwindow = None  # type: Optional[Toplevel]
        if tw:
            tw.destroy()

    @abstractmethod
    def _showcontents(self) -> ...:
        ...


class WidgetToolTip(ToolTipBase):
    def __init__(self, widget: Widget, items: List[str], **kwargs) -> None:
        super().__init__(widget, **kwargs)
        self.items = items or ['Tooltip is missing!']

    def _showcontents(self) -> None:
        box = Listbox(self.tipwindow, background=self.bgcolor, relief=self.relief, borderwidth=self.border_width, height=len(self.items))
        if self.timed:
            box.bind('<ButtonPress>', self.leave)

        box.pack()
        for item in self.items:
            box.insert(END, item)
        # autoconfig width
        box.configure(width=0)

#
#
#########################################
