# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from threading import Lock as ThreadLock
from time import localtime, strftime
from typing import Optional
from tkinter import END, INSERT

# internal
from app_gui_base import LogWindow
from app_gui_defines import STATE_NORMAL, STATE_DISABLED


class Logger:
    print_lock = ThreadLock()

    is_cmdline = False
    is_disabled = False
    wnd = None  # type: Optional[LogWindow]

    @staticmethod
    def init(is_cmd: bool, is_disabled: bool = False) -> None:
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
        # todo: add tests
        if old_pos[1] >= 1.0:
            Logger.wnd.text.mark_set(INSERT, END)
            Logger.wnd.text.see(END)
            Logger.wnd.text.yview_moveto(1.0)

    @staticmethod
    def _prepare(text: str) -> None:
        if Logger.is_cmdline is True:
            print(text)
        else:
            Logger._append(f'{text}\n')

    @staticmethod
    def log(message: str, safe: bool, timestamp: bool) -> None:
        if Logger.is_disabled is True:
            return
        if len(message) == 0:
            return

        if timestamp is True:
            non_n_idx = -1
            idx = 0
            while idx < len(message):
                if message[idx] != '\n':
                    non_n_idx = idx
                    break
                idx += 1

            textparts = (message[:non_n_idx], message[non_n_idx:]) if non_n_idx != -1 else ('', message)
            message = f'{textparts[0]}[{strftime("%X", localtime())}] {textparts[1]}'

        if safe:
            with Logger.print_lock:
                Logger._prepare(message)
        else:
            Logger._prepare(message)


def trace(message: str, safe: bool = False, timestamp: bool = False) -> None:
    Logger.log(message, safe, timestamp)

#
#
#########################################
