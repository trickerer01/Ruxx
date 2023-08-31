# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from locale import getpreferredencoding
from threading import Lock as ThreadLock
from time import localtime, strftime
from typing import Optional, List
from tkinter import END, INSERT

# internal
from app_defines import DEFAULT_ENCODING
from app_gui_defines import STATE_NORMAL, STATE_DISABLED
from app_utils import find_first_not_of

__all__ = ('Logger', 'trace')


class Logger:
    print_lock = ThreadLock()

    pending_strings = []  # type: List[str]
    is_cmdline = False
    is_disabled = False
    wnd = None  # type: Optional['LogWindow']  # noqa F821

    @staticmethod
    def init(is_cmd: bool, is_disabled=False) -> None:
        Logger.is_cmdline = is_cmd
        Logger.is_disabled = is_disabled

    @staticmethod
    def _append(text: str) -> None:
        # current scrollbar position
        Logger.wnd.scroll.update()  # required to get actual pos
        old_pos = Logger.wnd.scroll.get()

        # appending to text is impossible if text is disabled
        Logger.wnd.text.config(state=STATE_NORMAL)
        Logger.wnd.text.insert(END, text)
        Logger.wnd.text.config(state=STATE_DISABLED)

        # scroll to bottom if was at the bottom
        if old_pos[1] >= 1.0:
            Logger.wnd.text.mark_set(INSERT, END)
            Logger.wnd.text.see(END)
            Logger.wnd.text.yview_moveto(1.0)

    @staticmethod
    def _prepare(text: str) -> None:
        if Logger.is_cmdline is True:
            # need to circumvent non-unicode console errors
            try:
                print(text)
            except UnicodeError:
                # print(f'message was: {bytearray(map(ord, text))}')
                try:
                    print(text.encode(DEFAULT_ENCODING).decode())
                except Exception:
                    try:
                        print(text.encode(DEFAULT_ENCODING).decode(getpreferredencoding()))
                    except Exception:
                        print('<Message was not logged due to UnicodeError>')
                finally:
                    print('Previous message caused UnicodeError...')
        else:
            Logger._append(f'{text}\n')

    @staticmethod
    def log(message: str, safe: bool, timestamp: bool) -> None:
        if Logger.is_disabled is True:
            return
        if len(message) == 0:
            return

        if timestamp is True:
            non_n_idx = find_first_not_of(message, '\n')
            textparts = (message[:non_n_idx], message[non_n_idx:]) if non_n_idx != -1 else ('', message)
            message = f'{textparts[0]}[{strftime("%X", localtime())}] {textparts[1]}'

        if safe:
            with Logger.print_lock:
                Logger._prepare(message)
        else:
            Logger._prepare(message)

    @staticmethod
    def print_pending_strings(safe=False, timestamp=False) -> None:
        for ps in Logger.pending_strings:
            Logger.log(ps, safe, timestamp)
        Logger.pending_strings.clear()


def trace(message: str, safe=False, timestamp=False) -> None:
    Logger.log(message, safe, timestamp)

#
#
#########################################
