# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from tkinter import Label, Listbox, Toplevel, LEFT, END, SOLID, Widget
from typing import List, Optional

__all__ = ('WidgetToolTip',)


class ToolTipBase:
    def __init__(self, widget: Widget, timed: bool) -> None:
        self.widget = widget
        self.timed = timed
        self.tipwindow = None  # type: Optional[Toplevel]
        self.id = None  # type: Optional[str]
        self.x = self.y = 0
        if not self.timed:
            self._id1 = self.widget.bind('<Enter>', self.enter)
            self._id2 = self.widget.bind('<Leave>', self.leave)
            self._id3 = self.widget.bind('<ButtonPress>', self.leave)

        self.bgcolor = '#ffffdd'
        self.appear_delay = 1000
        self.border_width = 1
        self.relief = SOLID

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
        self.showcontents()
        if self.timed:
            self.schedule()

    def showcontents(self, text: str = 'Your text here') -> None:
        label = Label(self.tipwindow, text=text, justify=LEFT, background=self.bgcolor, relief=self.relief, borderwidth=self.border_width)
        label.pack()

    def hidetip(self) -> None:
        tw = self.tipwindow
        self.tipwindow = None  # type: Optional[Toplevel]
        if tw:
            tw.destroy()


class WidgetToolTip(ToolTipBase):
    def __init__(self, widget: Widget, items: List[str], timed: bool) -> None:
        super().__init__(widget, timed)
        self.items = items

    def showcontents(self, *ignored) -> None:
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
