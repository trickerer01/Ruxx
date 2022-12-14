# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
# circular imports caused by:
# app_gui, app_cmdargs

# native
from abc import ABC, abstractmethod
from base64 import b64decode
from datetime import datetime
from json import dumps as json_dumps, loads as json_loads
from os import curdir, path
from re import search as re_search, match as re_match, findall as re_findall
from tkinter import (
    Menu, Toplevel, messagebox, ttk, Text, Scrollbar, StringVar, Button, Entry, Widget, SOLID, SUNKEN, FLAT, END, LEFT, BOTH, RIGHT,
    TOP, INSERT, BooleanVar, Checkbutton, Label, Tk, Listbox, PhotoImage, IntVar, HORIZONTAL, W, E, S, X, Y, NO, YES
)
from typing import Optional, Callable, List, Union, Dict

# internal
from app_defines import PROXY_DEFAULT_STR, USER_AGENT, PROGRESS_BAR_MAX
from app_file_sorter import FileTypeFilter
from app_gui_defines import (
    BUT_ESCAPE, BUT_RETURN, STATE_READONLY, STATE_DISABLED, TOOLTIP_DELAY_DEFAULT, FONT_SANS_SMALL, COLOR_LIGHTGRAY, Options, STATE_NORMAL,
    TOOLTIP_INVALID_SYNTAX, CVARS, FONT_SANS_MEDIUM, COLUMNSPAN_MAX, BUT_CTRL_A, TOOLTIP_HCOOKIE_ADD_ENTRY, TOOLTIP_HCOOKIE_DELETE,
    BUT_DELETE, WINDOW_MINSIZE, PADDING_ROOTFRAME_I, Menus, menu_items, hotkeys, IMG_SAVE_DATA, IMG_PROC_RX_DATA, IMG_PROC_RN_DATA,
    IMG_OPEN_DATA, IMG_ADD_DATA, IMG_TEXT_DATA, IMG_PROC_RUXX_DATA, IMG_DELETE_DATA, STICKY_HORIZONTAL, PADDING_DEFAULT,
    OPTION_VALUES_VIDEOS, TOOLTIP_VIDEOS, Globals, OPTION_VALUES_IMAGES, TOOLTIP_IMAGES, OPTION_VALUES_THREADING, TOOLTIP_THREADING,
    OPTION_VALUES_DOWNORDER, TOOLTIP_ORDER, FMT_DATE, TOOLTIP_DATE, TOOLTIP_IDMIN, TOOLTIP_IDMAX, FONT_LUCIDA_MEDIUM, TOOLTIP_TAGS_CHECK,
    ROWSPAN_MAX, GLOBAL_COLUMNCOUNT, STICKY_VERTICAL_W, COLOR_DARKGRAY, STICKY_ALLDIRECTIONS, DATE_MIN_DEFAULT_REV, gobjects, Icons
)
from app_revision import __RUXX_DEBUG__, APP_VERSION, APP_NAME
from app_tooltips import WidgetToolTip
from app_utils import normalize_path
from app_validators import valid_proxy
# globals
# ROOOT

root = None  # type: Optional[AppRoot]
rootFrame = None  # type: Optional[BaseFrame]
rootMenu = None  # type: Optional[Menu]
# windows
window_proxy = None  # type: Optional[ProxyWindow]
window_hcookies = None  # type: Optional[HeadersAndCookiesWindow]
# counters
c_menu = None  # type: Optional[BaseMenu]
c_submenu = None  # type: Optional[BaseMenu]
int_vars = {}  # type: Dict[str, IntVar]
string_vars = {}  # type: Dict[str, StringVar]
# end globals

# loaded
register_count = 0
text_cmd = None  # type: Optional[Text]
# end loaded

# icons
icons = {
    ic: None for ic in Icons.__members__.values()
}  # type: Dict[Icons, Optional[PhotoImage]]
# end icons

c_col = None  # type: Optional[int]
c_row = None  # type: Optional[int]


def get_icon(index: Icons) -> Optional[PhotoImage]:
    return icons[index]


def cur_row() -> Optional[int]:
    return c_row


def cur_column() -> Optional[int]:
    return c_col


def next_row() -> Optional[int]:
    global c_row
    c_row = c_row + 1 if c_row is not None else 0
    return cur_row()


def next_column() -> Optional[int]:
    global c_col
    c_col = c_col + 1 if c_col is not None else 0
    return cur_column()


def first_row() -> Optional[int]:
    global c_row
    c_row = None
    return next_row()


def first_column() -> Optional[int]:
    global c_col
    c_col = None
    return next_column()


def attach_tooltip(widget: Widget, contents: List[str], appeardelay=TOOLTIP_DELAY_DEFAULT, border_width=1, relief=SOLID,
                   bgcolor: str = None, timed=False) -> WidgetToolTip:
    lbt = WidgetToolTip(widget, contents or ['Tooltip is missing!'], timed)
    if bgcolor is not None:
        lbt.bgcolor = bgcolor
    if appeardelay is not None:
        lbt.appear_delay = appeardelay
    if border_width is not None:
        lbt.border_width = border_width
    if relief is not None:
        lbt.relief = relief

    return lbt


def register_global(index: Globals, gobject: Union[Checkbutton, ttk.Combobox, Entry, Button, Label]) -> None:
    global register_count
    register_count += 1
    gobjects[index] = gobject


class AppRoot(Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        global rootFrame
        global rootMenu

        x = self.winfo_screenwidth() / 2 - WINDOW_MINSIZE[0] / 2
        y = self.winfo_screenheight() / 2 - WINDOW_MINSIZE[1] / 2 + self.winfo_screenheight() / (4 if __RUXX_DEBUG__ else 8)

        self.geometry(f'+{x:.0f}+{y:.0f}')
        self.title(f'{APP_NAME} {APP_VERSION}')
        self.default_bg_color = self['bg']

        rootFrame = BaseFrame(self)
        rootFrame.pack(fill=BOTH, expand=YES, anchor=S, padx=PADDING_ROOTFRAME_I)
        rootMenu = Menu(self)
        self.config(menu=rootMenu)
        first_row()
        first_column()

    def adjust_size(self) -> None:
        self.update()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())  # not smaller than these
        # print(self.winfo_reqwidth())
        # print(self.winfo_reqheight())
        # self.minsize(WINDOW_MINSIZE[0], WINDOW_MINSIZE[1])  # not smaller than these
        self.resizable(0, 0)

    def finalize(self) -> None:
        self.bind(BUT_ESCAPE, func=lambda _: self.focus_set())  # release focus from any element on `Esc`
        self.config(bg=self.default_bg_color)

        # self.protocol('WM_DELETE_WINDOW', quit_with_msg)
        self.mainloop()


class BaseMenu(Menu):
    def __init__(self, parent, *args, **kw) -> None:
        super().__init__(parent, *args, **kw)
        self.config(tearoff=0)


class BaseFrame(ttk.Frame):
    def __init__(self, parent, **kw) -> None:
        super().__init__(parent, **kw)


class BaseWindow:
    def __init__(self, parent, init_hidden=True) -> None:
        self.parent = parent
        self.window = None  # type: Optional[Toplevel]
        self.visible = False
        self.reinit(init_hidden)

    # requires override
    def config(self) -> None:
        messagebox.showerror('', 'nyi method \'config\' called!')
        assert False

    # requires override
    def finalize(self) -> None:
        messagebox.showerror('', 'nyi method \'finalize\' called!')
        assert False

    # requires override
    def toggle_visibility(self) -> None:
        messagebox.showerror('', 'nyi method \'toggle_visibility\' called!')
        assert False

    def reinit(self, init_hidden: bool) -> None:
        self.window = Toplevel(self.parent)
        self.visible = True
        self.config()
        if init_hidden:
            self.hide()

    def hide(self) -> None:
        self.window.withdraw()
        self.visible = False

    def show(self) -> None:
        self.window.deiconify()
        self.visible = True


class AwaitableAskWindow(BaseWindow, ABC):
    def __init__(self, parent, title: str) -> None:
        self.title = title or ''
        self.variable = StringVar(parent)
        self.but_ok = None  # type: Optional[Button]
        self.but_cancel = None  # type: Optional[Button]
        super().__init__(parent, False)

    def config(self) -> None:
        self.window.title(self.title)

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=12, pady=12, row=first_row())

        self._put_widgets(downframe)

        BaseFrame(downframe, height=16).grid(row=next_row(), columnspan=2)

        self.but_ok = Button(downframe, width=8, text='Ok', command=lambda: self.ok())
        self.but_cancel = Button(downframe, width=8, text='Cancel', command=lambda: self.cancel())
        self.but_ok.grid(row=next_row(), column=first_column(), columnspan=1)
        self.but_cancel.grid(row=cur_row(), column=next_column(), columnspan=1)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_reqwidth()) / 2
        y = self.parent.winfo_y() + 50
        self.window.geometry(f'+{x:.0f}+{y:.0f}')
        self.window.wait_visibility()
        self.window.grab_set()
        self.window.update()
        self.window.transient(self.parent)  # remove minimize and maximize buttons
        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(0, 0)
        self.window.focus_set()

        self.window.bind(BUT_ESCAPE, lambda _: self.cancel())
        self.window.bind(BUT_RETURN, lambda _: self.ok())

    def ok(self) -> None:
        self.window.grab_release()
        self.window.destroy()

    def cancel(self) -> None:
        self.variable.set('')
        self.window.grab_release()
        self.window.destroy()

    @abstractmethod
    def _put_widgets(self, frame: BaseFrame) -> None:
        ...


class AskFileTypeFilterWindow(AwaitableAskWindow):
    VALUES = ['Media type', 'Extension']

    def __init__(self, parent) -> None:
        self.cbox = None  # type: Optional[ttk.Combobox]
        super().__init__(parent, 'File types')

    def finalize(self) -> None:
        self.variable.set(AskFileTypeFilterWindow.VALUES[0])
        AwaitableAskWindow.finalize(self)

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.cbox = ttk.Combobox(frame, values=AskFileTypeFilterWindow.VALUES, state=STATE_READONLY, width=18, textvariable=self.variable)
        self.cbox.grid(row=first_row(), column=first_column(), columnspan=2)

    def value(self) -> FileTypeFilter:
        try:
            # noinspection PyArgumentList
            return FileTypeFilter(AskFileTypeFilterWindow.VALUES.index(self.variable.get()) + 1)
        except Exception:
            return FileTypeFilter.FILTER_INVALID


class AskFileSizeFilterWindow(AwaitableAskWindow):
    def __init__(self, parent) -> None:
        self.entry = None  # type: Optional[Entry]
        super().__init__(parent, 'Size thresholds MB')

    def finalize(self) -> None:
        self.variable.set('')
        AwaitableAskWindow.finalize(self)
        self.entry.focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.entry = Entry(frame, width=18, textvariable=self.variable)
        self.entry.grid(row=first_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> Optional[List[float]]:
        try:
            return [float(val) for val in re_findall(r'[^, ]+', self.variable.get())]
        except Exception:
            return None


class AskIntWindow(AwaitableAskWindow):
    def __init__(self, parent, validator: Callable[[int], bool], title='Enter number') -> None:
        self.validator = validator or (lambda _: True)
        self.entry = None  # type: Optional[Entry]
        super().__init__(parent, title)

    def finalize(self) -> None:
        self.variable.set('')
        AwaitableAskWindow.finalize(self)
        self.entry.focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.entry = Entry(frame, width=18, textvariable=self.variable)
        self.entry.grid(row=first_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> Optional[int]:
        try:
            val = int(self.variable.get())
            assert self.validator(val)
            return val
        except Exception:
            return None


class AskFileScoreFilterWindow(AwaitableAskWindow):
    def __init__(self, parent) -> None:
        self.entry = None  # type: Optional[Entry]
        super().__init__(parent, 'Score thresholds')

    def finalize(self) -> None:
        self.variable.set('')
        AwaitableAskWindow.finalize(self)
        self.entry.focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.entry = Entry(frame, width=18, textvariable=self.variable)
        self.entry.grid(row=first_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> Optional[List[int]]:
        try:
            return [int(val) for val in re_findall(r'[^, ]+', self.variable.get())]
        except Exception:
            return None


class LogWindow(BaseWindow):
    log_window_base_height = 120

    def __init__(self, parent) -> None:
        self.text = None  # type: Optional[Text]
        self.scroll = None  # type: Optional[Scrollbar]
        self.firstshow = True
        super().__init__(parent)

    def config(self) -> None:
        self.window.title('Log')

        # elements
        upframe = BaseFrame(self.window, height=25)
        upframe.pack(side=TOP, fill=X)

        but_clear = Button(upframe, height=1, text='Clear log', command=self._clear)
        but_clear.pack(fill=X)

        self.text = Text(self.window, font=FONT_SANS_SMALL, relief=SUNKEN, bd=1, bg=COLOR_LIGHTGRAY, height=1)
        self.text.pack(padx=1, pady=1, fill=BOTH, side=LEFT, expand=YES)
        self.text.config(state=STATE_DISABLED)

        self.scroll = Scrollbar(self.window)
        self.scroll.pack(fill=Y, side=RIGHT, expand=NO)
        self.scroll['command'] = self.text.yview

        self.text.config(yscrollcommand=self.scroll.set)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        self.window.transient(self.parent)  # remove minimize and maximize buttons
        self.window.minsize(self.parent.winfo_width() - 2, LogWindow.log_window_base_height)
        self.window.resizable(0, 1)

        self.window.bind(BUT_ESCAPE, lambda _: self.toggle_visibility())

    def toggle_visibility(self) -> None:
        if self.visible is True:
            self.hide()
        else:
            if self.firstshow:
                self.firstshow = False
                log_window_offset_y = LogWindow.log_window_base_height + 26
                x = self.parent.winfo_x()
                y = max(self.parent.winfo_y() - log_window_offset_y, 0)
                self.window.geometry(f'+{x:.0f}+{y:.0f}')
                self.window.update()
                self.text.mark_set(INSERT, END)
                self.text.see(END)
                self.text.yview_moveto(1.0)
            self.show()
        setrootconf(Options.OPT_ISLOGOPEN, self.visible)

    def _clear(self) -> None:
        self.text.config(state=STATE_NORMAL)
        self.text.delete(1.0, END)
        self.text.config(state=STATE_DISABLED)

    def on_destroy(self) -> None:
        # just hide
        self.hide()
        setrootconf(Options.OPT_ISLOGOPEN, False)


class ProxyWindow(BaseWindow):
    def __init__(self, parent) -> None:
        self.entry = None  # type: Optional[Entry]
        self.opchb_socks_var_fake = None  # type: Optional[BooleanVar]
        self.opchb_socks_var = None  # type: Optional[BooleanVar] # need to store variable so it doesn't get purged later
        self.cb_socks = None  # type: Optional[Checkbutton]
        self.but_ok = None  # type: Optional[Button]
        self.but_cancel = None  # type: Optional[Button]
        self.err_message = None  # type: Optional[WidgetToolTip]
        super().__init__(parent)

    def config(self) -> None:
        self.window.title('Proxy')

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=12, pady=12, row=1)

        proxyhint = Label(downframe, font=FONT_SANS_SMALL, text='for example 101.100.100.10:65335')
        proxyhint.config(state=STATE_DISABLED)
        proxyhint.grid(row=0, column=0, columnspan=12)

        disentry = Entry(downframe, font=FONT_SANS_MEDIUM, width=5)
        disentry.insert(END, 'http://')
        disentry.config(state=STATE_DISABLED)
        disentry.grid(row=1, column=0, columnspan=1)
        _ = Entry(textvariable=StringVar(rootm(), PROXY_DEFAULT_STR if __RUXX_DEBUG__ else '', CVARS[Options.OPT_PROXYSTRING]))
        self.entry = Entry(downframe, font=FONT_SANS_MEDIUM, width=23,
                           textvariable=StringVar(rootm(), '', CVARS[Options.OPT_PROXYSTRING_TEMP]))
        if __RUXX_DEBUG__:
            self.entry.insert(END, PROXY_DEFAULT_STR)
        self.err_message = attach_tooltip(self.entry, TOOLTIP_INVALID_SYNTAX, 5000, timed=True)
        self.entry.grid(row=1, column=1, columnspan=6)

        # BaseFrame(downframe, height=16).grid(row=2, columnspan=COLUMNSPAN_MAX)
        BaseFrame(downframe, height=16).grid(row=4, columnspan=COLUMNSPAN_MAX)

        self.opchb_socks_var_fake = BooleanVar(rootm(), __RUXX_DEBUG__, CVARS[Options.OPT_PROXY_SOCKS_TEMP])
        self.opchb_socks_var = BooleanVar(rootm(), __RUXX_DEBUG__, CVARS[Options.OPT_PROXY_SOCKS])
        self.cb_socks = Checkbutton(downframe, text='Use SOCKS5 instead', variable=self.opchb_socks_var_fake)
        # register_global(Globals.GOBJECT_CHECK_SOCKS, self.cb_socks)
        self.cb_socks.grid(row=3, column=0, columnspan=COLUMNSPAN_MAX)

        self.but_ok = Button(downframe, width=8, text='Ok', command=lambda: self.ok())
        self.but_cancel = Button(downframe, width=8, text='Cancel', command=lambda: self.cancel())
        self.but_ok.grid(row=5, column=1, columnspan=1)
        self.but_cancel.grid(row=5, column=2, columnspan=1)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_reqwidth()) / 2
        y = self.parent.winfo_y() + 50
        self.window.geometry(f'+{x:.0f}+{y:.0f}')
        self.window.update()
        self.window.transient(self.parent)
        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(0, 0)

        self.window.bind(BUT_RETURN, lambda _: self.ok())
        self.window.bind(BUT_ESCAPE, lambda _: self.cancel())
        self.window.bind(BUT_CTRL_A, lambda _: self.select_all())

    def select_all(self) -> None:
        if self.visible is True:
            self.entry.focus_set()
            self.entry.selection_range(0, END)
            self.entry.icursor(END)

    def ok(self) -> None:
        # Address validation
        newval = str(getrootconf(Options.OPT_PROXYSTRING_TEMP))

        # moved to cmdargs, wrapped here
        try:
            newval = valid_proxy(newval)
            adr_valid = True
        except Exception:
            adr_valid = False

        if not adr_valid:
            self.err_message.showtip()
        else:
            setrootconf(Options.OPT_PROXYSTRING, newval)
            setrootconf(Options.OPT_PROXY_SOCKS, bool(int(getrootconf(Options.OPT_PROXY_SOCKS_TEMP))))
            self.hide()

    def cancel(self) -> None:
        setrootconf(Options.OPT_PROXYSTRING_TEMP, str(getrootconf(Options.OPT_PROXYSTRING)))
        setrootconf(Options.OPT_PROXY_SOCKS_TEMP, bool(int(getrootconf(Options.OPT_PROXY_SOCKS))))
        self.hide()

    def ask(self) -> None:
        if self.visible is False:
            self.show()
            self.select_all()

    def on_destroy(self) -> None:
        self.cancel()


# noinspection DuplicatedCode
class HeadersAndCookiesWindow(BaseWindow):
    MAX_COOKIES = 3
    MAX_HEADERS = 3

    LBOX_WIDTH = 65

    def __init__(self, parent) -> None:
        self.lbox_h = None  # type: Optional[Listbox]
        self.bdel_h = None  # type: Optional[Button]
        self.badd_h = None  # type: Optional[Button]
        self.entry_h = None  # type: Optional[Entry]
        self.err_message_syntax_h = None  # type: Optional[WidgetToolTip]
        self.err_message_count_h = None  # type: Optional[WidgetToolTip]
        self.lbox_c = None  # type: Optional[Listbox]
        self.bdel_c = None  # type: Optional[Button]
        self.badd_c = None  # type: Optional[Button]
        self.entry_c = None  # type: Optional[Entry]
        self.err_message_syntax_c = None  # type: Optional[WidgetToolTip]
        self.err_message_count_c = None  # type: Optional[WidgetToolTip]
        super().__init__(parent)

    def config(self) -> None:
        self.window.title('Headers / Cookies')

        base_width = HeadersAndCookiesWindow.LBOX_WIDTH

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=6, pady=6, row=1, column=0, columnspan=COLUMNSPAN_MAX)

        hframe = ttk.LabelFrame(downframe, text='Headers list')
        hframe.pack()

        self.lbox_h = Listbox(hframe, width=base_width, height=HeadersAndCookiesWindow.MAX_HEADERS, borderwidth=2, font=FONT_SANS_MEDIUM)
        self.lbox_h.pack(padx=5, pady=0)

        self.bdel_h = Button(hframe, image=get_icon(Icons.ICON_DELETE), command=self.delete_selected_h)
        self.bdel_h.pack(side=LEFT, padx=5, pady=5)
        attach_tooltip(self.bdel_h, TOOLTIP_HCOOKIE_DELETE)

        self.badd_h = Button(hframe, image=get_icon(Icons.ICON_ADD), command=self.add_header_to_list)
        self.badd_h.pack(side=LEFT, padx=0, pady=5)

        self.entry_h = Entry(hframe, font=FONT_SANS_MEDIUM, textvariable=StringVar(rootm(), '', CVARS[Options.OPT_HEADER_ADD_STR]))
        self.entry_h.pack(side=LEFT, padx=5, pady=5, fill=X, expand=YES)
        attach_tooltip(self.entry_h, TOOLTIP_HCOOKIE_ADD_ENTRY)

        self.err_message_syntax_h = attach_tooltip(self.entry_h, TOOLTIP_INVALID_SYNTAX, 5000, timed=True)
        self.err_message_count_h = attach_tooltip(self.entry_h, ['Too many headers!'], 5000, timed=True)

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=6, pady=6, row=1, column=0, columnspan=COLUMNSPAN_MAX)

        cframe = ttk.LabelFrame(downframe, text='Cookies list')
        cframe.pack()

        self.lbox_c = Listbox(cframe, width=base_width, height=HeadersAndCookiesWindow.MAX_COOKIES, borderwidth=2, font=FONT_SANS_MEDIUM)
        self.lbox_c.pack(padx=5, pady=0)

        self.bdel_c = Button(cframe, image=get_icon(Icons.ICON_DELETE), command=self.delete_selected_c)
        self.bdel_c.pack(side=LEFT, padx=5, pady=5)
        attach_tooltip(self.bdel_c, TOOLTIP_HCOOKIE_DELETE)

        self.badd_c = Button(cframe, image=get_icon(Icons.ICON_ADD), command=self.add_coookie_to_list)
        self.badd_c.pack(side=LEFT, padx=0, pady=5)

        self.entry_c = Entry(cframe, font=FONT_SANS_MEDIUM, textvariable=StringVar(rootm(), '', CVARS[Options.OPT_COOKIE_ADD_STR]))
        self.entry_c.pack(side=LEFT, padx=5, pady=5, fill=X, expand=YES)
        attach_tooltip(self.entry_c, TOOLTIP_HCOOKIE_ADD_ENTRY)

        self.err_message_syntax_c = attach_tooltip(self.entry_c, TOOLTIP_INVALID_SYNTAX, 5000, timed=True)
        self.err_message_count_c = attach_tooltip(self.entry_c, ['Too many cookies!'], 5000, timed=True)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_reqwidth()) / 4
        y = self.parent.winfo_y() - 60
        self.window.geometry(f'+{x:.0f}+{y:.0f}')
        self.window.update()
        self.window.transient(self.parent)

        # initial values just for convenience
        self.lbox_h.insert(0, f'user-agent:{USER_AGENT}')
        self.entry_h.insert(0, 'user-agent:')
        self.entry_c.insert(0, 'cf_clearance:')

        # configure required width (needed if we change default useragent in the future)
        def get_maxlen(b: Listbox) -> int:
            return max(len(str(b.get(i))) for i in range(b.size())) if b.size() > 0 else 0

        maxlen = max(max(get_maxlen(lbox) for lbox in [self.lbox_h, self.lbox_c]), HeadersAndCookiesWindow.LBOX_WIDTH)
        self.lbox_h.configure(width=maxlen)
        self.lbox_c.configure(width=maxlen)

        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(0, 0)

        self.window.bind(BUT_ESCAPE, lambda _: self.hide())
        self.lbox_h.bind(BUT_DELETE, lambda _: self.delete_selected_h())
        self.lbox_c.bind(BUT_DELETE, lambda _: self.delete_selected_c())
        self.entry_h.bind(BUT_RETURN, lambda _: self.add_header_to_list())
        self.entry_c.bind(BUT_RETURN, lambda _: self.add_coookie_to_list())

    def toggle_visibility(self) -> None:
        if self.visible is False:
            self.show()
            self.select_all_c()
        else:
            self.hide()

        setrootconf(Options.OPT_ISHCOOKIESOPEN, self.visible)

    @staticmethod
    def _listbox_to_json(lb: Listbox) -> str:
        ls = {}  # type: Dict[str, str]
        for i in range(lb.size()):
            part1, part2 = tuple(str(lb.get(i)).split(':', 1))
            ls.update({part1: part2})

        return json_dumps(ls, skipkeys=True)

    def get_json_h(self) -> str:
        return self._listbox_to_json(self.lbox_h)

    def get_json_c(self) -> str:
        return self._listbox_to_json(self.lbox_c)

    def add_header_to_list(self) -> None:
        syntax_valid = True

        h_count = self.lbox_h.size()
        newval = str(getrootconf(Options.OPT_HEADER_ADD_STR))

        try:
            parts = re_search(r'^([^: ,]+)[: ,](.+)$', newval)
            h_title, h_value = parts.group(1), parts.group(2)
            for i in range(self.lbox_h.size()):
                part1, _ = tuple(str(self.lbox_h.get(i)).split(':', 1))
                if part1.lower() == h_title.lower():
                    raise KeyError
            newval = f'{h_title}:{h_value}'
        except Exception:
            syntax_valid = False

        if h_count >= HeadersAndCookiesWindow.MAX_HEADERS:
            self.err_message_count_h.showtip()
        elif not syntax_valid:
            self.err_message_syntax_h.showtip()
        else:
            self.lbox_h.insert(END, newval)
            self.entry_h.delete(0, END)

    def delete_selected_h(self) -> None:
        cur = self.lbox_h.curselection()
        if cur:
            i = self.lbox_h.index(cur)
            self.lbox_h.delete(cur)
            if self.lbox_h.size() != 0:
                self.lbox_h.selection_set(min(i, self.lbox_h.size() - 1))

    def add_coookie_to_list(self) -> None:
        syntax_valid = True

        c_count = self.lbox_c.size()
        newval = str(getrootconf(Options.OPT_COOKIE_ADD_STR))

        try:
            parts = re_search(r'^([^: ,]+)[: ,](.+)$', newval)
            c_title, c_value = parts.group(1), parts.group(2)
            for i in range(self.lbox_c.size()):
                part1, _ = tuple(str(self.lbox_c.get(i)).split(':', 1))
                if part1.lower() == c_title.lower():
                    raise KeyError
            newval = f'{c_title}:{c_value}'
        except Exception:
            syntax_valid = False

        if c_count >= HeadersAndCookiesWindow.MAX_COOKIES:
            self.err_message_count_c.showtip()
        elif not syntax_valid:
            self.err_message_syntax_c.showtip()
        else:
            self.lbox_c.insert(END, newval)
            self.entry_c.delete(0, END)

    def delete_selected_c(self) -> None:
        cur = self.lbox_c.curselection()
        if cur:
            i = self.lbox_c.index(cur)
            self.lbox_c.delete(cur)
            if self.lbox_c.size() != 0:
                self.lbox_c.selection_set(min(i, self.lbox_c.size() - 1))

    def select_all_c(self) -> None:
        if self.visible is True:
            self.entry_c.focus_set()
            self.entry_c.selection_range(0, END)
            self.entry_c.icursor(END)

    def set_to_h(self, json_h: str) -> None:
        if self.lbox_h.size() > 0:
            self.lbox_h.delete(0, END)
        newvals = json_loads(json_h)
        for k, v in newvals.items():
            self.lbox_h.insert(END, f'{str(k)}:{str(v)}')

    def set_to_c(self, json_c: str) -> None:
        if self.lbox_c.size() > 0:
            self.lbox_c.delete(0, END)
        newvals = json_loads(json_c)
        for k, v in newvals.items():
            self.lbox_c.insert(END, f'{str(k)}:{str(v)}')

    def on_destroy(self) -> None:
        self.hide()
        setrootconf(Options.OPT_ISHCOOKIESOPEN, False)


def init_additional_windows() -> None:

    def create_window_proxy() -> None:
        global window_proxy
        window_proxy = ProxyWindow(root)
        window_proxy.window.wm_protocol('WM_DELETE_WINDOW', window_proxy.on_destroy)
        rootm().bind_all(hotkeys[Options.OPT_ISPROXYOPEN], func=lambda _: window_proxy.ask())

    def create_window_hcookies() -> None:
        global window_hcookies
        window_hcookies = HeadersAndCookiesWindow(root)
        window_hcookies.window.wm_protocol('WM_DELETE_WINDOW', window_hcookies.on_destroy)
        rootm().bind_all(hotkeys[Options.OPT_ISHCOOKIESOPEN], func=lambda _: window_hcookies.toggle_visibility())

    create_window_proxy()
    create_window_hcookies()


def register_menu(label: str, menu_id: Menus = None) -> Menu:
    global rootMenu
    global c_menu
    menu = BaseMenu(rootMenu)
    # register in global container for later
    if menu_id is not None:
        if menu_id in menu_items.keys():
            menu_items[menu_id][0] = menu
    root_menum().add_cascade(menu=menu, label=label)
    c_menu = menu
    return menu


def register_submenu(label: str) -> Menu:
    global c_submenu
    submenu = BaseMenu(rootMenu)
    c_menum().add_cascade(menu=submenu, label=label)
    c_submenu = submenu
    return submenu


def getrootconf(index: Options) -> Union[int, str]:
    return rootm().getvar(CVARS[index])


def setrootconf(index: Options, value: Union[int, str, bool]) -> None:
    return rootm().setvar(CVARS[index], value)


def rootm() -> AppRoot:
    assert root
    return root or AppRoot()


def root_framem() -> BaseFrame:
    assert rootFrame
    return rootFrame or BaseFrame(rootm())


def root_menum() -> Menu:
    assert rootMenu
    return rootMenu or Menu()


def c_menum() -> BaseMenu:
    assert c_menu
    return c_menu or BaseMenu(rootm())


def c_submenum() -> BaseMenu:
    assert c_submenu
    return c_submenu or BaseMenu(c_menum())


def window_proxym() -> ProxyWindow:
    assert window_proxy
    return window_proxy or ProxyWindow(rootm())


def window_hcookiesm() -> HeadersAndCookiesWindow:
    assert window_hcookies
    return window_hcookies or HeadersAndCookiesWindow(rootm())


def text_cmdm() -> Text:
    assert text_cmd
    return text_cmd or Text()


# noinspection PyPep8Naming
def CreateRoot() -> None:
    global root
    assert root is None
    root = AppRoot()


# noinspection PyPep8Naming
def GetRoot() -> Optional[AppRoot]:
    return root


def create_base_window_widgets() -> None:
    global text_cmd

    CreateRoot()

    # icons
    icons[Icons.ICON_RUXX] = PhotoImage(data=b64decode(IMG_PROC_RUXX_DATA))
    icons[Icons.ICON_RX] = PhotoImage(data=b64decode(IMG_PROC_RX_DATA))
    icons[Icons.ICON_RN] = PhotoImage(data=b64decode(IMG_PROC_RN_DATA))
    icons[Icons.ICON_OPEN] = PhotoImage(data=b64decode(IMG_OPEN_DATA))
    icons[Icons.ICON_SAVE] = PhotoImage(data=b64decode(IMG_SAVE_DATA))
    icons[Icons.ICON_DELETE] = PhotoImage(data=b64decode(IMG_DELETE_DATA))
    icons[Icons.ICON_ADD] = PhotoImage(data=b64decode(IMG_ADD_DATA))
    icons[Icons.ICON_TEXT] = PhotoImage(data=b64decode(IMG_TEXT_DATA))  # unused

    rootm().iconphoto(True, get_icon(Icons.ICON_RUXX))

    # validators
    #  number
    valid_int = rootm().register(lambda x: (re_match(r'[\d-]', str(x)) is not None) or len(str(x)) == 0)
    valid_uint = rootm().register(lambda x: (re_match(r'\d', str(x)) is not None) or len(str(x)) == 0)
    # valid_tag = rootm().register(lambda x: (re_match(tap.re_not_allowed_tag_symbol, str(x).lower())) is None)
    # valid_date = rootm().register(is_date_valid)
    # valid_nope = rootm().register(lambda _: False)
    # vars need to be inited here, need to assign something, otherwise this won't work
    string_vars[CVARS[Options.OPT_LASTPATH]] = StringVar(rootm(), '', CVARS[Options.OPT_LASTPATH])

    # Main menu
    # init_menus()

    # Style conf
    # ttkstyle = ttk.Style()
    # ttkstyle.theme_use('alt')
    # ttkstyle.configure('Horizontal.TProgressbar', thickness=5, bg=COLOR_STEELBLUE)

    # Options #
    #  Videos
    opframe_vid = ttk.LabelFrame(root_framem(), text='Videos')
    opframe_vid.grid(row=cur_row(), column=cur_column(), rowspan=1, columnspan=1,
                     sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    op_vid = ttk.Combobox(opframe_vid, values=OPTION_VALUES_VIDEOS, state=STATE_READONLY, width=18,
                          textvariable=StringVar(rootm(), '', CVARS[Options.OPT_VIDSETTING]))
    register_global(Globals.GOBJECT_COMBOBOX_VIDEOS, op_vid)
    attach_tooltip(op_vid, TOOLTIP_VIDEOS)
    op_vid.current(1)
    op_vid.pack(padx=PADDING_DEFAULT * 2, pady=3)
    #  Images
    opframe_img = ttk.LabelFrame(root_framem(), text='Images')
    opframe_img.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                     sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    op_img = ttk.Combobox(opframe_img, values=OPTION_VALUES_IMAGES, state=STATE_READONLY, width=20,
                          textvariable=StringVar(rootm(), '', CVARS[Options.OPT_IMGSETTING]))
    register_global(Globals.GOBJECT_COMBOBOX_IMAGES, op_img)
    attach_tooltip(op_img, TOOLTIP_IMAGES)
    op_img.current(len(OPTION_VALUES_IMAGES) - 1)
    op_img.pack(padx=PADDING_DEFAULT * 2, pady=3)
    #  Threading
    opframe_thread = ttk.LabelFrame(root_framem(), text='Threading')
    opframe_thread.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                        sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    op_thread = ttk.Combobox(opframe_thread, values=OPTION_VALUES_THREADING, state=STATE_READONLY, width=18,
                             textvariable=StringVar(rootm(), '', CVARS[Options.OPT_THREADSETTING]))
    register_global(Globals.GOBJECT_COMBOBOX_THREADING, op_thread)
    attach_tooltip(op_thread, TOOLTIP_THREADING)
    op_thread.current(len(OPTION_VALUES_THREADING) - 1)
    op_thread.pack(padx=PADDING_DEFAULT * 2, pady=3)
    # Download order
    opframe_order = ttk.LabelFrame(root_framem(), text='Order')
    opframe_order.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=COLUMNSPAN_MAX - 3,
                       sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    op_order = ttk.Combobox(opframe_order, values=OPTION_VALUES_DOWNORDER, state=STATE_READONLY, width=18,
                            textvariable=StringVar(rootm(), '', CVARS[Options.OPT_DOWNORDER]))
    register_global(Globals.GOBJECT_COMBOBOX_DOWNORDER, op_order)
    attach_tooltip(op_order, TOOLTIP_ORDER)
    op_order.current(1)
    op_order.pack(padx=PADDING_DEFAULT * 2, pady=3)

    # Search limits  #
    opframe_slim = ttk.LabelFrame(root_framem(), text='Search limits')
    opframe_slim.grid(row=next_row(), column=first_column(), rowspan=1, columnspan=COLUMNSPAN_MAX,
                      sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    #  Date min
    op_dateaf = Label(opframe_slim, text='Date min:')
    op_dateaf.pack(padx=(0, 0), pady=3, expand=YES, side=LEFT, anchor=E)
    op_dateaf_t = Entry(opframe_slim, width=13,  # validate='all', validatecommand=(valid_date, '%P'),
                        textvariable=StringVar(rootm(), '', CVARS[Options.OPT_DATEAFTER]))
    register_global(Globals.GOBJECT_FIELD_DATEAFTER, op_dateaf_t)
    op_dateaf_t.insert(0, DATE_MIN_DEFAULT_REV)
    op_dateaf_t.pack(padx=(0, 0), pady=3, expand=NO, side=LEFT)
    #  Date max
    op_datebe = Label(opframe_slim, text='Date max:')
    op_datebe.pack(padx=(8, 0), pady=3, expand=YES, side=LEFT, anchor=E)
    op_datebe_t = Entry(opframe_slim, width=13,  # validate='all', validatecommand=(valid_date, '%P'),
                        textvariable=StringVar(rootm(), '', CVARS[Options.OPT_DATEBEFORE]))
    register_global(Globals.GOBJECT_FIELD_DATEBEFORE, op_datebe_t)
    op_datebe_t.insert(0, datetime.today().strftime(FMT_DATE))
    op_datebe_t.pack(padx=(0, 0), pady=3, expand=NO, side=LEFT)
    attach_tooltip(op_dateaf_t, TOOLTIP_DATE)
    attach_tooltip(op_datebe_t, TOOLTIP_DATE)
    #  ID min
    op_idaf = Label(opframe_slim, text='ID min:')
    op_idaf.pack(padx=(8, 0), pady=3, expand=YES, side=LEFT, anchor=E)
    op_idaf_t = Entry(opframe_slim, width=18, validate='key', validatecommand=(valid_uint, '%S'),
                      textvariable=StringVar(rootm(), '', CVARS[Options.OPT_IDMIN]))
    register_global(Globals.GOBJECT_FIELD_IDMIN, op_idaf_t)
    op_idaf_t.insert(0, '0')
    op_idaf_t.pack(padx=(0, 0), pady=3, expand=NO, side=LEFT)
    #  ID max
    op_idbe = Label(opframe_slim, text='ID max:')
    op_idbe.pack(padx=(8, 0), pady=3, expand=YES, side=LEFT, anchor=E)
    op_idbe_t = Entry(opframe_slim, width=18, validate='key', validatecommand=(valid_int, '%S'),
                      textvariable=StringVar(rootm(), '', CVARS[Options.OPT_IDMAX]))
    register_global(Globals.GOBJECT_FIELD_IDMAX, op_idbe_t)
    op_idbe_t.insert(0, '0')
    op_idbe_t.pack(padx=(0, PADDING_DEFAULT + 1), pady=3, expand=NO, side=LEFT)
    attach_tooltip(op_idaf_t, TOOLTIP_IDMIN)
    attach_tooltip(op_idbe_t, TOOLTIP_IDMAX)
    # Tags #
    opframe_tags = ttk.LabelFrame(root_framem(), text='Tags')
    opframe_tags.grid(row=next_row(), column=first_column(), columnspan=COLUMNSPAN_MAX,
                      sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    #  Text
    op_tagsstr = Entry(opframe_tags, font=FONT_LUCIDA_MEDIUM, textvariable=StringVar(rootm(), 'sfw', CVARS[Options.OPT_TAGS]))
    #   need to set validation again because it will be forcefully disabled on such a value set
    setrootconf(Options.OPT_TAGS, 'sfw')
    # op_tagsstr.config(validate='key', validatecommand=(valid_tag, '%S'))
    register_global(Globals.GOBJECT_FIELD_TAGS, op_tagsstr)
    op_tagsstr.pack(padx=2, pady=3, expand=YES, side=LEFT, fill=X)
    #  Button check
    op_tagsbutcheck = Button(opframe_tags, text='check')
    register_global(Globals.GOBJECT_BUTTON_CHECKTAGS, op_tagsbutcheck)
    op_tagsbutcheck.pack(padx=2, pady=3, expand=NO, side=LEFT)
    attach_tooltip(op_tagsbutcheck, TOOLTIP_TAGS_CHECK)
    #  Button clear
    op_tagsbutclear = Button(opframe_tags, text='clear', command=lambda: setrootconf(Options.OPT_TAGS, ''))
    register_global(Globals.GOBJECT_BUTTON_CLEARTAGS, op_tagsbutclear)
    op_tagsbutclear.pack(padx=2, pady=3, expand=NO, side=LEFT)

    # Path #
    opframe_path = ttk.LabelFrame(root_framem(), text='Path')
    opframe_path.grid(row=next_row(), column=first_column(), columnspan=COLUMNSPAN_MAX,
                      sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    #  Text
    op_pathstr = Entry(opframe_path, font=FONT_LUCIDA_MEDIUM,
                       textvariable=StringVar(rootm(), '', CVARS[Options.OPT_PATH]))
    register_global(Globals.GOBJECT_FIELD_PATH, op_pathstr)
    # op_pathstr.insert(0, decode_string(path.abspath(curdir), getpreferredencoding(False)))  # 2.7
    op_pathstr.insert(0, normalize_path(path.abspath(curdir), False))  # 3.8
    op_pathstr.pack(padx=2, pady=3, expand=YES, side=LEFT, fill=X)
    #  Button open
    op_pathbut = Button(opframe_path, image=get_icon(Icons.ICON_OPEN))
    register_global(Globals.GOBJECT_BUTTON_OPENFOLDER, op_pathbut)
    op_pathbut.pack(padx=2, pady=3, expand=NO, side=RIGHT)

    # Cmdline and _download button #
    #  Cmdline  #
    #   Note: global
    text_cmd = Text(root_framem(), font=FONT_SANS_SMALL, relief=SUNKEN, bd=0, bg=rootm().default_bg_color, height=3)
    text_cmdm().grid(row=next_row(), column=first_column(), columnspan=COLUMNSPAN_MAX - 1, rowspan=ROWSPAN_MAX,
                     sticky=STICKY_ALLDIRECTIONS, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    #  Button _download  #
    dw_but = Button(root_framem(), text='Download', width=8, font=FONT_SANS_MEDIUM)
    dw_but.grid(row=cur_row(), column=GLOBAL_COLUMNCOUNT - 1, columnspan=1, rowspan=ROWSPAN_MAX,
                sticky=STICKY_VERTICAL_W, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    register_global(Globals.GOBJECT_BUTTON_DOWNLOAD, dw_but)

    # root_framem().grid_rowconfigure(cur_row(), weight=1)  # make plastic

    # This one is after root_framem()1
    pb1 = ttk.Progressbar(rootm(), value=0, maximum=PROGRESS_BAR_MAX, mode='determinate', orient=HORIZONTAL,
                          variable=IntVar(rootm(), 0, CVARS[Options.OPT_PROGRESS]))
    pb1.pack(fill=X, expand=NO, anchor=S)

    # This one is after progressbar
    sb_frame = BaseFrame(rootm())
    sb_frame.pack(fill=X, expand=NO, anchor=S)

    ib1 = Label(sb_frame, borderwidth=1, relief=FLAT, anchor=W, image=get_icon(Icons.ICON_RX))
    ib1.pack(expand=NO, side=LEFT)
    register_global(Globals.GOBJECT_MODULE_ICON, ib1)

    sb1 = Label(sb_frame, borderwidth=1, relief=SUNKEN, anchor=W, text='Ready', bg=COLOR_DARKGRAY,
                textvariable=StringVar(rootm(), '', CVARS[Options.OPT_STATUS]))
    sb1.pack(fill=X, expand=NO)

    # Safety precautions
    if register_count < int(Globals.MAX_GOBJECTS):
        messagebox.showinfo('', 'Not all GOBJECTS were registered')

#
#
#########################################
