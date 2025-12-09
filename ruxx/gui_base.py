# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
# circular imports caused by:
# gui.py

import base64
import ctypes
import json
import os
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from tkinter import (
    BOTH,
    END,
    FLAT,
    HORIZONTAL,
    INSERT,
    LEFT,
    NO,
    NONE,
    RIGHT,
    SEL,
    SUNKEN,
    TOP,
    YES,
    BooleanVar,
    Button,
    Checkbutton,
    IntVar,
    Label,
    Listbox,
    Menu,
    PhotoImage,
    S,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    Toplevel,
    W,
    Widget,
    X,
    Y,
    filedialog,
    messagebox,
    ttk,
)
from tkinter.ttk import Entry
from typing import Literal, TypeAlias

from .debug import __RUXX_DEBUG__
from .defines import (
    API_KEY_LEN_RX,
    CONNECT_RETRIES_BASE,
    CONNECT_TIMEOUT_BASE,
    DATE_MAX_DEFAULT,
    DATE_MIN_DEFAULT,
    KNOWN_EXTENSIONS_STR,
    PLATFORM_WINDOWS,
    PROGRESS_BAR_MAX,
    PROXY_DEFAULT_STR,
    SITENAME_B_BB,
    SITENAME_B_EN,
    SITENAME_B_RN,
    SITENAME_B_RP,
    SITENAME_B_RS,
    SITENAME_B_RX,
    SITENAME_B_XB,
    USER_AGENT,
)
from .file_parser import prepare_id_list, prepare_tag_lists
from .file_sorter import FileTypeFilter
from .gui_defines import (
    BEGIN,
    BUT_CTRL_A,
    BUT_CTRL_BACKSPACE,
    BUT_CTRL_DELETE,
    BUT_CTRL_SPACE,
    BUT_DELETE,
    BUT_ESCAPE,
    BUT_RETURN,
    BUTTONS_TO_UNFOCUS,
    COLOR_DARKGRAY,
    COLOR_LIGHTGRAY,
    COLUMNSPAN_MAX,
    CVARS,
    FONT_LUCIDA_MEDIUM,
    FONT_SANS_MEDIUM,
    FONT_SANS_SMALL,
    GLOBAL_COLUMNCOUNT,
    IMG_ADD_DATA,
    IMG_DELETE_DATA,
    IMG_OPEN_DATA,
    IMG_PROC_BB_DATA,
    IMG_PROC_EN_DATA,
    IMG_PROC_RN_DATA,
    IMG_PROC_RP_DATA,
    IMG_PROC_RS_DATA,
    IMG_PROC_RUXX_DATA,
    IMG_PROC_RX_DATA,
    IMG_PROC_XB_DATA,
    IMG_SAVE_DATA,
    IMG_TEXT_DATA,
    OPTION_VALUES_DOWNLOAD_ORDER,
    OPTION_VALUES_IMAGES,
    OPTION_VALUES_PARCHI,
    OPTION_VALUES_PROXYTYPE,
    OPTION_VALUES_THREADING,
    OPTION_VALUES_VIDEOS,
    PADDING_DEFAULT,
    PADDING_ROOTFRAME_I,
    ROWSPAN_MAX,
    SLASH,
    STATE_DISABLED,
    STATE_NORMAL,
    STATE_READONLY,
    STICKY_ALLDIRECTIONS,
    STICKY_HORIZONTAL,
    TOOLTIP_DATE,
    TOOLTIP_DELAY_DEFAULT,
    TOOLTIP_DOWNLOAD_LIMIT,
    TOOLTIP_DOWNLOAD_ORDER,
    TOOLTIP_HCOOKIE_ADD_ENTRY,
    TOOLTIP_HCOOKIE_DELETE,
    TOOLTIP_IMAGES,
    TOOLTIP_INVALID_SYNTAX,
    TOOLTIP_PARCHI,
    TOOLTIP_TAGS_CHECK,
    TOOLTIP_THREADING,
    TOOLTIP_VIDEOS,
    WINDOW_MINSIZE,
    Globals,
    Icons,
    Menus,
    Options,
    SubMenus,
    gobjects,
    hotkeys,
    menu_items,
)
from .help import (
    ABOUT_MSG,
    HELP_TAGS_MSG_BB,
    HELP_TAGS_MSG_EN,
    HELP_TAGS_MSG_RN,
    HELP_TAGS_MSG_RP,
    HELP_TAGS_MSG_RS,
    HELP_TAGS_MSG_RX,
    HELP_TAGS_MSG_XB,
)
from .module import ProcModule
from .rex import re_ask_values, re_json_entry_value, re_space_mult
from .tagsdb import TagsDB
from .tooltips import WidgetToolTip
from .utils import garble_text, normalize_path
from .validators import valid_api_key, valid_positive_int, valid_proxy, valid_window_position
from .version import APP_NAME, APP_VERSION

__all__ = (
    'AskChecksWindow',
    'AskFileScoreFilterWindow',
    'AskFileSizeFilterWindow',
    'AskFileTypeFilterWindow',
    'AskFirstLastWindow',
    'AskIntWindow',
    'GetRoot',
    'ask_filename',
    'browse_path',
    'config_global',
    'config_menu',
    'create_base_window_widgets',
    'get_all_media_files_in_cur_dir',
    'get_curdir',
    'get_global',
    'get_icon',
    'get_media_files_dir',
    'getrootconf',
    'help_about',
    'help_tags',
    'hotkey_text',
    'init_additional_windows',
    'int_vars',
    'is_focusing',
    'is_global_disabled',
    'is_menu_disabled',
    'load_batch_download_tag_list',
    'load_id_list',
    'register_menu',
    'register_menu_checkbutton',
    'register_menu_command',
    'register_menu_radiobutton',
    'register_menu_separator',
    'register_submenu',
    'register_submenu_command',
    'register_submenu_radiobutton',
    'rootm',
    'set_console_shown',
    'setrootconf',
    'text_cmdm',
    'toggle_autocompletion',
    'toggle_console',
    'trigger_autocomplete_tag',
    'unfocus_buttons_once',
    'update_garbled_text_states',
    'update_lastpath',
    'window_apikeym',
    'window_hcookiesm',
    'window_logm',
    'window_proxym',
    'window_retriesm',
    'window_timeoutm',
)

LITERAL_TYPE_FIRST_LAST: TypeAlias = Literal['first', 'last', None]

SITENAMES_PER_PROC_MODULE = {
    ProcModule.RX: SITENAME_B_RX,
    ProcModule.RN: SITENAME_B_RN,
    ProcModule.RS: SITENAME_B_RS,
    ProcModule.RP: SITENAME_B_RP,
    ProcModule.EN: SITENAME_B_EN,
    ProcModule.XB: SITENAME_B_XB,
    ProcModule.BB: SITENAME_B_BB,
}
HELP_TAGS_PER_PROC_MODULE = {
    ProcModule.RX: HELP_TAGS_MSG_RX,
    ProcModule.RN: HELP_TAGS_MSG_RN,
    ProcModule.RS: HELP_TAGS_MSG_RS,
    ProcModule.RP: HELP_TAGS_MSG_RP,
    ProcModule.EN: HELP_TAGS_MSG_EN,
    ProcModule.XB: HELP_TAGS_MSG_XB,
    ProcModule.BB: HELP_TAGS_MSG_BB,
}


def set_console_shown(shown: bool) -> None:
    global console_shown
    console_shown = shown


def get_icon(index: Icons) -> PhotoImage | None:
    return icons.get(index)


def cur_row() -> int | None:
    return c_row


def cur_column() -> int | None:
    return c_col


def next_row() -> int | None:
    global c_row
    c_row = c_row + 1 if c_row is not None else 0
    return cur_row()


def next_column() -> int | None:
    global c_col
    c_col = c_col + 1 if c_col is not None else 0
    return cur_column()


def first_row() -> int | None:
    global c_row
    c_row = None
    return next_row()


def first_column() -> int | None:
    global c_col
    c_col = None
    return next_column()


def attach_tooltip(widget: Widget, contents: Iterable[str] | Callable[[], Iterable[str]],
                   appeardelay=TOOLTIP_DELAY_DEFAULT, border_width: int | None = None,
                   relief: str | None = None, bgcolor: str | None = None, timed=False) -> WidgetToolTip:
    return WidgetToolTip(widget, contents, timed=timed, bgcolor=bgcolor, appear_delay=appeardelay, border_width=border_width, relief=relief)


def register_global(index: Globals, gobject: Widget) -> None:
    assert index in gobjects and gobjects.get(index) is None
    gobjects[index] = gobject


class AppRoot(Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        global rootFrame
        global rootMenu

        self.title(f'{APP_NAME} {APP_VERSION}')
        self.default_bg_color = self['bg']

        rootFrame = BaseFrame(self)
        rootFrame.pack(fill=BOTH, expand=YES, anchor=S, padx=PADDING_ROOTFRAME_I)
        rootMenu = Menu(self)
        self.config(menu=rootMenu)
        first_row()
        first_column()

    def set_position(self, x: float, y: float) -> None:
        wh_fmt = f'{x:.0f}x{y:.0f}'
        geom_fmt = valid_window_position(wh_fmt, self)
        self.geometry(geom_fmt)
        setrootconf(Options.WINDOW_POSITION, wh_fmt)

    def adjust_position(self) -> None:
        x = self.winfo_screenwidth() / 2 - WINDOW_MINSIZE[0] / 2
        y = self.winfo_screenheight() / 2 - WINDOW_MINSIZE[1] / 2 + self.winfo_screenheight() / (3.5 if __RUXX_DEBUG__ else 8)
        self.set_position(x, y)
        self.update()
        # self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())  # not smaller than these
        self.resizable(False, False)

    def finalize(self) -> None:
        self.bind(BUT_ESCAPE, func=lambda _: self.focus_set())  # release focus from any element on `Esc`
        self.config(bg=self.default_bg_color)
        self.mainloop()


class BaseMenu(Menu):
    def __init__(self, parent, *args, **kw) -> None:
        super().__init__(parent, *args, **kw)
        self.config(tearoff=False)


class BaseFrame(ttk.Frame):
    def __init__(self, parent, **kw) -> None:
        super().__init__(parent, **kw)


class BaseText(Text):
    CTRL_DELETION_DELIMS = ' ,.!~/-=:;'

    def __init__(self, parent=None, *args, **kw) -> None:
        known_bindings: dict[str, Callable[[...], None]] = kw.pop('bindings', {})
        self._textvariable = kw.pop('textvariable', StringVar(rootm(), '', ''))
        self._textrealvariable: StringVar | None = kw.pop('encodevariable', None)
        self._option_name = str(self._textrealvariable) if str(self._textrealvariable) != str(None) else str(self._textvariable)
        kw.update(height=1, undo=True, maxundo=500, wrap=NONE)
        super().__init__(parent, *args, **kw)

        self._initted_value = False
        self._text_override = ''
        self._bg_color_orig = self['bg']

        self.insert(END, self._textvariable.get())
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {
                set result [uplevel [linsert $args 0 $widget_command]]
                if {([lindex $args 0] in {insert replace delete})} {
                    event generate $widget <<Change>> -when tail
                }
                return $result
            }
        ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

        def parent_event(sequence: str, *args_) -> str:
            if sequence in known_bindings:
                known_bindings[sequence](*args_)
            return 'break'

        self._textvariable.trace_add('unset', self._on_var_change)
        self._textvariable.trace_add('write', self._on_var_change)
        self.bind('<<Change>>', self._on_widget_change)
        self.bind('<<Paste>>', self._handle_paste)
        self.bind('<<Selection>>', self._handle_select)
        self.bind('<FocusIn>', self._handle_enter)
        self.bind('<FocusOut>', self._handle_exit)
        self.bind(BUT_RETURN, lambda e: parent_event(BUT_RETURN, e))
        self.bind(BUT_CTRL_BACKSPACE, self.on_event_ctrl_backspace)
        self.bind(BUT_CTRL_DELETE, self.on_event_ctrl_delete)
        self.bind(BUT_CTRL_SPACE, self.on_event_ctrl_space)

    def clear(self) -> None:
        self.delete(BEGIN, END)

    def is_type(self, check_type: Options) -> bool:
        return CVARS[check_type] == self._option_name

    @staticmethod
    def encoding_enabled() -> bool:
        return bool(int(getrootconf(Options.HIDE_PERSONAL_INFO)))

    def is_encoded(self) -> bool:
        return isinstance(self._textrealvariable, StringVar)

    def is_text_encoded(self) -> bool:
        assert self.is_encoded()
        return self._textvariable.get().count('*') == len(self._textvariable.get())

    def get_text_real(self) -> str:
        assert self.is_encoded()
        return self._textrealvariable.get()

    def get_text_encoded(self) -> str:
        assert self.is_encoded()
        return garble_text(self.get_text_real())

    def set_text_real(self) -> None:
        assert self.is_encoded()
        self.settext(self.get_text_real())

    def set_text_encoded(self) -> None:
        assert self.is_encoded()
        self.settext(self.get_text_encoded())

    def update_encoded_state(self) -> None:
        assert self.is_encoded()
        if self.encoding_enabled() and not is_focusing(self):
            self.set_text_encoded()
        else:
            self.set_text_real()

    def gettext(self) -> str:
        return self.get(BEGIN, f'{END}-1c')

    def settext(self, text: str, *args) -> None:
        my_text = text
        is_same = self.gettext() == my_text
        idx = int((self.index(INSERT) if is_focusing(self) else self.index(f'{END}-1c')).split('.')[1])
        self.clear()
        self.insert(BEGIN, my_text, *args)
        self._on_widget_change()
        if is_focusing(self):
            self.mark_set(INSERT, f'1.{idx - (1 - int(is_same)):d}')

    def select_all(self) -> None:
        end_index = f'{END}-1c'
        self.tag_add(SEL, BEGIN, end_index)
        self.mark_set(INSERT, self.index(end_index))

    def set_state(self, state: str) -> None:
        self.configure(bg=self._bg_color_orig if state == STATE_NORMAL else rootm().default_bg_color)

    def _handle_enter(self, *_) -> None:
        if self.is_encoded() and self.encoding_enabled():
            self.set_text_real()

    def _handle_exit(self, *_) -> None:
        if self.is_encoded() and self.encoding_enabled():
            self.set_text_encoded()

    def _handle_select(self, *_) -> None:
        sel = self.tag_ranges(SEL)
        if sel and float(str(sel[1])) >= 2.0:
            end_index = f'{END}-1c'
            self.tag_remove(SEL, end_index)
            self.tag_add(SEL, sel[0], end_index)
            self.mark_set(INSERT, end_index)

    def _handle_paste(self, *_) -> None:
        self._handle_paste_text(self.clipboard_get())

    def _handle_paste_text(self, pasted_text: str, force=False) -> None:
        cur_text = self.gettext()
        new_text = re_space_mult.sub(r' ', pasted_text.replace('\n', ' '))
        idx_adjust = len(new_text)
        sel = self.tag_ranges(SEL)
        if sel:
            idx = int(str(sel[0]).split('.')[1])
            idx2 = 999999 if float(str(sel[1])) >= 2.0 else int(str(sel[1]).split('.')[1])
        else:
            idx = idx2 = int(self.index(INSERT).split('.')[1])
        self._text_override = f'{cur_text[:idx]}{new_text}{cur_text[idx2:]}'
        if force:
            self._on_widget_change()
        self.after(1, lambda *_: self.mark_set(INSERT, f'1.{idx + idx_adjust:d}'))

    def _on_var_change(self, *_) -> None:
        my_text = self.gettext()
        var_text = self._textvariable.get()
        if my_text != var_text:
            self.settext(var_text)
        if self.is_encoded() and not self.is_text_encoded():
            self._textrealvariable.set(var_text)
        if self._initted_value is False:
            self._initted_value = True
            self.edit_reset()

    def _on_widget_change(self, *_) -> None:
        self._textvariable.set(
            self._text_override or
            (re_space_mult.sub(r' ', self.gettext().replace('\n', ' '))
             if getattr(self._textvariable, '_name', '') == CVARS[Options.TAGS] else self.gettext()))
        self._text_override = ''

    def on_event_ctrl_backspace(self, *_) -> None:
        if self.tag_ranges(SEL):
            return
        my_str = self.gettext()
        cur_idx = prev_idx = int(self.index(INSERT).split('.')[1])
        while prev_idx >= 1:
            prev_idx -= 1
            if prev_idx >= 1 and my_str[prev_idx] == my_str[prev_idx - 1]:
                continue
            if my_str[prev_idx] in self.CTRL_DELETION_DELIMS:
                if prev_idx == cur_idx - 1:
                    continue
                if my_str[prev_idx] != my_str[prev_idx + 1]:
                    prev_idx += 1
                break
        self.delete(f'1.{prev_idx + 1:d}', INSERT)

    def on_event_ctrl_delete(self, *_) -> None:
        if self.tag_ranges(SEL):
            return
        my_str = self.gettext()
        cur_idx = next_idx = int(self.index(INSERT).split('.')[1])
        end_idx = int(self.index(f'{END}-1c').split('.')[1]) - 1
        while next_idx < end_idx:
            next_idx += 1
            if next_idx < end_idx and my_str[next_idx] == my_str[next_idx + 1]:
                continue
            if my_str[next_idx] in self.CTRL_DELETION_DELIMS:
                if next_idx != cur_idx:
                    continue
                if my_str[next_idx] != my_str[next_idx - 1]:
                    next_idx -= 1
                break
        self.delete(INSERT, f'1.{next_idx:d}')

    def on_event_ctrl_space(self, *_) -> None:
        if int(getrootconf(Options.AUTOCOMPLETION_ENABLE)) == 0:
            return
        if self.tag_ranges(SEL):
            return
        my_str = self.gettext()
        cur_idx = int(self.index(INSERT).split('.')[1])
        end_idx = int(self.index(f'{END}-1c').split('.')[1]) - 1
        prev_idx = min(cur_idx, end_idx)
        while prev_idx > 0:
            if prev_idx != cur_idx and my_str[prev_idx] in ' ~' + '/\\' * self.is_type(Options.PATH):
                last_idx = min(end_idx, cur_idx)
                prev_idx = min(prev_idx + 1, last_idx)
                if prev_idx < last_idx and my_str[prev_idx] == '-':
                    prev_idx += 1
                break
            prev_idx -= 1
        atext = my_str[prev_idx:cur_idx]
        autocompletions = TagsDB.autocomplete_tag(ProcModule.name(), atext)
        if not autocompletions:
            return
        if len(autocompletions) == 1:
            if autocompletions[0][0]:
                self._handle_paste_text(autocompletions[0][0], True)
            return
        om = BaseMenu(self)
        for mtag, count in autocompletions:
            om.add_command(label=f'{atext}{mtag} ({count:d})', command=lambda t=mtag: self._handle_paste_text(t, True))
        om.tk_popup(self.winfo_rootx() + self.bbox(INSERT)[0], self.winfo_rooty() + self.bbox(INSERT)[1] + 18)


class BaseWindow:
    def __init__(self, parent, init_hidden=True) -> None:
        self.parent = parent
        self.window: Toplevel | None = None
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
    def __init__(self, parent, title: str, variables_count=1) -> None:
        self.title = title or ''
        self.but_ok: Button | None = None
        self.but_cancel: Button | None = None
        self._variables = [StringVar(parent) for _ in range(variables_count)]
        super().__init__(parent, False)

    def _set_variable(self, num: int, value: str) -> None:
        assert len(self._variables) <= num
        self._variables[num - 1].set(value)

    def get_variable(self, num: int) -> str:
        assert len(self._variables) <= num
        return self._variables[num - 1].get()

    def config(self) -> None:
        self.window.title(self.title)

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=12, pady=12, row=first_row())

        self._put_widgets(downframe)

        BaseFrame(downframe, height=16).grid(row=next_row(), columnspan=2)

        self.but_ok = Button(downframe, width=8, text='Ok', command=self.ok)
        self.but_cancel = Button(downframe, width=8, text='Cancel', command=self.cancel)
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
        self.window.resizable(False, False)
        self.window.focus_set()

        self.window.bind(BUT_ESCAPE, lambda _: self.cancel())
        self.window.bind(BUT_RETURN, lambda _: self.ok())

    def ok(self) -> None:
        self.window.grab_release()
        self.window.destroy()

    def cancel(self) -> None:
        self._set_variable(1, '')
        self.window.grab_release()
        self.window.destroy()

    @abstractmethod
    def _put_widgets(self, frame: BaseFrame) -> None:
        ...


class AskChecksWindow(AwaitableAskWindow):
    def __init__(self, parent, texts: Iterable[str]) -> None:
        self.texts = list(texts)
        self.checkbuttons: list[Checkbutton | None] = [None for _ in texts]
        super().__init__(parent, 'Options', variables_count=len(self.checkbuttons))

    def finalize(self) -> None:
        [self._set_variable(i + 1, '0') for i in range(len(self.checkbuttons))]
        AwaitableAskWindow.finalize(self)
        self.checkbuttons[0].focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.checkbuttons[0] = Checkbutton(frame, variable=self._variables[0], text=self.texts[0])
        self.checkbuttons[0].grid(row=first_row(), column=first_column(), padx=12, columnspan=2)
        for i in range(len(self.checkbuttons) - 1):
            n = i + 1
            self.checkbuttons[n] = Checkbutton(frame, variable=self._variables[n], text=self.texts[n])
            self.checkbuttons[n].grid(row=next_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> list[bool] | None:
        try:
            return [bool(int(self.get_variable(_ + 1))) for _ in range(len(self.checkbuttons))]
        except Exception:
            return None


class AskFileTypeFilterWindow(AwaitableAskWindow):
    VALUES = ['Media type', 'Extension']

    def __init__(self, parent) -> None:
        self.cbox: ttk.Combobox | None = None
        super().__init__(parent, 'File types')

    def finalize(self) -> None:
        self._set_variable(1, AskFileTypeFilterWindow.VALUES[0])
        AwaitableAskWindow.finalize(self)

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.cbox = ttk.Combobox(frame, values=AskFileTypeFilterWindow.VALUES, state=STATE_READONLY, width=18,
                                 textvariable=self._variables[0])
        self.cbox.grid(row=first_row(), column=first_column(), columnspan=2)

    def value(self) -> FileTypeFilter:
        try:
            # noinspection PyArgumentList
            return FileTypeFilter(AskFileTypeFilterWindow.VALUES.index(self.get_variable(1)) + 1)
        except Exception:
            return FileTypeFilter.INVALID


class AskFileSizeFilterWindow(AwaitableAskWindow):
    def __init__(self, parent) -> None:
        self.entry: BaseText | None = None
        super().__init__(parent, 'Size thresholds MB')

    def finalize(self) -> None:
        self._set_variable(1, '')
        AwaitableAskWindow.finalize(self)
        self.entry.focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.entry = BaseText(frame, width=18, textvariable=self._variables[0], bindings={BUT_RETURN: lambda _: self.ok()})
        self.entry.grid(row=first_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> list[float] | None:
        try:
            return [float(val) for val in re_ask_values.findall(self.get_variable(1))]
        except Exception:
            return None


class AskIntWindow(AwaitableAskWindow):
    def __init__(self, parent, validator: Callable[[int], bool], title='Enter number', *, default='') -> None:
        self.validator = validator
        self.entry: BaseText | None = None
        self.default = default
        super().__init__(parent, title)

    def finalize(self) -> None:
        self._set_variable(1, self.default)
        AwaitableAskWindow.finalize(self)
        self.entry.select_all()
        self.entry.focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.entry = BaseText(frame, width=18, textvariable=self._variables[0], bindings={BUT_RETURN: lambda _: self.ok()})
        self.entry.grid(row=first_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> int | None:
        try:
            val = int(self.get_variable(1))
            assert self.validator(val)
            return val
        except Exception:
            return None


class AskFileScoreFilterWindow(AwaitableAskWindow):
    def __init__(self, parent) -> None:
        self.entry: BaseText | None = None
        super().__init__(parent, 'Score thresholds')

    def finalize(self) -> None:
        self._set_variable(1, '')
        AwaitableAskWindow.finalize(self)
        self.entry.focus_set()

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.entry = BaseText(frame, width=18, textvariable=self._variables[0], bindings={BUT_RETURN: lambda _: self.ok()})
        self.entry.grid(row=first_row(), column=first_column(), padx=12, columnspan=2)

    def value(self) -> list[int] | None:
        try:
            return [int(val) for val in re_ask_values.findall(self.get_variable(1))]
        except Exception:
            return None


class AskFirstLastWindow(AwaitableAskWindow):
    VALUES = ('Keep first', 'Keep last')

    def __init__(self, parent, title='Enter number', *, default: LITERAL_TYPE_FIRST_LAST) -> None:
        self.cbox: ttk.Combobox | None = None
        self.default = default
        super().__init__(parent, title)

    def finalize(self) -> None:
        self._set_variable(1, AskFirstLastWindow.VALUES[0])
        AwaitableAskWindow.finalize(self)

    def _put_widgets(self, frame: BaseFrame) -> None:
        self.cbox = ttk.Combobox(frame, values=AskFirstLastWindow.VALUES, state=STATE_READONLY, width=25, textvariable=self._variables[0])
        self.cbox.grid(row=first_row(), column=first_column(), columnspan=2)

    def value(self) -> LITERAL_TYPE_FIRST_LAST:
        try:
            if AskFirstLastWindow.VALUES.index(self.get_variable(1)) == 0:
                return 'first'
            return 'last'
        except Exception:
            return self.default


class LogWindow(BaseWindow):
    log_window_base_height = 120

    def __init__(self, parent) -> None:
        self.text: Text | None = None
        self.scroll: Scrollbar | None = None
        self.firstshow = True
        super().__init__(parent)

    def append(self, text: str) -> None:
        # current scrollbar position
        self.scroll.update()  # required to get actual pos
        old_pos = self.scroll.get()

        # appending to text is impossible if text is disabled
        self.text.config(state=STATE_NORMAL)
        self.text.insert(END, text)
        self.text.config(state=STATE_DISABLED)

        # scroll to bottom if was at the bottom
        if old_pos[1] >= 1.0:
            self.text.mark_set(INSERT, END)
            self.text.see(END)
            self.text.yview_moveto(1.0)

    def config(self) -> None:
        self.window.title('Log')

        # elements
        upframe = BaseFrame(self.window, height=25)
        upframe.pack(side=TOP, fill=X)

        but_clear = Button(upframe, height=1, text='Clear log', command=self.clear)
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
        self.window.resizable(False, True)

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
        setrootconf(Options.ISLOGOPEN, self.visible)

    def clear(self) -> None:
        self.text.config(state=STATE_NORMAL)
        self.text.delete(1.0, END)
        self.text.config(state=STATE_DISABLED)

    def on_destroy(self) -> None:
        # just hide
        self.hide()
        setrootconf(Options.ISLOGOPEN, False)


class ProxyWindow(BaseWindow):
    def __init__(self, parent) -> None:
        self.ptype_var: StringVar | None = None
        self.entry_addr: BaseText | None = None
        self.but_ok: Button | None = None
        self.but_cancel: Button | None = None
        self.err_message: WidgetToolTip | None = None
        super().__init__(parent)

    def config(self) -> None:
        self.window.title('Proxy')

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=12, pady=12, row=1)

        proxyhint = Label(downframe, font=FONT_SANS_SMALL, text='for example: 101.100.100.10:65335')
        proxyhint.config(state=STATE_DISABLED)
        proxyhint.grid(row=0, column=0, columnspan=15)

        ptype_index = len(OPTION_VALUES_PROXYTYPE) - 1 if __RUXX_DEBUG__ else 0
        self.ptype_var = StringVar(rootm(), OPTION_VALUES_PROXYTYPE[ptype_index], CVARS[Options.PROXYTYPE])
        cbtype = ttk.Combobox(downframe, values=OPTION_VALUES_PROXYTYPE, state=STATE_READONLY, width=6,
                              textvariable=StringVar(rootm(), '', CVARS[Options.PROXYTYPE_TEMP]))
        cbtype.current(ptype_index)
        cbtype.grid(row=1, column=0, columnspan=5)
        cbtype.config(state=STATE_READONLY)
        _ = BaseText(textvariable=StringVar(rootm(), PROXY_DEFAULT_STR if __RUXX_DEBUG__ else '', CVARS[Options.PROXYSTRING]))
        self.entry_addr = BaseText(downframe, font=FONT_SANS_MEDIUM, width=21,
                                   textvariable=StringVar(rootm(), '', CVARS[Options.PROXYSTRING_TEMP]),
                                   bindings={BUT_RETURN: lambda _: self.ok()})
        if __RUXX_DEBUG__:
            self.entry_addr.insert(END, PROXY_DEFAULT_STR)
        self.err_message = attach_tooltip(self.entry_addr, TOOLTIP_INVALID_SYNTAX, 3000, timed=True)
        self.entry_addr.grid(row=1, column=5, columnspan=10)

        BaseFrame(downframe, height=16).grid(row=4, columnspan=15)

        self.but_ok = Button(downframe, width=8, text='Ok', command=self.ok)
        self.but_cancel = Button(downframe, width=8, text='Cancel', command=self.cancel)
        self.but_ok.grid(row=5, column=3, columnspan=5)
        self.but_cancel.grid(row=5, column=8, columnspan=5)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_reqwidth()) / 2
        y = self.parent.winfo_y() + 50
        self.window.geometry(f'+{x:.0f}+{y:.0f}')
        self.window.update()
        self.window.transient(self.parent)
        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(False, False)

        self.window.bind(BUT_RETURN, lambda _: self.ok())
        self.window.bind(BUT_ESCAPE, lambda _: self.cancel())
        self.window.bind(BUT_CTRL_A, lambda _: self.select_all())

    def select_all(self) -> None:
        if self.visible is True:
            self.entry_addr.focus_set()
            self.entry_addr.select_all()

    def ok(self) -> None:
        # Address validation
        newval = str(getrootconf(Options.PROXYSTRING_TEMP))

        # moved to cmdargs, wrapped here
        try:
            newval = valid_proxy(newval, False)
            adr_valid = True
        except Exception:
            adr_valid = False

        if not adr_valid:
            self.err_message.showtip()
        else:
            setrootconf(Options.PROXYSTRING, newval)
            setrootconf(Options.PROXYTYPE, getrootconf(Options.PROXYTYPE_TEMP))
            self.hide()

    def cancel(self) -> None:
        setrootconf(Options.PROXYSTRING_TEMP, str(getrootconf(Options.PROXYSTRING)))
        self.hide()

    def ask(self) -> None:
        if self.visible is False:
            self.show()
        self.select_all()

    def on_destroy(self) -> None:
        self.cancel()


class HeadersAndCookiesWindow(BaseWindow):
    MAX_COOKIES = 3
    MAX_HEADERS = 3
    LBOX_WIDTH = 65

    def __init__(self, parent) -> None:
        self.lbox_h: Listbox | None = None
        self.bdel_h: Button | None = None
        self.badd_h: Button | None = None
        self.entry_h: BaseText | None = None
        self.err_message_syntax_h: WidgetToolTip | None = None
        self.err_message_count_h: WidgetToolTip | None = None
        self.lbox_c: Listbox | None = None
        self.bdel_c: Button | None = None
        self.badd_c: Button | None = None
        self.entry_c: BaseText | None = None
        self.err_message_syntax_c: WidgetToolTip | None = None
        self.err_message_count_c: WidgetToolTip | None = None
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

        self.bdel_h = Button(hframe, image=get_icon(Icons.DELETE), command=self.delete_selected_h)
        self.bdel_h.pack(side=LEFT, padx=5, pady=5)
        attach_tooltip(self.bdel_h, TOOLTIP_HCOOKIE_DELETE)

        self.badd_h = Button(hframe, image=get_icon(Icons.ADD), command=self.add_header_to_list)
        self.badd_h.pack(side=LEFT, padx=0, pady=5)

        self.entry_h = BaseText(hframe, font=FONT_SANS_MEDIUM, textvariable=StringVar(rootm(), '', CVARS[Options.HEADER_ADD_STR]),
                                bindings={BUT_RETURN: lambda _: self.add_header_to_list()})
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

        self.bdel_c = Button(cframe, image=get_icon(Icons.DELETE), command=self.delete_selected_c)
        self.bdel_c.pack(side=LEFT, padx=5, pady=5)
        attach_tooltip(self.bdel_c, TOOLTIP_HCOOKIE_DELETE)

        self.badd_c = Button(cframe, image=get_icon(Icons.ADD), command=self.add_cookie_to_list)
        self.badd_c.pack(side=LEFT, padx=0, pady=5)

        self.entry_c = BaseText(cframe, font=FONT_SANS_MEDIUM, textvariable=StringVar(rootm(), '', CVARS[Options.COOKIE_ADD_STR]),
                                bindings={BUT_RETURN: lambda _: self.add_cookie_to_list()})
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
        self.lbox_h.insert(0, f'User-Agent:{USER_AGENT}')
        self.entry_h.settext('User-Agent:')
        self.entry_c.settext('cf_clearance:')

        # configure required width (needed if we change default useragent in the future)
        def get_maxlen(b: Listbox) -> int:
            return max(len(str(b.get(i))) for i in range(b.size())) if b.size() > 0 else 0

        maxlen = max(*(get_maxlen(lbox) for lbox in (self.lbox_h, self.lbox_c)), HeadersAndCookiesWindow.LBOX_WIDTH)
        self.lbox_h.configure(width=maxlen)
        self.lbox_c.configure(width=maxlen)

        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(False, False)

        self.window.bind(BUT_ESCAPE, lambda _: self.hide())
        self.lbox_h.bind(BUT_DELETE, lambda _: self.delete_selected_h())
        self.lbox_c.bind(BUT_DELETE, lambda _: self.delete_selected_c())
        # self.entry_h.bind(BUT_RETURN, lambda _: self.add_header_to_list())
        # self.entry_c.bind(BUT_RETURN, lambda _: self.add_coookie_to_list())

    def toggle_visibility(self) -> None:
        if self.visible is False:
            self.show()
            self.select_all_c()
        else:
            self.hide()

        setrootconf(Options.ISHCOOKIESOPEN, self.visible)

    @staticmethod
    def _listbox_to_json(lb: Listbox) -> dict[str, str]:
        ls: dict[str, str] = {}
        for i in range(lb.size()):
            part1, part2 = tuple(str(lb.get(i)).split(':', 1))
            ls.update({part1: part2})
        return ls

    @staticmethod
    def _listbox_to_json_s(lb: Listbox) -> str:
        return json.dumps(HeadersAndCookiesWindow._listbox_to_json(lb), skipkeys=True)

    def get_json_h(self) -> dict[str, str]:
        return self._listbox_to_json(self.lbox_h)

    def get_json_c(self) -> dict[str, str]:
        return self._listbox_to_json(self.lbox_c)

    def get_json_h_s(self) -> str:
        return self._listbox_to_json_s(self.lbox_h)

    def get_json_c_s(self) -> str:
        return self._listbox_to_json_s(self.lbox_c)

    def add_header_to_list(self) -> None:
        syntax_valid = True

        h_count = self.lbox_h.size()
        newval = str(getrootconf(Options.HEADER_ADD_STR))

        try:
            parts = re_json_entry_value.search(newval)
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
            self.entry_h.settext('User-Agent:')
            self.select_all_h()

    def delete_selected_h(self) -> None:
        if cur := self.lbox_h.curselection():
            i = self.lbox_h.index(cur)
            self.lbox_h.delete(cur)
            if self.lbox_h.size() != 0:
                self.lbox_h.selection_set(min(i, self.lbox_h.size() - 1))

    def select_all_h(self) -> None:
        if self.visible is True:
            self.entry_h.focus_set()
            self.entry_h.select_all()

    def add_cookie_to_list(self) -> None:
        syntax_valid = True

        c_count = self.lbox_c.size()
        newval = str(getrootconf(Options.COOKIE_ADD_STR))

        try:
            parts = re_json_entry_value.search(newval)
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
            self.entry_c.settext('cf_clearance:')
            self.select_all_c()

    def delete_selected_c(self) -> None:
        if cur := self.lbox_c.curselection():
            i = self.lbox_c.index(cur)
            self.lbox_c.delete(cur)
            if self.lbox_c.size() != 0:
                self.lbox_c.selection_set(min(i, self.lbox_c.size() - 1))

    def select_all_c(self) -> None:
        if self.visible is True:
            self.entry_c.focus_set()
            self.entry_c.select_all()

    def set_headers(self, json_h: dict) -> None:
        if self.lbox_h.size() > 0:
            self.lbox_h.delete(0, END)
        newvals = json_h
        for k, v in newvals.items():
            self.lbox_h.insert(END, f'{k!s}:{v!s}')

    def set_cookies(self, json_c: dict) -> None:
        if self.lbox_c.size() > 0:
            self.lbox_c.delete(0, END)
        newvals = json_c
        for k, v in newvals.items():
            self.lbox_c.insert(END, f'{k!s}:{v!s}')

    def set_headers_s(self, json_h: str) -> None:
        if self.lbox_h.size() > 0:
            self.lbox_h.delete(0, END)
        newvals = json.loads(json_h)
        for k, v in newvals.items():
            self.lbox_h.insert(END, f'{k!s}:{v!s}')

    def set_cookies_s(self, json_c: str) -> None:
        if self.lbox_c.size() > 0:
            self.lbox_c.delete(0, END)
        newvals = json.loads(json_c)
        for k, v in newvals.items():
            self.lbox_c.insert(END, f'{k!s}:{v!s}')

    def on_destroy(self) -> None:
        self.hide()
        setrootconf(Options.ISHCOOKIESOPEN, False)


class ConnectRequestIntWindow(BaseWindow):
    def __init__(self, parent, conf_open: Options, conf_str: Options, conf_str_temp: Options,
                 title: str, hint: str, baseval: int, minmax: tuple[int, int]) -> None:
        self.title = title
        self.hint = hint
        self.baseval = baseval
        self.minmax = minmax
        self.conf_open, self.conf_str, self.conf_str_temp = conf_open, conf_str, conf_str_temp
        self.var: IntVar | None = None
        self.entry: BaseText | None = None
        self.but_ok: Button | None = None
        self.but_cancel: Button | None = None
        self.err_message: WidgetToolTip | None = None
        super().__init__(parent)

    def config(self) -> None:
        self.window.title(self.title)

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=12, pady=12, row=1)

        hint = Label(downframe, font=FONT_SANS_SMALL, text=self.hint)
        hint.config(state=STATE_DISABLED)
        hint.grid(row=0, column=0, columnspan=15)

        _ = BaseText(textvariable=StringVar(rootm(), str(self.baseval), CVARS[self.conf_str]))
        self.entry = BaseText(downframe, font=FONT_SANS_MEDIUM, width=19,
                              textvariable=StringVar(rootm(), '', CVARS[self.conf_str_temp]),
                              bindings={BUT_RETURN: lambda _: self.ok()})
        self.entry.insert(END, str(self.baseval))
        self.err_message = attach_tooltip(self.entry, TOOLTIP_INVALID_SYNTAX, 3000, timed=True)
        self.entry.grid(row=1, column=3, columnspan=10)

        BaseFrame(downframe, height=16).grid(row=4, columnspan=15)

        self.but_ok = Button(downframe, width=8, text='Ok', command=self.ok)
        self.but_cancel = Button(downframe, width=8, text='Cancel', command=self.cancel)
        self.but_ok.grid(row=5, column=3, columnspan=5)
        self.but_cancel.grid(row=5, column=8, columnspan=5)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_reqwidth()) / 2
        y = self.parent.winfo_y() + 50
        self.window.geometry(f'+{x:.0f}+{y:.0f}')
        self.window.update()
        self.window.transient(self.parent)
        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(False, False)
        self.window.bind(BUT_RETURN, lambda _: self.ok())
        self.window.bind(BUT_ESCAPE, lambda _: self.cancel())
        self.window.bind(BUT_CTRL_A, lambda _: self.select_all())

    def select_all(self) -> None:
        if self.visible is True:
            self.entry.focus_set()
            self.entry.select_all()

    def ok(self) -> None:
        try:
            # Value validation
            newval = str(getrootconf(self.conf_str_temp))
            newval = str(valid_positive_int(newval, lb=self.minmax[0], ub=self.minmax[1]))
            setrootconf(self.conf_str, newval)
            self.hide()
        except Exception:
            self.err_message.showtip()

    def cancel(self) -> None:
        setrootconf(self.conf_str_temp, str(getrootconf(self.conf_str)))
        self.hide()

    def ask(self) -> None:
        if self.visible is False:
            self.show()
            self.select_all()

    def on_destroy(self) -> None:
        self.cancel()


class ConnectionTimeoutWindow(ConnectRequestIntWindow):
    def __init__(self, parent) -> None:
        super().__init__(parent, Options.ISTIMEOUTOPEN, Options.TIMEOUTSTRING, Options.TIMEOUTSTRING_TEMP,
                         'Timeout', '3 .. 300, in seconds', CONNECT_TIMEOUT_BASE, (3, 300))


class ConnectionRetriesWindow(ConnectRequestIntWindow):
    def __init__(self, parent) -> None:
        super().__init__(parent, Options.ISRETRIESOPEN, Options.RETRIESSTRING, Options.RETRIESSTRING_TEMP,
                         'Retries', '5 .. inf.', CONNECT_RETRIES_BASE, (5, 2**63))


class APIRequestStrIntWindow(BaseWindow):
    def __init__(self, parent, title: str, hint1: str, hint2: str, baseval: tuple[str, str],
                 conf_str1: Options, conf_str2: Options, conf_str_temp1: Options, conf_str_temp2: Options) -> None:
        self.title = title
        self.hint1 = hint1
        self.hint2 = hint2
        self.baseval = baseval
        self.conf_str1, self.conf_str2 = conf_str1, conf_str2
        self.conf_str_temp1, self.conf_str_temp2 = conf_str_temp1, conf_str_temp2
        self.var: IntVar | None = None
        self.entry1: BaseText | None = None
        self.entry2: BaseText | None = None
        self.but_ok: Button | None = None
        self.but_cancel: Button | None = None
        self.err_message: WidgetToolTip | None = None
        super().__init__(parent)

    def config(self) -> None:
        self.window.title(self.title)

        upframe = BaseFrame(self.window)
        upframe.pack()

        downframe = BaseFrame(upframe)
        downframe.grid(padx=12, pady=12, row=1)

        hint1 = Label(downframe, font=FONT_SANS_SMALL, text=self.hint1)
        hint1.config(state=STATE_DISABLED)
        hint1.grid(row=0, column=0, columnspan=15)
        _ = BaseText(textvariable=StringVar(rootm(), str(self.baseval[0]), CVARS[self.conf_str1]))
        self.entry1 = BaseText(downframe, font=FONT_SANS_MEDIUM, width=38,
                               textvariable=StringVar(rootm(), '', CVARS[self.conf_str_temp1]),
                               bindings={BUT_RETURN: lambda _: self.ok()})
        self.entry1.insert(END, str(self.baseval[0]))
        self.err_message = attach_tooltip(self.entry1, TOOLTIP_INVALID_SYNTAX, 3000, timed=True)
        self.entry1.grid(row=1, column=3, columnspan=10)

        hint2 = Label(downframe, font=FONT_SANS_SMALL, text=self.hint2)
        hint2.config(state=STATE_DISABLED)
        hint2.grid(row=3, column=0, columnspan=15)
        _ = BaseText(textvariable=StringVar(rootm(), str(self.baseval[1]), CVARS[self.conf_str2]))
        self.entry2 = BaseText(downframe, font=FONT_SANS_MEDIUM, width=19,
                               textvariable=StringVar(rootm(), '', CVARS[self.conf_str_temp2]),
                               bindings={BUT_RETURN: lambda _: self.ok()})
        self.entry2.insert(END, str(self.baseval[1]))
        self.err_message = attach_tooltip(self.entry2, TOOLTIP_INVALID_SYNTAX, 3000, timed=True)
        self.entry2.grid(row=4, column=3, columnspan=10)

        BaseFrame(downframe, height=16).grid(row=5, columnspan=15)

        self.but_ok = Button(downframe, width=8, text='Ok', command=self.ok)
        self.but_cancel = Button(downframe, width=8, text='Cancel', command=self.cancel)
        self.but_ok.grid(row=6, column=3, columnspan=5)
        self.but_cancel.grid(row=6, column=8, columnspan=5)

        self.window.config(bg=self.parent.default_bg_color)

    def finalize(self) -> None:
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_reqwidth()) / 2
        y = self.parent.winfo_y() + 50
        self.window.geometry(f'+{x:.0f}+{y:.0f}')
        self.window.update()
        self.window.transient(self.parent)
        self.window.minsize(self.window.winfo_reqwidth(), self.window.winfo_reqheight())
        self.window.resizable(False, False)
        self.window.bind(BUT_RETURN, lambda _: self.ok())
        self.window.bind(BUT_ESCAPE, lambda _: self.cancel())
        self.window.bind(BUT_CTRL_A, lambda _: self.select_all())

    def select_all(self) -> None:
        if self.visible is True:
            self.entry1.focus_set()
            self.entry1.select_all()

    def ok(self) -> None:
        try:
            # Value validation
            key = str(getrootconf(self.conf_str_temp1))
            user_id = str(getrootconf(self.conf_str_temp2))
            _ = str(valid_api_key(f'{key},{user_id}'))
            setrootconf(self.conf_str1, key)
            setrootconf(self.conf_str2, user_id)
            self.hide()
        except Exception:
            self.err_message.showtip()

    def cancel(self) -> None:
        setrootconf(self.conf_str_temp1, str(getrootconf(self.conf_str1)))
        setrootconf(self.conf_str_temp2, str(getrootconf(self.conf_str2)))
        self.hide()

    def ask(self) -> None:
        if self.visible is False:
            self.show()
            self.select_all()

    def on_destroy(self) -> None:
        self.cancel()


class ApiKeyWindow(APIRequestStrIntWindow):
    def __init__(self, parent) -> None:
        super().__init__(parent, 'API Key', f'Key ({API_KEY_LEN_RX:d} symbols)', 'User ID (number)', ('', ''),
                         Options.APIKEY_KEY, Options.APIKEY_USERID, Options.APIKEY_KEY_TEMP, Options.APIKEY_USERID_TEMP)


def init_additional_windows() -> None:
    global window_log
    global window_proxy
    global window_hcookies
    global window_timeout
    global window_retries
    global window_apikey
    window_log = LogWindow(root)
    window_log.window.wm_protocol('WM_DELETE_WINDOW', window_log.on_destroy)
    window_proxy = ProxyWindow(root)
    window_proxy.window.wm_protocol('WM_DELETE_WINDOW', window_proxy.on_destroy)
    window_hcookies = HeadersAndCookiesWindow(root)
    window_hcookies.window.wm_protocol('WM_DELETE_WINDOW', window_hcookies.on_destroy)
    window_timeout = ConnectionTimeoutWindow(root)
    window_timeout.window.wm_protocol('WM_DELETE_WINDOW', window_timeout.on_destroy)
    window_retries = ConnectionRetriesWindow(root)
    window_retries.window.wm_protocol('WM_DELETE_WINDOW', window_retries.on_destroy)
    window_apikey = ApiKeyWindow(root)
    window_apikey.window.wm_protocol('WM_DELETE_WINDOW', window_apikey.on_destroy)


def register_menu(label: str, menu_id: Menus = None) -> Menu:
    global c_menu
    menu = BaseMenu(rootMenu)
    # register in global container for later
    if menu_id and menu_id in menu_items:
        menu_items[menu_id].menu = menu
    root_menum().add_cascade(menu=menu, label=label)
    c_menu = menu
    return menu


def register_submenu(label: str) -> Menu:
    global c_submenu
    submenu = BaseMenu(rootMenu)
    c_menum().add_cascade(menu=submenu, label=label)
    c_submenu = submenu
    return submenu


def getrootconf(index: Options) -> int | str:
    return rootm().getvar(CVARS[index])


def setrootconf(index: Options, value: int | str | bool) -> None:
    return rootm().setvar(CVARS[index], value)


def rootm() -> AppRoot:
    assert root is not None
    return root


def root_framem() -> BaseFrame:
    assert rootFrame is not None
    return rootFrame


def root_menum() -> Menu:
    assert rootMenu is not None
    return rootMenu


def c_menum() -> BaseMenu:
    assert c_menu is not None
    return c_menu


def c_submenum() -> BaseMenu:
    assert c_submenu is not None
    return c_submenu


def window_logm() -> LogWindow:
    assert window_log is not None
    return window_log


def window_proxym() -> ProxyWindow:
    assert window_proxy is not None
    return window_proxy


def window_hcookiesm() -> HeadersAndCookiesWindow:
    assert window_hcookies is not None
    return window_hcookies


def window_timeoutm() -> ConnectionTimeoutWindow:
    assert window_timeout is not None
    return window_timeout


def window_retriesm() -> ConnectionRetriesWindow:
    assert window_retries is not None
    return window_retries


def window_apikeym() -> ApiKeyWindow:
    assert window_apikey is not None
    return window_apikey


def text_cmdm() -> Text:
    assert text_cmd is not None
    return text_cmd


# noinspection PyPep8Naming
def CreateRoot() -> None:
    global root
    assert root is None
    root = AppRoot()


# noinspection PyPep8Naming
def GetRoot() -> AppRoot | None:
    return root


def create_base_window_widgets() -> None:
    global text_cmd

    CreateRoot()

    # icons
    icons[Icons.RUXX] = PhotoImage(data=base64.b64decode(IMG_PROC_RUXX_DATA))
    icons[Icons.RS] = PhotoImage(data=base64.b64decode(IMG_PROC_RS_DATA))
    icons[Icons.RN] = PhotoImage(data=base64.b64decode(IMG_PROC_RN_DATA))
    icons[Icons.RP] = PhotoImage(data=base64.b64decode(IMG_PROC_RP_DATA))
    icons[Icons.EN] = PhotoImage(data=base64.b64decode(IMG_PROC_EN_DATA))
    icons[Icons.XB] = PhotoImage(data=base64.b64decode(IMG_PROC_XB_DATA))
    icons[Icons.BB] = PhotoImage(data=base64.b64decode(IMG_PROC_BB_DATA))
    icons[Icons.RX] = PhotoImage(data=base64.b64decode(IMG_PROC_RX_DATA))
    icons[Icons.OPEN] = PhotoImage(data=base64.b64decode(IMG_OPEN_DATA))
    icons[Icons.SAVE] = PhotoImage(data=base64.b64decode(IMG_SAVE_DATA))
    icons[Icons.DELETE] = PhotoImage(data=base64.b64decode(IMG_DELETE_DATA))
    icons[Icons.ADD] = PhotoImage(data=base64.b64decode(IMG_ADD_DATA))
    icons[Icons.TEXT] = PhotoImage(data=base64.b64decode(IMG_TEXT_DATA))  # unused

    rootm().iconphoto(True, get_icon(Icons.RUXX))

    # validators
    string_vars[CVARS[Options.LASTPATH]] = StringVar(rootm(), '', CVARS[Options.LASTPATH])
    string_vars[CVARS[Options.TAGLISTS_PATH]] = StringVar(rootm(), '', CVARS[Options.TAGLISTS_PATH])

    # Options #
    opframe_main = ttk.LabelFrame(root_framem(), text='Download options')
    opframe_main.grid(row=cur_row(), column=cur_column(), rowspan=1, columnspan=COLUMNSPAN_MAX,
                      sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    #  Videos
    opframe_vid = ttk.LabelFrame(opframe_main, text='Videos')
    opframe_vid.grid(row=cur_row(), column=cur_column(), rowspan=1, columnspan=1,
                     sticky=STICKY_HORIZONTAL, padx=1, pady=0, ipadx=0)
    op_vid = ttk.Combobox(opframe_vid, values=OPTION_VALUES_VIDEOS, state=STATE_READONLY, width=14 if IS_WIN else 12,
                          textvariable=StringVar(rootm(), '', CVARS[Options.VIDSETTING]))
    register_global(Globals.COMBOBOX_VIDEOS, op_vid)
    attach_tooltip(op_vid, TOOLTIP_VIDEOS)
    op_vid.current(3)
    op_vid.pack(padx=1, pady=3)
    #  Images
    opframe_img = ttk.LabelFrame(opframe_main, text='Images')
    opframe_img.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                     sticky=STICKY_HORIZONTAL, padx=1, pady=0, ipadx=0)
    op_img = ttk.Combobox(opframe_img, values=OPTION_VALUES_IMAGES, state=STATE_READONLY, width=14 if IS_WIN else 12,
                          textvariable=StringVar(rootm(), '', CVARS[Options.IMGSETTING]))
    register_global(Globals.COMBOBOX_IMAGES, op_img)
    attach_tooltip(op_img, TOOLTIP_IMAGES)
    op_img.current(len(OPTION_VALUES_IMAGES) - 1)
    op_img.pack(padx=1, pady=3)
    #  Date min
    opframe_datemin = ttk.LabelFrame(opframe_main, text='Date min')
    opframe_datemin.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                         sticky=STICKY_HORIZONTAL, padx=1, pady=PADDING_DEFAULT, ipadx=0)
    op_datemin_t = BaseText(opframe_datemin, width=10, textvariable=StringVar(rootm(), '', CVARS[Options.DATEMIN]))
    register_global(Globals.FIELD_DATEMIN, op_datemin_t)
    op_datemin_t.insert(END, DATE_MIN_DEFAULT)
    op_datemin_t.pack(padx=1, pady=PADDING_DEFAULT * (1.5 if IS_WIN else 1))
    attach_tooltip(op_datemin_t, TOOLTIP_DATE)
    #  Date max
    opframe_datemax = ttk.LabelFrame(opframe_main, text='Date max')
    opframe_datemax.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                         sticky=STICKY_HORIZONTAL, padx=1, pady=PADDING_DEFAULT, ipadx=0)
    op_datemax_t = BaseText(opframe_datemax, width=10, textvariable=StringVar(rootm(), '', CVARS[Options.DATEMAX]))
    register_global(Globals.FIELD_DATEMAX, op_datemax_t)
    op_datemax_t.insert(END, DATE_MAX_DEFAULT)
    op_datemax_t.pack(padx=1, pady=PADDING_DEFAULT * (1.5 if IS_WIN else 1))
    attach_tooltip(op_datemax_t, TOOLTIP_DATE)
    #  Parent posts / child posts
    opframe_parch = ttk.LabelFrame(opframe_main, text='Parent posts / child posts')
    opframe_parch.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                       sticky=STICKY_HORIZONTAL, padx=1, pady=0, ipadx=0)
    op_parch = ttk.Combobox(opframe_parch, values=OPTION_VALUES_PARCHI, state=STATE_READONLY, width=21 if IS_WIN else 18,
                            textvariable=StringVar(rootm(), '', CVARS[Options.PARCHISETTING]))
    register_global(Globals.COMBOBOX_PARCHI, op_parch)
    attach_tooltip(op_parch, TOOLTIP_PARCHI)
    op_parch.current(len(OPTION_VALUES_PARCHI) - 2)
    op_parch.pack(padx=1, pady=3)
    #  Threading
    opframe_thread = ttk.LabelFrame(opframe_main, text='Threading')
    opframe_thread.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                        sticky=STICKY_HORIZONTAL, padx=1, pady=0, ipadx=0)
    op_thread = ttk.Combobox(opframe_thread, values=OPTION_VALUES_THREADING, state=STATE_READONLY, width=9,
                             textvariable=StringVar(rootm(), '', CVARS[Options.THREADSETTING]))
    register_global(Globals.COMBOBOX_THREADING, op_thread)
    attach_tooltip(op_thread, TOOLTIP_THREADING)
    op_thread.current(len(OPTION_VALUES_THREADING) - 1)
    op_thread.pack(padx=1, pady=3)
    #  Download order
    opframe_dorder = ttk.LabelFrame(opframe_main, text='Download order')
    opframe_dorder.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=1,
                        sticky=STICKY_HORIZONTAL, padx=1, pady=0, ipadx=0)
    op_dorder = ttk.Combobox(opframe_dorder, values=OPTION_VALUES_DOWNLOAD_ORDER, state=STATE_READONLY, width=13 if IS_WIN else 12,
                             textvariable=StringVar(rootm(), '', CVARS[Options.DOWNLOAD_ORDER]))
    register_global(Globals.COMBOBOX_DOWNLOAD_ORDER, op_dorder)
    attach_tooltip(op_dorder, TOOLTIP_DOWNLOAD_ORDER)
    op_dorder.current(0)
    op_dorder.pack(padx=1, pady=3)
    #  Download limit
    opframe_dlimit = ttk.LabelFrame(opframe_main, text='Posts limit')
    opframe_dlimit.grid(row=cur_row(), column=next_column(), rowspan=1, columnspan=COLUMNSPAN_MAX - 7,
                        sticky=STICKY_HORIZONTAL, padx=1, pady=0, ipadx=0)
    op_dlimit = Entry(opframe_dlimit, width=0, textvariable=StringVar(rootm(), '', CVARS[Options.DOWNLOAD_LIMIT]), justify='center')
    register_global(Globals.FIELD_DOWNLOAD_LIMIT, op_dlimit)
    op_dlimit.pack(expand=NO, fill=X, padx=1, pady=3)
    attach_tooltip(op_dlimit, TOOLTIP_DOWNLOAD_LIMIT)

    # Tags #
    opframe_tags = ttk.LabelFrame(root_framem(), text='Tags')
    opframe_tags.grid(row=next_row(), column=first_column(), columnspan=COLUMNSPAN_MAX,
                      sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=PADDING_DEFAULT)
    #  Text
    op_tagsstr = BaseText(opframe_tags, width=0, font=FONT_LUCIDA_MEDIUM,
                          textvariable=StringVar(rootm(), 'sfw', CVARS[Options.TAGS]))
    register_global(Globals.FIELD_TAGS, op_tagsstr)
    op_tagsstr.pack(padx=2, pady=3, expand=YES, side=LEFT, fill=X)
    #  Button check
    op_tagsbutcheck = Button(opframe_tags, text='check')
    register_global(Globals.BUTTON_CHECKTAGS, op_tagsbutcheck)
    op_tagsbutcheck.pack(padx=2, pady=3, expand=NO, side=LEFT)
    attach_tooltip(op_tagsbutcheck, TOOLTIP_TAGS_CHECK)
    #  Button clear
    op_tagsbutclear = Button(opframe_tags, text='clear', command=lambda: setrootconf(Options.TAGS, ''))
    register_global(Globals.BUTTON_CLEARTAGS, op_tagsbutclear)
    op_tagsbutclear.pack(padx=2, pady=3, expand=NO, side=LEFT)

    # Path #
    opframe_path = ttk.LabelFrame(root_framem(), text='Path')
    opframe_path.grid(row=next_row(), column=first_column(), columnspan=COLUMNSPAN_MAX,
                      sticky=STICKY_HORIZONTAL, padx=PADDING_DEFAULT, pady=0)
    #  Text
    op_pathstr = BaseText(opframe_path, width=0, font=FONT_LUCIDA_MEDIUM, textvariable=StringVar(rootm(), '', CVARS[Options.PATH_VISUAL]),
                          encodevariable=StringVar(rootm(), '', CVARS[Options.PATH]))
    register_global(Globals.FIELD_PATH, op_pathstr)
    op_pathstr.insert(END, normalize_path(os.path.abspath(os.curdir), False))
    op_pathstr.pack(padx=2, pady=3, expand=YES, side=LEFT, fill=X)
    #  Button open
    op_pathbut = Button(opframe_path, image=get_icon(Icons.OPEN))
    register_global(Globals.BUTTON_OPENFOLDER, op_pathbut)
    op_pathbut.pack(padx=2, pady=3, expand=NO, side=RIGHT)

    # Cmdline and _download button #
    #  Cmdline  #
    #   Note: global (not registered)
    text_cmd = Text(root_framem(), font=FONT_SANS_SMALL, relief=SUNKEN, bd=0, bg=rootm().default_bg_color, height=3, width=0)
    text_cmdm().grid(row=next_row(), column=first_column(), columnspan=COLUMNSPAN_MAX - 1, rowspan=ROWSPAN_MAX,
                     sticky=STICKY_ALLDIRECTIONS, padx=PADDING_DEFAULT * 2, pady=PADDING_DEFAULT)
    #  Button _download  #
    dw_but = Button(root_framem(), text='Download', width=10, font=FONT_SANS_MEDIUM)
    dw_but.grid(row=cur_row(), column=GLOBAL_COLUMNCOUNT - 1, columnspan=1, rowspan=ROWSPAN_MAX,
                sticky=STICKY_ALLDIRECTIONS, padx=PADDING_DEFAULT * 3 - 1, pady=PADDING_DEFAULT * 2)
    register_global(Globals.BUTTON_DOWNLOAD, dw_but)

    # This one is after root_frame
    pb1 = ttk.Progressbar(rootm(), value=0, maximum=PROGRESS_BAR_MAX, mode='determinate', orient=HORIZONTAL,
                          variable=IntVar(rootm(), 0, CVARS[Options.PROGRESS]))
    pb1.pack(fill=X, expand=NO, anchor=S, pady=0, padx=0)

    # This one is after progressbar
    sb_frame = BaseFrame(rootm())
    sb_frame.pack(fill=X, expand=NO, anchor=S)

    ib1 = Label(sb_frame, borderwidth=1, relief=FLAT, anchor=W, image=get_icon(Icons.RX))
    ib1.pack(expand=NO, side=LEFT)
    register_global(Globals.MODULE_ICON, ib1)
    attach_tooltip(ib1, lambda: [get_cur_module_sitename()], relief=FLAT)

    sb1 = Label(sb_frame, borderwidth=1, relief=SUNKEN, anchor=W, text='Ready', bg=COLOR_DARKGRAY,
                textvariable=StringVar(rootm(), '', CVARS[Options.STATUS]))
    sb1.pack(fill=X, expand=NO)

    # Safety precautions
    if len(gobjects) < int(Globals.MAX_GOBJECTS):
        messagebox.showinfo('', 'Not all GOBJECTS were registered')


def get_global(index: Globals) -> Text | BaseText | Button:
    return gobjects[index]


def config_global(index: Globals, **kwargs) -> None:
    get_global(index).config(kwargs)


def is_global_disabled(index: Globals) -> bool:
    return str(get_global(index).cget('state')) == STATE_DISABLED


def config_menu(menu: Menus, submenu: SubMenus, **kwargs) -> None:
    if gmenu := menu_items.get(menu):
        gmenu.menu.entryconfigure(submenu.value, **kwargs)


def is_menu_disabled(menu: Menus, submenu: SubMenus) -> bool:
    if gmenu := menu_items.get(menu):
        if submenu in gmenu.statefuls:
            return gmenu.menu.entrycget(submenu.value, 'state') == STATE_DISABLED
    return False


def is_focusing(glob: Globals | Widget) -> bool:
    try:
        return rootm().focus_get() == (get_global(glob) if isinstance(glob, Globals) else glob)
    except Exception:
        return False


def toggle_console() -> None:
    global console_shown
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), not console_shown)
    console_shown = not console_shown


def hotkey_text(option: Options) -> str:
    return (hotkeys[option].strip('<>').replace('-', '+').upper()
            .replace('CONTROL', 'Ctrl').replace('SHIFT', 'Shift')
            .replace('ALT', 'Alt').replace('SPACE', 'Space'))


def get_curdir(prioritize_last_path=True) -> str:
    lastloc = str(getrootconf(Options.LASTPATH))
    curloc = str(getrootconf(Options.PATH))
    if prioritize_last_path:
        return lastloc if len(lastloc) > 0 else curloc if os.path.isdir(curloc) else os.path.abspath(os.curdir)
    else:
        return curloc if os.path.isdir(curloc) else lastloc if len(lastloc) > 0 else os.path.abspath(os.curdir)


def get_cur_module_sitename() -> str:
    if int(getrootconf(Options.REVEALNAMES)) == 0:
        return ProcModule.name().upper()
    return ((base64.b64decode(SITENAMES_PER_PROC_MODULE.get(ProcModule.value(), '')) or b'UNK/').decode()[:-1]
            .replace('https://', '').replace('api.', ''))


# def unfocus_buttons() -> None:
#     unfocus_buttons_once()
#     rootm().after(GUI2_UPDATE_DELAY_DEFAULT // 3, unfocus_buttons)


def unfocus_buttons_once() -> None:
    for g in BUTTONS_TO_UNFOCUS:
        if is_focusing(g):
            rootm().focus_set()
            break


def help_tags(title='Tags') -> None:
    messagebox.showinfo(title=title, message=HELP_TAGS_PER_PROC_MODULE[ProcModule.value()], icon='info')


def help_about(title=f'About {APP_NAME}', message=ABOUT_MSG, icon='info') -> None:
    messagebox.showinfo(title=title, message=message, icon=icon)


def load_id_list() -> None:
    if filepath := ask_filename((('Text files', '*.txt'), ('All files', '*.*'))):
        success, file_tags = prepare_id_list(filepath)
        if success:
            setrootconf(Options.TAGS, file_tags)
            # reset settings for immediate downloading
            setrootconf(Options.DATEMIN, DATE_MIN_DEFAULT)
            setrootconf(Options.DATEMAX, DATE_MAX_DEFAULT)
        else:
            messagebox.showwarning(message=f'Unable to load ids from {filepath[filepath.rfind("/") + 1:]}!')


def load_batch_download_tag_list() -> list[str]:
    if filepath := ask_filename((('Text files', '*.txt'), ('All files', '*.*'))):
        success, file_tag_lists = prepare_tag_lists(filepath)
        if success:
            return file_tag_lists
        else:
            messagebox.showwarning(message=f'Unable to load tags from {filepath[filepath.rfind("/") + 1:]}!')
    return []


def ask_filename(ftypes: Iterable[tuple[str, str]]) -> str:
    if fullpath := filedialog.askopenfilename(filetypes=ftypes, initialdir=get_curdir()):
        setrootconf(Options.LASTPATH, fullpath[:normalize_path(fullpath, False).rfind(SLASH) + 1])  # not bound
        return fullpath
    return ''


def browse_path() -> None:
    if loc := filedialog.askdirectory(initialdir=get_curdir()):
        setrootconf(Options.PATH, loc)
        setrootconf(Options.LASTPATH, loc[:normalize_path(loc, False).rfind(SLASH) + 1])  # not bound
        update_garbled_text_states()


def update_garbled_text_states() -> None:
    get_global(Globals.FIELD_PATH).update_encoded_state()


def register_menu_command(label: str, command: Callable[[], None], hotkey_opt: Options = None, do_bind=False,
                          icon: PhotoImage | None = None) -> None:
    try:
        accelerator = hotkey_text(hotkey_opt)
    except Exception:
        accelerator = None
    c_menum().add_command(label=label, image=icon, compound=LEFT, command=command, accelerator=accelerator)
    if accelerator and do_bind:
        rootm().bind(hotkeys[hotkey_opt], func=lambda _: command())


def register_submenu_command(label: str, command: Callable[[], None], hotkey_opt: Options = None, do_bind=False,
                             icon: PhotoImage | None = None) -> None:
    try:
        accelerator = hotkey_text(hotkey_opt)
    except Exception:
        accelerator = None
    c_submenum().add_command(label=label, image=icon, compound=LEFT, command=command, accelerator=accelerator)
    if accelerator and do_bind:
        rootm().bind(hotkeys[hotkey_opt], func=lambda _: command())


def register_menu_checkbutton(label: str, varname: str,
                              command: Callable[[], None] | None = None, hotkey: str | None = None) -> None:
    if varname not in bool_vars:
        bool_vars[varname] = BooleanVar(rootm(), False, name=varname)  # needed so it won't be discarded
    c_menum().add_checkbutton(label=label, command=command, variable=bool_vars[varname], accelerator=hotkey)


def register_menu_radiobutton(label: str, varname: str, value: int,
                              command: Callable[[], None] | None = None, hotkey: str | None = None) -> None:
    if varname not in int_vars:
        int_vars[varname] = IntVar(rootm(), value=value, name=varname)  # needed so it won't be discarded
    c_menum().add_radiobutton(label=label, command=command, variable=int_vars[varname], value=value, accelerator=hotkey)


def register_submenu_radiobutton(label: str, varname: str, value: int,
                                 command: Callable[[], None] | None = None, hotkey: str | None = None) -> None:
    if varname not in int_vars:
        int_vars[varname] = IntVar(rootm(), value=value, name=varname)  # needed so it won't be discarded
    c_submenum().add_radiobutton(label=label, command=command, variable=int_vars[varname], value=value, accelerator=hotkey)


def register_menu_separator() -> None:
    c_menum().add_separator()


def get_all_media_files_in_cur_dir() -> tuple[str]:
    return filedialog.askopenfilenames(initialdir=get_curdir(), filetypes=(('All supported', KNOWN_EXTENSIONS_STR),))


def get_media_files_dir() -> str:
    return str(filedialog.askdirectory(initialdir=get_curdir(), mustexist=True))


def update_lastpath(filefullpath: str) -> None:
    setrootconf(Options.LASTPATH, filefullpath[:normalize_path(filefullpath, False).rfind(SLASH) + 1])


def toggle_autocompletion() -> None:
    # current state is AFTER being toggled
    if bool(int(getrootconf(Options.AUTOCOMPLETION_ENABLE))):
        last_path = str(getrootconf(Options.TAGLISTS_PATH)) or get_curdir()
        if TagsDB.try_set_basepath(last_path):
            setrootconf(Options.TAGLISTS_PATH, last_path)
        else:
            loc = str(filedialog.askdirectory(initialdir=last_path, mustexist=True,
                                              title='Select a directory where tag lists are located (rx_tags.json, rn_tags.json, etc.)'))
            if len(loc) > 0 and (not last_path or loc != last_path) and TagsDB.try_set_basepath(loc):
                setrootconf(Options.TAGLISTS_PATH, loc)
            else:
                setrootconf(Options.AUTOCOMPLETION_ENABLE, 0)
    else:
        TagsDB.clear()
        setrootconf(Options.TAGLISTS_PATH, '')


def trigger_autocomplete_tag() -> None:
    get_global(Globals.FIELD_TAGS).on_event_ctrl_space()


# globals
# ROOOT
root: AppRoot | None = None
rootFrame: BaseFrame | None = None
rootMenu: Menu | None = None
# windows
IS_WIN = sys.platform == PLATFORM_WINDOWS
window_log: LogWindow | None = None
window_proxy: ProxyWindow | None = None
window_hcookies: HeadersAndCookiesWindow | None = None
window_timeout: ConnectionTimeoutWindow | None = None
window_retries: ConnectionRetriesWindow | None = None
window_apikey: ApiKeyWindow | None = None
# counters
c_menu: BaseMenu | None = None
c_submenu: BaseMenu | None = None
# these containers keep technically unbound variables so they arent purged by GC
bool_vars: dict[str, BooleanVar] = {}
int_vars: dict[str, IntVar] = {}
string_vars: dict[str, StringVar] = {}
# end globals

# loaded
console_shown: bool = True
text_cmd: Text | None = None
# end loaded

# icons
icons: dict[Icons, PhotoImage | None] = dict.fromkeys(Icons.__members__.values())
# end icons

# GUI grid composition: current column / row universal counters (resettable)
c_col: int | None = None
c_row: int | None = None

#
#
#########################################
